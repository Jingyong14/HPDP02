#!/usr/bin/env python
# coding: utf-8

# In[21]:


import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download the lexicon once
nltk.download('vader_lexicon')

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Load your CSV file
df = pd.read_csv('cleaned_data.csv')

# Function to classify sentiment from compound score
def get_sentiment_label(text):
    if not isinstance(text, str) or text.strip() == "":
        return 'neutral'  # handle empty or missing text gracefully
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:
        return 'positive'
    elif score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

# Apply the function on 'preprocessed_content' column to create 'label'
df['label'] = df['preprocessed_content'].apply(get_sentiment_label)

# Optional: save the updated DataFrame to a new CSV
df.to_csv('cleaned_data_with_labels.csv', index=False)

# Check output
print(df[['preprocessed_content', 'label']].head(10))


# In[23]:


import matplotlib.pyplot as plt

# Count the number of each label
label_counts = df['label'].value_counts()
print(label_counts)

# Optional: show percentages
print("\nPercentage distribution:")
print(label_counts / len(df) * 100)

# Plot as bar chart
label_counts.plot(kind='bar', color=['green', 'gray', 'red'])
plt.title('Sentiment Label Distribution')
plt.xlabel('Sentiment')
plt.ylabel('Number of Samples')
plt.xticks(rotation=0)
plt.show()


# In[ ]:




