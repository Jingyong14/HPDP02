from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, udf
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer
from pyspark.ml.classification import LogisticRegression, NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.linalg import Vector
from pyspark.sql.types import StringType, IntegerType
from datetime import datetime

def train_and_evaluate(model, trainingData, testData, name):
    pipeline = Pipeline(stages=[
        Tokenizer(inputCol="text", outputCol="words"),
        StopWordsRemover(inputCol="words", outputCol="filtered"),
        CountVectorizer(inputCol="filtered", outputCol="features"),
        model
    ])
    model_fit = pipeline.fit(trainingData)
    predictions = model_fit.transform(testData)

    evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy"
    )
    accuracy = evaluator.evaluate(predictions)
    return model_fit, predictions, accuracy

def main():
    spark = SparkSession.builder \
        .appName("IMDB Sentiment Analysis - Model Comparison") \
        .config("spark.jars.packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0") \
        .getOrCreate()

    try:
        raw_data = spark.read.option("header", "true").csv("IMDB Dataset.csv")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        spark.stop()
        return

    if "sentiment" not in raw_data.columns or "review" not in raw_data.columns:
        print("❌ Required columns 'sentiment' or 'review' are missing.")
        spark.stop()
        return

    data = raw_data.withColumn("label", when(col("sentiment") == "positive", 1).otherwise(0)) \
                   .withColumnRenamed("review", "text")

    trainingData, testData = data.randomSplit([0.8, 0.2], seed=42)

    # Train both models
    print("\n📌 Training Logistic Regression...")
    lr_model, lr_preds, lr_acc = train_and_evaluate(LogisticRegression(labelCol="label", featuresCol="features"),
                                                    trainingData, testData, "Logistic Regression")

    print("📌 Training Naive Bayes...")
    nb_model, nb_preds, nb_acc = train_and_evaluate(NaiveBayes(labelCol="label", featuresCol="features"),
                                                    trainingData, testData, "Naive Bayes")

    # Print results
    print("\n📊 Model Performance Comparison:")
    print(f"🔹 Logistic Regression Accuracy : {lr_acc:.4f}")
    print(f"🔹 Naive Bayes Accuracy         : {nb_acc:.4f}")

    # Choose best model
    if lr_acc >= nb_acc:
        best_model, best_preds, best_name, best_acc = lr_model, lr_preds, "Logistic Regression", lr_acc
    else:
        best_model, best_preds, best_name, best_acc = nb_model, nb_preds, "Naive Bayes", nb_acc

    print(f"\n✅ Selected Best Model: {best_name}")
    print(f"🎯 Accuracy: {best_acc:.4f}")

    # Save model
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = f"/tmp/imdb_sentiment_model_{best_name.replace(' ', '_').lower()}_{timestamp}"
    try:
        best_model.write().overwrite().save(model_path)
        print(f"📁 Model saved to: {model_path}")
    except Exception as e:
        print(f"❌ Error saving model: {e}")

    # Format for Elasticsearch
    vec_to_str = udf(lambda v: str(v) if isinstance(v, Vector) else None, StringType())
    best_preds = best_preds.withColumn("probability_str", vec_to_str("probability"))
    best_preds = best_preds.withColumn("label", col("label").cast(IntegerType())) \
                           .withColumn("prediction", col("prediction").cast(IntegerType()))
    final_df = best_preds.select("text", "label", "prediction", "probability_str")

    es_write_conf = {
        "es.nodes": "es01",
        "es.port": "9200",
        "es.resource": "imdb_sentiment_test_results",
        "es.nodes.wan.only": "true",
    }

    try:
        final_df.write \
            .format("org.elasticsearch.spark.sql") \
            .options(**es_write_conf) \
            .mode("overwrite") \
            .save()
        print("✅ Predictions written to Elasticsearch.")
    except Exception as e:
        print(f"❌ Error writing to Elasticsearch: {e}")

    spark.stop()

if __name__ == "__main__":
    main()
