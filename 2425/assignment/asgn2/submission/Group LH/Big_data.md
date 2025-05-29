
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

## 📊 Dataset Overview

- **Source**: [NYC Yellow Taxi Trip Data - Kaggle](https://www.kaggle.com/datasets/elemento/nyc-yellow-taxi-trip-data)
- **Domain**: Transportation / Ride Hailing
- **Total Size**: ~800MB+
- **Files Used**: 
  - yellow_tripdata_2016-01.csv
  - yellow_tripdata_2016-02.csv
  - yellow_tripdata_2016-03.csv
  - yellow_tripdata_2025-01.csv
- **Number of Records (Jan 2016)**: ~10.6 million

---

## 🧾 Dataset Details

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

## 🧪 Tasks & Implementation

### ✅ Task 1: Load and Inspect Data



### ⚙️ Task 2: Load Less Data



### 🔁 Task 3: Chunking



### ⚖️ Task 4: Optimize Data Types



### 🧪 Task 5: Sampling



### ⚡ Task 6: Parallel Processing with Dask



### 🚀 Task 7: Parallel Processing with Modin



### 📈 Task 8: Performance Benchmarking



### 📊 Task 9: Visualisation & Table Summary



## 📌 Key Observations



---

## ✅ Benefits & Limitations of Each Method

| Method  | Benefits                                               | Limitations                                   |
|---------|--------------------------------------------------------|-----------------------------------------------|
| Pandas  | Simple, fast for small/medium datasets                 | Cannot handle out-of-memory datasets          |
| Dask    | Parallel, scalable to big data                         | Lazy execution, startup overhead              |
| Modin   | Pandas-compatible, parallel execution                  | Requires Ray engine, overhead for small tasks |

---

## 💡 Reflections

- This assignment provided hands-on experience in managing and analysing large datasets.
- Learned how to optimise performance by selecting only required data and processing in chunks.
- Got familiar with **Dask** and **Modin** as tools for parallel and distributed data processing.
- It is important to choose the right tool based on the **dataset size** and **processing goals**.
