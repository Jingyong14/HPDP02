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
| **File Size**         | Approximately 3.48 GB                                                                     |
| **Domain**            | Music Streaming                                                              |
| **Number of Records** | 26,173,514                                                                   |
| **File Format**       | CSV                                                                          |
| **Columns**           | title (song name), artist, rank, date, region, chart type, streams (NULL for "viral50"), trend (popularity indicator), url (track link)                |

</div>

This dataset is suitable for performance comparison tasks as it is large in volume and contains diverse types of data (e.g., numerical, categorical, missing values), providing a practical use case for benchmarking data processing libraries.

## 3.0 Load and Inspect Data

To prepare the dataset for use, the Spotify Charts data was downloaded from Kaggle using the Kaggle API. The process began with installing the Kaggle package to enable command-line access to Kaggle resources. Then, the required credentials (Kaggle username and API key) were set manually as environment variables to authenticate the session. After successful authentication, the dataset was downloaded using the `kaggle datasets download` command and extracted from the ZIP archive. **Figure 3.0.1** demonstrates how the Kaggle API is configured and used to download and extract the dataset efficiently. Once extracted, the dataset files were ready for inspection and further processing.

After loading the dataset, a basic inspection was performed to understand its structure and content. The inspection began by using the pandas library to read the CSV file `charts.csv` into a DataFrame. The code used for this process is shown in **Figure 3.0.2**, which check the dataset's shape and retrieve summary information such as data types and non-null counts. The `shape` output indicated that the dataset contains over 26 million rows and 9 columns. To further explore the structure, the `info()` function was used, revealing that most columns are of object type, with only one integer and one float column. **Figure 3.0.3** displays this output, highlighting the presence of all expected columns such as `title`, `artist`, `rank`, and `streams`, as well as confirming that no null values were present across the dataset.

<div align="center"> <img src="https://github.com/user-attachments/assets/914643c2-d0c4-4a29-aa7a-67f6c46a9562" alt="Figure 3.0.1" width="400"> <br><strong>Figure 3.0.1: Code snippet demonstrating the process of loading data using Kaggle API.</strong> </div><br>
<div align="center"> <img src="https://github.com/user-attachments/assets/41432251-baff-4398-9566-3477e6848b8b" alt="Figure 3.0.2" width="400"><br><strong>Figure 3.0.2: Code snippet inspecting the Spotify Charts dataset.</strong> </div><br>
<div align="center"> <img src="https://github.com/user-attachments/assets/7a508734-cea7-493c-9433-bdb186546b1c" alt="Figure 3.0.3" width="400" style="border: '1px' solid #ccc; border-radius: '8px'; padding: '4px';"> <br><strong>Figure 3.0.3: Summary output of the dataset inspection showing entry count, column structure, and memory usage.</strong> </div><br>

## 4.0 Big Data Handling Strategies
## 5.0 Comparative Analysis
## 6.0 Conclusion
## 7.0 References
- Dhruvildave. (n.d.). *Spotify Charts Dataset* [Data set]. Kaggle. https://www.kaggle.com/datasets/dhruvildave/spotify-charts
- Shahizan, D. (n.d.). drshahizan [GitHub repository]. GitHub. https://github.com/drshahizan/drshahizan
