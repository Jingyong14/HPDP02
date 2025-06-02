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

<p align="center"> <img src="https://github.com/user-attachments/assets/dc7cffef-f971-4d71-9ad7-9b1155e0e77c" alt="NYC Bus Data Overview" /> <br><strong>Figure 2.1.1 - Overview of New York City Bus Data</strong> </p>

As shown in Figure 2.1.1, this dataset provides a comprehensive overview of bus movement data across New York City, making it highly relevant for urban mobility analysis. The dataset is approximately **1.33 GB in size** and contains about **6.4 million rows** and **17 columns**, which satisfies the criteria of being large and rich enough for exploratory and performance comparisons.

### 2.2 Features Included

<p align="center"> <img src="https://github.com/user-attachments/assets/6112396b-dc45-460c-b17b-8a3e43202367" alt="15 first rows"/>
<p align="center"> <img src="https://github.com/user-attachments/assets/6c4b7019-7a7f-4409-84e8-fd4abf32b28e" alt="15 last rows" /> 
<br><strong>Figure 2.2.1 - Data Columns and Row Counts from CSV File</strong> </p>

Figure 2.2.1 illustrates a sample view of the dataset's structure, including column names and record counts. Among the features included are various timestamp fields such as *RecordedAtTime*, *ExpectedArrivalTime*, and *ScheduledArrivalTime*, which are essential for tracking punctuality and delay patterns. Additionally, the dataset captures bus route identifiers like *PublishedLineName* and *DirectionRef*, as well as origin and destination information with corresponding latitude and longitude coordinates. The presence of live GPS locations, next stop predictions, and fields such as *DistanceFromStop* and *ArrivalProximityText* further enhances the real-time and operational value of this dataset.

### 2.3 Justification
This dataset is particularly suitable for a big data handling assignment because of its large volume, structured schema, and real-time characteristics. It offers practical opportunities to explore and apply big data techniques such as chunked or parallelized data loading, data type optimization for memory efficiency, and performance benchmarking using tools like Dask against traditional Pandas operations. Moreover, the dataset simulates a real-world use case where a transportation agency must process millions of records to monitor services, analyze delays, and optimize route planning.

## 3.0 Data Loading and Inspection
This section outlines the essential steps taken to access, manage, and prepare the dataset from Kaggle for analysis in a Google Colab environment. The process begins with authenticating Kaggle API access, followed by downloading and extracting the dataset, then saving it to Google Drive for persistence, and finally performing a brief inspection of the data to understand its structure.

### 3.1 Kaggle API Setup for Dataset Download

To access and download datasets directly from Kaggle within Google Colab, we first need to authenticate using the Kaggle API. This requires a Kaggle account and an API key (kaggle.json). <br> 

<p align="center"> <img src="https://github.com/user-attachments/assets/0a805554-e4a2-464b-a503-78e5e7c4ea6e" alt="ss code 1" /> 
<br><strong>Figure 3.1.1 - Kaggle API Setup </strong> </p>

The first line in figure 3.1.1 prompts the user to upload the kaggle.json file, which contains the API credentials. <br>
The second commands in figure 3.1.1 create a hidden .kaggle directory in the user’s home path. Then, it copy the uploaded kaggle.json file into this directory. Next, it set the appropriate permissions (read/write for user only) to ensure security and avoid access issues.

### 3.2 Dataset Download and Extraction

<p align="center"> <img src="https://github.com/user-attachments/assets/16e9d301-8f6a-4542-ab22-499dd2d45f63" alt="ss code 2" /> 
<br><strong>Figure 3.2.1 - Dataset Download and Extraction </strong> </p>

Once the Kaggle API is properly configured, the commands in figure 3.2.1 are used to download and extract the dataset. The first command uses the kaggle CLI tool to download the dataset from Kaggle. The dataset will be downloaded as a ZIP file into the current working directory. The second command extracts the contents of the downloaded ZIP file into a folder named nyc_transport. The -o flag allows existing files to be overwritten if they already exist. After extraction, the raw dataset (e.g., mta_1712.csv) will be available for further processing, cleaning, and analysis.

### 3.3 Saving Dataset to Google Drive

<p align="center"> <img src="https://github.com/user-attachments/assets/b3e0b18c-e007-4478-bced-dd38fc946674" alt="ss code 3" /> 
<br><strong>Figure 3.3.1 - Saving Dataset to Google Drive </strong> </p>

The following code in figure 3.3 is used to save the donwnloaded dataset to Google Drive for persistent storage and future use. The first command mounts the Google Drive to the Colab environment, allowing to read from and write to Drive directly. The second section creates a directory path inside Google Drive named Assign2/nyc_transport_data. In the third command, the cleaned DataFrame df is saved as a CSV file named mta_1712_cleaned.csv inside the target directory. The dataset is now saved securely in Google Drive and can be accessed later for inspection, modeling, or additional analysis.

### 3.4 Brief Data Inspection 

<p align="center"> <img src="https://github.com/user-attachments/assets/263ec5e9-9f21-4464-b7a5-8937e442dbfb" alt="ss code 4" /> 
<br><strong>Figure 3.4.1 - Brief Data Inspection </strong> </p>

The code in figure 3.4.1 loads the CSV file into a pandas DataFrame for inspection.

<p align="center"> <img src="https://github.com/user-attachments/assets/63563598-6eb2-4ad7-be35-a19a355099d5" alt="ss code 5" /> 
<br><strong>Figure 3.4.2 - Inspection Output </strong> </p>

The output in figure 3.4.2 provides a quick overview of the dataset’s structure, including its dimensions, column names, and data types, laying the groundwork for deeper analysis and optimization steps.


## 4.0 Big Data Handling Strategies

### 4.1 Pandas (Traditional Methods)
Before applying any big data optimization techniques, we used Pandas to clean the dataset and establish a baseline for memory and execution time. 

<p align="center"> <img src="https://github.com/user-attachments/assets/1578e861-d8bd-4b19-847a-be4ced2bf165" alt="dask first run" />
<br><strong>Figure 4.1.1 - Code Snippet for Inital Setup </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/87f82082-e0e5-4461-be16-ebb7b886a5f5" alt="dask first run" />
<br><strong>Figure 4.1.1 - Code Snippet for Inital Setup </strong> </p>

<p align="center"> <img src="https://github.com/user-attachments/assets/41fdacd1-cfc5-4a0a-8c25-db0e4684c500" alt="dask first run" />
<br><strong>Figure 4.1.1 - Code Snippet for Inital Setup </strong> </p>

### 4.2 Dask (Optimization)
<p align="center"> <img src="https://github.com/user-attachments/assets/852d5e31-26a0-4a0e-ab1a-1da8e7acc86f" alt="dask first run" />
<br><strong>Figure 4.3.1 -  Code Snippet for Inital Setup </strong> </p>

Figure 4.1.3 illustrates the process of loading a large transportation dataset efficiently using Dask.
Only selected columns were read into memory with optimized data types, followed by random sampling of 1% to reduce computational load prior to data cleaning.

<p align="center"> <img src="https://github.com/user-attachments/assets/41b28074-99b0-404b-bd2f-8a52b6592535" alt="Optimized Data Loading and Sampling Using Dask" /> <br><strong>Figure 4.1.3 - Optimized Data Loading and Sampling Using Dask</strong> </p>
Figure 4.1.4 illustrates the preprocessing steps, where categorical columns were converted and enriched with an 'Unknown' category.
Missing values were filled, duplicates removed, and the dataset was computed. Performance was tracked to measure memory and time efficiency.

<p align="center"> <img src="https://github.com/user-attachments/assets/8a78583a-eacb-4c68-b84c-406ee3923e45" alt="Data Preprocessing and Optimization" /> <br><strong>Figure 4.1.4 - Data Preprocessing and Optimization</strong> </p>



### 4.3 Polars (Optimization)
<p align="center"> <img src="https://github.com/user-attachments/assets/aee6140c-f4f4-43d9-9e94-11a61f547a61" alt="dask first run" />
<br><strong>Figure 4.3.1 -  Code Snippet for Inital Setup </strong> </p>

Figure 4.3.1 illustrates loading the dataset with Polars’ lazy evaluation, selecting relevant columns for efficiency. The dataset schema was inspected to verify column names and data types, along with a count of rows before any cleaning was applied.

<p align="center"> <img src="https://github.com/user-attachments/assets/fbbda807-8c2e-4c66-a907-9f3b564cb244" alt="dask first run" />
<br><strong>Figure 4.3.1 - Data Loading and Initial Inspection Using Polars </strong> </p>

Figure 4.1.6 shows how missing values were filled and selected columns cast to categorical types using Polars expressions. Duplicates were removed, and performance metrics for memory usage and execution time were recorded after processing.
<p align="center"> <img src="https://github.com/user-attachments/assets/5341ecc8-9d74-44d3-99fc-2cf8d93c2e5b" alt="Data Preprocessing and Optimization" /> <br><strong>Figure 4.1.4 - Data Preprocessing and Optimization</strong> </p>

## 5.0 Comparative Analysis
This section presents a detailed comparison of the performance characteristics (memory usage and execution time) of three popular Python data manipulation libraries: Pandas, Dask, and Polars. The analysis aims to highlight the efficiency gains achieved through optimization techniques when handling data cleaning operations.
### 5.1 Pandas Performance

<p align="center"> <img src="https://github.com/user-attachments/assets/2bd296b3-7926-45a7-a420-2f56e8eb7811" alt="pandas first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/2f12a085-a850-47aa-85b6-0eff4ccc5789" alt="pandas first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/8ce8d0c6-7462-4bfd-abfb-4a422e4c4b4e" alt="pandas first run" />
<br><strong>Figure 5.1.1 - Pandas Performance </strong> </p>

Figure 5.11 details the performance of the Pandas library before applying specific optimization strategies. The results show the memory consumed and the time taken for a given task using standard Pandas operations. Three different runs are presented to demonstrate the average in performance.

### 5.2 Dask Performance

<p align="center"> <img src="https://github.com/user-attachments/assets/cf2eb0a3-5aec-4291-95b0-cf89d3856f7c" alt="dask first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/1c17cd84-2071-4b70-866e-c744ebe71e53" alt="dask first run"/>
<p align="center"> <img src="https://github.com/user-attachments/assets/24715f28-3a99-4b65-860e-2b8f6e648e66" alt="dask first run" />
<br><strong>Figure 5.2.1 - Dask Performance </strong> </p>

Figure 5.2.1 presents the performance metrics when the data processing task is optimized using the Dask library. Dask is designed for parallel computing and out-of-core processing, aiming to improve efficiency for larger-than-memory datasets. The results showcase the memory and execution time after Dask optimization.

### 5.3 Polars Performance

<p align="center"> <img src="https://github.com/user-attachments/assets/c2f73513-477e-4c71-a135-ce3c59960901" alt="pandas first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/721736a9-2c83-4866-a3fb-8f3d4c98bbb5" alt="pandas first run" />
<p align="center"> <img src="https://github.com/user-attachments/assets/327db067-8ded-4ff0-8904-af7bffafb15d" alt="pandas first run" />
<br><strong>Figure 5.3.1 - Polars Performance </strong> </p>

Figure 5.3.1 illustrates the performance when the data processing task is optimized using the Polars library, specifically leveraging its "Lazy" evaluation mode. Polars is a DataFrame library written in Rust, known for its high performance and efficient memory management. The results above reflect the improvements in memory and execution time with Polars optimization.

### 5.4 Performance Comparison Table 

<h4 align="center"><strong>Table 5.4.1 - Performance Comparison Table</strong></h4>

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
      <td>1800.70</td>
      <td>84.21</td>
    </tr>
    <tr>
      <td>Dask</td>
      <td>304.79</td>
      <td>61.23</td>
    </tr>
    <tr>
      <td>Polars</td>
      <td>1004.32</td>
      <td>10.36</td>
    </tr>
  </tbody>
</table>
</div>

Table 5.4.1 presents the average performance evaluation of three libraries. It clearly highlights the significant disparities across the three methods. Pandas, a cornerstone of Python data analysis, registered the highest memory consumption at 1800.70 MB and the longest average execution time of 84.21 seconds. This underscores its potential limitations when handling large datasets that exceed available RAM or require rapid processing.

In stark contrast, Dask demonstrated exceptional memory efficiency, utilizing only 304.79 MB, making it the most memory-lean option. Its execution time of 61.23 seconds also represented a substantial improvement over Pandas. Polars, while consuming more memory than Dask at 1004.32 MB, delivered an astonishingly fast average execution time of just 10.36 seconds, setting it apart as the fastest among the three.


### 5.5 Performance Comparison Chart
<p align="center"> <img src="https://github.com/user-attachments/assets/c08922ea-53ee-4530-b935-b09abe02e7f9" alt="dask first run" />
<br><strong>Figure 5.5.1 - Performance Comparison Bar Chart </strong> </p>

**Memory Usage Comparison:**
The left panel of Figure 5.5.1 illustrates the "Memory Usage Comparison." The bar for Pandas is visibly the tallest, confirming its highest memory footprint of approximately 1800 MB. Dask's bar is significantly shorter, visually representing its superior memory efficiency, hovering around 300 MB. Polars' bar, while taller than Dask's, is still substantially lower than Pandas', indicating its moderate memory usage at roughly 1000 MB. This visual representation vividly demonstrates Dask's advantage in memory conservation, especially crucial for large-scale data operations where RAM is a constraint.

**Execution Time Comparison:**
The right panel, "Execution Time Comparison," graphically depicts the processing speed of each method. The bar representing Pandas' execution time is the longest, clearly showing its slower performance, nearing 85 seconds. Dask's bar is noticeably shorter than Pandas', indicating its faster execution time of around 60 seconds. However, the most striking visual is Polars' bar, which is remarkably short, unequivocally showcasing its dominant speed, completing the task in just over 10 seconds. This segment of the chart powerfully illustrates Polars' exceptional performance for time-sensitive data operations.

**Overall Insights:**
Collectively, Table 5.3.1 and Figure 5.5.1 provide compelling evidence that both Dask and Polars offer substantial performance advantages over Pandas for the evaluated task. Dask emerges as the superior choice for memory efficiency, making it ideal for processing datasets that may otherwise lead to out-of-memory errors with traditional Pandas. Polars, on the other hand, is the undisputed leader in execution speed, making it the prime candidate for scenarios demanding the fastest possible data processing on a single machine. While Pandas remains valuable for smaller datasets and its extensive ecosystem, these comparisons underscore the growing importance of libraries like Dask and Polars for tackling modern big data challenges effectively and efficiently.

## 6.0 Conclusion and Reflection

## 6.0 Conclusion and Reflection

This assignment has thoroughly explored and compared various strategies for handling large datasets in Python, utilizing Pandas, Dask, and Polars. Our objective was to evaluate and optimize performance in terms of memory usage and execution time, and to analyze the effectiveness of each method in a big data context. The "New York City Bus Data" dataset, with its substantial size of 1.33 GB and 6.4 million rows, proved to be an excellent real-world testbed for these comparisons.

The comparative analysis unequivocally demonstrated that both Dask and Polars offer significant performance advantages over traditional Pandas for large-scale data processing tasks. **Dask distinguished itself as the most memory-efficient library**, consuming merely 304.79 MB on average, a stark contrast to Pandas' 1800.70 MB. This makes Dask an invaluable tool for working with datasets that exceed available RAM, allowing for efficient "out-of-core" processing and distributed computing. Its improved execution time of 61.23 seconds also showcased the benefits of its parallel computing capabilities.

**Polars, however, emerged as the clear winner in terms of raw processing speed**, completing the task in an astonishing 10.36 seconds. This remarkable performance is largely attributed to its Rust-based, multi-threaded architecture and its efficient utilization of the Apache Arrow memory format. While its memory consumption of 1004.32 MB was higher than Dask's, it was still significantly more efficient than Pandas, solidifying its position as a go-to library for speed-critical, in-memory operations on large datasets.

It is crucial to acknowledge that the optimal performance of each library is highly dependent on how data is handled and processed. Our experiments highlighted that **each library has its own inherent design principles and best practices for optimization**. For instance, while Polars generally excels in speed, there are specific scenarios or **"wrong ways of data cleaning" where its performance might surprisingly be worse than Pandas**. This can occur if the operations are not aligned with Polars' vectorized approach or if intermediate data structures are inadvertently created in a less efficient manner. For example, excessive use of UDFs (User Defined Functions) or iterative row-wise operations in Polars, which are not optimized for its columnar processing, could lead to unexpected performance bottlenecks, potentially making a Pandas approach seem faster in specific, poorly optimized cases. This serves as a critical reminder that **understanding the underlying architecture and idiomatic usage of each library is paramount to achieving its full performance potential.**

In reflection, this assignment reinforced the notion that there is no one-size-fits-all solution for big data handling. The choice between Pandas, Dask, and Polars should be a strategic decision based on the specific task requirements, dataset characteristics (size, structure), available computational resources, and the desired trade-offs between memory efficiency and execution speed. Pandas remains a foundational library for its rich ecosystem and ease of use, particularly for smaller to medium-sized datasets. However, for genuinely "big data" challenges, Dask provides robust scalability for distributed and memory-constrained environments, while Polars offers unparalleled speed for in-memory, high-performance computing. Mastering big data handling truly involves understanding the unique strengths and optimal application strategies for each of these powerful tools.
