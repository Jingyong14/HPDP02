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
  The amount of data created today is accelerating. This poses challenges for classical data processing tools. For instance, libraries such as Pandas may run into issues when working with datasets in the range of several hundred megabytes. These tools can reach memory limits and experience long processing times. Consequently, businesses require more scalable and efficient methods to process and analyse the growing volume of data more effectively.
</p>

<h2>1.1 Objectives</h2>
<p>
  The objectives of this assignment are to address the challenges of large-scale data extraction and processing by:
</p>
<ul>
  <li>Applying various big data techniques, including chunking, sampling, type optimisation, and parallel computing.</li>
  <li>Evaluating and comparing the performance of traditional Pandas methods against optimised data handling strategies, such as Polars and Dask.</li>
  <li>Assessing the effectiveness of each technique in terms of memory usage, execution time, and ease of processing.</li>
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
  The selected dataset was loaded and processed using three libraries—Pandas, Polars, and Dask—to demonstrate their performance. The objective was to efficiently read and process a large file while preserving the validity of the data and enabling further analysis, as illustrated in Appendix A (Table A1).
</p>

<h2>4.0 Big Data Handling Strategies</h2>
<p>
  Efficient handling of large datasets is regarded as a critical aspect of working with data at scale. Traditional data processing methods are often constrained by memory limitations, reduced speed, and limited scalability. To overcome these challenges, various techniques have been developed to optimise memory usage, enhance processing speed, and enable parallel execution of tasks. In this section, several useful strategies—such as loading specific columns, optimising data types, and reading files efficiently—are discussed. These techniques are examined in the context of the capabilities provided by Pandas, Dask, and Polars to highlight how each library addresses big data challenges in resource- and performance-sensitive scenarios.
</p>

<h3>4.1 Environment Setup and Dataset Acquisition</h3>
<p>
  A uniform environment setup was employed across the three data processing libraries—Pandas, Polars, and Dask—to ensure real, comparable, and controlled performance experiments. All experiments were conducted using Google Colab, a platform well-suited for working with large datasets under limited resources, and offering support for live collaboration.
</p>

<figure>
  <img src="figures/figure1.png" alt="Pandas Environment Setup and Data Processing Workflow">
  <figcaption>Figure 1: Pandas Environment Setup and Data Processing Workflow</figcaption>
</figure>

<figure>
  <img src="figures/figure2.png" alt="Polars Environment Setup and Data Processing Workflow">
  <figcaption>Figure 2: Polars Environment Setup and Data Processing Workflow</figcaption>
</figure>

<figure>
  <img src="figures/figure3.png" alt="Dask Environment Setup and Data Processing Workflow">
  <figcaption>Figure 3: Dask Environment Setup and Data Processing Workflow</figcaption>
</figure>

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

<figure>
  <img src="figures/figure5.png" alt="Execution Time and Memory Usage Calculation in Pandas">
  <figcaption>Figure 5: Execution Time and Memory Usage Calculation in Pandas</figcaption>
</figure>

<figure>
  <img src="figures/figure6.png" alt="Execution Time and Memory Usage Calculation in Polars">
  <figcaption>Figure 6: Execution Time and Memory Usage Calculation in Polars</figcaption>
</figure>

<figure>
  <img src="figures/figure7.png" alt="Execution Time and Memory Usage Calculation in Dask">
  <figcaption>Figure 7: Execution Time and Memory Usage Calculation in Dask</figcaption>
</figure>

<h3>4.2 Pandas</h3>
<p>
  Pandas is a widely used Python library for data manipulation, analysis, and cleaning (Johari, 2018). While Pandas is capable of handling large datasets, its performance is constrained by the available system RAM. This limitation arises because Pandas loads the entire dataset into memory; therefore, if the dataset exceeds the available memory, it cannot be processed and execution is terminated.
</p>

<h4>4.2.1 Column Filtering</h4>
<p>
  As shown in Figure 8, ten essential columns were selected using the ‘usecols’ parameter. By loading only the required columns, memory usage was reduced and the dataset was efficiently prepared for analysis. The selected columns included: "Artist(s)", "song", "Length", "emotion", "Genre", "Release Date", "Popularity", "Energy", "Danceability", and "Positiveness".
</p>

<figure>
  <img src="figures/figure8.png" alt="Column Filtering Using Pandas">
  <figcaption>Figure 8: Column Filtering Using Pandas</figcaption>
</figure>

<h4>4.2.2 Optimise Data Types</h4>
<p>
  To further reduce memory consumption, data types were optimised using a predefined dictionary ‘dtype_map’, as shown in Figure 9. String-based columns were converted to ‘category’ type, while numerical columns were stored as ‘float32’, which is more memory-efficient than the default ‘float64’.
</p>

<figure>
  <img src="figures/figure9.png" alt="Data Type Optimisation Using Pandas">
  <figcaption>Figure 9: Data Type Optimisation Using Pandas</figcaption>
</figure>

<h4>4.2.3 Chunking, Data Cleaning, and Sampling</h4>
<p>
  Figure 10 illustrates how chunking, data cleaning, and sampling were applied simultaneously. The dataset was read in chunks of 5,000 rows using the chunksize parameter in pd.read_csv() to avoid memory issues. Within each chunk, missing values were removed using .dropna(). Then, a 10% random sample was extracted using the .sample(frac=0.1, random_state=42) method. The random_state=42 ensures reproducibility by returning the same random selection each time the code is executed—an essential practice for consistency in experiments. This reduced the data volume while preserving representativeness. The sampled subsets were stored and later combined into a final dataset.
</p>

<figure>
  <img src="figures/figure10.png" alt="Chunking, Cleaning, and Sampling with Pandas">
  <figcaption>Figure 10: Chunking, Cleaning, and Sampling with Pandas</figcaption>
</figure>

<h4>4.2.4 Combining Sampled Data</h4>
<p>
  As depicted in Figure 11, the list of sampled chunks was concatenated using pd.concat() to create the final DataFrame. This resulting dataset was optimised for further processing and performance testing, offering a balance between accuracy and efficiency.
</p>

<figure>
  <img src="figures/figure11.png" alt="Combining Sampled Chunks in Pandas">
  <figcaption>Figure 11: Combining Sampled Chunks in Pandas</figcaption>
</figure>

<h4>4.2.5 Output</h4>
<p>
  Figure 12 shows the output of loading and inspecting the sampled Spotify dataset using Pandas. The DataFrame contains 55,144 records and 10 columns, including artist names, song titles, length, emotion, genre, release date, and several audio features such as popularity, energy, danceability, and positiveness. The data types are a mix of ‘strings’ (object) for categorical fields and numerical fields stored as ‘float32’, ensuring optimised memory usage.

<figure>
  <img src="figures/figure12.png" alt="Output of Sampled Dataset in Pandas">
  <figcaption>Figure 12: Output of Sampled Dataset in Pandas</figcaption>
</figure>

<h3>4.3 Polars</h3>
<p>
  Polars is a fast DataFrame library implemented in Rust. It is designed for performance, supporting multi-threaded execution, zero-copy data access, and lazy evaluation, making it a powerful alternative to Pandas for large datasets. Polars can process data significantly faster while consuming less memory.
</p>

<h4>4.3.1 Column Filtering and Data Type Optimisation</h4>
<p>
  Figure 13 demonstrates how only selected columns were loaded using the <code>columns</code> parameter in <code>pl.read_csv()</code>. This allowed faster loading and lower memory consumption. Polars automatically infers data types and optimises them by default, thus reducing manual intervention.
</p>

<figure>
  <img src="figures/figure13.png" alt="Column Filtering and Type Optimisation in Polars">
  <figcaption>Figure 13: Column Filtering and Type Optimisation in Polars</figcaption>
</figure>

<h4>4.3.2 Sampling and Data Cleaning</h4>
<p>
  Figure 14 shows how missing values were dropped using <code>.drop_nulls()</code> and a 10% sample was extracted using <code>.sample(fraction=0.1, seed=42)</code>. This process is similar to Pandas but benefits from Polars' faster execution and efficient memory handling.
</p>

<figure>
  <img src="figures/figure14.png" alt="Sampling and Cleaning in Polars">
  <figcaption>Figure 14: Sampling and Cleaning in Polars</figcaption>
</figure>

<h4>4.3.3 Output</h4>
<p>
  Figure 15 shows the structure of the resulting DataFrame in Polars, containing 55,144 records and the selected 10 columns. This confirms that Polars effectively mirrored the Pandas process but with greater performance efficiency.
</p>

<figure>
  <img src="figures/figure15.png" alt="Output of Sampled Dataset in Polars">
  <figcaption>Figure 15: Output of Sampled Dataset in Polars</figcaption>
</figure>

<h3>4.4 Dask</h3>
<p>
  Dask is a parallel computing library that scales Python workflows for multi-core and distributed computing environments. It provides a familiar interface to Pandas users and supports out-of-core computations, meaning it can handle datasets larger than memory by processing them in parallel in smaller blocks.
</p>

<h4>4.4.1 Column Filtering and Data Type Optimisation</h4>
<p>
  In Figure 16, the Dask DataFrame was created with the <code>usecols</code> parameter to load only the relevant columns. Type optimisation was applied after reading the data by converting strings to categories and floats to <code>float32</code>, similar to Pandas.
</p>

<figure>
  <img src="figures/figure16.png" alt="Column Filtering and Type Optimisation in Dask">
  <figcaption>Figure 16: Column Filtering and Type Optimisation in Dask</figcaption>
</figure>

<h4>4.4.2 Chunking, Data Cleaning, and Sampling</h4>
<p>
  As shown in Figure 17, missing values were dropped using <code>.dropna()</code>, and sampling was performed using <code>.sample(frac=0.1, random_state=42)</code>. Dask delayed the computation until explicitly instructed to execute via <code>.compute()</code>, making it more memory-efficient.
</p>

<figure>
  <img src="figures/figure17.png" alt="Sampling and Cleaning in Dask">
  <figcaption>Figure 17: Sampling and Cleaning in Dask</figcaption>
</figure>

<h4>4.4.3 Output</h4>
<p>
  Figure 18 displays the final sampled Dask DataFrame. Like Pandas and Polars, the output contains 55,144 rows and 10 columns, validating that the same logic was applied using a scalable and parallelised approach.
</p>

<figure>
  <img src="figures/figure18.png" alt="Output of Sampled Dataset in Dask">
  <figcaption>Figure 18: Output of Sampled Dataset in Dask</figcaption>
</figure>

<h2>5.0 Comparative Analysis</h2>
<p>
  Table A1 (Appendix A) summarises the performance of the three libraries in terms of execution time, memory usage, and ease of implementation. Polars outperformed the others in execution speed, followed by Dask and Pandas. While Pandas is easiest to use, it is the least scalable. Dask offers better scalability, and Polars strikes a balance between performance and simplicity.
</p>

<h2>6.0 Conclusion</h2>
<p>
  This assignment highlights the importance of selecting appropriate tools and optimisation strategies for handling large datasets. Pandas, while user-friendly, falls short in scalability. Polars demonstrated superior speed and efficiency, making it ideal for high-performance computing tasks. Dask, though slightly more complex, is highly effective for parallel and distributed data processing. By leveraging column filtering, chunking, sampling, and data type optimisation, data scientists can significantly reduce memory usage and execution time, thus enhancing the performance of big data pipelines.
</p>

<h2>7.0 References</h2>
<ul>
  <li>Devdope. (n.d.). <em>500K+ Spotify songs with lyrics, emotions & more</em> [Data set]. Kaggle. <a href="https://www.kaggle.com/datasets/devdope/900k-spotify">https://www.kaggle.com/datasets/devdope/900k-spotify</a></li>
  <li>Edwin. (2025, February 27). <em>Dask: Detailed guide for scalable computing</em>. Python Central. <a href="https://www.pythoncentral.io/dask-detailed-guide-for-scalabale-computing/">https://www.pythoncentral.io/dask-detailed-guide-for-scalabale-computing/</a></li>
  <li>Fischer, B. (2024, December 23). <em>Python advanced: 10 things you can do with Polars (and didn’t know about it)</em>. Medium. <a href="https://captain-solaris.medium.com/python-advanced-10-things-you-can-do-with-polars-and-didnt-know-about-it-cb8c071227ba">https://captain-solaris.medium.com/python-advanced-10-things-you-can-do-with-polars-and-didnt-know-about-it-cb8c071227ba</a></li>
  <li>Johari, A. (2018, April 5). <em>Python Pandas guide - Learn Pandas for data analysis</em>. Medium. <a href="https://medium.com/edureka/python-pandas-tutorial-c5055c61d12e">https://medium.com/edureka/python-pandas-tutorial-c5055c61d12e</a></li>
  <li>Shahizan, D. (n.d.). <em>drshahizan</em> [GitHub repository]. GitHub. <a href="https://github.com/drshahizan/drshahizan">https://github.com/drshahizan/drshahizan</a></li>
  <li>Wijaya, C. Y. (2025, May 5). <em>Building end-to-end data pipelines with Dask</em>. KDnuggets. <a href="https://www.kdnuggets.com/building-end-to-end-data-pipelines-with-dask">https://www.kdnuggets.com/building-end-to-end-data-pipelines-with-dask</a></li>
</ul>