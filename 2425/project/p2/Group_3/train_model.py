#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Load labeled data
df = pd.read_csv('data/cleaned_data_with_labels.csv')
df = df.dropna(subset=['preprocessed_content', 'label'])  # Ensure no NaNs

# Features and labels
X = df['preprocessed_content'].fillna("")
y = df['label']

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)

# Train model
clf = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
clf.fit(X_train_vec, y_train)

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Print label mapping
print("Label mapping (LabelEncoder.classes_):", list(le.classes_))

# Save model and vectorizer
os.makedirs('model', exist_ok=True)
joblib.dump(clf, 'model/logistic_model.pkl')
joblib.dump(vectorizer, 'model/tfidf_vectorizer.pkl')
joblib.dump(le, 'model/label_encoder.pkl')

print("✅ Model and vectorizer saved to model/")


# In[ ]:




