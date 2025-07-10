#!/usr/bin/env python
# coding: utf-8

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, pandas_udf, current_timestamp
from pyspark.sql.types import StructType, StringType
import joblib
import pandas as pd
import re
import json
from elasticsearch import Elasticsearch
import logging

# Initialize logging for debug info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SparkStreamer")

# Start Spark Session
spark = SparkSession.builder.appName("FMTNewsSentimentAnalysis").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Define Kafka message schema
schema = StructType() \
    .add("id", StringType()) \
    .add("source", StringType()) \
    .add("category_rss", StringType()) \
    .add("title", StringType()) \
    .add("link", StringType()) \
    .add("summary", StringType()) \
    .add("full_content", StringType()) \
    .add("authors", StringType())

# Load trained model and vectorizer
model = joblib.load("/opt/spark-apps/model/logistic_model.pkl")
vectorizer = joblib.load("/opt/spark-apps/model/tfidf_vectorizer.pkl")
le = joblib.load("/opt/spark-apps/model/label_encoder.pkl")

# Preprocessing function
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Make sure NLTK resources are downloaded (once)
nltk.data.path.append("/opt/spark-apps/nltk_data")  # or wherever you mounted them in Docker

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www.\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]
    return " ".join(tokens)


# Inference function
def predict_sentiment(text):
    try:
        cleaned = preprocess(text)
        vec = vectorizer.transform([cleaned])
        prediction = model.predict(vec)[0]
        label_map = {i: label for i, label in enumerate(le.classes_)}
        return label_map.get(prediction, "unknown")
    except Exception as e:
        logger.error(f"Prediction error on text: {text[:50]}... - {e}")
        return "error"

# Define a Pandas UDF
@pandas_udf(StringType())
def predict_udf(content_series: pd.Series) -> pd.Series:
    def safe_predict(text):
        try:
            return predict_sentiment(text)
        except Exception as e:
            logger.error(f"❌ UDF crashed for input: {text[:50]} - {e}")
            return "error"
    return content_series.apply(safe_predict)


# Read from Kafka topic
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "fmtnews") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()


# Parse Kafka messages
df_json = df_raw.selectExpr("CAST(value AS STRING)")
df_data = df_json.select(from_json(col("value"), schema).alias("data")).select("data.*")
df_data = df_data.filter(col("id").isNotNull())  # Skip malformed rows

# Add sentiment prediction
df_result = df_data.withColumn("predicted_sentiment", predict_udf(col("full_content"))).coalesce(1)
df_result_with_timestamp = df_result.withColumn("timestamp", current_timestamp())
df_result_filtered = df_result_with_timestamp.filter(col("predicted_sentiment") != "error")

# Define output paths
csv_output_path = "/opt/spark-apps/output/sentiment_predictions"
checkpoint_path = "/opt/spark-apps/output/checkpoints"

# Write to CSV (single file per batch)
query_csv = df_result_filtered.writeStream \
    .outputMode("append") \
    .format("csv") \
    .option("path", csv_output_path) \
    .option("checkpointLocation", checkpoint_path) \
    .start()

# Function to send batch to Elasticsearch
def send_to_elasticsearch(df, epoch_id):
    es = Elasticsearch("http://elasticsearch:9200")
    try:
        rows = df.toJSON().collect()
        for row_json in rows:
            doc = json.loads(row_json)
            es.index(index="fmt_sentiment", document=doc)
        logger.info(f"Indexed batch {epoch_id} to Elasticsearch with {len(rows)} docs.")
    except Exception as e:
        logger.error(f"Elasticsearch error in batch {epoch_id}: {e}")

# Write to Elasticsearch
query_es = df_result_filtered.writeStream \
    .foreachBatch(send_to_elasticsearch) \
    .outputMode("append") \
    .start()

# Print status of active streams
for q in spark.streams.active:
    print(f"Query name: {q.name}, id: {q.id}, status: {q.status}")

# Keep job alive
spark.streams.awaitAnyTermination()
