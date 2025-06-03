# Assignment 2: Big Data Handling and Optimization Using NYC Taxi Trip Dataset🚕 
## 👥 Group Members

| Name               | Matric Number |
|--------------------|---------------|
|VINESH A/L VIJAYAKUMAR       | A22EC0090       |
|NAVASARATHY A/L S.GANEWARAN       | A22EC0091       |

---
## Summary 🚀
This project demonstrates effective strategies for handling and optimizing large-scale data processing using the ```NYC Yellow Taxi Trip dataset``` 🚕. By sampling, chunking, and selectively loading relevant columns, we manage memory usage efficiently when working with CSV files too large for traditional Pandas workflows 🐼.

We explored multiple tools—**Pandas** 🐼, **Dask** ⚡, and **Polars** ❄️—highlighting their strengths and weaknesses in terms of speed, scalability, and memory consumption. While Pandas is straightforward and suitable for smaller datasets, Dask excels in parallel and out-of-core computation, handling large datasets with remarkable speed and low memory overhead. Polars offers fast performance but can consume more memory in some cases.

Key techniques implemented include:

- 📥 Loading partial data and columns to reduce memory footprint
- 📚 Reading large files in manageable chunks
- 🧠 Optimizing data types to minimize memory usage
- 🎲 Sampling for quick data exploration
- ⚙️ Leveraging parallel processing with Dask for scalability

The comparative analysis shows Dask as the best performer in handling big data efficiently, while Pandas struggles with memory limitations. This underscores the importance of selecting appropriate tools and methods based on dataset size and processing needs.

Overall, this project reinforces best practices in big data handling and provides practical insights for optimizing data workflows in Python 🐍.
