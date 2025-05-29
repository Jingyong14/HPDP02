## 🎓 SECP3133 – High Performance Data Processing (Section 02)

### 📊 Assignment 2: *Mastering Big Data Handling*

### Lecturer: Dr. Aryati binti Bakri
**Group: LogiCode**

| Member Name         | Matric No.  |
|------------------------|----------------|
| Ong Yi Yan       | `A22EC0101`     |
| Tang Yan Qing | `A22EC0109`     |

## 1.0 Introduction
## 1.1 Objectives
## 2.0 Dataset Selection
To conduct a meaningful performance and scalability comparison among different data processing libraries, the Spotify Charts Dataset from Kaggle has been selected. It contains historical data of all “Top 200” and “Viral 50” charts published by Spotify globally, updated every 2–3 days since January 1, 2017. The dataset includes over 26 million records, with key details such as song title, artist, rank, date, region, chart type, number of streams, trend indicator, and track URL.

Table 2.0.1 shows an overview of the Spotify Charts dataset used in this project, highlighting its size, source, domain, and the structure of its key features.

<div align="center">

 Table 2.0.1: Dataset Overview
| **Attribute**         | **Details**                                                                 |
|-----------------------|------------------------------------------------------------------------------|
| **Dataset Name**      | Spotify Charts Dataset                                                       |
| **Source**            | [Kaggle](https://www.kaggle.com/datasets/dhruvildave/spotify-charts)         |
| **File Size**         | ~3.48 GB                                                                     |
| **Domain**            | Music Streaming                                                              |
| **Number of Records** | 26,173,514                                                                   |
| **File Format**       | CSV                                                                          |
| **Columns**           | title (song name), artist, rank, date, region, chart type, streams (NULL for "viral50"), trend (popularity indicator), url (track link)                |
| **Temporal Coverage** | January 2017 to present                                                      |

</div>

This dataset is suitable for performance comparison tasks as it is large in volume and contains diverse types of data (e.g., numerical, categorical, missing values), providing a practical use case for benchmarking data processing libraries.

## 3.0 Load and Inspect Data
To prepare the dataset for use, the Spotify Charts data was downloaded from Kaggle using the Kaggle API. The process began with installing the Kaggle package to enable command-line access to Kaggle resources. Then, the required credentials — Kaggle username and API key — were set manually as environment variables to authenticate the session. After successful authentication, the dataset was downloaded using the `kaggle datasets download` command and extracted from the ZIP archive. Once extracted, the dataset files were ready for inspection and further processing.

<div align="center">
  <img src="https://github.com/user-attachments/assets/914643c2-d0c4-4a29-aa7a-67f6c46a9562" alt="Figure 3.0.1" width="400">
</div>

## 4.0 Big Data Handling Strategies
## 5.0 Comparative Analysis
## 6.0 Conclusion
## 7.0 References
