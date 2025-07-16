# Real-Time Processing

- `reddit_realtime_producer.py`: Streams new Reddit posts/comments to Kafka
- `spark_realtime_consumer.py`: Consumes and processes real-time data from Kafka
- `Dockerfile.realtime_producer`, `Dockerfile.realtime_consumer`: Dockerfiles for real-time mode

Run with Docker Compose using the `realtime` profile.
