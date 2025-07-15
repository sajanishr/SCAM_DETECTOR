from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from .forms import TextDetectionForm, ScamReportForm, UserRegistrationForm
from .models import DetectionHistory, ScamReport, ScamStatistics
from .ml_model import get_scam_detector


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    """Home page view"""
    if request.method == 'POST':
        form = TextDetectionForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            
            # Get scam detector and make prediction
            detector = get_scam_detector()
            result = detector.predict(text)
            
            # Save to detection history
            detection = DetectionHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                text=text,
                is_scam=result['is_scam'],
                confidence_score=result['confidence'],
                ip_address=get_client_ip(request)
            )
            
            # Update statistics
            today = timezone.now().date()
            stats, created = ScamStatistics.objects.get_or_create(date=today)
            stats.total_detections += 1
            if result['is_scam']:
                stats.scam_detections += 1
            else:
                stats.legitimate_detections += 1
            stats.save()
            
            # Add detection_id and user_feedback to result for template
            result['detection_id'] = detection.id
            result['user_feedback'] = detection.user_feedback
            
            return render(request, 'detector/home.html', {
                'form': form,
                'result': result,
                'analyzed_text': text
            })
    else:
        form = TextDetectionForm()
    
    # Get recent statistics
    try:
        today_stats = ScamStatistics.objects.get(date=timezone.now().date())
    except ScamStatistics.DoesNotExist:
        today_stats = None
    
    context = {
        'form': form,
        'today_stats': today_stats,
    }
    return render(request, 'detector/home.html', context)


def results_analysis(request):
    """Results and analysis page (user-specific)"""
    days = request.GET.get('days', 7)
    try:
        days = int(days)
    except ValueError:
        days = 7
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    # User-specific statistics and detections
    if request.user.is_authenticated:
        detections = DetectionHistory.objects.filter(
            user=request.user,
            detected_at__date__range=[start_date, end_date]
        ).order_by('-detected_at')
    else:
        detections = DetectionHistory.objects.filter(
            user=None,
            detected_at__date__range=[start_date, end_date]
        ).order_by('-detected_at')
    # Paginate detections
    paginator = Paginator(detections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Calculate summary statistics
    total_detections = detections.count()
    total_scams = detections.filter(is_scam=True).count()
    total_legitimate = detections.filter(is_scam=False).count()
    scam_percentage = (total_scams / total_detections * 100) if total_detections > 0 else 0

    # Calculate average confidence for scam and legitimate
    scam_confidences = []
    legitimate_confidences = []
    for d in detections:
        # Use the stored prediction output if available, otherwise recompute
        result = get_scam_detector().predict(d.text)
        if d.is_scam:
            scam_confidences.append(result['probability_spam'])
        else:
            legitimate_confidences.append(result['probability_ham'])
    avg_scam_conf = round(sum(scam_confidences)/len(scam_confidences), 3) if scam_confidences else None
    avg_legit_conf = round(sum(legitimate_confidences)/len(legitimate_confidences), 3) if legitimate_confidences else None

    context = {
        'page_obj': page_obj,
        'total_detections': total_detections,
        'total_scams': total_scams,
        'total_legitimate': total_legitimate,
        'scam_percentage': scam_percentage,
        'days': days,
        'date_range': f"Last {days} days",
        'avg_scam_conf': avg_scam_conf,
        'avg_legit_conf': avg_legit_conf,
    }
    return render(request, 'detector/results_analysis.html', context)


def detection_history(request):
    """Detection history page"""
    if request.user.is_authenticated:
        detections = DetectionHistory.objects.filter(user=request.user).order_by('-detected_at')
    else:
        detections = DetectionHistory.objects.filter(user=None).order_by('-detected_at')
    # Filter by scam type
    scam_filter = request.GET.get('filter')
    if scam_filter == 'scam':
        detections = detections.filter(is_scam=True)
    elif scam_filter == 'legitimate':
        detections = detections.filter(is_scam=False)
    # Paginate results
    paginator = Paginator(detections, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'scam_filter': scam_filter,
    }
    return render(request, 'detector/detection_history.html', context)


def report_scam(request):
    """Report a scam page"""
    if request.method == 'POST':
        form = ScamReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.ip_address = get_client_ip(request)
            report.save()
            
            messages.success(request, 'Thank you for reporting this scam. We will investigate it.')
            return redirect('detector:report_scam')
    else:
        form = ScamReportForm()
    
    # Get recent reports
    recent_reports = ScamReport.objects.all().order_by('-reported_at')[:5]
    
    context = {
        'form': form,
        'recent_reports': recent_reports,
    }
    return render(request, 'detector/report_scam.html', context)


def model_performance(request):
    """Model performance and classification report page"""
    detector = get_scam_detector()
    # Only retrain if not already trained
    if not detector.is_trained:
        accuracy = detector.train()
    else:
        accuracy = getattr(detector, '_last_accuracy', 0.0)
        # Ensure classification report is available
        if detector.get_classification_report() is None:
            # Regenerate classification report
            texts, labels = detector.load_and_prepare_data()
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
            y_pred = detector.model.predict(X_test)
            from sklearn.metrics import classification_report, recall_score
            detector.classification_report_str = classification_report(y_test, y_pred, target_names=['ham', 'spam'])
    print('DEBUG: detector._last_accuracy =', getattr(detector, '_last_accuracy', 'MISSING'))
    print('DEBUG: accuracy used for display =', accuracy)
    try:
        from sklearn.metrics import classification_report
        y_pred = None
        try:
            texts, labels = detector.load_and_prepare_data()
            total_samples = len(texts)
            legitimate_count = sum(1 for label in labels if label == 'ham')
            spam_count = sum(1 for label in labels if label == 'spam')
            legitimate_percentage = (legitimate_count / total_samples) * 100 if total_samples else 0
            spam_percentage = (spam_count / total_samples) * 100 if total_samples else 0
            classification_report_str = detector.get_classification_report()
        except Exception as e:
            total_samples = 0
            legitimate_count = 0
            spam_count = 0
            legitimate_percentage = 0
            spam_percentage = 0
            classification_report_str = None
        performance_data = {
            'accuracy': accuracy * 100,
            'accuracy_value': round(accuracy * 100, 1),
            'remaining_value': round(100 - (accuracy * 100), 1),
            'total_samples': total_samples,
            'legitimate_count': legitimate_count,
            'spam_count': spam_count,
            'legitimate_percentage': legitimate_percentage,
            'spam_percentage': spam_percentage,
            'feature_count': len(detector.model.vocab),
            'model_type': 'Multinomial Naive Bayes',
            'vectorizer_type': 'TF-IDF',
            'is_trained': detector.is_trained,
            'classification_report': classification_report_str
        }
    except Exception as e:
        performance_data = {
            'error': str(e),
            'accuracy': 0,
            'accuracy_value': 0,
            'remaining_value': 0,
            'total_samples': 0,
            'legitimate_count': 0,
            'spam_count': 0,
            'legitimate_percentage': 0,
            'spam_percentage': 0,
            'feature_count': 'N/A',
            'model_type': 'Naive Bayes (from scratch)',
            'vectorizer_type': 'Custom (in-code)',
            'is_trained': False,
            'classification_report': None
        }
    context = {
        'performance': performance_data,
    }
    print('DEBUG: Model Performance Data:', performance_data)  # Debug print
    return render(request, 'detector/model_performance.html', context)


def about(request):
    """About page"""
    return render(request, 'detector/about.html')


def how_it_works(request):
    """How it works page"""
    return render(request, 'detector/how_it_works.html')


def api_detect(request):
    """API endpoint for text detection"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            if not text:
                return JsonResponse({'error': 'Text is required'}, status=400)
            # Get scam detector and make prediction
            detector = get_scam_detector()
            result = detector.predict(text)
            # Save to detection history
            DetectionHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                text=text,
                is_scam=result['is_scam'],
                confidence_score=result['confidence'],
                ip_address=get_client_ip(request)
            )
            return JsonResponse({
                'success': True,
                'result': result,
                'text': text
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST method required'}, status=405)


def api_statistics(request):
    """API endpoint for statistics"""
    days = request.GET.get('days', 7)
    try:
        days = int(days)
    except ValueError:
        days = 7
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    stats = ScamStatistics.objects.filter(
        date__range=[start_date, end_date]
    ).values('date', 'total_detections', 'scam_detections', 'legitimate_detections')
    
    return JsonResponse({
        'success': True,
        'stats': list(stats),
        'days': days
    })


@require_POST
@csrf_exempt
def mark_detection_feedback(request):
    """AJAX endpoint to mark a detection as correct/incorrect"""
    try:
        data = json.loads(request.body)
        detection_id = data.get('detection_id')
        feedback = data.get('feedback')
        if feedback not in ['correct', 'incorrect']:
            return JsonResponse({'success': False, 'error': 'Invalid feedback value.'}, status=400)
        detection = DetectionHistory.objects.get(id=detection_id)
        detection.user_feedback = feedback
        detection.save()
        return JsonResponse({'success': True, 'feedback': feedback})
    except DetectionHistory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Detection not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            return redirect('detector:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'detector/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    # User detection stats
    detections = DetectionHistory.objects.filter(user=user)
    total_detections = detections.count()
    scam_count = detections.filter(is_scam=True).count()
    legitimate_count = detections.filter(is_scam=False).count()
    feedback_correct = detections.filter(user_feedback='correct').count()
    feedback_incorrect = detections.filter(user_feedback='incorrect').count()
    recent_detections = detections.order_by('-detected_at')[:5]
    return render(request, 'detector/profile.html', {
        'user': user,
        'total_detections': total_detections,
        'scam_count': scam_count,
        'legitimate_count': legitimate_count,
        'feedback_correct': feedback_correct,
        'feedback_incorrect': feedback_incorrect,
        'recent_detections': recent_detections,
    })


@login_required
@require_POST
def clear_history(request):
    DetectionHistory.objects.filter(user=request.user).delete()
    messages.success(request, 'Your detection history has been cleared.')
    return redirect('detector:detection_history') 