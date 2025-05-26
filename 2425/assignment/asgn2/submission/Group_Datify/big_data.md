<h1>SECP3133 High Performance Data Processing - Section 02</h1>

<h2>Assignment 2 - Mastering Big Data Handling</h2>

<h3>Group Datify:</h3>
<ul>
<li><strong>CAMILY TANG JIA LEI</strong> - A22EC0039</li>
<li><strong>NG SHU YU</strong> - A22EC0228</li>
</ul>

<hr>

<h2>1.0 Introduction</h2>
<p>
  TThe amount of data created today is accelerating. This poses challenges for classical data processing tools. For instance, libraries such as Pandas may run into issues when working with datasets in the range of several hundred megabytes. These tools can reach memory limits and experience long processing times. Consequently, businesses require more scalable and efficient methods to process and analyse the growing volume of data more effectively.
</p>

<h2>1.1 Objectives</h2>
<p>
  The objectives of this assignment are to address the challenges of large-scale data extraction and processing by:
</p>
<ul>
  <li>To apply various big data techniques, including chunking, sampling, type optimisation, and parallel computing.</li>
  <li>To evaluate and compare the performance of traditional Pandas methods against optimised data handling strategies, such as Polars and Dask.</li>
  <li>To assess the effectiveness of each technique in terms of memory usage, execution time, and ease of processing.</li>
</ul>

<h2>2.0 Dataset Selection</h2>
<p>
  The dataset selected is the “500K+ Spotify Songs with Lyrics, Emotions & More” dataset, which is publicly available on Kaggle (Devdope, n.d.). This dataset contains information on over 500,000 Spotify songs, including audio features, metadata, and popularity metrics. For the purpose of this analysis, the CSV version of the dataset was utilised, comprising 551,440 entries.
</p>
<ul>
  <li><strong>Source:</strong> <a href="https://www.kaggle.com/datasets/devdope/900k-spotify/data">Kaggle</a></li>
  <li><strong>File Format:</strong> CSV</li>
  <li><strong>File Size:</strong> Approximately 1,122 MB (uncompressed)</li>
  <li><strong>Domain:</strong> Music Streaming and Audio Analysis</li>
  <li><strong>Total Records:</strong> 551,440 entries</li>
  <li><strong>Key Features:</strong> Song title, artist, genre, release date, popularity, and audio features such as tempo, energy, acousticness, and danceability.</li>
</ul>
<p>
  The size and variety of the dataset used to test big data handling methods are considered impressive. Both categorical and continuous data are included, allowing for the application of different optimisation approaches. Moreover, challenges commonly faced by organisations in the music streaming sector are presented in the dataset, effectively mirroring real-world conditions.
</p>

<h2>3.0 Load and Inspect Data</h2>
<p>
  The selected dataset was loaded and processed using three libraries—Pandas, Polars, and Dask—to demonstrate their performance. The objective was to efficiently read and process a large file while preserving the validity of the data and enabling further analysis, as illustrated in Table 1.
</p>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <caption style="caption-side: top; font-weight: bold; margin-bottom: 8px;">
    Table 1: Summary of Dataset Handling and Evaluation Procedures Across Libraries
  </caption>
  <tbody>
    <tr>
      <th style="text-align: left; width: 20%;">Environment Setup</th>
      <td>The Kaggle API key was uploaded and configured in Google Colab to download and extract the dataset for all methods.</td>
    </tr>
    <tr>
      <th style="text-align: left;">Data Loading</th>
      <td>Each library loaded the same subset of relevant columns: artist, song, length, emotion, genre, release date, popularity, energy, danceability, and positiveness. Data types were optimised by converting strings to categorical types and numerical features to 32-bit floats to reduce memory usage.</td>
    </tr>
    <tr>
      <th style="text-align: left;">Data Processing</th>
      <td>Missing values were removed, and a 10% random sample was taken to ensure fair comparison across libraries.</td>
    </tr>
    <tr>
      <th style="text-align: left;">Performance Measurement</th>
      <td>Execution time for loading, cleaning, and sampling was recorded. Memory usage of the sampled dataset was also calculated to evaluate efficiency.</td>
    </tr>
    <tr>
      <th style="text-align: left;">Inspection</th>
      <td>Each sampled dataset was inspected by displaying basic info such as column names, data types, number of entries, execution time, memory usage, and a preview of the first few rows.</td>
    </tr>
  </tbody>
</table>

<h2>4.0 Big Data Handling Strategies</h2>
<p>
  Efficient handling of large datasets is regarded as a critical aspect of working with data at scale. Traditional data processing methods are often constrained by memory limitations, reduced speed, and limited scalability. To overcome these challenges, various techniques have been developed to optimise memory usage, enhance processing speed, and enable parallel execution of tasks. In this section, several useful strategies—such as loading specific columns, optimising data types, and reading files efficiently—are discussed. These techniques are examined in the context of the capabilities provided by Pandas, Dask, and Polars to highlight how each library addresses big data challenges in resource- and performance-sensitive scenarios.
</p>

<h3>4.1 Environment Setup and Dataset Acquisition</h3>
<p>
  A uniform environment setup was employed across the three data processing libraries—Pandas, Polars, and Dask—to ensure real, comparable, and controlled performance experiments. All experiments were conducted using Google Colab, a platform well-suited for working with large datasets under limited resources, and offering support for live collaboration.
</p>

<p>
  As shown in Figures 1, 2, and 3, the respective libraries were imported and initiated with standard preprocessing procedures. The uniform setup began with the upload of the Kaggle API access key (kaggle.json) and its definition in the system environment, which enabled secure access to the dataset. The dataset, titled “500K+ Spotify Songs with Lyrics, Emotions & More”, was accessed via the Kaggle API and extracted using Python’s ‘zipfile module’. Once extracted, the dataset was prepared for loading and processing within each of the libraries.
</p>


<figure>
  <img src="figures/figure1.png" alt="Pandas Environment Setup and Data Processing Workflow">
  <figcaption>Figure 1: Pandas Environment Setup and Data Processing Workflow</figcaption>
</figure>

<br>

<figure>
  <img src="figures/figure2.png" alt="Polars Environment Setup and Data Processing Workflow">
  <figcaption>Figure 2: Polars Environment Setup and Data Processing Workflow</figcaption>
</figure>

<br>

<figure>
  <img src="figures/figure3.png" alt="Dask Environment Setup and Data Processing Workflow">
  <figcaption>Figure 3: Dask Environment Setup and Data Processing Workflow</figcaption>
</figure>

<br>

<p>
  To facilitate performance analysis, execution time was monitored using the ‘time’ module by marking the beginning and end of the execution interval. This process is illustrated in Figure 4, where the script initiates time tracking.
</p>

<figure>
  <img src="figures/figure4.png" alt="Start of Execution Time Tracking in All Libraries">
  <figcaption>Figure 4: Start of Execution Time Tracking in All Libraries</figcaption>
</figure>

<p>
  Moreover, each library provided its own method for determining execution time and memory usage, as shown in Figures 5, 6, and 7 for Pandas, Polars, and Dask, respectively. The total execution time was calculated by subtracting the start time from the end time, while memory consumption was obtained using library-specific functions. 
</p>

<p>
  For Pandas, memory usage was calculated using .memory_usage(deep=True).sum(). In Polars, the .estimated_size() method was applied. For Dask, .memory_usage(deep=True) was used, followed by aggregation of the results. 
</p>

<p>
  These measurements allowed for a reasonably fair comparison of memory usage and execution time across the three libraries during the dataset processing.
</p>

<figure>
  <img src="figures/figure5.png" alt="Execution Time and Memory Usage Calculation in Pandas">
  <figcaption>Figure 5: Execution Time and Memory Usage Calculation in Pandas</figcaption>
</figure>

<br>

<figure>
  <img src="figures/figure6.png" alt="Execution Time and Memory Usage Calculation in Polars">
  <figcaption>Figure 6: Execution Time and Memory Usage Calculation in Polars</figcaption>
</figure>

<br>

<figure>
  <img src="figures/figure7.png" alt="Execution Time and Memory Usage Calculation in Dask">
  <figcaption>Figure 7: Execution Time and Memory Usage Calculation in Dask</figcaption>
</figure>

<h2>7.0 References</h2>
<ul>
  <li>Devdope. (n.d.). <em>500K+ Spotify songs with lyrics, emotions & more</em> [Data set]. Kaggle. <a href="https://www.kaggle.com/datasets/devdope/900k-spotify">https://www.kaggle.com/datasets/devdope/900k-spotify</a></li>
  <li>Edwin. (2025, February 27). <em>Dask: Detailed guide for scalable computing</em>. Python Central. <a href="https://www.pythoncentral.io/dask-detailed-guide-for-scalabale-computing/">https://www.pythoncentral.io/dask-detailed-guide-for-scalabale-computing/</a></li>
  <li>Fischer, B. (2024, December 23). <em>Python advanced: 10 things you can do with Polars (and didn’t know about it)</em>. Medium. <a href="https://captain-solaris.medium.com/python-advanced-10-things-you-can-do-with-polars-and-didnt-know-about-it-cb8c071227ba">https://captain-solaris.medium.com/python-advanced-10-things-you-can-do-with-polars-and-didnt-know-about-it-cb8c071227ba</a></li>
  <li>Johari, A. (2018, April 5). <em>Python Pandas guide - Learn Pandas for data analysis</em>. Medium. <a href="https://medium.com/edureka/python-pandas-tutorial-c5055c61d12e">https://medium.com/edureka/python-pandas-tutorial-c5055c61d12e</a></li>
  <li>Shahizan, D. (n.d.). <em>drshahizan</em> [GitHub repository]. GitHub. <a href="https://github.com/drshahizan/drshahizan">https://github.com/drshahizan/drshahizan</a></li>
  <li>Wijaya, C. Y. (2025, May 5). <em>Building end-to-end data pipelines with Dask</em>. KDnuggets. <a href="https://www.kdnuggets.com/building-end-to-end-data-pipelines-with-dask">https://www.kdnuggets.com/building-end-to-end-data-pipelines-with-dask</a></li>
</ul>