# Real-Time Sentiment Analysis Pipeline using Apache Spark and Kafka

> **See the main `../readme.md` for full pipeline instructions, Docker usage, and deliverables.**

A complete real-time sentiment analysis system that processes Malaysian social media data (Reddit) using Apache Spark for big data processing and Apache Kafka for real-time streaming. The system implements machine learning models for sentiment classification and provides interactive dashboards for visualization.

## 🎯 Project Overview

This project implements a scalable real-time sentiment analysis pipeline with the following key features:
- **Data Collection**: Reddit API integration for Malaysian-relevant content
- **Real-time Processing**: Apache Kafka for data streaming
- **Machine Learning**: Multiple sentiment models (Naive Bayes, Logistic Regression) 
- **Big Data Processing**: Apache Spark for scalable data processing
- **Visualization**: Elasticsearch + Kibana dashboards
- **Model Comparison**: Batch vs Real-time processing performance analysis

## 📁 Project Structure

```
Project-SentimentAnalysis/
├── README.md                           # This file
├── data/
│   ├── raw_data/                      # Raw Reddit data (JSONL format)
│   └── cleaned_data.csv               # Processed data sample
├── notebooks/
│   ├── preprocessing.ipynb            # Data cleaning and feature engineering (80/20 split)
│   └── model_training.ipynb           # Model training and comparison
├── kafka_spark_pipeline/
│   ├── kafka_producer.py              # Reddit data producer
│   └── spark_streaming.py             # Real-time sentiment processing
├── dashboard/
│   ├── elastic_mappings.json          # Elasticsearch index mappings
│   └── kibana_visualizations.ndjson   # Dashboard configurations
├── reports/
│   ├── final_report.pdf               # Comprehensive project report
│   └── presentation_slides.pptx       # Presentation materials
└── requirements.txt                    # Python dependencies
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Setup Reddit API credentials in .env.local
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret  
REDDIT_PASSWORD=your_password
```

### 2. Data Preprocessing and Model Training
```bash
# Run preprocessing notebook (creates 80/20 train/test split)
jupyter notebook notebooks/preprocessing.ipynb

# Train and compare models (Naive Bayes vs Logistic Regression)
jupyter notebook notebooks/model_training.ipynb
```

### 3. Start Real-time Pipeline
```bash
# Start Kafka and pipeline services
docker-compose up -d

# Monitor pipeline
docker-compose logs -f reddit-producer
docker-compose logs -f spark-streaming
```

## 🤖 Machine Learning Models

The system implements and compares multiple sentiment analysis approaches:

### Models Implemented:
- **Naive Bayes**: Fast, interpretable baseline model
- **Logistic Regression**: Linear model with regularization
- *(Future)* **LSTM**: Deep learning approach for sequential data

### Performance Metrics:
- Accuracy, Precision, Recall, F1-Score
- Confusion Matrix Analysis  
- ROC Curve Analysis
- **Batch vs Real-time Processing Comparison**

### Data Split:
- **Training**: 80% of labeled data
- **Testing**: 20% of labeled data
- Models evaluated on holdout test set

## 📊 Real-time Processing Pipeline

### Architecture:
1. **Data Collection**: Reddit API → Raw JSONL files
2. **Stream Processing**: Kafka Producer → Kafka Topic → Spark Streaming
3. **Sentiment Analysis**: Trained ML models applied in real-time
4. **Storage**: Results stored in Elasticsearch
5. **Visualization**: Kibana dashboards for live monitoring

### Performance Analysis:
- **Real-time Latency**: How fast can individual posts be processed?
- **Batch Throughput**: How many posts can be processed per minute?
- **Model Accuracy**: Consistent performance across batch vs streaming modes

## 🎛️ Dashboard Features

The Kibana dashboard provides:
- **Sentiment Distribution**: Pie charts showing positive/negative/neutral ratios
- **Sentiment Over Time**: Time series analysis of sentiment trends
- **Word Clouds**: Most frequent positive and negative terms
- **Real-time Stream**: Live sentiment classification results
- **Performance Metrics**: System throughput and latency monitoring

## 🛠️ Technical Stack

- **Big Data**: Apache Spark 3.3+, Apache Kafka
- **Machine Learning**: scikit-learn, Spark MLlib
- **NLP**: NLTK, spaCy for text preprocessing
- **Storage**: Elasticsearch for search and analytics
- **Visualization**: Kibana for interactive dashboards
- **Infrastructure**: Docker for containerization
- **Data Source**: Reddit API (r/Malaysia, Malaysian content)

## 📈 Model Performance Comparison

The project evaluates models across two key dimensions:

### 1. Model Accuracy Comparison
| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Naive Bayes | TBD | TBD | TBD | TBD |
| Logistic Regression | TBD | TBD | TBD | TBD |

### 2. Processing Mode Comparison  
| Metric | Batch Processing | Real-time Processing |
|--------|------------------|---------------------|
| Throughput | TBD posts/min | TBD posts/min |
| Latency | TBD seconds | TBD milliseconds |
| Accuracy | TBD% | TBD% |

## 🔧 Troubleshooting

### Common Issues:
- **Kafka Connection**: Ensure Kafka is running on localhost:9092
- **Spark Memory**: Increase driver/executor memory for large datasets
- **Reddit API**: Check API credentials and rate limits
- **Elasticsearch**: Verify ES cluster is running and accessible

### Debugging:
```bash
# Check service logs
docker-compose logs [service-name]

# Test Reddit API connection
python test_reddit_auth.py

# Verify Kafka topics
kafka-topics.sh --list --bootstrap-server localhost:9092
```

## 👥 Team Information

**Project Team**: [Your Team Name]
**Members**: [List team members]
**Course**: Real-Time Big Data Analytics
**Submission**: June 27, 2025

## 📄 Deliverables

- [x] Complete source code and configuration files
- [x] Trained ML models with performance comparison
- [x] Real-time streaming pipeline implementation  
- [x] Interactive dashboard with visualizations
- [ ] Final comprehensive report (reports/final_report.pdf)
- [ ] Presentation slides (reports/presentation_slides.pptx)

---

**Note**: This project implements the required 80/20 train/test split and compares multiple ML approaches as specified in the project requirements. The pipeline supports both batch and real-time processing modes for comprehensive performance analysis.
