# SECP3133 High Performance Data Processing - Section 02

## Assignment 2 - Mastering Big Data Handling

<p><strong>LECTURER: DR. ARYATI BINTI BAKRI</strong></p>

### Group Green Forest 

<ul>
<li><strong>NURUL ERINA BINTI ZAINUDDIN</strong> - A22EC0254</li>
<li><strong>NUR ARINI FATIHAH BINTI MOHD SABIR</strong> - A22EC0244</li>
</ul>

## Table of Contents
- [1.0 Introduction](#10-introduction)
- [2.0 Dataset Selection](#20-dataset-selection)
- [3.0 Data Loading and Inspection](#30-data-loading-and-inspection)
- [4.0 Big Data Handling Strategies](#40-big-data-handling-strategies)
- [5.0 Comparative Analysis](#50-comparative-analysis)
- [6.0 Conclusion and Reflection](#60-conclusion-and-reflection)


## 1.0 Introduction

This assignment focuses on exploring practical strategies for efficient big data handling using Python. Optimization techniques such as chunking, data type reduction, sampling, and selective data loading are implemented to improve processing efficiency. In addition, parallel computing approaches are applied using libraries such as Dask and Polars, alongside traditional Pandas, to compare performance across different frameworks in terms of memory usage and execution time.

A dataset exceeding 1 GB in size is selected to simulate real-world scenarios where transportation systems, urban infrastructure, or other domains require large-scale data handling. Through this investigation, insights are gained into scalable techniques that enhance the performance and practicality of data analytics workflows in big data contexts.

### 1.1 Objectives

1. To implement and compare big data handling strategies using Pandas, Dask, and Polars.

2. To evaluate and optimize performance through memory-efficient loading, processing, and sampling techniques.

3. To analyze and reflect on the effectiveness of each method in handling large datasets based on speed, resource usage, and scalability.

## 2.0 Dataset Selection
This section introduces and justifies the selection of the “New York City Bus Data” dataset, which serves as the core dataset for the assignment. The dataset is chosen for its substantial size, structured format, and real-time public transportation context, all of which align well with the goals of high-performance big data analysis.

### 2.1 Dataset Details
For this assignment, the dataset chosen is titled **"New York City Bus Data"**, **sourced from [Kaggle](https://www.kaggle.com/datasets/stoney71/new-york-city-transport-statistics?select=mta_1712.csv) and 
uploaded by Michael Stone**. It contains real-time location data of buses operating under the Metropolitan Transportation Authority (MTA) in New York City. This dataset falls under the **urban mobility and public transportation domain**, making it ideal for studying large-scale, real-time data typically encountered by smart city infrastructure systems.

As shown in Figure 2.1.1, this dataset provides a comprehensive overview of bus movement data across New York City, making it highly relevant for urban mobility analysis. The dataset is approximately **1.33 GB in size** and contains about **6.4 million rows** and **17 columns**, which satisfies the criteria of being large and rich enough for exploratory and performance comparisons.

<p align="center"> <img src="https://github.com/user-attachments/assets/dc7cffef-f971-4d71-9ad7-9b1155e0e77c" alt="NYC Bus Data Overview" /> <br><strong>Figure 2.1.1 - Overview of New York City Bus Data</strong> </p>

### 2.2 Features Included
Figure 2.2.1 illustrates a sample view of the dataset's structure, including column names and record counts. Among the features included are various timestamp fields such as *RecordedAtTime*, *ExpectedArrivalTime*, and *ScheduledArrivalTime*, which are essential for tracking punctuality and delay patterns. Additionally, the dataset captures bus route identifiers like *PublishedLineName* and *DirectionRef*, as well as origin and destination information with corresponding latitude and longitude coordinates. The presence of live GPS locations, next stop predictions, and fields such as *DistanceFromStop* and *ArrivalProximityText* further enhances the real-time and operational value of this dataset.

<p align="center"> <img src="https://github.com/user-attachments/assets/6112396b-dc45-460c-b17b-8a3e43202367" alt="15 first rows"/>
<p align="center"> <img src="https://github.com/user-attachments/assets/6c4b7019-7a7f-4409-84e8-fd4abf32b28e" alt="15 last rows" /> 
<br><strong>Figure 2.2.1 - Data Columns and Row Counts from CSV File</strong> </p>

### 2.3 Justification
This dataset is particularly suitable for a big data handling assignment because of its large volume, structured schema, and real-time characteristics. It offers practical opportunities to explore and apply big data techniques such as chunked or parallelized data loading, data type optimization for memory efficiency, and performance benchmarking using tools like Dask against traditional Pandas operations. Moreover, the dataset simulates a real-world use case where a transportation agency must process millions of records to monitor services, analyze delays, and optimize route planning.

## 3.0 Data Loading and Inspection
This section outlines the essential steps taken to access, manage, and prepare the dataset from Kaggle for analysis in a Google Colab environment. The process begins with authenticating Kaggle API access, followed by downloading and extracting the dataset, then saving it to Google Drive for persistence, and finally performing a brief inspection of the data to understand its structure.

### 3.1 Kaggle API Setup for Dataset Download

To access and download datasets directly from Kaggle within Google Colab, we first need to authenticate using the Kaggle API. This requires a Kaggle account and an API key (kaggle.json). <br> 
The first line in figure 3.1 prompts the user to upload the kaggle.json file, which contains the API credentials. <br>
The second commands in figure 3.1 create a hidden .kaggle directory in the user’s home path. Then, it copy the uploaded kaggle.json file into this directory. Next, it set the appropriate permissions (read/write for user only) to ensure security and avoid access issues.

<p align="center"> <img src="https://github.com/user-attachments/assets/0a805554-e4a2-464b-a503-78e5e7c4ea6e" alt="ss code 1" /> 
<br><strong>Figure 3.1.1 - Kaggle API Setup </strong> </p>

### 3.2 Dataset Download and Extraction
Once the Kaggle API is properly configured, the commands in figure 3.2 are used to download and extract the dataset. The first command uses the kaggle CLI tool to download the dataset from Kaggle. The dataset will be downloaded as a ZIP file into the current working directory. The second command extracts the contents of the downloaded ZIP file into a folder named nyc_transport. The -o flag allows existing files to be overwritten if they already exist. After extraction, the raw dataset (e.g., mta_1712.csv) will be available for further processing, cleaning, and analysis.

<p align="center"> <img src="https://github.com/user-attachments/assets/16e9d301-8f6a-4542-ab22-499dd2d45f63" alt="ss code 2" /> 
<br><strong>Figure 3.2.1 - Dataset Download and Extraction </strong> </p>

### 3.3 Saving Dataset to Google Drive

The following code in figure 3.3 is used to save the donwnloaded dataset to Google Drive for persistent storage and future use. The first command mounts the Google Drive to the Colab environment, allowing to read from and write to Drive directly. The second section creates a directory path inside Google Drive named Assign2/nyc_transport_data. In the third command, the cleaned DataFrame df is saved as a CSV file named mta_1712_cleaned.csv inside the target directory. The dataset is now saved securely in Google Drive and can be accessed later for inspection, modeling, or additional analysis.

<p align="center"> <img src="https://github.com/user-attachments/assets/b3e0b18c-e007-4478-bced-dd38fc946674" alt="ss code 3" /> 
<br><strong>Figure 3.3.1 - Saving Dataset to Google Drive </strong> </p>

### 3.4 Brief Data Inspection

The code in figure 3.4.1 loads the CSV file into a pandas DataFrame for inspection. 

<p align="center"> <img src="https://github.com/user-attachments/assets/263ec5e9-9f21-4464-b7a5-8937e442dbfb" alt="ss code 4" /> 
<br><strong>Figure 3.4.1 - Brief Data Inspection </strong> </p>

The output in figure 3.4.2 provides a quick overview of the dataset’s structure, including its dimensions, column names, and data types, laying the groundwork for deeper analysis and optimization steps.

<p align="center"> <img src="https://github.com/user-attachments/assets/63563598-6eb2-4ad7-be35-a19a355099d5" alt="ss code 5" /> 
<br><strong>Figure 3.4.2 - Inspection Output </strong> </p>


## 4.0 Big Data Handling Strategies

### 4.1 Pandas (Traditional Methods)
Before applying any big data optimization techniques, we used Pandas to clean the dataset and establish a baseline for memory and execution time. 

<p align="center"> <img src="https://github.com/user-attachments/assets/1578e861-d8bd-4b19-847a-be4ced2bf165" alt="dask first run" />
<br><strong>Figure 4.1.1 - Code Snippet for Inital Setup </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/33f57c64-2952-497a-aee3-0adbdde1ff3b" alt="dask first run" />
<br><strong>Figure 4.1.2 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/702760e8-d6f4-438f-9c9c-f8fda69cdef6" alt="dask first run" />
<br><strong>Figure 4.1.3 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/e7672b5d-d5f4-4496-841a-0737ba6567d5" alt="dask first run" />
<br><strong>Figure 4.1.4 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/59c009a7-2cb4-4dd6-9847-2bacc0ec6071" alt="dask first run" />
<br><strong>Figure 4.1.5 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/6c29f376-3cf4-41b9-8180-b7638cd6c4e4" alt="dask first run" />
<br><strong>Figure 4.1.6 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/af881bb1-586c-43c9-a721-ab04fd705f87" alt="dask first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/56a57adf-7c25-41db-9298-01f5f2d147d7" alt="dask first run" />
<br><strong>Figure 4.1.7 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/df98b6e3-d531-4c09-bc54-306231ca85ee" alt="dask first run" />
<br><strong>Figure 4.1.8 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/d8d80abd-fe2d-424b-acf2-cc89acadd144" alt="dask first run" />
<br><strong>Figure 4.1.9 - Code Snippet to Start Performance Tracking </strong> </p>

### 4.2 Dask (Optimization)

<p align="center"> <img src="https://github.com/user-attachments/assets/2152689d-f28f-408d-ab62-7d8a3d5e2fea" alt="dask first run" />
<br><strong>Figure 4.2.1 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/effcb687-0e6d-4f58-b0ed-f5557d123edc" alt="dask first run" />
<br><strong>Figure 4.2.2 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/d923a130-eb76-40de-be60-c999602857af" alt="dask first run" />
<br><strong>Figure 4.2.3 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/f8f47e1b-7ce3-4b70-a271-6842a5a91c9b" alt="dask first run" />
<br><strong>Figure 4.2.4 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/3fac57d6-6036-4a1b-829a-59bcc7dde7c2" alt="dask first run" />
<br><strong>Figure 4.2.5 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/d020573f-784f-4b27-a3f7-6a4e149d31e3" alt="dask first run" />
<br><strong>Figure 4.2.6 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/122cde5e-e85b-45ef-ad36-8361874bdb6b" alt="dask first run" />
<br><strong>Figure 4.2.7 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/71375d27-0836-4dd6-b0b8-0df62ed5e34c" alt="dask first run" />
<br><strong>Figure 4.2.8 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/6150c5f8-58a9-46a2-929e-bc9f13f9defb" alt="dask first run" />
<br><strong>Figure 4.2.9 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/b1d9403e-eded-4db8-afe9-8db9506800df" alt="dask first run" />
<br><strong>Figure 4.2.10 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/dd7dd303-3260-4b57-9773-6643fc9641e6" alt="dask first run" />
<br><strong>Figure 4.2.11 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/125c5ea6-a7bb-4d73-9551-1d1c1761de7a" alt="dask first run" />
<br><strong>Figure 4.2.12 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/125c5ea6-a7bb-4d73-9551-1d1c1761de7a" alt="dask first run" />
<br><strong>Figure 4.2.13 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/67eccaf7-3544-4458-8761-46af7c305e0f" alt="dask first run" />
<br><strong>Figure 4.2.14 - Code Snippet to Start Performance Tracking </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/c360d52f-6a4a-4209-831a-aae186bb9f17" alt="dask first run" />
<br><strong>Figure 4.2.15 - Code Snippet to Start Performance Tracking </strong> </p>

### 4.3 Another Library (Optimization)

## 5.0 Comparative Analysis

### 5.1 Pandas Performance

<p align="center"> <img src="https://github.com/user-attachments/assets/97a092e3-0468-4ee9-b12b-e9df06aa3456" alt="pandas first run" />
<br><strong>Figure 4.1 - Pandas Performance </strong> </p>

![image](https://github.com/user-attachments/assets/d4b693cc-255a-4033-aad5-3f486f176155)


### 5.2 Dask Performance

<p align="center"> <img src="https://github.com/user-attachments/assets/4521e075-8ecb-4149-9e8b-09b1b99efd6b" alt="dask first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/9cabd3c2-08cc-472c-9dac-837c6a074951" alt="dask first run"/>
<p align="center"> <img src="https://github.com/user-attachments/assets/f6015abd-25ab-441e-b93a-3b105fb26897" alt="dask first run" />
<br><strong>Figure 4.1 - Dask Performance </strong> </p>

![image](https://github.com/user-attachments/assets/6d48f46b-72bc-4e6f-b1b5-cd12567a5918)


### 5.3 Another Library Performance


### 5.4 Performance Comparison Table 

<h4 align="center"><strong>Table 5.3.1 - Performance Comparison Table</strong></h4>

<div align="center">

<table>
  <thead>
    <tr>
      <th>Method</th>
      <th>Average Memory Used (MB)</th>
      <th>Average Execution Time (s)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Pandas</td>
      <td>2143.75</td>
      <td>67.23</td>
    </tr>
    <tr>
      <td>Dask</td>
      <td>285.65</td>
      <td>33.10</td>
    </tr>
    <tr>
      <td>Another Library</td>
      <td>-</td>
      <td>-</td>
    </tr>
  </tbody>
</table>

</div>

### 5.5 Performance Comparison Graph


## 6.0 Conclusion and Reflection
