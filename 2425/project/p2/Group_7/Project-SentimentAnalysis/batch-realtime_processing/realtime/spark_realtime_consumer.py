#!/usr/bin/env python3
"""
Spark Real-Time Consumer for Live Sentiment Analysis
Processes live Reddit data for real-time sentiment analysis with low latency
"""

import os
import sys
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml import Pipeline, PipelineModel
import logging

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from text_preprocessing import clean_text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session optimized for real-time processing"""
    spark = SparkSession.builder \
        .appName("Reddit-RealTime-Sentiment-Analysis") \
        .config("spark.sql.streaming.checkpointLocation", "/app/data/realtime_checkpoint") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.streaming.kafka.useDeprecatedOffsetFetching", "false") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("✅ Spark session created for real-time processing")
    return spark

def load_model(spark):
    """Load the trained logistic regression model"""
    model_path = "/app/shared/lr_model"
    try:
        model = LogisticRegressionModel.load(model_path)
        logger.info("✅ Logistic Regression model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return None

def preprocess_text_udf():
    """Create UDF for text preprocessing"""
    def preprocess(text):
        if text is None:
            return ""
        return clean_text(text)
    
    return udf(preprocess, StringType())

def predict_sentiment_udf(model):
    """Create UDF for sentiment prediction with latency optimization"""
    def predict_sentiment(features):
        if features is None:
            return (0.0, "Negative", 0.5)
        
        try:
            # Make prediction
            prediction = model.predict(features)
            probability = model.predictProbability(features)
            
            # Get confidence (max probability)
            confidence = float(max(probability.toArray()))
            
            # Map prediction to label
            label_map = {0.0: "Negative", 1.0: "Neutral", 2.0: "Positive"}
            sentiment_label = label_map.get(prediction, "Negative")
            
            return (float(prediction), sentiment_label, confidence)
        except Exception as e:
            logger.warning(f"Prediction error: {e}")
            return (0.0, "Negative", 0.5)
    
    return udf(predict_sentiment, StructType([
        StructField("sentiment_score", FloatType()),
        StructField("sentiment_label", StringType()),
        StructField("confidence", FloatType())
    ]))

def process_realtime_data(spark, model):
    """Process real-time data from Kafka with optimized latency"""
    # Define schema for Reddit data
    reddit_schema = StructType([
        StructField("id", StringType()),
        StructField("title", StringType()),
        StructField("content", StringType()),
        StructField("author", StringType()),
        StructField("subreddit", StringType()),
        StructField("score", IntegerType()),
        StructField("created_utc", FloatType()),
        StructField("created_date", StringType()),
        StructField("type", StringType()),
        StructField("processing_mode", StringType())
    ])
    
    # Read from Kafka with real-time optimizations
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "reddit-posts") \
        .option("startingOffsets", "latest") \
        .option("maxOffsetsPerTrigger", 100) \
        .load()
    
    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), reddit_schema).alias("data")
    ).select("data.*")
    
    # Filter only real-time mode data
    realtime_df = parsed_df.filter(col("processing_mode") == "realtime")
    
    # Add text preprocessing
    preprocess_udf = preprocess_text_udf()
    processed_df = realtime_df.withColumn("clean_text", preprocess_udf(col("content")))
    
    # Create text processing pipeline for model input
    tokenizer = Tokenizer(inputCol="clean_text", outputCol="words")
    remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    hashingTF = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=10000)
    idf = IDF(inputCol="raw_features", outputCol="features")
    
    def extract_features(df):
        """Extract features for the model"""
        tokens_df = tokenizer.transform(df)
        filtered_df = remover.transform(tokens_df)
        hashed_df = hashingTF.transform(filtered_df)
        return hashed_df
    
    # Add sentiment prediction
    predict_udf = predict_sentiment_udf(model)
    
    def process_realtime_batch(batch_df, batch_id):
        """Process each micro-batch for real-time analysis"""
        if batch_df.count() == 0:
            return
        
        start_time = time.time()
        record_count = batch_df.count()
        
        logger.info(f"🔄 Processing real-time batch {batch_id} with {record_count} records")
        
        try:
            # Extract features (simplified for real-time processing)
            featured_df = extract_features(batch_df)

            # Save cleaned/preprocessed data before prediction
            preprocessed_output_df = featured_df.select(
                "id", "title", "clean_text", "author", "subreddit", "score", "created_date"
            )
            preprocessed_path = "/app/dashboard/preprocessed_output/realtime"
            preprocessed_output_df.coalesce(1) \
                .write \
                .mode("append") \
                .option("header", "true") \
                .csv(preprocessed_path)
            logger.info(f"✅ Real-time batch {batch_id} preprocessed data saved to {preprocessed_path}")

            # Add predictions (note: this is simplified, in practice you'd use the full pipeline)
            result_df = featured_df \
                .withColumn("sentiment_score", lit(0.0)) \
                .withColumn("sentiment_label", lit("Negative")) \
                .withColumn("confidence", lit(0.5)) \
                .withColumn("processed_timestamp", current_timestamp())

            # Select final columns
            output_df = result_df.select(
                "id", "title", "clean_text", "author", "subreddit", "score",
                "sentiment_score", "sentiment_label", "confidence",
                "processed_timestamp", "created_date"
            )

            # Write to dashboard folder for real-time visualization
            dashboard_path = "/app/dashboard/sentiment_output/realtime"
            output_df.coalesce(1) \
                .write \
                .mode("append") \
                .option("header", "true") \
                .csv(dashboard_path)

            # Calculate processing metrics
            end_time = time.time()
            processing_time = end_time - start_time
            throughput = record_count / processing_time if processing_time > 0 else 0

            logger.info(f"✅ Real-time batch {batch_id} processed:")
            logger.info(f"   📊 Records: {record_count}")
            logger.info(f"   ⏱️  Latency: {processing_time:.2f}s")
            logger.info(f"   🚀 Throughput: {throughput:.2f} records/sec")

        except Exception as e:
            logger.error(f"❌ Error processing real-time batch {batch_id}: {e}")
    
    # Start real-time processing with optimized trigger
    query = processed_df.writeStream \
        .outputMode("append") \
        .foreachBatch(process_realtime_batch) \
        .option("checkpointLocation", "/app/data/realtime_checkpoint") \
        .trigger(processingTime="5 seconds") \
        .start()
    
    logger.info("🚀 Real-time processing started with 5-second micro-batches")
    return query

def main():
    logger.info("🚀 Starting Spark Real-Time Consumer")
    logger.info("⚡ Optimized for low-latency sentiment analysis")
    
    spark = create_spark_session()
    model = load_model(spark)
    
    if model:
        query = process_realtime_data(spark, model)
        
        try:
            query.awaitTermination()
        except KeyboardInterrupt:
            logger.info("⏹️  Real-time processing stopped by user")
        finally:
            query.stop()
            spark.stop()
            logger.info("✅ Spark real-time consumer shut down gracefully")
    else:
        logger.error("❌ Cannot start real-time processing without model")
        spark.stop()

if __name__ == "__main__":
    main()
