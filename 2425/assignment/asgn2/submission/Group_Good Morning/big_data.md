# Assignment 2: Mastering Big Data Handling

## Group Name: Good Morning

| Name                       | Matric No   |
|----------------------------|-------------|
| Neo Zheng Weng             | A22EC0093   |
| Wong Khai Shian Nicholas   | A22EC0292   |

---

## Table of Contents

- [Introduction](#introduction)
- [Objectives](#objectives)
- [Task 1: Dataset Selection](#task-1-dataset-selection)
- [Task 2: Load and Inspect Data](#task-2-load-and-inspect-data)
- [Task 3: Apply Big Data Handling Strategies](#task-3-apply-big-data-handling-strategies)
- [Task 4: Comparative Analysis](#task-4-comparative-analysis)
- [Task 5: Conclusion & Reflection](#task-5-conclusion--reflection)  

---

## Introduction

In today’s data-driven environment, analysts must process datasets that exceed traditional memory constraints. This project utilizes the 2019 Airline Delays and Cancellations dataset (1.37 GB) from Kaggle to demonstrate scalable data loading and processing. Using Python with Pandas, Dask, and Polars, we apply selective column loading, chunked reading, data‐type optimization, sampling, and parallel execution to handle big data processing. We evaluate each library’s performance by measuring execution time and memory usage, thereby identifying efficient approaches for large‐volume flight analytics.

## Objectives

The objectives of this assignment are:

- To handle data volumes above 700MB.
- To apply big data handling strategies, including chunking, sampling, type optimization, and parallel computing.
- To evaluate and compare the performance between traditional Pandas and optimized data handling methods in Pandas, Dask, and Polars based on execution time and memory usage.

## Task 1: Dataset Selection

In this assignment, the 2019 Airline Delays and Cancellations dataset from Kaggle has been selected as a single CSV file named full_data_flightdelay.csv (approximately 1.4 GB in size). This dataset provides comprehensive information about airline delays and cancellations across the United States in 2019. It contains 6,489,062 flight records from January 1, 2019 to December 31, 2019, each with 26 fields capturing both operational (e.g., airline, airport, aircraft) and environmental (e.g., weather) attributes. This dataset falls under the broader Aviation domain and is tailored for data analysis in airline operations, delay prediction, and transportation planning. The further details of the dataset is listed below and as showned in Figure 1.1.

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
  <strong>Figure 1.1</strong>
</p>

## Task 2: Load and Inspect Data

## Task 3: Apply Big Data Handling Strategies

## Task 4: Comparative Analysis

## Task 5: Conclusion & Reflection
