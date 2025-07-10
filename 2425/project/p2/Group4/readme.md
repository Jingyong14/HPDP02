
# Real-Time Sentiment Analysis Using Apache Spark and Kafka

## Project Overview
This project implements a real-time sentiment analysis system using **Apache Spark**, **Apache Kafka**, and **Elasticsearch**. The system analyzes **IMDB movie reviews** in both **batch** and **real-time** modes to predict sentiment (positive or negative) with a hybrid data processing architecture. The project also leverages **Docker** and **Docker Compose** to containerize the system and ensure environment consistency across development and production setups.

## Technologies Used
- **Apache Spark**: Distributed data processing and machine learning model training.
- **Apache Kafka**: Real-time message broker for streaming data.
- **Elasticsearch**: Storage and fast querying of sentiment analysis results.
- **Kibana**: Visualization tool for real-time sentiment dashboards.
- **Docker**: Containerization for environment consistency and scalability.
- **PySpark**: Python API for Apache Spark to facilitate sentiment analysis model development.

## Key Features
- **Batch Processing**: Trains and evaluates sentiment models on historical IMDB movie review data.
- **Real-Time Processing**: Processes incoming IMDB reviews in real-time, using Kafka for data ingestion and Spark for prediction.
- **Dockerized Architecture**: All components (Kafka, Spark, Elasticsearch, Kibana) are containerized for easy setup and scaling.
- **Visualization**: Kibana provides real-time dashboards for visualizing sentiment trends and model performance.

## System Architecture
The system architecture integrates **batch** and **real-time** processing pipelines:

### Batch Processing
- Trains two models (Logistic Regression and Naive Bayes) using PySpark.
- Performs sentiment analysis on a fixed dataset of IMDB reviews.
- Stores predictions in **Elasticsearch** for easy querying and visualization.

### Real-Time Processing
- Scrapes real-time IMDB reviews using a web scraper.
- Streams review data into **Apache Kafka**, which is then consumed by **Apache Spark** for sentiment prediction.
- Real-time predictions are stored in **Elasticsearch** and visualized using **Kibana**.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/sentiment-analysis.git
cd sentiment-analysis
```

### 2. Install Docker and Docker Compose
Make sure Docker and Docker Compose are installed. Follow the instructions from the official [Docker website](https://www.docker.com/get-started) for installation.

### 3. Docker Compose Setup
Run the following command to set up the environment:

```bash
docker-compose up
```

This command will start all necessary services, including Apache Kafka, Apache Spark, Elasticsearch, and Kibana.

### 4. Running the Sentiment Analysis
#### Batch Processing
To run the batch processing pipeline:

```bash
spark-submit --class org.apache.spark.examples.SentimentAnalysis --master local[4] batch_sentiment_analysis.py
```

#### Real-Time Processing
To run the real-time sentiment analysis pipeline:

```bash
spark-submit --class org.apache.spark.examples.RealtimeSentimentAnalysis --master local[4] realtime_sentiment_analysis.py
```

### 5. Access Kibana Dashboard
Once the system is running, navigate to `http://localhost:5601` to access the Kibana dashboard. Here, you can visualize sentiment trends and performance metrics.

## Results

### Batch Processing
- The batch sentiment analysis model achieved an accuracy of **82.4%**.
- Predictions were indexed into **Elasticsearch** for easy querying.

### Real-Time Processing
- The real-time sentiment prediction system provided insights with low-latency results, immediately displaying sentiment analysis on new movie reviews.

## Optimization & Comparison

### Optimization Strategies
- Docker was used to containerize services for easier deployment and scalability.
- **Apache Spark** provided distributed processing for large-scale data handling, while **Apache Kafka** ensured real-time data ingestion.

### Comparison of Batch vs. Real-Time Processing
- Batch processing handled historical data and was optimized for accuracy.
- Real-time processing prioritized low-latency predictions but faced challenges in handling nuances in sentiment detection.

## Future Work
- **Model Improvement**: Address data imbalance using resampling techniques or implement advanced deep learning models.
- **Real-time Adaptation**: Integrate online learning for incremental model updates.
- **Scalability**: Transition to a cluster-based deployment using **YARN** or **Kubernetes** for larger datasets.
- **User Interaction**: Enhance the Kibana dashboard with more interactive features and user feedback loops.

## Conclusion
This project successfully demonstrates the practical application of modern big data technologies to perform sentiment analysis on IMDB movie reviews in both batch and real-time modes. The hybrid architecture and containerization ensure the system is scalable and efficient, ready for real-world use cases.

