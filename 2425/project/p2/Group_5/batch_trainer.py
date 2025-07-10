#!/usr/bin/env python3
import os
import re
import pickle

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from elasticsearch import Elasticsearch

from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer as SparkTokenizer, HashingTF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline as SparkPipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import classification_report

from tensorflow.keras.preprocessing.text import Tokenizer as KerasTokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# ─── Configuration ──────────────────────────────────────────────────────────────
ES_HOST          = 'http://elasticsearch:9200'
ES_INDEX         = 'news_articles_batch_uncleaned'
SPARK_MODEL_DIR  = "models/spark_lr_model"
LSTM_MODEL_PATH  = "models/keras_lstm_model.h5" 
TOKENIZER_PATH   = "models/keras_tokenizer.pkl"

VOCAB_SIZE = 5000
MAXLEN     = 100
EMBED_DIM  = 128
LSTM_UNITS = 128
BATCH_SIZE = 64
EPOCHS     = 10

# ─── NLTK Setup ─────────────────────────────────────────────────────────────────
stop_words = set(stopwords.words('english'))
stemmer    = PorterStemmer()
sia        = SentimentIntensityAnalyzer()

# ─── Preprocessing Functions ────────────────────────────────────────────────────
def clean_and_tokenize_for_spark(text: str) -> str:
    """Clean for Spark (stopwords + stemming)."""
    text = re.sub(r'[^A-Za-z0-9\s]', '', text).lower()
    tokens = word_tokenize(text)
    filtered = [w for w in tokens if w not in stop_words]
    stemmed = [stemmer.stem(w) for w in filtered]
    return " ".join(stemmed)

def clean_and_tokenize_for_lstm(text: str) -> str:
    """Clean for LSTM (preserve stopwords)."""
    text = re.sub(r'[^A-Za-z0-9\s]', '', text).lower()
    return text

def sentiment_label(text: str) -> str:
    """Use VADER to assign positive/neutral/negative."""
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:
        return 'positive'
    elif score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

# ─── Elasticsearch Fetch ────────────────────────────────────────────────────────
def fetch_from_es():
    print(f"[Batch] Connecting to ES at {ES_HOST}, index='{ES_INDEX}'", flush=True)
    es = Elasticsearch(ES_HOST)
    resp = es.search(index=ES_INDEX, size=10000, body={"query": {"match_all": {}}}, scroll='2m')
    sid  = resp['_scroll_id']
    hits = resp['hits']['hits']
    all_docs = hits.copy()

    while hits:
        resp = es.scroll(scroll_id=sid, scroll='2m')
        sid  = resp['_scroll_id']
        hits = resp['hits']['hits']
        all_docs.extend(hits)

    print(f"[Batch] Fetched {len(all_docs)} documents from ES.", flush=True)
    return [d['_source'] for d in all_docs]

# ─── Spark Model ────────────────────────────────────────────────────────────────
def train_and_save_spark_model(df: pd.DataFrame):
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import Tokenizer as SparkTokenizer, CountVectorizer, IDF
    from pyspark.ml.classification import LogisticRegression
    from pyspark.ml import Pipeline as SparkPipeline
    from pyspark.ml.evaluation import MulticlassClassificationEvaluator

    print("[Spark] Starting SparkSession...", flush=True)
    spark = SparkSession.builder \
        .appName("NewsMLPipeline") \
        .config("spark.jars.packages", "org.elasticsearch:elasticsearch-spark-30_2.12:7.17.21") \
        .getOrCreate()

    # Optional: Balance the dataset
    print("[Spark] Rebalancing training data (upsampling minority classes)...", flush=True)
    majority_df = df[df["sentiment_numeric"] == 2]
    minority_df = df[df["sentiment_numeric"] != 2]
    resampled_df = pd.concat([
        majority_df,
        minority_df.sample(n=len(majority_df), replace=True, random_state=42)
    ])

    # Create Spark DataFrame from resampled data
    sdf = spark.createDataFrame(resampled_df[["processed_text_spark", "sentiment_numeric"]]) \
               .withColumnRenamed("processed_text_spark", "processed_text")

    # Define pipeline: Tokenizer → CountVectorizer → IDF → LogisticRegression
    tokenizer = SparkTokenizer(inputCol="processed_text", outputCol="words")
    cv        = CountVectorizer(inputCol="words", outputCol="rawFeatures", vocabSize=10000)
    idf       = IDF(inputCol="rawFeatures", outputCol="features")
    lr        = LogisticRegression(featuresCol="features", labelCol="sentiment_numeric", maxIter=50)

    pipeline = SparkPipeline(stages=[tokenizer, cv, idf, lr])

    # Train-test split and model training
    print("[Spark] Training Logistic Regression with TF-IDF...", flush=True)
    train, test = sdf.randomSplit([0.8, 0.2], seed=42)
    model = pipeline.fit(train)

    # Evaluation
    print("[Spark] Evaluating model...", flush=True)
    preds = model.transform(test)
    evaluator = MulticlassClassificationEvaluator(
        labelCol="sentiment_numeric", predictionCol="prediction", metricName="accuracy"
    )
    acc = evaluator.evaluate(preds)
    print(f"[Spark] Test Accuracy = {acc:.4f}", flush=True)

    # Full classification report using sklearn
    y_true = preds.select("sentiment_numeric").rdd.flatMap(lambda x: x).collect()
    y_pred = preds.select("prediction").rdd.flatMap(lambda x: x).collect()
    print("[Spark] Classification Report:")
    print(classification_report(y_true, y_pred, target_names=["negative", "neutral", "positive"]))

    # Save the model
    os.makedirs(os.path.dirname(SPARK_MODEL_DIR), exist_ok=True)
    model.write().overwrite().save(SPARK_MODEL_DIR)
    print(f"[Spark] Model saved to {SPARK_MODEL_DIR}", flush=True)

    spark.stop()

# ─── Keras LSTM Model ───────────────────────────────────────────────────────────
def train_and_save_keras_lstm(df: pd.DataFrame):
    texts  = df["processed_text_lstm"].tolist()
    labels = df["sentiment_numeric"].values

    kt = KerasTokenizer(num_words=VOCAB_SIZE)
    kt.fit_on_texts(texts)
    seqs = kt.texts_to_sequences(texts)
    X    = pad_sequences(seqs, maxlen=MAXLEN)
    y    = labels

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    print("[Keras] Training 3-class LSTM...", flush=True)
    model = Sequential([
        Embedding(input_dim=VOCAB_SIZE, output_dim=EMBED_DIM, input_length=MAXLEN),
        LSTM(LSTM_UNITS, dropout=0.2, recurrent_dropout=0.2),
        Dense(3, activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    es_cb = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)
    model.fit(X_train, y_train, validation_data=(X_test, y_test),
              epochs=EPOCHS, batch_size=BATCH_SIZE, callbacks=[es_cb], verbose=2)

    # Evaluate and print classification report
    y_pred = model.predict(X_test).argmax(axis=1)
    print("[Keras] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['negative', 'neutral', 'positive']))

    os.makedirs(os.path.dirname(LSTM_MODEL_PATH), exist_ok=True)
    model.save(LSTM_MODEL_PATH)
    with open(TOKENIZER_PATH, "wb") as f:
        pickle.dump(kt, f)
    print(f"[Keras] Model saved to {LSTM_MODEL_PATH}", flush=True)
    print(f"[Keras] Tokenizer saved to {TOKENIZER_PATH}", flush=True)

# ─── Main ───────────────────────────────────────────────────────────────────────
def main():
    docs = fetch_from_es()
    if not docs:
        print("[Batch] No documents found. Exiting.", flush=True)
        return

    df = pd.DataFrame(docs)

    # Preprocess + label
    df["combined_text"] = df["title"].fillna("") + " " + df["description"].fillna("")
    df["processed_text_spark"] = df["combined_text"].apply(clean_and_tokenize_for_spark)
    df["processed_text_lstm"]  = df["combined_text"].apply(clean_and_tokenize_for_lstm)
    df["sentiment_label"]      = df["processed_text_lstm"].apply(sentiment_label)
    df["sentiment_numeric"]    = df["sentiment_label"].map({'negative': 0, 'neutral': 1, 'positive': 2})

    print("[Batch] Label distribution:")
    print(df["sentiment_label"].value_counts())

    # Train models
    train_and_save_spark_model(df)
    train_and_save_keras_lstm(df)

if __name__ == "__main__":
    main()
