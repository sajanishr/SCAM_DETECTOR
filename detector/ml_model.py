import pandas as pd
import numpy as np
import re
import pickle
import os
from detector.naive_bayes_scratch import NaiveBayesAlgorithmFromScratch

class ScamDetector:
    """Naive Bayes from scratch for detecting scam offers"""
    def __init__(self):
        self.model = NaiveBayesAlgorithmFromScratch()
        self.is_trained = False
        self.classification_report_str = None
        self.load_model()

    def preprocess_text(self, text):
        # Use the same preprocessing as the scratch model
        return self.model.preprocess(text)

    def load_and_prepare_data(self, csv_path='spam.csv'):
        """Load and prepare the spam dataset"""
        try:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    break
                except Exception:
                    continue
            if df is None:
                raise Exception("Could not load CSV file with any encoding")
            # Rename columns for clarity
            df.columns = ['label', 'text'] + [f'col_{i}' for i in range(len(df.columns) - 2)]
            df = df.dropna(subset=['text'])
            # No need to map labels to 0/1, use 'ham'/'spam' as strings
            X = df['text'].tolist()
            y = df['label'].tolist()
            return X, y
        except Exception as e:
            print(f"Error loading data: {e}")
            return self._create_dummy_data()

    def _create_dummy_data(self):
        legitimate_texts = [
            "Hello, how are you doing today?",
            "Please confirm your appointment for tomorrow",
            "Your order has been shipped and will arrive soon",
            "Thank you for your purchase",
            "Meeting scheduled for 3 PM today",
            "Your account has been updated successfully",
            "Please review the attached document",
            "Happy birthday! Hope you have a great day",
            "The weather is nice today",
            "Looking forward to seeing you soon"
        ]
        scam_texts = [
            "CONGRATULATIONS! You've won $1000! Click here to claim",
            "URGENT: Your account has been suspended. Call now to verify",
            "FREE iPhone! Limited time offer. Text YES to claim",
            "You've been selected for a $5000 prize! Call immediately",
            "Your bank account needs verification. Click this link",
            "WINNER! You've won a luxury vacation. Claim now!",
            "URGENT: Your package is waiting. Click to track",
            "FREE money! You've been chosen for a cash prize",
            "Your computer has a virus. Call this number immediately",
            "CONGRATULATIONS! You're our lucky winner!"
        ]
        X = legitimate_texts + scam_texts
        y = ["ham"] * len(legitimate_texts) + ["spam"] * len(scam_texts)
        return X, y

    def train(self, csv_path='spam.csv', force_retrain=False):
        if self.is_trained and not force_retrain:
            return getattr(self, '_last_accuracy', 0.0)
        X, y = self.load_and_prepare_data(csv_path)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        accuracy = self.model.score(X_test, y_test)
        self._last_accuracy = accuracy
        self.is_trained = True
        self.save_model()
        from sklearn.metrics import classification_report
        y_pred = self.model.predict(X_test)
        print('DEBUG: First 10 true labels:', y_test[:10])
        print('DEBUG: First 10 predicted labels:', y_pred[:10])
        self.classification_report_str = classification_report(y_test, y_pred, target_names=['ham', 'spam'])
        return accuracy

    def get_classification_report(self):
        return getattr(self, 'classification_report_str', None)

    def predict(self, text):
        if not self.is_trained:
            self.train()
        # The model expects a list of texts
        pred, confidence, proba = self.model.predict([text], return_confidence=True)[0]
        # proba is a dict: {label: probability}
        is_scam = (pred == 'spam')
        return {
            'is_scam': is_scam,
            'confidence': confidence * 100,  # Convert to percentage
            'label': pred,
            'probability_ham': proba.get('ham', 0.0) * 100,  # Convert to percentage
            'probability_spam': proba.get('spam', 0.0) * 100  # Convert to percentage
        }

    def save_model(self, filepath='scam_detector_model.pkl'):
        # Save the model and last accuracy
        with open(filepath, 'wb') as f:
            pickle.dump({'model': self.model, '_last_accuracy': getattr(self, '_last_accuracy', 0.0)}, f)

    def load_model(self, filepath='scam_detector_model.pkl'):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        self.model = data.get('model', NaiveBayesAlgorithmFromScratch())
                        self._last_accuracy = data.get('_last_accuracy', 0.0)
                    else:
                        self.model = data
                        self._last_accuracy = 0.0
                self.is_trained = True
            except Exception:
                self.is_trained = False

def get_scam_detector():
    if not hasattr(get_scam_detector, '_instance'):
        get_scam_detector._instance = ScamDetector()
    return get_scam_detector._instance 