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
- To apply big data handling strategies, including selective column loading, chunking, sampling, type optimization, and parallel computing.
- To evaluate and compare the performance between traditional Pandas and optimized data handling methods with Pandas, Dask, and Polars based on execution time, memory usage, and ease of processing.

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
This section uses the traditional pandas workflow as baseline to load the entire CSV into a DataFrame and then inspect the resulting DataFrame by printing its shape, column names, data types, and a five-row preview. Subsequent big data handling methods with different libraries will follow the same “load → clean → inspect” steps for a fair performance comparison.

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
* **`psutil`**: Allows querying system resources—here, it’s used to capture the Python process’s resident memory before and after loading.
* **`pandas`**: Offers `DataFrame` structures and functions for loading, cleaning, and analyzing tabular data.

Next, a `psutil.Process(os.getpid())` object is created and used to record `mem_before = process.memory_info().rss` (in bytes) so that peak memory usage can be determined. A timestamp is then recorded in `start_time` to mark the beginning of the operation. The entire CSV file is loaded into a DataFrame via `df_pd = pd.read_csv(csv_path)`

After loading, basic cleaning is performed by chaining `.dropna()` to remove any rows containing null values, followed by `.drop_duplicates()` to eliminate duplicate records. Once these operations finish, a second timestamp is captured in `end_time`, and `mem_after = process.memory_info().rss` is recorded. The difference between `mem_after` and `mem_before` yields the total process‐level memory consumed by the load‐and‐clean pipeline, while `end_time – start_time` gives the total runtime.

<p align="center">
  <img src="https://github.com/user-attachments/assets/1eeb12fd-cbcb-4424-9a13-7ea636691db5" alt="img">
  <br>
  <strong>Figure 3.2: Data Loading and Processing (Pandas Traditional)</strong>
</p>

### 3.3 Evaluate Performance
The performance of the traditional pandas data loading was measured next, as shown in Figure 3.3.1. The total memory consumed by the process (in megabytes) was computed by taking the difference between `mem_after` and `mem_before` (both obtained via `psutil.Process(os.getpid()).memory_info().rss`) and dividing by 1024². The duration of the loading step was determined by subtracting `start_time` from `end_time`. Finally, both the peak process memory increase (2992.44 MB) and the total execution time (57.97 seconds) were displayed, as shown in Figure 3.3.2, underscoring the need for optimization when handling very large CSV files.

<p align="center">
  <img src="https://github.com/user-attachments/assets/9b172050-f6d4-4ee7-98d6-71f06de39394" alt="img">
  <br>
  <strong>Figure 3.3.1: Performance Evaluation (Pandas Traditional)</strong>
  <br>
  <img src="https://github.com/user-attachments/assets/7d41d8dc-2204-42c4-90bd-fb825448b8d8" alt="img">
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
This chapter evaluates and compares performance between traditional Pandas full loading and optimized data handling methods (selective column loading, chunking, sampling, type optimization, and parallel computing) in each library (Pandas, Dask, and Polars) based on execution time (seconds), memory usage (MB), and ease of processing as illustrated in Figure 5.1 and Table 5.2.

**Execution Time Comparison**:

Polars demonstrated the fastest performance, completing the full load–clean–sample workflow in just **9.05 seconds**, thanks to its SIMD‐accelerated, multi‐threaded CSV parser. Optimized Pandas followed in second place, finishing in **23.57 seconds** by reducing I/O overhead through selective column loading, dtype downcasting, chunked reads, and early sampling. Dask closely trailed optimized Pandas at **24.81 seconds**, with its block‐parallel approach incurring only a small scheduling overhead. By contrast, unoptimized Pandas was the slowest, requiring **54.15 seconds** to load and process the entire 6.5 million‐row dataset without any optimizations.

**Memory Usage Comparison**:

When measuring the final in‐memory footprint after sampling, optimized Pandas used the least memory at just **2.1 MB**, because it dropped unused columns, cast to smaller dtypes (`int8`/`int16` and `category`), and sampled only 10 % of rows. Dask maintained a modest peak of **154.0 MB** by processing the dataset in 100 MB blocks and only materializing needed partitions upon calling `.compute()`. Polars required **380.3 MB**, balancing its columnar, Arrow‐based buffers and multi‐threaded parsing overhead. Unoptimized Pandas consumed the most memory by far **2,575.7 MB** since it loaded all 26 columns at default 64‐bit dtypes without chunking or filtering.

**Ease of Processing**:

Unoptimized Pandas is the simplest to implement: a single `pd.read_csv()` call followed by `.dropna()` and `.drop_duplicates()`. No additional code is required, but performance and memory costs are prohibitively high for large datasets. Optimized Pandas demands more effort, requiring explicit `usecols` and `dtype` mappings, manual chunk loops, and early sampling logic; these extra steps yield dramatic improvements in both memory and speed, but at the expense of greater code complexity. Dask strikes a balance by offering a nearly identical Pandas‐like API (`dd.read_csv()`, `.dropna()`, `.drop_duplicates()`, `.sample()`), handling out‐of‐core and parallel execution transparently—though users must understand lazy evaluation and the need to call `.compute()` to materialize results. Polars requires learning a new Rust‐based DataFrame API (`pl.read_csv()`, `.filter()`, `.unique()`, `.sample()`), which adds a small learning curve; once mastered, it delivers the fastest parsing and transformation operations among all methods.

<p align="center">
  <img src="https://github.com/Jingyong14/HPDP02/blob/821b114892212b66271814036a7655823f1cadb5/2425/assignment/asgn2/submission/Group_Good%20Morning/figures/performance_chart.png" alt="Performance evaluation chart">
  <br>
  <strong>Figure 5.1: Performance Comparative Analysis</strong>
  <br>
  <br>
  <strong>Table 5.2: Performance Result</strong>
</p>

| Method                 | Execution Time (s) | Memory Used (MB) | Ease of Processing                                                                                              |
|------------------------|--------------------|------------------|------------------------------------------------------------------------------------------------------|
| **Pandas (No Opt)**    | 54.15              | 2,575.7          | Very simple to implement (single `read_csv()`) but slow and extremely memory‐intensive for large CSVs.   |
| **Pandas (Optimized)** | 23.57              | 2.1              | Requires column filtering, dtype downcasting, chunking, and sampling—but yields minimal memory use and moderate speed. |
| **Dask**               | 24.81              | 154.0            | Familiar Pandas‐like API with lazy, block‐parallel execution. Efficient memory usage, though slight scheduling overhead. |
| **Polars**             | 9.05               | 380.3            | Fastest SIMD‐accelerated, multi‐threaded parser. Moderate memory footprint; requires learning a new Rust‐based API. |



## 6.0 Conclusion & Reflection

