import numpy as np
import re
from collections import defaultdict, Counter

class NaiveBayesAlgorithmFromScratch:
    def __init__(self):
        self.class_priors = {}         # P(class)
        self.word_counts = {}          # {class: {word: count}}
        self.class_word_totals = {}    # {class: total_words_in_class}
        self.vocab = set()             # All unique words
        self.fitted = False

    def preprocess(self, text):
        # Lowercase, remove non-letters, split into words
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        words = text.split()
        return words

    def fit(self, X, y):
        """
        X: list of text samples
        y: list of class labels (e.g., 'spam' or 'ham')
        """
        label_counts = Counter(y)
        total_samples = len(y)
        self.class_priors = {label: count / total_samples for label, count in label_counts.items()}
        self.word_counts = {label: defaultdict(int) for label in label_counts}
        self.class_word_totals = {label: 0 for label in label_counts}
        self.vocab = set()

        for text, label in zip(X, y):
            words = self.preprocess(text)
            for word in words:
                self.word_counts[label][word] += 1
                self.class_word_totals[label] += 1
                self.vocab.add(word)
        self.fitted = True

    def predict(self, X, return_confidence=False):
        """
        X: list of text samples
        Returns: list of predicted class labels
        """
        if not self.fitted:
            raise Exception("Model not trained. Call fit() first.")
        predictions = []
        confidences = []
        proba = self.predict_proba(X)
        for i, probs in enumerate(proba):
            best_label = max(probs, key=probs.get)
            predictions.append(best_label)
            confidences.append(probs[best_label])
        if return_confidence:
            return list(zip(predictions, confidences, proba))
        return predictions

    def predict_proba(self, X):
        if not self.fitted:
            raise Exception("Model not trained. Call fit() first.")
        results = []
        vocab_size = len(self.vocab)
        for text in X:
            words = self.preprocess(text)
            log_probs = {}
            for label in self.class_priors:
                log_prob = np.log(self.class_priors[label])
                for word in words:
                    word_count = self.word_counts[label].get(word, 0)
                    log_prob += np.log((word_count + 1) / (self.class_word_totals[label] + vocab_size))
                log_probs[label] = log_prob
            # Convert log-probs to probabilities
            max_log = max(log_probs.values())
            exp_probs = {label: np.exp(log_probs[label] - max_log) for label in log_probs}
            total = sum(exp_probs.values())
            probs = {label: exp_probs[label] / total for label in exp_probs}
            results.append(probs)
        return results

    def score(self, X, y):
        """
        Returns accuracy on the given data.
        """
        preds = self.predict(X)
        correct = sum(p == t for p, t in zip(preds, y))
        return correct / len(y) 