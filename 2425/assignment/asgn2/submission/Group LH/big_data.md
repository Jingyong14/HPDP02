
# 🚕 Big Data Handling and Optimization Using NYC Taxi Trip Dataset

## 👥 Group Members

| Name               | Matric Number |
|--------------------|---------------|
| Muhammad Luqman Hakim Bin Mohd Rizaudin           | A22EC0086       |
| Muhammad Daniel Hakim bin Syahrulnizam           | A22EC0207       |

---

## 📌 Project Overview

This project explores multiple strategies for handling and processing large-scale datasets in Python, specifically using the **NYC Yellow Taxi Trip Data** from Kaggle. The aim is to demonstrate how big data techniques can optimize performance in terms of memory usage and execution time when dealing with CSV files too large to process with traditional Pandas alone.

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

---

### Task 2: Load and Inspect Data



---

### Task 3: Apply Big Data Handling Strategies
| Task | Explanation | Code Snippet | Screenshot |
|------|-------------|--------------|------------|
| **3.1 Load Less Data** | Instead of loading the entire dataset, load only the required columns or rows using `usecols` and `nrows`. | ```python import pandas as pd df = pd.read_csv("large_dataset.csv", usecols=["id", "name"], nrows=1000) print(df.head()) ``` | ![3.1-output](images/3.1_output.png) |
| **3.2 Use Chunking** | Process large datasets in smaller chunks to save memory using the `chunksize` parameter in `pandas.read_csv()`. | ```python import pandas as pd chunks = pd.read_csv("large_dataset.csv", chunksize=5000) for chunk in chunks: print(chunk.shape) ``` | ![3.2-output](images/3.2_output.png) |
| **3.3 Optimize Data Types** | Reduce memory usage by converting columns to appropriate data types (e.g., `int8`, `category`). | ```python df = pd.read_csv("large_dataset.csv") df["id"] = df["id"].astype("int32") df["category"] = df["category"].astype("category") print(df.info()) ``` | ![3.3-output](images/3.3_output.png) |
| **3.4 Sampling** | Load and analyze a representative subset of the dataset to perform quick analysis. | ```python import pandas as pd df = pd.read_csv("large_dataset.csv") sample_df = df.sample(frac=0.1, random_state=42) print(sample_df.head()) ``` | ![3.4-output](images/3.4_output.png) |
| **3.5 Parallel Processing with Dask** | Use Dask to process data in parallel, making use of all CPU cores. Dask is similar to Pandas but supports lazy evaluation and parallelism. | ```python import dask.dataframe as dd ddf = dd.read_csv("large_dataset.csv") print(ddf.head()) ``` | ![3.5-output](images/3.5_output.png) |

---

### Task 4: Comparative Analysis


---

### Task 5: Conclusion & Reflection
- This assignment provided hands-on experience in managing and analysing large datasets.
- Learned how to optimise performance by selecting only required data and processing in chunks.
- Got familiar with **Dask** and **Modin** as tools for parallel and distributed data processing.
- It is important to choose the right tool based on the **dataset size** and **processing goals**.

---

## 📌 Key Observations


---

## ✅ Benefits & Limitations of Each Method

| Method  | Benefits                                               | Limitations                                   |
|---------|--------------------------------------------------------|-----------------------------------------------|
| Pandas  | Simple, fast for small/medium datasets                 | Cannot handle out-of-memory datasets          |
| Dask    | Parallel, scalable to big data                         | Lazy execution, startup overhead              |
| Polars  | Pandas-compatible, parallel execution                  | Requires Ray engine, overhead for small tasks |

---
