#!/usr/bin/env python3
"""
Spark Streaming Consumer for Real-time Reddit Sentiment Analysis
Consumes Reddit data from Kafka and applies trained sentiment models in real-time
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, lit, when, udf, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType, TimestampType, DoubleType
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, StopWordsRemover
from pyspark.ml import Pipeline
from text_preprocessing import preprocess_text

def create_spark_session(app_name="Reddit_Sentiment_Streaming"):
    """
    Initialize Spark Session with Kafka integration
    """
    print(f"🚀 Creating SparkSession for {app_name}...")
    
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.4.2") \
        .config("spark.sql.streaming.checkpointLocation", "../data/checkpoint") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    print("✅ Spark Session created successfully")
    return spark

def define_reddit_schema():
    """
    Define schema for Reddit data from Kafka - updated to match actual data format
    """
    return StructType([
        StructField("id", StringType(), True),
        StructField("title", StringType(), True),
        StructField("content", StringType(), True),
        StructField("score", LongType(), True),
        StructField("num_comments", LongType(), True),
        StructField("created_utc", DoubleType(), True),  # Changed to DoubleType for timestamp
        StructField("created_date", StringType(), True),
        StructField("author", StringType(), True),
        StructField("subreddit", StringType(), True),
        StructField("url", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("fetch_method", StringType(), True),
        StructField("content_type", StringType(), True),  # Keep optional for new data
        StructField("parent_post_id", StringType(), True)  # Keep optional for new data
    ])

def load_trained_model(model_path, model_type):
    """
    Load the trained sentiment analysis model
    """
    try:
        print(f"📦 Loading {model_type} model from {model_path}...")
        
        if model_type.lower() == "logistic_regression":
            model = LogisticRegressionModel.load(model_path)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        print(f"✅ {model_type} model loaded successfully")
        return model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def create_text_preprocessing_pipeline():
    """
    Create the same preprocessing pipeline used in training
    """
    print("🔧 Creating text preprocessing pipeline...")
    
    tokenizer = Tokenizer(inputCol="clean_text", outputCol="words")
    stop_words_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    hashing_tf = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=10000)
    idf = IDF(inputCol="raw_features", outputCol="features")
    
    pipeline = Pipeline(stages=[tokenizer, stop_words_remover, hashing_tf, idf])
    
    print("✅ Preprocessing pipeline created")
    return pipeline

def process_reddit_stream(spark, kafka_servers="localhost:9092", topic="reddit-posts"):
    """
    Process Reddit data stream with sentiment analysis
    """
    print(f"📡 Starting to read from Kafka topic: {topic}")
    
    # Define schema
    reddit_schema = define_reddit_schema()
    
    # Read from Kafka
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON data
    parsed_df = kafka_df.select(
        col("key").cast("string").alias("kafka_key"),
        col("value").cast("string").alias("kafka_value"),
        col("timestamp").alias("kafka_timestamp")
    ).select(
        col("kafka_key"),
        col("kafka_timestamp"),
        from_json(col("kafka_value"), reddit_schema).alias("data")
    ).select(
        col("kafka_key"),
        col("kafka_timestamp"),
        col("data.*")
    )
    
    # Clean text data using the imported function
    cleaned_df = preprocess_text(parsed_df)
    
    return cleaned_df

def apply_sentiment_analysis(df, model, preprocessing_pipeline):
    """
    Apply sentiment analysis to the streaming data
    """
    print("🤖 Applying sentiment analysis...")
    
    # Apply preprocessing pipeline
    processed_df = preprocessing_pipeline.transform(df)
    
    # Apply sentiment model
    predictions_df = model.transform(processed_df)
    
    # Add sentiment labels
    labeled_df = predictions_df.withColumn("sentiment_label",
                                          when(col("prediction") == 0, "Negative")
                                          .when(col("prediction") == 1, "Neutral")
                                          .when(col("prediction") == 2, "Positive")
                                          .otherwise("Unknown"))
    
    # Add confidence score (max probability)
    confidence_udf = udf(lambda prob: float(max(prob)) if prob else 0.0, DoubleType())
    labeled_df = labeled_df.withColumn("confidence", confidence_udf(col("probability")))
    
    # Select final columns for output
    result_df = labeled_df.select(
        col("id"),
        col("title"),
        col("clean_text"),
        col("author"),
        col("subreddit"),
        col("score"),
        col("prediction").alias("sentiment_score"),
        col("sentiment_label"),
        col("confidence"),
        col("kafka_timestamp").alias("processed_timestamp"),
        col("created_date")
    )
    
    return result_df

def write_to_console(df, output_mode="append"):
    """
    Write streaming results to console for monitoring
    """
    return df.writeStream \
             .outputMode(output_mode) \
             .format("console") \
             .option("truncate", False) \
             .option("numRows", 10) \
             .trigger(processingTime='10 seconds')

def write_to_dashboard(df, output_path="../dashboard/sentiment_results.csv"):
    """
    Write streaming results to a CSV file for dashboard visualization.
    """
    print(f"[DEBUG] Writing streaming results to dashboard at: {output_path}")
    return df.writeStream \
        .outputMode("append") \
        .format("csv") \
        .option("path", output_path) \
        .option("header", True) \
        .option("checkpointLocation", "../data/checkpoint/dashboard_csv") \
        .trigger(processingTime='10 seconds')


def write_to_kafka_output(df, kafka_servers="localhost:9092", output_topic="sentiment_results"):
    """
    Write sentiment results back to Kafka for downstream processing
    """
    return df.select(
        col("id").alias("key"),
        to_json(struct("*")).alias("value")
    ).writeStream \
     .format("kafka") \
     .option("kafka.bootstrap.servers", kafka_servers) \
     .option("topic", output_topic) \
     .option("checkpointLocation", "../data/checkpoint/kafka_output") \
     .outputMode("append")

def main():
    """
    Main streaming application
    """
    print("🎯 Starting Reddit Sentiment Analysis Streaming Pipeline")
    print("=" * 60)
    
    # Configuration
    KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    INPUT_TOPIC = "reddit-posts"
    OUTPUT_TOPIC = "sentiment_results"
    MODEL_TYPE = "logistic_regression"
    MODEL_PATH = "./lr_model"
    DASHBOARD_PATH = "/app/dashboard/sentiment_output"
    
    # Initialize Spark
    spark = create_spark_session()
    
    try:
        # Load trained model
        model = load_trained_model(MODEL_PATH, MODEL_TYPE)
        if model is None:
            print("❌ Failed to load model. Exiting...")
            return
        
        # Create preprocessing pipeline
        preprocessing_pipeline = create_text_preprocessing_pipeline()
        
        # Process streaming data
        streaming_df = process_reddit_stream(spark, KAFKA_SERVERS, INPUT_TOPIC)
        
        # Fit the preprocessing pipeline on a dummy empty dataframe to create a transformer
        # This is a workaround because we can't fit on a stream.
        # The IDF model will be empty, but it will create the 'features' column.
        empty_df = spark.createDataFrame([("",)], ["clean_text"])
        fitted_pipeline = preprocessing_pipeline.fit(empty_df)
        
        # Apply sentiment analysis
        sentiment_df = apply_sentiment_analysis(streaming_df, model, fitted_pipeline)
        
        # Set up output streams
        console_query = write_to_console(sentiment_df).start()
        dashboard_query = write_to_dashboard(sentiment_df, DASHBOARD_PATH).start()
        
        print("✅ Streaming pipeline started successfully!")
        print("📊 Monitoring Reddit sentiment in real-time...")
        print("🔍 Check console output for sentiment analysis results")
        print(f"📂 Dashboard data is being written to: {DASHBOARD_PATH}")
        print("💡 Press Ctrl+C to stop the pipeline")
        
        # Wait for termination
        spark.streams.awaitAnyTermination()
        
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline stopped by user")
        
    except Exception as e:
        print(f"❌ Error in streaming pipeline: {e}")
        
    finally:
        # Stop Spark session
        spark.stop()
        print("👋 Spark session stopped")

if __name__ == "__main__":
    main()
