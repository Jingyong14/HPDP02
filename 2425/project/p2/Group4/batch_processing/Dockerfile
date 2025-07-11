# Use Bitnami Spark base image
FROM bitnami/spark:3.5

# Set working directory
WORKDIR /app

# Copy all files from local batch_processing folder into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy custom Spark config
COPY spark-defaults.conf /opt/bitnami/spark/conf/

# Run Spark batch job
CMD ["spark-submit", "--packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.4", "project2_code.py"]
