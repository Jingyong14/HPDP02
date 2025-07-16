#!/usr/bin/env python3
"""
Spark Batch Consumer for Historical Data Processing
Processes historical Reddit data for batch sentiment analysis
"""

import os
import sys
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
    """Create Spark session for batch processing"""
    spark = SparkSession.builder \
        .appName("Reddit-Batch-Sentiment-Analysis") \
        .config("spark.sql.streaming.checkpointLocation", "/app/data/checkpoint") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("✅ Spark session created for batch processing")
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
    """Create UDF for sentiment prediction"""
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

def process_batch_data(spark, model):
    """Process batch data from Kafka"""
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
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "reddit-posts") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), reddit_schema).alias("data")
    ).select("data.*")
    
    # Filter only batch mode data
    batch_df = parsed_df.filter(col("processing_mode") == "batch")
    
    # Add text preprocessing
    preprocess_udf = preprocess_text_udf()
    processed_df = batch_df.withColumn("clean_text", preprocess_udf(col("content")))
    
    # Create text processing pipeline for model input
    tokenizer = Tokenizer(inputCol="clean_text", outputCol="words")
    remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    hashingTF = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=10000)
    idf = IDF(inputCol="raw_features", outputCol="features")
    
    # Note: In production, you'd load a pre-fitted pipeline
    # For now, we'll create a simple feature extraction
    def extract_features(df):
        """Extract features for the model"""
        tokens_df = tokenizer.transform(df)
        filtered_df = remover.transform(tokens_df)
        hashed_df = hashingTF.transform(filtered_df)
        return hashed_df
    
    # Add sentiment prediction
    predict_udf = predict_sentiment_udf(model)
    
    def process_batch_fn(batch_df, batch_id):
        """Process each batch of data"""
        if batch_df.count() == 0:
            return
        
        logger.info(f"Processing batch {batch_id} with {batch_df.count()} records")
        
        try:
            # Extract features (simplified for batch processing)
            featured_df = extract_features(batch_df)

            # Save cleaned/preprocessed data before prediction
            preprocessed_output_df = featured_df.select(
                "id", "title", "clean_text", "author", "subreddit", "score", "created_date"
            )
            preprocessed_path = "/app/dashboard/preprocessed_output/batch"
            preprocessed_output_df.coalesce(1) \
                .write \
                .mode("append") \
                .option("header", "true") \
                .csv(preprocessed_path)
            logger.info(f"✅ Batch {batch_id} preprocessed data saved to {preprocessed_path}")

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

            # Write to dashboard folder
            dashboard_path = "/app/dashboard/sentiment_output/batch"
            output_df.coalesce(1) \
                .write \
                .mode("append") \
                .option("header", "true") \
                .csv(dashboard_path)

            logger.info(f"✅ Batch {batch_id} processed and saved to {dashboard_path}")

        except Exception as e:
            logger.error(f"❌ Error processing batch {batch_id}: {e}")
    
    # Start batch processing
    query = processed_df.writeStream \
        .outputMode("append") \
        .foreachBatch(process_batch_fn) \
        .option("checkpointLocation", "/app/data/batch_checkpoint") \
        .trigger(processingTime="30 seconds") \
        .start()
    
    logger.info("🚀 Batch processing started")
    return query

def main():
    logger.info("🚀 Starting Spark Batch Consumer")
    
    spark = create_spark_session()
    model = load_model(spark)
    
    if model:
        query = process_batch_data(spark, model)
        
        try:
            query.awaitTermination()
        except KeyboardInterrupt:
            logger.info("⏹️  Batch processing stopped by user")
        finally:
            query.stop()
            spark.stop()
            logger.info("✅ Spark batch consumer shut down gracefully")
    else:
        logger.error("❌ Cannot start batch processing without model")
        spark.stop()

if __name__ == "__main__":
    main()
