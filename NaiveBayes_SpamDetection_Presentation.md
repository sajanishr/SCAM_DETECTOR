# Naive Bayes Spam Detection: From Scratch

## 1. Motivation
- **Spam detection** is a classic text classification problem.
- **Naive Bayes** is a simple, effective, and interpretable algorithm for this task.
- Implementing it from scratch (no ML libraries) demonstrates deep understanding and transparency.

---

## 2. How Does Naive Bayes Work?
- **Bayes' Theorem:**
  - Calculates the probability of a class (e.g., spam) given the words in a message.
- **"Naive" Assumption:**
  - Assumes all words are independent given the class (not true, but works well!).

---

## 3. Step-by-Step Process

### **A. Training**
1. **Preprocess Text:**
   - Lowercase, remove non-letters, split into words.
2. **Count:**
   - For each class (spam/ham), count how many times each word appears.
   - Count total words and messages per class.
3. **Calculate Probabilities:**
   - Class prior: P(class) = #messages in class / total messages
   - Word likelihood: P(word|class) = (word count in class + 1) / (total words in class + vocab size)

### **B. Prediction**
1. **Preprocess new message.**
2. **For each class:**
   - Start with log(P(class)).
   - For each word, add log(P(word|class)).
3. **Choose the class with the highest score.**
4. **Convert scores to probabilities for confidence.**

---

## 4. Visual Diagram

```mermaid
graph TD;
    A[Training Data] --> B[Preprocess Text];
    B --> C[Count Words per Class];
    C --> D[Calculate Class Priors];
    D --> E[Store Vocabulary];
    E --> F[Model is Trained];

    G[New Message] --> H[Preprocess Text];
    H --> I[For Each Class: Calculate Log-Probability];
    I --> J[Add Log(Prior) + Log(Word Likelihoods)];
    J --> K[Convert Log-Probabilities to Probabilities];
    K --> L[Choose Class with Highest Probability];
    L --> M[Output Prediction & Confidence];
```

---

## 5. Why This Approach?
- **Transparency:** Every step is visible and explainable.
- **No black-box ML libraries.**
- **Educational:** Shows the math and logic behind spam detection.
- **Customizable:** Easy to tweak or extend for new features.

---

## 6. Example

| Label | Message                  |
|-------|--------------------------|
| ham   | see you at lunch         |
| spam  | win money now            |
| ham   | let's meet for lunch     |
| spam  | claim your free money    |

- For a new message: "win free lunch"
- Calculate P(spam|message) and P(ham|message)
- Choose the class with the higher probability

---

## 7. Key Takeaways
- **Naive Bayes is simple, fast, and effective for text.**
- **From-scratch implementation** proves understanding and control.
- **Model is now fully explainable and auditable.**

---

*Prepared by: [Your Name]* 