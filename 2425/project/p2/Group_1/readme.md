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
      <a href="https://github.com/Jingyong14/HPDP02](https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p2/Group_1/docker-compose" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/9679/9679659.png" width="24px" height="23px" alt="Source Code Icon">
      </a>
    </td>
  </tr>
</table>



# 1.0 Introduction

## 1.1 Background

This project aims to design and implement a scalable real-time sentiment analysis pipeline for processing YouTube comments related to Malaysian content. The primary objective is to extract and analyze public sentiment in response to videos covering topics such as politics, history, culture, and social issues. By categorizing user comments into positive, negative, or neutral sentiments, the system offers a data-driven perspective on audience engagement and emotional response.

Real-time sentiment analysis holds significant value in the Malaysian context. It enables:
- Content creators
- Marketers
- Media analysts
- Policymakers

to monitor evolving public discourse, assess reactions to key events, and align content strategies accordingly. This timely feedback mechanism supports more responsive and informed decision-making.

## 1.2 Objectives

This project focuses on the development of a real-time sentiment analysis system designed to monitor and interpret public sentiment from Malaysian YouTube comments. The primary objectives are:

1. **Data Pipeline Development**  
   To build an end-to-end data pipeline capable of ingesting, processing, and analyzing large volumes of YouTube comment data in real time using big data technologies such as:
   - Apache Kafka
   - Apache Spark

2. **Sentiment Classification**  
   To accurately classify public sentiment into three categories:
   - Positive
   - Negative
   - Neutral  
   based on the textual content of user comments, using trained machine learning models.

3. **Trend Visualization**  
   To track and visualize sentiment trends associated with specific videos over time, enabling stakeholders to observe how public opinion evolves in response to:
   - Different content themes
   - Events
   - Viral topics
