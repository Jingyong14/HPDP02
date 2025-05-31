## 🎓 SECP3133 – High Performance Data Processing (Section 02)

### 📊 Assignment 2: *Mastering Big Data Handling*

### Lecturer: Dr. Aryati binti Bakri
**Group: LogiCode**

| Member Name         | Matric No.  |
|------------------------|----------------|
| Ong Yi Yan       | `A22EC0101`     |
| Tang Yan Qing | `A22EC0109`     |

## 1.0 Introduction
In today’s data-driven era, handling massive datasets that exceed traditional processing capabilities presents significant challenges. This assignment focuses on practical techniques for managing and analyzing large-scale data using Python. Using the Spotify Charts Dataset (approximately 3.48 GB), key strategies such as chunking, sampling, data type optimization, and parallel computing with Pandas, Dask, and Polars are applied to improve memory efficiency, reduce execution time, and enhance overall data processing performance.
## 1.1 Objectives
The assignment aims to develop effective big data handling skills using Python libraries. The key objectives are:

- Utilize Pandas, Dask, and Polars to manage and process large datasets.
- Apply strategies such as chunking, sampling, and data type optimization using these libraries.
- Evaluate performance differences across traditional and optimized methods in terms of memory usage, execution time and ease of use.
## 2.0 Dataset Selection
To conduct a meaningful performance and scalability comparison among different data processing libraries, the Spotify Charts Dataset from Kaggle has been selected. It contains historical data of all “Top 200” and “Viral 50” charts published by Spotify globally, updated every 2–3 days since January 1, 2017. The dataset includes over 26 million records, with key details such as song title, artist, rank, date, region, chart type, number of streams, trend indicator, and track URL.

Table 2.0.1 shows an overview of the Spotify Charts dataset used in this project, highlighting its size, source, domain, and the structure of its key features.

<div align="center">

**Table 2.0.1: Dataset Overview**
| **Attribute**         | **Details**                                                                 |
|-----------------------|------------------------------------------------------------------------------|
| **Dataset Name**      | Spotify Charts Dataset                                                       |
| **Source**            | [Kaggle](https://www.kaggle.com/datasets/dhruvildave/spotify-charts)         |
| **File Size**         | Approximately 3.48 GB                                                                     |
| **Domain**            | Music Streaming                                                              |
| **Number of Records** | 26,173,514                                                                   |
| **File Format**       | CSV                                                                          |
| **Columns**           | title (song name), artist, rank, date, region, chart type, streams (NULL for "viral50"), trend (popularity indicator), url (track link)                |

</div>

This dataset is suitable for performance comparison tasks as it is large in volume and contains diverse types of data like numerical, categorical, and missing values, providing a practical use case for benchmarking data processing libraries.

## 3.0 Load and Inspect Data

To prepare the dataset for use, the Spotify Charts data was downloaded from Kaggle using the Kaggle API. The process began with installing the Kaggle package to enable command-line access to Kaggle resources. Then, the required credentials (Kaggle username and API key) were set manually as environment variables to authenticate the session. After successful authentication, the dataset was downloaded using the `kaggle datasets download` command and extracted from the ZIP archive. **Figure 3.0.1** demonstrates how the Kaggle API is configured and used to download and extract the dataset efficiently. Once extracted, the dataset files were ready for inspection and further processing.

<div align="center"><kbd><img src="https://github.com/user-attachments/assets/914643c2-d0c4-4a29-aa7a-67f6c46a9562" alt="Figure 3.0.1" width="400"></kbd><br><strong>Figure 3.0.1: Code snippet demonstrating the process of loading data using Kaggle API.</strong> </div><br>

After loading the dataset, a basic inspection was performed to understand its structure and content. The inspection began by using the pandas library to read the CSV file `charts.csv` into a DataFrame. The code used for this process is shown in **Figure 3.0.2**, which check the dataset's shape and retrieve summary information such as data types and non-null counts. The `shape` output indicated that the dataset contains over 26 million rows and 9 columns. To further explore the structure, the `info()` function was used, revealing that most columns are of object type, with only one integer and one float column. **Figure 3.0.3** displays this output, highlighting the presence of all expected columns such as `title`, `artist`, `rank`, and `streams`, as well as confirming that no null values were present across the dataset.

<div align="center"><kbd><img src="https://github.com/user-attachments/assets/41432251-baff-4398-9566-3477e6848b8b" alt="Figure 3.0.2" width="400"></kbd><br><strong>Figure 3.0.2: Code snippet inspecting the Spotify Charts dataset.</strong> </div><br>
<div align="center"><kbd><img src="https://github.com/user-attachments/assets/7a508734-cea7-493c-9433-bdb186546b1c" alt="Figure 3.0.3" width="300"></kbd><br><strong>Figure 3.0.3: Summary output of the dataset inspection showing entry count, column structure, and memory usage.</strong> </div><br>

## 4.0 Big Data Handling Strategies
To optimize performance and reduce memory usage, only **necessary columns were loaded** from the dataset. Columns like `url` and `trend` were excluded, keeping only essential fields such as `title`, `rank`, `date`, `artist`, `region`, `chart`, and `streams`. This selective loading reduces data size and speeds up processing, which is crucial when handling large datasets. **Defining appropriate data types before loading data helps reduce memory usage and improve processing speed. For the seven selected columns, explicit types were assigned based on their content: `rank` and `streams` as integer, `region` and `chart` as categorical, and `title`, `artist`, and `date` as strings. This predefinition minimizes automatic type inference overhead and ensures efficient storage. The optimized data types were applied consistently across pandas, Dask, and Polars, further enhancing their performance when handling large datasets. Figures 4.0.1 to 4.0.4 present the workflow for loading less data and optimizing data types. **Figure 4.0.1** defines the important columns and their optimized data types used for pandas and Polars. **Figure 4.0.2** and **Figure 4.0.3** demonstrate how pandas and Polars apply these settings during CSV reading, while **Figure 4.0.4** shows Dask’s implementation, which uses a different approach to data types.
<div align="center"> <kbd><img src="https://github.com/user-attachments/assets/eeb89102-4a72-4207-8d11-c594bdbadec2" alt="Figure 4.0.1" width="600"></kbd> <br><strong>Figure 4.0.1: Definition of selected columns and their optimized data types for efficient loading in pandas and Polars.</strong> </div>
<div align="center"> <kbd><img src="https://github.com/user-attachments/assets/3af27974-db69-4797-ba39-f2ed7bddb10e" alt="Figure 4.0.2" width="500"></kbd> <br><strong>Figure 4.0.2: Pandas code snippet for reading the dataset with selective columns and predefined data types.</strong> </div>
<div align="center"> <kbd><img src="https://github.com/user-attachments/assets/bd414beb-2978-44b9-ae23-0599eca4d1b3" alt="Figure 4.0.3" width="500"></kbd> <br><strong>Figure 4.0.3: Dask code snippet showing selective data loading and optimized data types during CSV reading.</strong> </div>
<div align="center"> <kbd><img src="https://github.com/user-attachments/assets/4fbb778c-bf02-4d7d-a43a-f9bc076a9bf7" alt="Figure 4.0.4" width="400"></kbd> <br><strong>Figure 4.0.4: Polars code snippet demonstrating selective column loading with Polars-specific data type handling.</strong> </div>

## 5.0 Comparative Analysis
To evaluate the performance and efficiency of different data processing libraries on large-scale datasets, a comparative analysis was conducted between three libraries: Pandas, Dask and Polars using the Spotify Charts dataset. Two primary metrics — memory usage and execution time were measured during the processing of the dataset. In addition, ease of processing was qualitatively evaluated based on experience during implementation.

In terms of memory usage, as shown in **Figure 5.0.1**, Pandas used the most memory at 575.81 MB, followed by Dask at 146.91 MB. Polars was the most efficient, using only 99.91 MB. Even though Pandas reads the dataset in chunks rather than all at once, the full data still ends up in memory after processing, which explains the high usage. Dask performed better because it uses lazy evaluation and parallel processing, avoiding loading the entire dataset into memory at once. It also only converted the sampled 10% into a usable format, which helped save memory. Polars stood out due to its lazy execution style and how it manages memory using Rust. It handled all steps in a single, optimized pipeline without creating large copies in between, leading to much lower memory usage. These results show that using more efficient libraries—especially Polars—can really help when working with large datasets, especially on systems with limited resources.

<div align="center"><kbd><img src="https://github.com/user-attachments/assets/0510cf7c-0b4a-41a9-a108-23f301833ddc" alt="Figure 4.0.1" width="600"/></kbd><br><strong>Figure 5.0.1: Bar Chart of Memory Usage by Libraries</strong></div><br>

Execution time results are illustrated in **Figure 5.0.2**. It showed a similar trend to the memory usage results. Pandas required the longest time to complete data processing tasks, with a total of 133.48 seconds. Dask did slightly better, completing the same operations in 118.00 seconds. Polars significantly outperformed both by completing the task in just 13.70 seconds. Pandas is the slowest because it processes each chunk one by one and does most of the work using Python, which is slower and adds extra time when combining the chunks. Dask was able to speed things up a little by running parts of the task in parallel, but the performance boost was limited due to system constraints and Dask’s internal overhead. Polars had a clear advantage because it uses Rust-based backend and lazy evaluation. Instead of doing each step right away, it plans the whole process first, then runs it all at once in a fast and efficient way. This made Polars much quicker at cleaning and sampling the data.

<div align="center"><kbd><img src="https://github.com/user-attachments/assets/3eb42698-2e1a-435f-8c65-f71754100306" alt="Figure 4.0.2" width="600"/></kbd><br><strong>Figure 5.0.2: Bar Chart of Execution Time by Libraries</strong></div><br>

Regarding ease of use, Pandas is the simplest to work with because of its familiar syntax and rich documentation. Dask is quite similar to Pandas, which makes it easier for people who already know Pandas to get started. However, while Dask offers better performance with large datasets, it introduces some extra complexity. This includes setting up the environment properly and understanding how lazy evaluation works. Polars, while the fastest and most memory-efficient, uses different syntax and ideas like lazy evaluation and expressions, which may take more time to learn. Also, its documentation is not as complete or beginner-friendly as Pandas or Dask, so users might need extra effort when starting out.

Overall, while Pandas remains easy to use, Polars provides the best performance in both speed and memory usage, making it a strong choice for processing large datasets efficiently.

## 6.0 Conclusion
Through the comparison of Pandas, Dask and Polars using the Spotify Charts dataset, several important observations were made. Each library has its own strengths and weaknesses depending on the dataset size and available system resources. In terms of performance, Polars stood out as the best performer. It used the least memory (99.91 MB) and completed the task in the shortest time (13.70 seconds). This efficiency is mainly due to the lazy execution and the use of a fast, Rust-based engine. However, Polars also requires a different coding style, which can be confusing for beginners. Its documentation is still developing and may not as beginner-friendly as more established libraries. Dask ranked between Polars and Pandas, using 146.91 MB of memory and completing the process in 118.00 seconds. While not as fast as Polars, Dask handled larger data more effectively than Pandas by using lazy evaluation and parallel processing. For users already familiar with Pandas, Dask is generally easier to adopt. However, it still requires a basic understanding of how its task graph works and how to configure the system properly. It can add some complexity to the workflow. Pandas, despite being the slowest (133.48 seconds) and using the most memory (575.81 MB), remains the most accessible. Its simple syntax, wide range of features and strong community support make it ideal for beginners and for small to medium-sized datasets where performance is not a top priority. It does not require much setup or learning beyond basic Python skills, making it the easiest to use among the three libraries.

In summary, the results show that choosing the right data processing library depends on the task. Pandas is a good choice for ease of use and smaller datasets. Dask is useful when scalability is needed and performance matters, without changing too much of the existing code. Polars is the best option for high performance and low memory usage, especially on large datasets with limited resources.

This comparison also helped improve understanding of how different libraries manage data, memory and execution. It introduced key ideas such as lazy evaluation and parallel processing, which are not as visible in traditional tools like Pandas. Running and measuring real performance results showed how knowing what happens behind the scenes can help make better decisions and build more efficient data pipelines. It also showed the value of trying new tools, even if they are harder to learn at first, because the benefits in speed and memory usage can be significant in real-world situations.

## 7.0 References
- Dask — Dask documentation. (n.d.). Dask.org. https://docs.dask.org/
- Dhruvildave. (n.d.). *Spotify Charts Dataset* [Data set]. Kaggle. https://www.kaggle.com/datasets/dhruvildave/spotify-charts
- Index - Polars user guide. (n.d.). Github.io. https://pola-rs.github.io/polars/
- Shahizan, D. (n.d.). drshahizan [GitHub repository]. GitHub. https://github.com/drshahizan/drshahizan

