from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json, lower, regexp_replace, trim
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.ml import PipelineModel
from elasticsearch import Elasticsearch, helpers

def send_to_es(df: DataFrame, epoch_id: int):
    if df.count() == 0:
        return

    print(f"--- Batch {epoch_id} ---")
    records = df.toPandas().to_dict("records")

    actions = [{"_index": "imdb_sentiment_stream_results", "_source": r} for r in records]

    try:
        es = Elasticsearch(hosts=["http://es01:9200"])
        helpers.bulk(es, actions)
        print(f"✅ Successfully sent {len(records)} records to Elasticsearch.")
    except Exception as e:
        print(f"❌ Error sending to Elasticsearch: {e}")

spark = SparkSession.builder.appName("IMDB Streaming Prediction").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

print("✅ SparkSession started.")

model_path = "./imdb_sentiment_model"
model = PipelineModel.load(model_path)
print(f"✅ Model loaded from {model_path}")

KAFKA_TOPIC = "imdb_topic"
KAFKA_SERVER = "kafka:9093"

schema = StructType([StructField("text", StringType(), True)])
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

parsed_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

cleaned_df = parsed_df.withColumn("text", lower(col("text"))) \
    .withColumn("text", regexp_replace(col("text"), r"[^a-zA-Z\s]", "")) \
    .withColumn("text", trim(col("text")))

predictions = model.transform(cleaned_df)
final_df = predictions.select("text", col("prediction").alias("sentiment"))

query = final_df.writeStream \
    .outputMode("append") \
    .foreachBatch(send_to_es) \
    .start()

print("✅ Streaming started. Waiting for data...")
query.awaitTermination()