
# 🚕 Big Data Handling and Optimization Using NYC Taxi Trip Dataset

## 👥 Group Members

| Name               | Matric Number |
|--------------------|---------------|
| Muhammad Luqman Hakim Bin Mohd Rizaudin        | A22EC0086       |
| Muhammad Daniel Hakim bin Syahrulnizam         | A22EC0207       |

---

## 📌 Project Overview

This project explores multiple strategies for handling and processing large-scale datasets in Python, specifically using the **NYC Yellow Taxi Trip Data** from Kaggle. The aim is to demonstrate how big data techniques can optimize performance in terms of memory usage and execution time when dealing with CSV files too large to process with traditional Pandas alone.

---

## 📌 Key Observations
### ✅ Benefits & Limitations of Each Method

| Method  | Benefits                                               | Limitations                                   |
|---------|--------------------------------------------------------|-----------------------------------------------|
| Pandas  | Simple, fast for small/medium datasets                 | Cannot handle out-of-memory datasets          |
| Dask    | Parallel, scalable to big data                         | Lazy execution, startup overhead              |
| Polars  | Pandas-compatible, parallel execution                  | Requires Ray engine, overhead for small tasks |

---

## 🧪 Tasks & Implementation

### Task 1: Dataset Selection

#### 📊 Dataset Overview

- **Source**: [NYC Yellow Taxi Trip Data - Kaggle](https://www.kaggle.com/datasets/elemento/nyc-yellow-taxi-trip-data)
- **Domain**: Transportation / Ride Hailing
- **Total Size**: ~800MB+
- **Files Used**: 
  - yellow_tripdata_2016-01.csv
  - yellow_tripdata_2016-02.csv
  - yellow_tripdata_2016-03.csv
  - yellow_tripdata_2025-01.csv
- **Number of Records (Jan 2016)**: ~10.6 million

#### 🧾 Dataset Details

| Column Name              | Description                                              |
|--------------------------|----------------------------------------------------------|
| vendor_id                | Code indicating the provider                             |
| tpep_pickup_datetime     | Date and time of pickup                                  |
| tpep_dropoff_datetime    | Date and time of drop-off                                |
| passenger_count          | Number of passengers                                     |
| trip_distance            | Distance of the trip in miles                            |
| ratecode_id              | Rate code identifier                                     |
| store_and_fwd_flag       | Whether the trip was stored before sending               |
| pu_location_id           | Pickup location ID                                       |
| do_location_id           | Drop-off location ID                                     |
| payment_type             | Type of payment                                          |
| fare_amount              | Fare amount                                              |
| extra                    | Additional charges                                       |
| mta_tax                  | MTA tax                                                  |
| tip_amount               | Tip given                                                |
| tolls_amount             | Tolls paid                                               |
| improvement_surcharge    | Surcharge fee                                            |
| total_amount             | Total charged amount                                     |

<br><br>

---

### Task 2: Load and Inspect Data

![image](https://github.com/user-attachments/assets/d1e53a20-9a62-40fc-92e5-775ceb7b6a32)

The above code imports the Pandas library as `pd` and reads the first 500,000 rows from the CSV file `combined_yellow_tripdata.csv` into a DataFrame called `df`. This sampling approach helps manage memory usage when dealing with large datasets. 

It then:
- Prints the shape of the DataFrame to show the number of rows and columns,
- Lists all column names to give an overview of the dataset structure,
- Displays the data types of each column to understand how Pandas has interpreted the data, which is essential for proper data processing and analysis.

<br>

![image](https://github.com/user-attachments/assets/0e05e91e-99a5-46d3-87b8-b675a67e65f0)

The output shows that the dataset contains 500,000 rows and 19 columns, indicating a substantial sample of trip records. The column names describe various attributes of each trip, such as vendor ID, timestamps for pickup and drop-off, number of passengers, trip distance, pickup/drop-off coordinates, fare details, and payment information. 

The data types reveal how Pandas interpreted each column:  
- Numerical values like ```VendorID```, ```passenger_count```, and ```RateCodeID``` are stored as ```int64```;  
- Continuous values such as ```trip_distance``` and fare-related columns are ```float64```;  
- Textual or date-like data such as ```tpep_pickup_datetime```, ```tpep_dropoff_datetime```, and ```store_and_fwd_flag``` are currently recognized as ```object``` types, which are generic and may need to be explicitly converted to ```datetime``` or ```category``` formats for proper analysis.

This summary helps assess data readiness and identify preprocessing steps needed for further analysis.


---

### Task 3: Apply Big Data Handling Strategies

**3.1 Load Less Data**  
The code efficiently loads a portion of a large CSV file using pandas. It first defines a list of specific columns to read: pickup and dropoff times, passenger count, trip distance, and fare amount. Then, it uses `pd.read_csv()` to load only those columns and the first 100,000 rows from the file, reducing memory usage. Finally, `filtered_df.head()` displays the first five rows to verify the data was loaded correctly.  
![Load Less Data](https://github.com/user-attachments/assets/1c8be1ac-43bc-448d-ad1d-733ece3ac5b6)  
![Load Less Data Screenshot](https://github.com/user-attachments/assets/c498e0b6-4741-4653-935e-22e5f5a2b677)

---

**3.2 Use Chunking**  
The code reads a large CSV file in chunks of 100,000 rows using `pd.read_csv()` with `chunksize`. It loads only selected columns (`use_cols`) and stores all chunks in a list. Finally, it prints the first five rows of the first chunk to preview the data. This method is memory-efficient for handling large files.  
![Chunking Code](https://github.com/user-attachments/assets/9683a42c-0cf5-4d5b-adb3-467239f84c3b)  
![Chunking Screenshot](https://github.com/user-attachments/assets/03ce04da-bad6-4620-b7e5-f18c6d51e068)

---

**3.3 Optimize Data Types**  
The code creates a copy of the DataFrame and reduces memory usage by changing data types: `passenger_count` to `uint8`, and `trip_distance` and `fare_amount` to `float32`. It then prints the updated data types.  
![Optimize Data Types Code](https://github.com/user-attachments/assets/f0676cc4-1751-4fda-8497-e95666c975d8)  
![Optimize Data Types Screenshot](https://github.com/user-attachments/assets/c69b3c74-398e-46f5-aff9-640663b8b128)

---

**3.4 Sampling**  
This code takes a random 10% sample of the DataFrame `df` using `df.sample(frac=0.1)`. The `random_state=1` ensures the sampling is reproducible. It then prints the shape (rows, columns) of the sampled DataFrame, `sample_df`.  
![Sampling Code](https://github.com/user-attachments/assets/93f4d286-c9f0-4c83-91a8-2e0e5c0d0927)  
![Sampling Screenshot](https://github.com/user-attachments/assets/0b917be5-af71-4a61-b7ce-389ae6fb8fb0)

---

**3.5 Parallel Processing with Dask**  
It imports Dask’s dataframe module and reads `"combined_yellow_tripdata.csv"` with only the specified columns (`use_cols`). The `blocksize="25MB"` tells Dask to load the file in 25 MB chunks, enabling parallel and out-of-core processing. Finally, `print(dask_df.head())` shows the first few rows to preview the data. This approach helps handle large datasets that don’t fit into memory.  
![Dask Code](https://github.com/user-attachments/assets/fe57504c-f546-4e39-b1f5-66c81c81c34d)  
![Dask Screenshot](https://github.com/user-attachments/assets/63fda419-d6a9-439e-8047-dc615d877fa7)

---

### Task 4: Comparative Analysis
![image](https://github.com/user-attachments/assets/30a7c60f-9145-4c6d-a162-5e3ee70f9faa)

To evaluate the performance of different data processing libraries, we conducted a comparison between Pandas, Polars, and Dask using a dataset and a set of operations. The key performance metrics considered were execution time and memory usage.

Polars completed the task in 65.19 seconds, but it consumed a significantly large amount of memory — approximately 10,118.38 MB. This suggests that while Polars can be fast in many scenarios, its memory efficiency might be a concern for certain large-scale operations or environments with limited resources.

Dask, in contrast, demonstrated exceptional performance, completing the same task in just 0.39 seconds. Interestingly, it also showed a negative memory usage value (-56.74 MB). This may indicate that Dask managed to free up memory during execution, possibly due to lazy evaluation or distributed computing efficiencies.

As for Pandas, the operation failed to complete — it crashed during execution, likely due to memory constraints or inefficiencies when handling larger datasets or complex computations.

The chart visually reinforces these observations, with Polars showing a tall bar for both time and memory usage, while Dask remains low on both axes. The absence of a bar for Pandas indicates its inability to complete the task, highlighting a limitation when compared to Polars and Dask in this context.


---

### Task 5: Conclusion & Reflection
This project provided valuable hands-on experience in managing and analyzing large datasets from Kaggle. It highlighted the importance of efficient data handling techniques, such as selecting only the necessary columns and processing data in chunks to reduce memory usage and improve performance.

Through this assignment, we became familiar with powerful parallel and distributed computing tools like Dask and Modin. These libraries proved to be significantly more efficient than traditional tools like Pandas, especially when working with large datasets. Dask, in particular, stood out for its fast execution time and low memory footprint.

A key takeaway from this experience is that selecting the right tool is crucial and should be based on the dataset size and the specific processing goals. While Pandas is useful for small-scale tasks, tools like Dask are better suited for large-scale data processing due to their scalability and performance benefits.

---
