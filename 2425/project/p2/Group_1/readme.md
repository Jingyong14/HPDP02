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
- [📚 References](#references)

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
