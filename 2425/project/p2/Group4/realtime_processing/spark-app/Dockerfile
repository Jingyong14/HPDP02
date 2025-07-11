# 1. Start from the latest official Jupyter image with PySpark.
FROM jupyter/pyspark-notebook:latest

# 2. This image runs as user 'jovyan'. Switch to root for installations.
USER root

# 3. Set the working directory
WORKDIR /home/jovyan/work

# 4. Copy requirements.txt into container and install Python packages
COPY --chown=jovyan:users requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 5. Copy trained model and real-time prediction script
# 👇 FIXED: model now copied directly from realtime_processing/imdb_sentiment_model
COPY --chown=jovyan:users ../imdb_sentiment_model ./imdb_sentiment_model
COPY --chown=jovyan:users realtime_prediction.py .

# 6. Copy producers
COPY --chown=jovyan:users fake_streaming.py .
COPY --chown=jovyan:users real_producer_imdb_scraper.py .

# 7. Switch back to the default non-root user
USER jovyan

# 8. Start the Spark streaming prediction app
CMD ["/usr/local/spark/bin/spark-submit", \
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.5.3", \
    "realtime_prediction.py"]
