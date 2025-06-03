# Big Data Handling Analysis Report

## 🧠 Assignment 2: Mastering Big Data Handling

> **Group JSON**  
> 👤 TIEW CHUAN SHEN — `A22EC0113`  
> 👤 JOSEPH LAU YEO KAI — `A22EC0055`

---

## 1. Dataset Description

### 1.1 Dataset Overview
- **Name**: Traffic and Weather Datasets
- **Source**: Kaggle (orvile/traffic-and-weather-datasets)
- **Size**: >700MB
- **Domain**: Transportation and Weather
- **Records**: 103681 record entries

### 1.2 Dataset Structure
The dataset combines traffic and weather information, providing a comprehensive view of how weather conditions affect traffic patterns. This makes it an excellent candidate for big data analysis as it contains:
- Traffic flow data
- Weather conditions
- Temporal information
- Location data

## 2. Data Loading and Inspection

### 2.1 Initial Data Loading
```python
import kagglehub
import pandas as pd
import numpy as np
import dask.dataframe as dd
import time
import psutil
import matplotlib.pyplot as plt

# Download dataset
path = kagglehub.dataset_download("orvile/traffic-and-weather-datasets")
```

### 2.2 Basic Inspection Results
[To be filled after running the code]

## 3. Big Data Handling Strategies

### 3.1 Load Less Data
#### Implementation
```python
# Load only essential columns
essential_columns = ['timestamp', 'traffic_flow', 'weather_condition', 'temperature']
df_optimized = pd.read_csv('dataset.csv', usecols=essential_columns)
```

#### Results
- Memory usage reduction: 276.57mb
- Loading time improvement: 32.4s

### 3.2 Chunking
#### Implementation
```python
# Process data in chunks
chunk_size = 100000
chunks = pd.read_csv('dataset.csv', chunksize=chunk_size)

# Process each chunk
for chunk in chunks:
    # Process chunk
    pass
```

#### Results
- Memory efficiency: 330.07mb used only
- Processing time: 38.55s

### 3.3 Data Type Optimization
#### Implementation
```python
# Optimize data types
dtype_dict = {
    'traffic_flow': 'int32',
    'temperature': 'float32',
    'weather_condition': 'category'
}
df_optimized = pd.read_csv('dataset.csv', dtype=dtype_dict)
```

#### Results
- Memory reduction: 276.57mb
- Performance impact: Increased throughput

### 3.4 Sampling
#### Implementation
```python
# Random sampling
sample_size = 100000
df_sample = pd.read_csv('dataset.csv').sample(n=sample_size, random_state=42)
```

#### Results
- Sample representativeness: 10% of the data
- Processing speed improvement: 32.3s

### 3.5 Parallel Processing with Dask
#### Implementation
```python
# Dask implementation
ddf = dd.read_csv('dataset.csv')
result = ddf.compute()
```

#### Results
- Parallel processing efficiency: 16586.01 row/s
- Memory usage: 53.50mb

## 4. Comparative Analysis

### 4.1 Performance Metrics
| Method | Memory Usage | Execution Time | Ease of Processing |
|--------|--------------|----------------|-------------------|
| Traditional | 330.07mb | 38.55s | No |
| Load Less | 53.50mb | 6.25s | Yes |
| Chunking | 4817.09mb | 5.08s | Yes but memory increased |
| Type Optimization | 330.07mb | 38.55s | No |
| Sampling | 4817.09mb | 5.08 | Little |
| Dask | 53.50mb | 6.25s | Yes |

### 4.2 Visualization
[To be added: Performance comparison charts]

## 5. Conclusion and Reflection

### 5.1 Key Observations
[To be filled after analysis]

### 5.2 Benefits and Limitations
#### Benefits
- [To be filled after analysis]

#### Limitations
- [To be filled after analysis]

### 5.3 Learning Outcomes
[To be filled after analysis]

## 6. References
1. Pandas Documentation: https://pandas.pydata.org/
2. Dask Documentation: https://docs.dask.org/
3. Kaggle Dataset: https://www.kaggle.com/datasets/orvile/traffic-and-weather-datasets 
