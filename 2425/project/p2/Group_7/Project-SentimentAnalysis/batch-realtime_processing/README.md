# Real-Time and Batch Sentiment Analysis Pipeline

## 🎯 Overview

This project implements a comprehensive sentiment analysis pipeline that processes Reddit data from Malaysian subreddits using Apache Kafka and Spark. The system supports both **batch processing** (historical data analysis) and **real-time processing** (live data monitoring).

## 📁 Project Structure

```
Project-SentimentAnalysis/
├── batch-realtime_processing/
│   ├── batch/                     # Batch processing components
│   │   ├── reddit_batch_producer.py       # Fetches Jan 2025 historical data
│   │   ├── spark_batch_consumer.py        # Processes batch data with high throughput
│   │   ├── Dockerfile.batch_producer      # Container for batch producer
│   │   └── Dockerfile.batch_consumer      # Container for batch consumer
│   ├── realtime/                  # Real-time processing components
│   │   ├── reddit_realtime_producer.py    # Monitors last 3 hours continuously
│   │   ├── spark_realtime_consumer.py     # Processes with low latency optimization
│   │   ├── Dockerfile.realtime_producer   # Container for realtime producer
│   │   └── Dockerfile.realtime_consumer   # Container for realtime consumer
│   └── shared/                    # Shared components
│       ├── text_preprocessing.py          # Consistent NLP preprocessing
│       └── lr_model/                      # Trained Logistic Regression model
├── dashboard/
│   ├── batch_sentiment_output/            # Batch processing results
│   └── realtime_sentiment_output/         # Real-time processing results
└── data/                          # Model training data and checkpoints
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Reddit API credentials (.env.local file)

### Batch Processing (Historical Analysis)
```bash
# Windows
start_batch_pipeline.bat

# Linux/Mac
./start_batch_pipeline.sh
```
**Purpose**: Analyze January 1-31, 2025 Reddit data for throughput comparison

### Real-Time Processing (Live Monitoring)
```bash
# Windows
start_realtime_pipeline.bat

# Linux/Mac
./start_realtime_pipeline.sh
```
**Purpose**: Monitor last 3 hours of posts for latency comparison

## 🔧 Configuration

Create `.env.local` file with your Reddit API credentials:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

## 📊 Data Sources

**Target Subreddits:**
- r/malaysia (General Malaysian discussions)
- r/MalaysianFood (Food-related content)
- r/malaysiauni (University discussions)

## 🎯 Pipeline Comparison

| Aspect | Batch Processing | Real-Time Processing |
|--------|------------------|---------------------|
| **Data Source** | Jan 1-31, 2025 historical data | Last 3 hours of posts |
| **Optimization** | High throughput | Low latency |
| **Frequency** | One-time processing | Every 5 minutes |
| **Purpose** | Historical trend analysis | Live monitoring |
| **Metrics** | Posts per minute | Milliseconds per post |
| **Output** | `/dashboard/batch_sentiment_output/` | `/dashboard/realtime_sentiment_output/` |

## 🔬 Sentiment Analysis

**Model**: Logistic Regression (trained on labeled dataset)
**Classes**: Positive, Negative, Neutral
**Features**: TF-IDF vectorized text after NLP preprocessing

**Preprocessing Steps**:
1. Convert to lowercase
2. Remove URLs, mentions, hashtags
3. Remove stop words and punctuation
4. Tokenization and stemming

## 📈 Performance Metrics

### Batch Processing Metrics
- **Throughput**: Posts processed per minute
- **Total Volume**: Historical data volume processed
- **Processing Time**: Total time for January 2025 dataset

### Real-Time Processing Metrics
- **Latency**: Time from data ingestion to prediction
- **Response Time**: End-to-end processing per post
- **Availability**: Pipeline uptime percentage

## 🐳 Docker Architecture

**Infrastructure Services:**
- Zookeeper: Kafka coordination
- Kafka: Message streaming
- Spark Master/Worker: Distributed processing

**Processing Services:**
- Batch Producer/Consumer: Historical data pipeline
- Real-Time Producer/Consumer: Live data pipeline

## 🎛️ Monitoring and Logs

```bash
# Check container status
docker-compose -f docker-compose-new.yml ps

# View logs
docker-compose -f docker-compose-new.yml logs batch-consumer
docker-compose -f docker-compose-new.yml logs realtime-consumer

# Stop services
docker-compose -f docker-compose-new.yml down
```

## 📋 Output Format

Both pipelines generate CSV files with identical schema:
```csv
id,title,clean_text,author,subreddit,score,sentiment_score,sentiment_label,confidence,processed_timestamp,created_date
```

## 🎯 Project Requirements Fulfillment

✅ **Malaysian-relevant data source** (Reddit Malaysian subreddits)
✅ **NLP preprocessing** (Consistent text cleaning pipeline)
✅ **ML model deployment** (Logistic Regression in production)
✅ **Apache Kafka + Spark** (Containerized streaming architecture)
✅ **Batch vs Real-time comparison** (Separate optimized pipelines)
✅ **Performance metrics** (Throughput vs Latency measurement)

## 🔧 Development

For development or debugging:
```bash
# Build only (no start)
docker-compose -f docker-compose-new.yml --profile batch build

# Start specific service
docker-compose -f docker-compose-new.yml up kafka zookeeper
```

## 📞 Support

This implementation demonstrates production-ready sentiment analysis with proper separation of concerns, containerization, and performance optimization for both batch and streaming use cases.
