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

<h2>Task 2: Load and Inspect Data</h2>

<p>In this section, the dataset was obtained using the Kaggle API and processed with Pandas in Google Colab. We also performed a basic inspection to understand the dataset's structure and contents.</p>

<div align="center">
  <img src="figures/Task2.1.png" width="700">
  <p><strong>Figure 2.1:</strong> Use of Kaggle API in Google Colab</p>
</div>

<p>Figure 2.2 below shows the installation of the Kaggle CLI tool and the command to download the desired dataset. This step automates the dataset retrieval process from the Kaggle website.</p>

<div align="center">
  <img src="figures/Task2.2.png" width="700">
  <p><strong>Figure 2.2:</strong> Installing Kaggle CLI and downloading dataset</p>
</div>

<p>Figure 2.3 below shows the code used to load the dataset (<code>continental2.csv</code>) into memory using the Pandas library. This method is commonly used for small to medium-sized datasets and is sufficient for initial inspection and cleaning.</p>

<div align="center">
  <img src="figures/Task2.3.png" width="700">
  <p><strong>Figure 2.3:</strong> Loading dataset using Pandas</p>
</div>

<p>After loading the dataset, we performed a basic inspection to understand its structure and contents, as shown in Figure 2.4 below.</p>

<div align="center">
  <img src="figures/Task2.4.png" width="700">
  <p><strong>Figure 2.4:</strong> Dataset inspection using Pandas</p>
</div>

<br>

<h2>Task 3: Apply Big Data Handling Strategies</h2>
<p>In this section, we showcase how the Dask and Polars libraries are used to optimize the performance of dataset loading.</p>

<h3>Dask</h3>
<p>Dask is a parallel computing library that scales the Pandas interface for large-memory data processing using lazy evaluation and task scheduling. In this section, we apply five optimization strategies using Dask to handle a large dataset efficiently. The complete implementation is shown in Figure 3.1 below.</p>

<div align="center">
  <img src="figures/Task3.1.png" width="500" height="650">
  <p><strong>Figure 3.1:</strong> Full implementation using Dask</p>
</div>

<p>Figure 3.1.1 shows the line 11 of the implementation. Only relevant columns are selected to reduce load size to reduce memory usage and speed up loading by skipping irrelevant data.
</p>

<div align="center">
  <img src="figures/Task3.1.1.png" width="700">
  <p><strong>Figure 3.1.1:</strong> Selecting relevant columns</p>
</div>

<p>
Figure 3.1.2 shows the line 14 of the implementation. Data types are optimized by converting numeric fields to float32 and categorical columns to category to reduce memory usage.
</p>

<div align="center">
  <img src="figures/Task3.1.2.png" width="400" height="300">
  <p><strong>Figure 3.1.2:</strong> Optimizing data types</p>
</div>

<p>
Figure 3.1.3 shows the line 18 of the implementation. The CSV file is loaded in parallel using dd.read_csv() with a blocksize=”128MB” to split data into smaller partitions which is chunking.
</p>

<div align="center">
  <img src="figures/Task3.1.3.png" width="700">
  <p><strong>Figure 3.1.3:</strong> Loading CSV in chunks with Dask</p>
</div>

<p>
Figure 3.1.4 shows the line 23 of the implementation. A 10% sample of the dataset is taken for faster prototyping.
</p>

<div align="center">
  <img src="figures/Task3.1.4.png" width="700">
  <p><strong>Figure 3.1.4:</strong> Sampling a portion of the dataset</p>
</div>

<p>
Figure 3.1.5 shows the line 26 of the implementation. The function compute() is triggered to execute all processes of all lazy operations.
</p>

<div align="center">
  <img src="figures/Task3.1.5.png" width="700">
  <p><strong>Figure 3.1.5:</strong> Executing lazy operations with compute()</p>
</div>

<p>
Figure 3.2 shows the output after running the code. Dask successfully demonstrates how these strategies collectively reduce memory usage and prepare data efficiently.
</p>

<div align="center">
  <img src="figures/Task3.2.png" width="700">
  <p><strong>Figure 3.2:</strong> Output after executing all Dask operations</p>
</div>

<h3>Polars</h3>
<p>The <strong>Polars</strong> library is also used for optimization of dataset loading. Polars excels in handling datasets that are big but still fit into memory, making it a perfect choice for our scenario. Polars utilizes <em>lazy evaluation</em> and <em>multithreading</em>, which we will demonstrate in the figures below.</p>

<p>Figure 3.3 shows the full code used in our Polars library optimization technique:</p>
<ul>  
<li><strong>Line 1</strong>: Polars library is imported.</li>
<li><strong>Line 4</strong>: Dataset is read lazily using the `lazy()` function.</li>
<li><strong>Lines 7 to 14</strong>: Polars methods are used to display dataset shape, columns, and data types.</li>
<li><strong>Lines 17 to end</strong>: Null and duplicated data are dropped, and the `collect()` function is used to trigger actual execution.
</ul>

<div align="center">
  <img src="figures/polars_coding.png" width="700">
  <p><strong>Figure 3.3:</strong> Full coding of Polars optimization technique</p>
</div>

<p>Figure 3.4 shows the output after running the code. Output of column names were truncated due to string length exceeding browser width.</p>

<div align="center">
  <img src="figures/polars_result.png" width="700">
  <p><strong>Figure 3.4:</strong> Output of the Polars optimization code</p>
</div>

<br>

<h2>Task 4: Comparative Analysis</h2>
<p>In this section, we evaluate the performance of each library and present the results of our qualitative performance measurements using graphs.</p>

<h3>How We Compare</h3>
<p>To assess performance, we use Python libraries such as <code>time</code>, <code>psutil</code>, and <code>os</code> to calculate:</p>
<ul>
  <li>The <strong>time taken</strong></li>
  <li>The <strong>total memory used</strong></li>
</ul>
<p>These measurements are taken at the <strong>start</strong> and <strong>end</strong> of the code execution that processes a large dataset. Each experiment is repeated <strong>three times</strong> to calculate the <strong>average</strong> processing time and memory usage for greater accuracy.</p>

<p>Figure 4.1 shows the code snippet of the libraries imported for performance measurement and the initialization of starting variables.</p>

<div align="center">
  <img src="figures/analysis_initial.png" width="700">
  <p><strong>Figure 4.1:</strong> Code snippet for importing libraries and initializing performance tracking</p>
</div>

<p>Figure 4.2 shows the code snippet for recording final variables and calculations to determine the actual time taken for operation processing and total memory used.</p>

<div align="center">
  <img src="figures/analysis_final.png" width="700">
  <p><strong>Figure 4.2:</strong> Code snippet for capturing final measurements and calculating performance</p>
</div>

<h3>Performance Results by Library</h3>

<p>Figure 4.3 shows the results of the first, second, and third run using the pandas library.</p>

<div align="center">
  <img src="figures/Task4.3.1.jpg" width="500">
  <img src="figures/Task4.3.2.jpg" width="500">
  <img src="figures/Task4.3.3.jpg" width="500">
  <p><strong>Figure 4.3:</strong> Three runs using Pandas library</p>
</div>

<p>Figure 4.4 shows the results of the first, second, and third run using the polars library.</p>

<div align="center">
  <img src="figures/Task4.3.4.jpg" width="500">
  <img src="figures/Task4.3.5.jpg" width="500">
  <img src="figures/Task4.3.6.jpg" width="500">
  <p><strong>Figure 4.4:</strong> Three runs using Polars library</p>
</div>

<p>Figure 4.5 shows the results of the first, second, and third run using the dask library</p>

<div align="center">
  <img src="figures/Task4.3.7.png" width="500">
  <img src="figures/Task4.3.8.png" width="500">
  <img src="figures/Task4.3.9.png" width="500">
  <p><strong>Figure 4.5:</strong> Three runs using Dask library</p>
</div>

<h3>Execution Time Comparison</h3>

<p>Figure 4.6 below presents a bar chart showing the processing time (in seconds) taken by each method over three repeated runs. Pandas took around 27 seconds on average and Polars consistently outperformed the others by completing tasks in as little as 11-16 seconds. Dask, while designed for scalability, showed longer processing time (around 42 seconds) due to task scheduling and overhead in parallel execution.
</p>

<div align="center">
  <img src="figures/Task4.4.png" width="700">
  <p><strong>Figure 4.6:</strong> Execution time comparison of Pandas, Polars, and Dask</p>
</div>

<h3>Memory Usage Comparison</h3>

<p>Figure 4.7 below presents a line chart showing the memory usage (in MB) for each approach across three runs. Pandas used the most memory (~1350MB), which may be problematic for large datasets. Polars significantly reduced memory usage to around 1100MB due to its efficient memory management in Rust. Dask showed the extremely lowest memory usage because it loads data in chunks rather than all at once.
</p>

<div align="center">
  <img src="figures/Task4.5.png" width="700">
  <p><strong>Figure 4.7:</strong> Memory usage comparison across Pandas, Polars, and Dask</p>
</div>

<h3>Ease of Processing</h3>
<div align="center">
  <table border="1" cellspacing="0" cellpadding="6">
    <tr>
      <th>Method</th>
      <th>Ease of Processing</th>
    </tr>
    <tr>
      <td>Pandas</td>
      <td>Easiest to use with familiar syntax but lacks optimization for large data.</td>
    </tr>
    <tr>
      <td>Polars</td>
      <td>Performed excellently with simple multithreading and is relatively easy to adopt.</td>
    </tr>
    <tr>
      <td>Dask</td>
      <td>Powerful scalability but requires more setup and understanding of parallel processing concepts.</td>
    </tr>
  </table>
<p><strong>Table 4.8: </strong>Ease of processing for each method</p>
</div>

<br>

<h2>Task 5: Conclusion & Reflection</h2>

<p>From this assignment, we are able to understand the significance of using optimization libraries such as Dask or Polars when working with big data. Several observations were made during the progression of the project.</p>

<p>Initially, Modin and Ray library were chosen as the tertiary library to perform optimization. However, the performance shows negative improvement, possibly due to the dataset not being big enough (even if it's 1GB). Memory used also increased significantly, due to Ray workers paralleling jobs and taking more space.</p>

<p>Next, simplicity of task or operation when using these optimization libraries also play a part in defining the performance of the libraries. For example, due to this assignment measuring only the process of loading the dataset and some simple data inspections, libraries such as Dask get an increase in processing time due to its parallel and distributed architecture. This means extra time is used to create a “Task graph” to allow Dask to perform parallelism, which exceeds the actual time taken to run the codes. However, memory usage significantly decreases as chunk processing (128 MB in our case) loads shards of the entire dataset into each worker, lowering peak memory usage overall.</p>

<p>Pandas library on the other hand performs averagely in terms of processing time and memory usage. As an eager execution library, processing time of loading the dataset was not significantly high due to simplicity of operation. However, memory usage across each run (Refer Task 4) appears the highest because the entire 1 GB dataset is loaded into memory on runtime through a single CPU and no parallelization.
</p>

<p>Last but not least, Polars is the best library option for our exact scenario. Polars support datasets which are not overly large (> 10 GB) due to multithreading which utilizes CPU cores instead of spawning workers like Dask. This factor lowers memory usage. Lazy execution property of Polars also optimizes the coding pipeline which is user-defined, rather than creating a new system-defined “Task Graph” like Dask on runtime, ensuring the total processing time does not surpass the actual time used to process the operations.
</p>

<p>With that being said, we can determine libraries efficiency can be ordered as:
</p>

<div align="center">
	<strong>Polars > Dask > Pandas</strong>
</div>
<br>

<p>Where the dataset is not significantly large while processing operation is simple.</p>
