import os
import json
import time
import joblib
import nltk
import numpy as np
import psutil # New import for resource usage
import sys    # New import for sys.stderr

from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel

# --- Configuration for Metrics ---
THROUGHPUT_REPORT_INTERVAL_SECONDS = 30 # Report throughput every N seconds
MEMORY_REPORT_INTERVAL_RECORDS = 100   # Report memory every N records

print("[Startup] Downloading NLTK resources...")
# (downloads only the first time; quiet to reduce console noise)
# nltk.download('stopwords', quiet=True)
# nltk.download('punkt', quiet=True)
# nltk.download('vader_lexicon', quiet=True) # VADER for batch_trainer, but useful for general NLTK setup
stop_words = set(nltk.corpus.stopwords.words('english'))

def clean_and_tokenize(text):
    import re
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

inv_label_map = {2: 'positive', 1: 'neutral', 0: 'negative'}

print("[Startup] Loading models and tokenizer...")
try:
    # Load Spark model (whole pipeline)
    # Get or create SparkSession (important for PySpark inside Docker)
    spark = SparkSession.builder.appName("predictor").getOrCreate()
    spark_model = PipelineModel.load('models/spark_lr_model')
    print("   - Spark Logistic Regression Pipeline loaded.")

    # Load Keras LSTM model and tokenizer
    with open('models/keras_tokenizer.pkl', 'rb') as f:
        tokenizer = joblib.load(f)
    print("   - Keras Tokenizer loaded.")
    lstm_model = load_model('models/keras_lstm_model.h5')
    print("   - Keras LSTM model loaded.")
except Exception as e:
    print(f"[Startup][Error] Failed to load models: {e}", file=sys.stderr)
    sys.exit(1) # Use sys.exit(1) for cleaner exit on startup error
print("[Startup] All models loaded successfully.")

KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_STREAM_TOPIC', 'live_news_stream')

print(f"[Startup] Connecting to Elasticsearch at http://elasticsearch:9200 ...", flush=True)
try:
    es = Elasticsearch('http://elasticsearch:9200')
    if not es.ping():
        raise Exception("Elasticsearch is not reachable!")
    print("[Startup] Connected to Elasticsearch successfully.", flush=True)
except Exception as e:
    print(f"[Startup][Error] Cannot connect to Elasticsearch: {e}", file=sys.stderr)
    sys.exit(1)

print(f"[Startup] Connecting to Kafka at {KAFKA_BOOTSTRAP} (topic: '{KAFKA_TOPIC}') ...", flush=True)
try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id="news_predict_group"
    )
    print("[Startup] Kafka consumer created. Waiting for messages ...", flush=True)
except Exception as e:
    print(f"[Startup][Error] Cannot connect to Kafka: {e}", file=sys.stderr)
    sys.exit(1)

# --- Performance Metrics Setup ---
total_records_processed = 0
overall_start_time = time.perf_counter()
last_throughput_report_time = overall_start_time

process = psutil.Process(os.getpid()) # Get current process for memory usage

for msg in consumer:
    article = msg.value
    title = article.get('title', '')
    description = article.get('description', '')
    link = article.get('link', '')
    text = f"{title} {description}".strip()
    print(f"\n[Kafka] Received new article: {title} ({link})")
    processed = clean_and_tokenize(text)
    print("   [Predict] Text cleaned and tokenized.")

    # --- Logistic Regression using PySpark Pipeline ---
    lr_start_time = time.perf_counter()
    test_df = spark.createDataFrame([{"processed_text": processed}])
    predictions_lr_spark = spark_model.transform(test_df)
    # Collect prediction and probability
    lr_result = predictions_lr_spark.select("prediction", "probability").first()
    pred_lr = int(lr_result["prediction"])
    pred_lr_prob_vector = lr_result["probability"] # This is a Spark ML Vector
    # Convert Spark ML Vector to Python list for easier logging
    # pred_lr_probs will be a list of floats (e.g., [0.1, 0.2, 0.7] for 3 classes)
    pred_lr_probs = list(pred_lr_prob_vector) if hasattr(pred_lr_prob_vector, 'toArray') else pred_lr_prob_vector.tolist()
    lr_end_time = time.perf_counter()
    lr_latency_ms = (lr_end_time - lr_start_time) * 1000
    # FIX IS HERE: Removed :.4f as pred_lr_probs is a list
    print(f"   [Predict][Spark LR] Prediction: {inv_label_map.get(pred_lr, pred_lr)} (Probabilities: {pred_lr_probs})")
    print(f"   [Predict][Spark LR] Latency: {lr_latency_ms:.2f} ms")


    # --- LSTM ---
    lstm_start_time = time.perf_counter()
    seq = tokenizer.texts_to_sequences([processed])
    pad = pad_sequences(seq, maxlen=100)
    lstm_probabilities = lstm_model.predict(pad, verbose=0)[0]
    pred_lstm = int(np.argmax(lstm_probabilities))
    lstm_end_time = time.perf_counter()
    lstm_latency_ms = (lstm_end_time - lstm_start_time) * 1000
    print(f"   [Predict][LSTM] Prediction: {inv_label_map.get(pred_lstm, pred_lstm)} (Probabilities: {lstm_probabilities})")
    print(f"   [Predict][LSTM] Latency: {lstm_latency_ms:.2f} ms")


    total_records_processed += 1

    result = {
        'title': title,
        'description': description,
        'link': link,
        'text': text,
        'processed': processed,
        'logreg_pred': pred_lr,
        'logreg_pred_text': inv_label_map.get(pred_lr, 'unknown'),
        'logreg_probabilities': pred_lr_probs, # Store probabilities
        'logreg_latency_ms': lr_latency_ms,     # Store latency
        'lstm_pred': pred_lstm,
        'lstm_pred_text': inv_label_map.get(pred_lstm, 'unknown'),
        'lstm_probabilities': lstm_probabilities.tolist(), # Store probabilities as list
        'lstm_latency_ms': lstm_latency_ms,       # Store latency
        '@timestamp': datetime.now(timezone.utc).isoformat()
    }

    try:
        es.index(index='live_predictions', body=result)
        print("   [Elasticsearch] Prediction result saved successfully.\n")
    except Exception as e:
        print(f"   [Elasticsearch][Error] Failed to save prediction: {e}\n", file=sys.stderr)

    # --- Throughput Reporting ---
    current_time = time.perf_counter()
    elapsed_overall_time = current_time - overall_start_time

    if (current_time - last_throughput_report_time) >= THROUGHPUT_REPORT_INTERVAL_SECONDS:
        overall_throughput = total_records_processed / elapsed_overall_time
        print(f"\n--- Performance Report ({datetime.now().strftime('%H:%M:%S')}) ---", flush=True)
        print(f"  Total Records Processed: {total_records_processed}", flush=True)
        print(f"  Overall Throughput: {overall_throughput:.2f} records/sec", flush=True)

        # --- Resource Usage ---
        # Note: This measures the Python process's memory. For full Docker container CPU/RAM, use `docker stats`.
        mem_info = process.memory_info()
        rss_mb = mem_info.rss / (1024 * 1024) # Resident Set Size in MB
        vms_mb = mem_info.vms / (1024 * 1024) # Virtual Memory Size in MB
        print(f"  Current Python Process Memory (RSS): {rss_mb:.2f} MB", flush=True)
        print(f"  Current Python Process Memory (VMS): {vms_mb:.2f} MB", flush=True)

        print("-------------------------------------------\n", flush=True)
        last_throughput_report_time = current_time

print("[Shutdown] Exiting streamPredict.")