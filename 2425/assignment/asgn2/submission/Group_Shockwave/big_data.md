# SECP3133 High Performance Data Processing - Section 02

## Assignment 2 - Mastering Big Data Handling

### Group Shockwave:
- **LIM JING YONG** - A22EC0182  
- **LEE SOON DER** - A22EC0065

---

## Task 1: Dataset Selection

In this section, we decided to select our dataset in Kaggle due to its functionality to show the size of the dataset (in MB). This allows us to quickly find suitable and large enough dataset to undergo optimization during the dataset loading process.

The dataset we chose is the **continental2.csv** file from the _COVID-19 in the American Continent_ dataset, which consists of **1.07 GB** of data. This dataset records the number of COVID-19 cases that happened across the years 2020 to 2022 in different countries.

![Kaggle CSV View](figures/Kaggle_Dataset.png)  
**Figure 1.1**: View of the CSV file in Kaggle

The dataset consists of **14 columns** (2 irrelevant ID columns) and **1,048,576 rows** of data.

![CSV Screenshot Part 1](figures/csv_screenshot1.png)  
![CSV Screenshot Part 2](figures/csv_screenshot2.png)  
**Figure 1.2**: Data columns and row count from the CSV file

## Task 2: Load and Inspect Data

In this section, the dataset was obtained using the Kaggle API and processed with Pandas in Google Colab. We also performed a basic inspection to understand the dataset's structure and contents.

Figure 2.1 below shows the use of the Kaggle API to automate dataset retrieval. This step is mandatory for enabling authenticated downloads in Colab.

<img src="figures/Task2.1.png" alt="Using Kaggle API in Colab" width="600"/>  
**Figure 2.1:** Use of Kaggle API in Google Colab

Figure 2.2 below shows the installation of the Kaggle CLI tool and the command to download the desired dataset. This step automates the dataset retrieval process from the Kaggle website.

<img src="figures/Task2.2.png" alt="Installing Kaggle CLI and downloading dataset" width="600"/>  
**Figure 2.2:** Installing Kaggle CLI and downloading dataset

Figure 2.3 below shows the code used to load the dataset (`continental2.csv`) into memory using the Pandas library. This method is commonly used for small to medium-sized datasets and is sufficient for initial inspection and cleaning.

<img src="figures/Task2.3.png" alt="Loading CSV with Pandas" width="600"/>  
**Figure 2.3:** Loading dataset using Pandas

After loading the dataset, we performed a basic inspection to understand its structure and contents, as shown in Figure 2.4 below.

<img src="figures/Task2.4.png" alt="Inspecting the dataset with Pandas" width="600"/>  
**Figure 2.4:** Dataset inspection using Pandas


