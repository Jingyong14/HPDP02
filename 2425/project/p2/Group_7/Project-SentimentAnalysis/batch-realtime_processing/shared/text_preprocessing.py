
from pyspark.sql.functions import lower, regexp_replace, trim
from pyspark.sql.functions import col, when

def preprocess_text(df):
    """
    Applies the same text cleaning logic used during model training.
    """
    cleaned_df = df.withColumn("text_content",
                                     when(col("content").isNotNull(), col("content"))
                                     .otherwise(col("title"))) \
                          .withColumn("clean_text", lower(col("text_content"))) \
                          .withColumn("clean_text", regexp_replace(col("clean_text"),
                                     r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "")) \
                          .withColumn("clean_text", regexp_replace(col("clean_text"), r"@[A-Za-z0-9_]+", "")) \
                          .withColumn("clean_text", regexp_replace(col("clean_text"), r"#[A-Za-z0-9_]+", "")) \
                          .withColumn("clean_text", regexp_replace(col("clean_text"), r"[^a-zA-Z0-9\s]", "")) \
                          .withColumn("clean_text", regexp_replace(col("clean_text"), r"\s+", " ")) \
                          .withColumn("clean_text", trim(col("clean_text"))) \
                          .filter(col("clean_text") != "")
    return cleaned_df
