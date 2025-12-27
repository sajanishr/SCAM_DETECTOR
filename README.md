# Scam Detection System

A web-based Scam Detection System designed to identify fraudulent or scam emails using Machine Learning and Natural Language Processing (NLP) techniques.
The system allows users to manually paste email content and receive instant predictions on whether the email is a scam or legitimate.
This group project was developed for the partial fulfillment of the requirements for the 7th semester of B.Sc. CSIT at Bhaktapur Multiple Campus, Tribhuvan University by Sajani Shrestha, Sujisha Shankhadev, and Ruben Makrati.

## Features

🔍 Detects scam or legitimate emails from pasted text

🧠 Machine Learning–based classification

📊 Detection history and statistics tracking

👤 User authentication (login & registration)

📈 Model performance and accuracy display

📝 Scam reporting feature

## Algorithms Used

1.Text Preprocessing Algorithm
-Tokenization
-Stop-word removal
-Lowercasing and noise removal

2.TF-IDF Vectorization
-Converts text into numerical feature vectors
-Highlights important and rare scam-related terms

3.Multinomial Naive Bayes
-Probabilistic classifier suitable for text data
-Fast and efficient for large datasets

## Technology Stack

Frontend: HTML,CSS,JavaScript

Backend: Django (Python)

Database: SQLite / PostgreSQL

Machine Learning: Scikit-learn,TF-IDF,Naive Bayes

## Prerequisites

Before running the Scam Detection System, ensure that the following requirements are met:

* Python 3.8 or above – Required to run Django and machine learning libraries

* pip (Python Package Manager) – For installing dependencies

* Django Framework – Backend web framework

* Basic knowledge of Python and Django

* Web Browser – Google Chrome, Firefox, or any modern browser

* Virtual Environment (Recommended) – To manage dependencies

* Machine Learning Libraries:
  
   scikit-learn, numpy, pandas

* Database:
SQLite (default) or PostgreSQL


## Steps to Run the Project

1. Clone the repository
git clone https://github.com/your-username/scam-detection-system.git

2. Navigate to the project directory
cd scam-detection-system

3. Install dependencies
pip install -r requirements.txt

4. Run migrations
python manage.py migrate

5. Start the server
python manage.py runserver

## How the System Works

1. User pastes suspicious email content into the web application

2. Text is preprocessed to remove noise

3. TF-IDF converts text into numerical vectors

4. Naive Bayes classifier predicts scam or legitimate

5. Result is displayed with confidence score

6. Detection is stored for history and analysis
