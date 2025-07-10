#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install langdetect')


# In[22]:


import pandas as pd
import re
import nltk
from langdetect import detect
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from tqdm import tqdm

# One-time NLTK downloads
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load CSV
df = pd.read_csv('combined_raw_data.csv')

# Drop duplicate URLs
df = df.drop_duplicates(subset='url', keep='first')

# Filter English rows using langdetect
def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False

# Only keep English content
df = df[df['content'].apply(lambda x: isinstance(x, str) and is_english(x))].reset_index(drop=True)

# Prepare stopwords and lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Clean and preprocess content
def clean_text(text):
    # Lowercase
    text = text.lower()
    # Remove URLs, non-alphabetic chars, punctuation, digits
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)

# Apply cleaning
tqdm.pandas(desc="Cleaning content")
df['preprocessed_content'] = df['content'].progress_apply(clean_text)

# Optional: Save cleaned CSV
df[['preprocessed_content']].to_csv('cleaned_data.csv', index=False)


# In[24]:


print(df[['preprocessed_content']].head())


# In[26]:


df.shape


# In[ ]:




