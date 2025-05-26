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
- [References](#references)


## 1.0 Introduction
### 1.1 Objectives

## 2.0 Dataset Selection

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

### 🔐 Kaggle API Setup for Dataset Download

To access and download datasets directly from Kaggle within Google Colab, we first need to authenticate using the Kaggle API. This requires a Kaggle account and an API key (kaggle.json). <br> 
The first line in figure 3.1 prompts the user to upload the kaggle.json file, which contains the API credentials. <br>
The second commands in figure 3.1 create a hidden .kaggle directory in the user’s home path. Then, it copy the uploaded kaggle.json file into this directory. Next, it set the appropriate permissions (read/write for user only) to ensure security and avoid access issues.

<p align="center"> <img src="https://github.com/user-attachments/assets/0a805554-e4a2-464b-a503-78e5e7c4ea6e" alt="ss code 1" /> 
<br><strong>Figure 3.1 - Kaggle API Setup </strong> </p>

### 📥 Dataset Download and Extraction
Once the Kaggle API is properly configured, the commands in figure 3.2 are used to download and extract the dataset. The first command uses the kaggle CLI tool to download the dataset from Kaggle. The dataset will be downloaded as a ZIP file into the current working directory. The second command extracts the contents of the downloaded ZIP file into a folder named nyc_transport. The -o flag allows existing files to be overwritten if they already exist. After extraction, the raw dataset (e.g., mta_1712.csv) will be available for further processing, cleaning, and analysis.

<p align="center"> <img src="https://github.com/user-attachments/assets/16e9d301-8f6a-4542-ab22-499dd2d45f63" alt="ss code 2" /> 
<br><strong>Figure 3.2 - Dataset Download and Extraction </strong> </p>

### 💾 Saving Dataset to Google Drive

The following code in figure 3.3 is used to save the donwnloaded dataset to Google Drive for persistent storage and future use. The first command mounts the Google Drive to the Colab environment, allowing to read from and write to Drive directly. The second section creates a directory path inside Google Drive named Assign2/nyc_transport_data. In the third command, the cleaned DataFrame df is saved as a CSV file named mta_1712_cleaned.csv inside the target directory. The dataset is now saved securely in Google Drive and can be accessed later for inspection, modeling, or additional analysis.

<p align="center"> <img src="https://github.com/user-attachments/assets/b3e0b18c-e007-4478-bced-dd38fc946674" alt="ss code 3" /> 
<br><strong>Figure 3.3 - Saving Dataset to Google Drive </strong> </p>

### 🔍 Brief Data Inspection

The code in figure 3.4 loads the CSV file into a pandas DataFrame for inspection. 

<p align="center"> <img src="https://github.com/user-attachments/assets/263ec5e9-9f21-4464-b7a5-8937e442dbfb" alt="ss code 4" /> 
<br><strong>Figure 3.4 - Brief Data Inspection </strong> </p>

The output in figure 3.5 provides a quick overview of the dataset’s structure, including its dimensions, column names, and data types, laying the groundwork for deeper analysis and optimization steps.

<p align="center"> <img src="https://github.com/user-attachments/assets/63563598-6eb2-4ad7-be35-a19a355099d5" alt="ss code 5" /> 
<br><strong>Figure 3.5 - Inspection Output </strong> </p>


## 4.0 Big Data Handling Strategies

## 5.0 Comparative Analysis

Pandas Performance

<p align="center"> <img src="https://github.com/user-attachments/assets/97a092e3-0468-4ee9-b12b-e9df06aa3456" alt="ss output 1" />
<p align="center"> <img src="https://github.com/user-attachments/assets/1ebbf01b-f31f-4192-ab98-016ff77aef62" alt="ss output 2" />
<p align="center"> <img src="https://github.com/user-attachments/assets/e747dd40-ff6b-4fff-a2bb-5281e77b951d" alt="ss output 3" />
<br><strong>Figure 4.1 - Pandas Performance </strong> </p>

## 6.0 Conclusion and Reflection

## References
