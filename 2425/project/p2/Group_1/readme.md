<h1 align="center">
  🎥 Real-Time Sentiment Analysis of YouTube Comments
  <br>
</h1>

<div align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3R5aWF6YW93emZoNG41bDhneXg4MGxxaDlhb2U5MXdiaXpkdXJlNSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/13Nc3xlO1kGg3S/giphy.gif" width="300px" alt="Sentiment Analysis GIF">
</div>
<br>
<table border="solid" align="center">
  <tr>
    <th>Name</th>
    <th>Matric Number</th>
  </tr>
  <tr>
    <td width=80%>NEO ZHENG WENG</td>
    <td>A22EC0093</td>
  </tr>
  <tr>
    <td width=80%>NURUL ERINA BINTI ZAINUDDIN</td>
    <td>A22EC0254</td>
  </tr>
  <tr>
    <td width=80%>MUHAMMAD SAFWAN BIN MOHD AZMI</td>
    <td>A22EC0221</td>
  </tr>
  <tr>
    <td width=80%>NUR ARINI FATIHAH BINTI MOHD SABIR</td>
    <td>A22EC0244</td>
  </tr>
</table>

### Links for related documents:
<table>
  <tr>
    <th>Documents</th>
    <th>Links</th>
  </tr>
  <tr>
    <td>Full Report</td>
    <td align="center">
      <a href="">
        <img src="https://github.com/user-attachments/assets/4f5391d9-f205-4dd6-8c08-1f8307bd55bf" width="24px" height="23px" alt="Full Report Icon">
      </a>
    </td>
  </tr>
  <tr>
    <td>System Architecture</td>
    <td align="center">
      <a href="https://github.com/Jingyong14/HPDP02/blob/main/2425/project/p2/Group_1/img/System%20Architecture%20.jpg" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/8760/8760611.png" width="24px" height="23px" alt="System Architecture Icon">
      </a>
    </td>
  </tr>
  <tr>
    <td>Source Code</td>
    <td align="center">
      <a href="https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p2/Group_1/docker-compose" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/9679/9679659.png" width="24px" height="23px" alt="Source Code Icon">
      </a>
    </td>
  </tr>
</table>

## 📌 Table of Contents

- [1.0 Introduction](#10-introduction)
  - [1.1 Background](#11-background)
  - [1.2 Objectives](#12-objectives)
  - [1.3 Scopes](#13-scopes)
- [2.0 Data Acquisition & Preprocessing](#20-data-acquisition--preprocessing)
- [3.0 Sentiment Model Development](#30-sentiment-model-development)
- [4.0 Apache System Architecture](#40-apache-system-architecture)
- [5.0 Analysis & Results](#50-analysis--results)
- [6.0 Optimization & Comparison](#60-optimization--comparison)
- [7.0 Conclusion & Future Work](#70-conclusion--future-work)


---

## 1.0 Introduction

### 1.1 Background

This system monitors Malaysian YouTube videos covering politics, culture, and history. By analyzing comment sentiment in real-time, stakeholders gain timely feedback and public opinion tracking.

### 1.2 Objectives

- Build an end-to-end real-time data pipeline using Kafka & Spark.
- Classify sentiments using a machine learning model.
- Visualize sentiment trends and keyword insights over time.

### 1.3 Scopes

- **Platform**: YouTube only  
- **Language**: English  
- **Model Task**: 3-class sentiment (positive, negative, neutral)  
- **Tech stack**: Apache Kafka, Spark, Elasticsearch, Kibana

---

## 2.0 Data Acquisition & Preprocessing

### 📥 Data Sources
- **Batch**: YouTube Data API (via `youtube_extractor.py`)
- **Real-Time**: `youtube-comment-downloader`, `yt-dlp`, and `KafkaProducer`

### 🛠️ Tools Used

- `langdetect`, `re` (Python regex), Hugging Face `transformers`
- Apache Kafka, PySpark, scikit-learn

### 🧹 Data Cleaning Steps

- Lowercasing, removing URLs/symbols
- Tokenization and TF-IDF via pre-trained `tfidf_vectorizer.pkl`
- Sentiment prediction via `svm_sentiment_model.pkl`

---

## 3.0 Sentiment Model Development

- **Models tested**: Logistic Regression, Naive Bayes, SVM
- **Training**: On 100k+ labeled comments (via Hugging Face transformer)
- **Evaluation**: Accuracy & F1-score on holdout dataset
---
## 4.0 Apache System Architecture

This section outlines the design and execution of a real-time YouTube sentiment analysis pipeline. It includes data ingestion, model inference, and dashboard visualization, all orchestrated using Docker.

### 4.1 Sentiment Analysis Workflow

<p align="center">
  <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/System Architecture .jpg" alt="System Architecture" width="500"/>
</p>

The system processes YouTube comments using the following stages:

1. **Model Training**  
   - Collected ~100,000 Malaysia-related YouTube comments.
   - Labeled using `cardiffnlp/twitter-roberta-base-sentiment`.
   - Trained various classifiers using Spark MLlib and selected the best performing model (e.g., SVM).

2. **Data Ingestion with Kafka**  
   - Python script scrapes real-time comments and metadata.
   - Publishes data as JSON to Kafka topic: `youtube-comments`.

3. **Stream Processing with Spark**  
   - Spark reads Kafka streams, applies text preprocessing, transforms with TF-IDF, and classifies using pre-trained SVM model.
   - Outputs enriched data to Elasticsearch.

4. **Indexing and Visualization**  
   - Elasticsearch stores classified comments for full-text search and analytics.
   - Kibana displays sentiment trends, distributions, and keyword insights.

---

### 4.2 Component Roles and Configuration

Each component is containerized via `docker-compose`.

| Component      | Image                                           | Description                                               |
|----------------|--------------------------------------------------|-----------------------------------------------------------|
| **Zookeeper**  | `confluentinc/cp-zookeeper:7.6.1`                | Kafka coordination and metadata storage                   |
| **Kafka**      | `confluentinc/cp-kafka:7.6.1`                    | Comment queue and buffer                                  |
| **Spark**      | `bitnami/spark:3.4.2`                            | Real-time preprocessing and model inference               |
| **Elasticsearch** | `docker.elastic.co/elasticsearch:8.13.4`     | Stores structured sentiment-labeled comment data          |
| **Kibana**     | `docker.elastic.co/kibana/kibana:8.13.4`         | Dashboard and sentiment visualization                     |
| **ML Trainer** | Built via `Dockerfile.model`                    | Trains models and saves artifacts for Spark               |

---

## 5.0 Analysis & Results

### Dashboard Tools

- **Elasticsearch** for fast data indexing and search
- **Kibana** for interactive real-time visualizations and filters

### 5.1 Visualizations

1. **Donut Chart**
     <p align="center"> <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/Donut.png" alt="Sum of Likes Graph" width="250"/> </p>
     
   > 98.51% of comments were negative, revealing high dissatisfaction.

3. **Bar Chart - Monthly Likes**
  <p align="center"> <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/BarChart.png" alt="Sum of Likes Graph" width="250"/> </p>
  
   > Peak likes in June 2025 suggest viral content or trending topics.

4. **Treemap - Video Popularity**
   <p align="center"> <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/TreeMap.png" alt="Sum of Likes Graph" width="250"/> </p>
   
   > _"History of Malaysia in 12 Minutes"_ accounts for 47% of total views.

5. **Likes per Video**  
   > Historical and geopolitically themed videos received most likes.

6. **Total Comment Count**
   <p align="center"> <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/TotalYoutubeComment.png" alt="Sum of Likes Graph" width="250"/> </p>
   
   > 7,181 filtered comments analyzed.

7. **Word Cloud**
   <p align="center"> <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/CloudTag.png" alt="Sum of Likes Graph" width="250"/> </p>
   
   > Highlights political and historical terms like “1957 merdeka” and “Brunei wrongly illustrated”.

8. **Total Likes Summary**
   <p align="center"> <img src="https://github.com/Jingyong14/HPDP02/raw/main/2425/project/p2/Group_1/img/Sum%20of%20Likes" alt="Sum of Likes Graph" width="250"/> </p>
   
   > Cumulative likes: **112,637,424**

---

### 5.2 Findings and Insights

- High negativity due to sensitive historical or political content
- Strong engagement on concise, educational videos
- Global viewership based on comments (e.g., “Greetings from Germany”)
- Spikes in February and June suggest timely viral releases

---

## 6.0 Optimization & Comparison



---

## 7.0 Conclusion & Future Work

### ✅ Achievements:
- Real-time sentiment analysis system successfully deployed using Spark + Kafka
- Visual dashboard tracks emotional trends across Malaysia-themed content
- 100k+ comments processed, 7K+ analyzed in real time

### 🚀 Future Improvements:
- Add Malay language support
- Enhance sarcasm or emotion detection
- Integrate Twitter/Facebook for cross-platform sentiment tracking
- Improve model with periodic retraining using fresh data

---

