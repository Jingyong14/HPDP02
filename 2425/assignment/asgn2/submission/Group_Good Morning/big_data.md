# Assignment 2: Mastering Big Data Handling

## Group Name: Good Morning

| Name                       | Matric No   |
|----------------------------|-------------|
| Neo Zheng Weng             | A22EC0093   |
| Wong Khai Shian Nicholas   | A22EC0292   |

---

## Table of Contents

- [1 Introduction](#10-introduction)
- [1.1 Objectives](#11-objectives)
- [2.0 Dataset Selection](#20-dataset-selection)
- [3.0 Load and Inspect Data](#30-load-and-inspect-data)
- [4.0 Apply Big Data Handling Strategies](#40-apply-big-data-handling-strategies)
- [5.0 Comparative Analysis](#50-comparative-analysis)
- [6.0 Conclusion & Reflection](#60-conclusion--reflection)

---

## 1.0 Introduction

In today’s data-driven environment, analysts must process datasets that exceed traditional memory constraints. This project utilizes the 2019 Airline Delays and Cancellations dataset (1.37 GB) from Kaggle to demonstrate scalable data loading and processing. Using Python with Pandas, Dask, and Polars, we apply selective column loading, chunked reading, data‐type optimization, sampling, and parallel execution to handle big data processing. We evaluate each library’s performance by measuring execution time and memory usage, thereby identifying efficient approaches for large‐volume flight analytics.

## 1.1 Objectives

The objectives of this assignment are:

- To handle big data volumes above 700MB.
- To apply big data handling strategies, including chunking, sampling, type optimization, and parallel computing.
- To evaluate and compare the performance between traditional Pandas and optimized data handling methods in Pandas, Dask, and Polars based on execution time, memory usage, and ease of processing.

## 2.0 Dataset Selection

In this assignment, the 2019 Airline Delays and Cancellations dataset from Kaggle has been selected as a single CSV file named `full_data_flightdelay.csv` (approximately 1.4 GB in size). This dataset provides comprehensive information about airline delays and cancellations across the United States in 2019. It contains 6,489,062 flight records from January 1, 2019 to December 31, 2019, each with 26 fields capturing both operational (e.g., airline, airport, aircraft) and environmental (e.g., weather) attributes. This dataset falls under the broader Aviation domain and is tailored for data analysis in airline operations, delay prediction, and transportation planning. The further details of the dataset is listed below and as showned in Figure 1.1.

- Filename: full_data_flightdelay.csv
- Source: [2019 Airline Delays and Cancellations dataset from Kaggle](https://www.kaggle.com/datasets/threnjen/2019-airline-delays-and-cancellations)
- Data size: 1.37 GB
- Number of rows: 6,489,062
- Number of columns: 26
- Domain: Transportation / Aviation Analytics
- License: [U.S. Government Works](https://www.usa.gov/government-works/)

<p align="center">
  <img src="https://github.com/Jingyong14/HPDP02/blob/512799f6295cd4231040a926617364bc4b39d919/2425/assignment/asgn2/submission/Group_Good%20Morning/figures/dataset.png" alt="Dataset">
  <br>
  <strong>Figure 2.0: Overview of Dataset</strong>
</p>

## 3.0 Load and Inspect Data

### 3.1 Download Dataset
The dataset was downloaded via KaggleHub into Google Colab. Refer to Figure 3.1, the code first imported the necessary libraries - `os` for file‐path handling, `pandas` for data handling, and `kagglehub` to fetch Kaggle datasets. The code then downloaded the latest version of the “2019 Airline Delays and Cancellations” dataset and returns the local directory where the files were extracted. Finally, it built the full file path `csv_path` to the main CSV to be loaded later.

<p align="center">
  <img src="https://github.com/user-attachments/assets/e5e07677-02d6-4527-b573-40f5a1d088b0" alt="img">
  <br>
  <strong>Figure 3.1: Download Dataset</strong>
</p>

### 3.2 Load and Process Data
The loading and processing steps are shown in Figure 3.2. First, the `time`, `psutil`, and `pandas` libraries are imported, where:

* **`time`**: Provides `time.time()` to record timestamps and measure execution duration.
* **`psutil`**: Allows querying system resources (e.g., memory usage) during data operations.
* **`pandas`**: Offers DataFrame structures and functions for loading, cleaning, and analyzing tabular data.

Then, a timestamp is recorded in `start_time` to mark the beginning of the operation. The entire CSV file is then read into a DataFrame via `df_pd = pd.read_csv(csv_path)`.

After the data has been loaded, basic cleaning is performed by chaining `.dropna()` to remove any rows containing null values, followed by `.drop_duplicates()` to eliminate duplicate records. Once these operations are complete, a second timestamp is captured in `end_time` to determine the total runtime of the load-and-clean procedure.

<p align="center">
  <img src="https://github.com/user-attachments/assets/34a9b102-e167-411e-8954-3599a2600487" alt="img">
  <br>
  <strong>Figure 3.2: Data Loading and Processing (Pandas Traditional)</strong>
</p>

### 3.3 Evaluate Performance
The performance of the traditional pandas data loading was measured next, as shown in Figure 3.3.1. The total memory used by `df_pd` (in megabytes) was computed by summing all column memory usages (including object‐type columns) via `df_pd.memory_usage(deep=True).sum() / 1024**2`. Then, the duration of the loading step was calculated by subtracting `start_time` from `end_time`. Finally, both the peak memory usage (in MB) and the total execution time (in seconds) were displayed. It was observed that the full DataFrame load required approximately **2992.44 MB** of memory and completed in roughly **57.97 seconds** as shown in Figure 3.3.2, underscoring the need for optimization when handling very large CSV files.

<p align="center">
  <img src="https://github.com/user-attachments/assets/89ae47d1-f7fe-45cf-ad59-1628986b2ade" alt="img">
  <br>
  <strong>Figure 3.3.1: Performance Evaluation (Pandas Traditional)</strong>
  <br>
  <img src="https://github.com/user-attachments/assets/1c28c0ce-d39e-4233-9ce5-cdcca1578a16" alt="img">
  <br>
  <strong>Figure 3.3.2: Performance Result (Pandas Traditional)</strong>
</p>

### 3.4 Inspect Data
The data inspection process is illustrated in Figure 3.4.1, where the DataFrame’s shape is then retrieved via `df_pd.shape` and printed with (rows, columns). Next, the column names are obtained with `df_pd.columns.tolist()` and displayed, and each column’s data type is listed using `df_pd.dtypes`. Finally, `df_pd.head()` is invoked to present the first five rows of the dataset. The resulting output showing the DataFrame’s dimensions, the full list of column names, the data types for each column, and a preview of the first five records is displayed in Figure 3.4.2.

<p align="center">
  <img src="https://github.com/user-attachments/assets/18dc909f-2c42-4a4c-af6c-7b90893a7a93" alt="img">
  <br>
  <strong>Figure 3.4.1: Data Inspection (Pandas Traditional)</strong>
  <br>
  <img src="https://github.com/user-attachments/assets/b53b8dfe-db97-46fd-9263-ef2843cbde3b" alt="img">
  <br>
  <strong>Figure 3.4.2: Data Inspection Output (Pandas Traditional)</strong>
</p>

## 4.0 Apply Big Data Handling Strategies

## 5.0 Comparative Analysis

## 6.0 Conclusion & Reflection
