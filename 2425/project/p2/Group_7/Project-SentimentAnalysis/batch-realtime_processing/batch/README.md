# Batch Processing

- `reddit_batch_producer.py`: Produces historical Reddit data to Kafka
- `spark_batch_consumer.py`: Consumes and processes batch data from Kafka
- `Dockerfile.batch_producer`, `Dockerfile.batch_consumer`: Dockerfiles for batch mode

Run with Docker Compose using the `batch` profile.
