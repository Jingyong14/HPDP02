<h1>SECP3133 High Performance Data Processing - Section 02</h1>

<h2>Assignment 2 - Mastering Big Data Handling</h2>

<h3>Group Shockwave:</h3>
<ul>
<li><strong>LIM JING YONG</strong> - A22EC0182</li>
<li><strong>LEE SOON DER</strong> - A22EC0065</li>
</ul>

<hr>

<h2>Task 1: Dataset Selection</h2>

<p>In this section, we decided to select our dataset in Kaggle due to its functionality to show the size of the dataset (in MB). This allows us to quickly find suitable and large enough dataset to undergo optimization during the dataset loading process.</p>

<p>The dataset we chose is the <strong>continental2.csv</strong> file from the <em>COVID-19 in the American Continent</em> dataset, which consists of <strong>1.07 GB</strong> of data. This dataset records the number of COVID-19 cases that happened across the years 2020 to 2022 in different countries.</p>

<div align="center">
  <img src="figures/Kaggle_Dataset.png" width="700">
  <p><strong>Figure 1.1:</strong> View of the CSV file in Kaggle</p>
</div>

<p>The dataset consists of <strong>14 columns</strong> (2 irrelevant ID columns) and <strong>1,048,576 rows</strong> of data.</p>

<div align="center">
  <img src="figures/csv_screenshot1.png" width="600">
  <img src="figures/csv_screenshot2.png" width="600">
  <p><strong>Figure 1.2:</strong> Data columns and row count from the CSV file</p>
</div>

<br>

## Task 2: Load and Inspect Data

In this section, the dataset was obtained using the Kaggle API and processed with Pandas in Google Colab. We also performed a basic inspection to understand the dataset's structure and contents.

Figure 2.1 below shows the use of the Kaggle API to automate dataset retrieval. This step is mandatory for enabling authenticated downloads in Colab.

![Using Kaggle API](figures/Task2.1.png)  
**Figure 2.1:** Use of Kaggle API in Google Colab

Figure 2.2 below shows the installation of the Kaggle CLI tool and the command to download the desired dataset. This step automates the dataset retrieval process from the Kaggle website.

![Kaggle CLI Install and Download](figures/Task2.2.png)  
**Figure 2.2:** Installing Kaggle CLI and downloading dataset

Figure 2.3 below shows the code used to load the dataset (`continental2.csv`) into memory using the Pandas library. This method is commonly used for small to medium-sized datasets and is sufficient for initial inspection and cleaning.

![Loading CSV with Pandas](figures/Task2.3.png)  
**Figure 2.3:** Loading dataset using Pandas

After loading the dataset, we performed a basic inspection to understand its structure and contents, as shown in Figure 2.4 below.

![Inspecting the dataset with Pandas](figures/Task2.4.png)  
**Figure 2.4:** Dataset inspection using Pandas

<br>

## Task 3: Apply Big Data Handling Strategies

In this section, we showcase how the Dask and Polars libraries are used to optimize the performance of dataset loading.

### Dask

Dask is a parallel computing library that scales the Pandas interface for large-memory data processing using lazy evaluation and task scheduling. In this section, we apply five optimization strategies using Dask to handle a large dataset efficiently. The complete implementation is shown in Figure 3.1 below.

![Dask Full Implementation](figures/Task3.1.png)  
**Figure 3.1:** Full implementation using Dask

Figure 3.1.1 shows line 11 of the implementation. Only relevant columns are selected to reduce load size, which reduces memory usage and speeds up loading by skipping irrelevant data.

![Dask Column Selection](figures/Task3.1.1.png)  
**Figure 3.1.1:** Selecting relevant columns

Figure 3.1.2 shows line 14 of the implementation. Data types are optimized by converting numeric fields to float32 and categorical columns to category, reducing memory usage.

![Dask Data Type Optimization](figures/Task3.1.2.png)  
**Figure 3.1.2:** Optimizing data types

Figure 3.1.3 shows line 18 of the implementation. The CSV file is loaded in parallel using dd.read_csv() with blocksize="128MB" to split data into smaller partitions, also known as chunking.

![Dask Chunk Loading](figures/Task3.1.3.png)  
**Figure 3.1.3:** Loading CSV in chunks with Dask

Figure 3.1.4 shows line 23 of the implementation. A 10% sample of the dataset is taken for faster prototyping.

![Dask Sampling](figures/Task3.1.4.png)  
**Figure 3.1.4:** Sampling a portion of the dataset

Figure 3.1.5 shows line 26 of the implementation. The compute() function is triggered to execute all lazy operations.

![Dask Compute Function](figures/Task3.1.5.png)  
**Figure 3.1.5:** Executing lazy operations with compute()

Finally, Figure 3.2 shows the output after running the code. Dask successfully demonstrates how these strategies collectively reduce memory usage and prepare the data efficiently.

![Dask Output](figures/Task3.2.png)  
**Figure 3.2:** Output after executing all Dask operations

### Polars

Next, the **Polars** library is also used for optimization of dataset loading. Polars excels in handling datasets that are big but still fit into memory, making it a perfect choice for our scenario.

Polars utilizes **lazy evaluation** and **multithreading**, which we will demonstrate in the figures below.

Figure 3.3 shows the full code used in our Polars library optimization technique:  
- **Line 1**: Polars library is imported.  
- **Line 4**: Dataset is read lazily using the `lazy()` function.  
- **Lines 7 to 14**: Polars methods are used to display dataset shape, columns, and data types.  
- **Lines 17 to end**: Null and duplicated data are dropped, and the `collect()` function is used to trigger actual execution.

![Figure 3.3 - Full coding of Polars optimization technique](figures/polars_coding.png)

**Figure 3.3:** Full coding of Polars optimization technique

Figure 3.4 shows the output after running the code. Output of column names were truncated due to string length exceeding browser width.

![Figure 3.4 - Output of the Polars optimization code](figures/polars_result.png)

**Figure 3.4:** Output of the Polars optimization code

<br>

## Task 4: Comparative Analysis

In this section, we evaluate the performance of each library and present the results of our qualitative performance measurements using graphs.

### How We Compare

To assess performance, we use Python libraries such as `time`, `psutil`, and `os` to calculate:
- The **time taken**
- The **total memory used**

These measurements are taken at the **start** and **end** of the code execution that processes a large dataset. Each experiment is repeated **three times** to calculate the **average** processing time and memory usage for greater accuracy.

#### Code Snippets

The following figure shows the code used to import performance measurement libraries and initialize tracking variables:

![Figure 4.1 - Initial performance measurement code](figures/analysis_initial.png)  
**Figure 4.1:** Code snippet for importing libraries and initializing performance tracking

The next figure shows the code for recording final metrics and computing the actual time taken and memory consumed during the operation:

![Figure 4.2 - Final performance measurement code](figures/analysis_final.png)  
**Figure 4.2:** Code snippet for capturing final measurements and calculating performance

### Result

##### Performance Results by Library

Figure 4.3 shows the results of the first, second, and third run using the Pandas library.

![Pandas Run 1](figures/Task4.3.1.jpg)  
![Pandas Run 2](figures/Task4.3.2.jpg)  
![Pandas Run 3](figures/Task4.3.3.jpg)  
**Figure 4.3:** Three runs using Pandas library

Figure 4.4 shows the results of the first, second, and third run using the Polars library.

![Polars Run 1](figures/Task4.3.4.jpg)  
![Polars Run 2](figures/Task4.3.5.jpg)  
![Polars Run 3](figures/Task4.3.6.jpg)  
**Figure 4.4:** Three runs using Polars library

Figure 4.5 shows the results of the first, second, and third run using the Dask library.

![Dask Run 1](figures/Task4.3.7.png)  
![Dask Run 2](figures/Task4.3.8.png)  
![Dask Run 3](figures/Task4.3.9.png)  
**Figure 4.5:** Three runs using Dask library

---

#### Execution Time Comparison

Figure 4.6 presents a bar chart showing the processing time (in seconds) taken by each method over three repeated runs. Pandas took around 27 seconds on average. Polars consistently outperformed the others by completing tasks in as little as 11–16 seconds. Dask, while designed for scalability, showed longer processing time (around 42 seconds) due to task scheduling and overhead in parallel execution.

![Execution Time Bar Chart](figures/Task4.4.png)  
**Figure 4.6:** Execution time comparison of Pandas, Polars, and Dask

---

#### Memory Usage Comparison

Figure 4.7 presents a line chart showing the memory usage (in MB) for each approach across three runs. Pandas used the most memory (~1350MB), which may be problematic for large datasets. Polars significantly reduced memory usage to around 1100MB due to its efficient memory management in Rust. Dask showed the lowest memory usage because it loads data in chunks rather than all at once.

![Memory Usage Line Chart](figures/Task4.5.png)  
**Figure 4.7:** Memory usage comparison across Pandas, Polars, and Dask

#### Ease of Processing

| Method | Ease of Processing |
|--------|--------------------|
| Pandas | Easiest to use with familiar syntax but lacks optimization for large data. |
| Polars | Performed excellently with simple multithreading and is relatively easy to adopt. |
| Dask   | Powerful scalability but requires more setup and understanding of parallel processing concepts. |

<br>

## Task 5: Conclusion & Reflection

From this assignment, we are able to understand the significance of using optimization libraries such as Dask or Polars when working with big data. Several observations were made during the progression of the project.

Initially, Modin and Ray library were chosen as the tertiary library to perform optimization. However, the performance shows negative improvement, possibly due to the dataset not being big enough (even if it's 1GB). Memory used also increased significantly, due to Ray workers paralleling jobs and taking more space.

Next, simplicity of task or operation when using these optimization libraries also play a part in defining the performance of the libraries. For example, due to this assignment measuring only the process of loading the dataset and some simple data inspections, libraries such as Dask get an increase in processing time due to its parallel and distributed architecture. This means extra time is used to create a “Task graph” to allow Dask to perform parallelism, which exceeds the actual time taken to run the codes. However, memory usage significantly decreases as chunk processing (128 MB in our case) loads shards of the entire dataset into each worker, lowering peak memory usage overall.

Pandas library on the other hand performs averagely in terms of processing time and memory usage. As an eager execution library, processing time of loading the dataset was not significantly high due to simplicity of operation. However, memory usage across each run (Refer Task 4) appears the highest because the entire 1 GB dataset is loaded into memory on runtime through a single CPU and no parallelization.

Last but not least, Polars is the best library option for our exact scenario. Polars support datasets which are not overly large (> 10 GB) due to multithreading which utilizes CPU cores instead of spawning workers like Dask. This factor lowers memory usage. Lazy execution property of Polars also optimizes the coding pipeline which is user-defined, rather than creating a new system-defined “Task Graph” like Dask on runtime, ensuring the total processing time does not surpass the actual time used to process the operations.

With that being said, we can determine libraries efficiency can be ordered as:

**Polars > Dask > Pandas**

Where the dataset is not significantly large while processing operation is simple.
