# 🚀 Group 7: Reddit Real-Time Sentiment Analysis using Apache Spark and Kafka

## Group Members
<table border="1">
    <tr>
        <th>Group Member</th>
        <th>Matric No.</th>
    </tr>
  <tr>
        <td>JOSEPH LAU YEO KAI</td>
        <td>A22EC0055</td>
    </tr>
    <tr>
        <td>VINESH A/L VIJAYA KUMAR</td>
        <td>A22EC0290</td>
    </tr>
    <tr>
        <td>TIEW CHUAN SHEN</td>
        <td>A22EC0113</td>
    </tr>
  <tr>
        <td>NUR FARAH ADIBAH BINTI IDRIS</td>
        <td>A22EC0245</td>
    </tr>
</table>


## 🗓️ Logbook
| **Date**       | **Task / Description**                                                                 | **PIC**        | **Result**                                                                 |
|----------------|----------------------------------------------------------------------------------------|----------------|---------------------------------------------------------------------------|
| 30 May 2025    | Team formation and initial discussion                                                  | All members    | Decided to analyze Malaysian public sentiment; initially chose news data |
| 5 June 2025    | Collected sentiment-related news data                                                  | Farah            | Found insufficient data for training; switched focus to Twitter           |
| 10 June 2025    | Attempted to use Twitter API                                                           | Joseph    | Faced severe rate limiting; explored Reddit as alternative                |
| 15 June 2025    | Implemented Reddit API with Apache Kafka producer & consumer                          | All  | Successfully streamed Reddit posts and saved into `.jsonl` format         |
|  18June 2025    | Collected labeled dataset (Sentiment140) from Kaggle and began manual labeling Reddit | Farah, Chuan Shen         | Created combined dataset with both labeled Reddit + Kaggle data           |
| 20 June 2025   | Performed data preprocessing (cleaning, tokenization, lowercasing)                     | Farah    | Completed data cleaning and ready for model training                      |
| 25 June 2025   | Trained sentiment models (Naive Bayes and Logistic Regression)                         | All       | Selected Logistic Regression as final model due to higher performance     |
| 26 June 2025   | Integrated sentiment model with Apache Spark for real-time streaming                   | Joseph   | Real-time classification of Reddit posts working as expected              |
| 7 July 2025   | Connected Elasticsearch and designed Kibana dashboard                                  | All | Visualization of sentiment trends completed                               |
| 8 July 2025   | Conducted performance comparison: batch vs streaming                                   | All       | Included accuracy, latency, and resource usage comparison in report       |
| 11 July 2025   | Finalized all documentation and cleaned code                                           | All members    | Ready for submission                                                      |
| 11 July 2025   | Submitted final report, code, dataset, and dashboard | All           | Project completed and submitted on e-learning and GitHub     


## 📄 Project Documentation
- 📘 [Final Report](https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p2/Group_7/report)

