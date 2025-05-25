
# 🚗 Carlist.my Web Crawler & Big Data Processing Project

| Name                                   | Matrics Number    |
|---------------------------------------|------------------|
| MARCUS JOEY SAYNER                    | A22EC0193        |
| MUHAMMAD LUQMAN HAKIM BIN MOHD RIZAUDIN | A22EC0086    |
| CAMILY TANG JIA LEI                   | A22EC0039        |
| GOH JING YANG                        | A22EC0052        |

---

## 📝 Project Overview

This project focuses on developing a web crawler and data processing pipeline to extract and analyze real-time vehicle listings from **Carlist.my**, Malaysia’s leading online car marketplace. The extracted data includes specifications, prices, seller information, and location data for new, used, and reconditioned vehicles.

---

## 🌐 Target Website

**Website**: [Carlist.my](https://www.carlist.my)  
**Description**: A comprehensive Malaysian platform offering automotive listings with detailed car specs, pricing, seller info, and geographical details.

### 📊 Data Fields Extracted

| Attribute        | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Car Name         | The full name of the car, including model year, brand, and trim/version details. |
| Car Brand        | The manufacturer or brand of the vehicle.                                  |
| Car Model        | The specific model of the car.                                              |
| Manufacture Year | The year in which the car was made.                                        |
| Body Type        | The style or design of the car.                                             |
| Fuel Type        | The type of fuel the car uses.                                              |
| Mileage          | The total distance the car has been driven, measured in kilometres (KM).    |
| Transmission     | The type of transmission the car uses.                                      |
| Color            | The colour of the car’s exterior.                                           |
| Price            | The cost of the car, usually in the local currency.                        |
| Installment      | The monthly payment if the car is purchased through an installment plan.    |
| Condition        | The state of the car, either new, used or reconditioned.                   |
| Seat Capacity    | The number of people the car can accommodate, including the driver and passengers. |
| Location         | The geographic location where the car is being sold.                        |
| Sales Channel    | The type of seller or platform through which the car is being sold.         |

---

## 🧰 Web Crawling & Scraping Tools

| Name                          | Library (Crawler) | Library (Scraper) | Description |
|------------------------------|-------------------|--------------------|-------------|
| **Marcus Joey Sayner**       | `httpx`           | `parsel`           | `httpx` is an async HTTP client used for modern web requests. `parsel` extracts structured data using CSS/XPath selectors. |
| **Muhammad Luqman Hakim**    | `urllib`          | `Selectolax`       | `urllib` handles URL fetching; `Selectolax` is a high-speed HTML parser suited for large pages. |
| **Camily Tang Jia Lei**      | `urllib`          | `BeautifulSoup`    | `urllib` manages HTTP requests; `BeautifulSoup` is used for intuitive parsing of HTML. |
| **Goh Jing Yang**            | `requests`        | `BeautifulSoup`    | `requests` simplifies HTTP calls; `BeautifulSoup` extracts data from page elements. |

---

## ⚙️ Big Data Processing Tools

| Name                          | Library   | Description |
|-------------------------------|-----------|-------------|
| **Marcus Joey Sayner**        | `Polars`  | A lightning-fast DataFrame library with multi-threaded performance for large-scale processing. |
| **Muhammad Luqman Hakim**     | `Modin`   | Accelerates `pandas` operations by parallelizing computation across all CPU cores. |
| **Camily Tang Jia Lei**       | `Pandas`  | A powerful data manipulation library providing flexible and efficient structures like DataFrames. |
| **Goh Jing Yang**             | `Dask`    | Enables scalable computations on larger-than-memory datasets using a pandas-like API. |

---

## 📁 Dataset & Report Links

- 📦 [Dataset](https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p1/Group%201/data)    
- 📦 [Part 1](https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p1/Group%201/p1)
- 📦 [Part 2](https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p1/Group%201/p2)    
- 📄 [Final Report](https://github.com/Jingyong14/HPDP02/tree/main/2425/project/p1/Group%201/report)
- 📒 [Logbook (Google Sheets)](https://docs.google.com/spreadsheets/d/1WXl2k8qdNjoA4uV0U4B5zNe32f8GB3N3Twwo7Uki8Z4/edit?usp=sharing)

---

## 🗓️ Project Logbook
| No. | Date       | Activity / Task Description                                                              | PIC                                                       | Results                                                                                         |
|-----|------------|-------------------------------------------------------------------------------------------|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| 1   | 16/04/2025 | First proposal documentation (Chapter 1.0)                                               | Marcus Joey Sayner                                        | Draft of Chapter 1 completed                                                                   |
| 2   | 22/04/2025 | First proposal submission                                                                 | Marcus Joey Sayner                                        | Proposal submitted for review                                                                  |
| 3   | 23/04/2025 | Completion of Architecture                                                                | Camily Tang Jia Lei                                       | System architecture finalised and documented                                                   |
| 4   | 23/04/2025 | Discussion and selection of libraries                                                     | All                                                       | Pandas, Dask, Modin, Polars selected                                                           |
| 5   | 24/04/2025 | Discussion and changing of website for scraping                                           | All                                                       | Target website changed from Jobstreet to MauKerja                                             |
| 6   | 25/04/2025 | Discussion and changing of website for scraping                                           | All                                                       | Target website changed from MauKerja to Carlist                                               |
| 7   | 27/04/2025 | Report documentation (Chapter 1.0, 2.0, 3.0)                                              | Camily Tang Jia Lei                                       | Updated chapters to match new scraping target (Carlist)                                       |
| 8   | 27/04/2025 | Report documentation (Chapter 1.2)                                                        | Goh Jing Yang                                             | Revised Attribute List                                                                         |
| 9   | 29/04/2025 | Perform crawling and scraping using requests and BeautifulSoup                            | Goh Jing Yang                                             | Raw data successfully scraped using requests and BeautifulSoup                                |
| 10  | 30/04/2025 | Perform crawling and scraping using urllib and BeautifulSoup                              | Camily Tang Jia Lei                                       | Raw data successfully scraped using urllib and BeautifulSoup                                  |
| 11  | 30/04/2025 | Perform crawling and scraping using urllib and Selectolax                                 | Muhammad Luqman Hakim                                     | Raw data successfully scraped using urllib and Selectolax                                     |
| 12  | 03/05/2025 | Perform Big data processing using Pandas                                                  | Camily Tang Jia Lei                                       | Combined all individual raw datasets into a single CSV and performed initial cleaning         |
| 13  | 04/05/2025 | Perform crawling and scraping using httpx and parsel                                      | Marcus Joey Sayner                                        | Raw data successfully scraped using httpx and Parsel                                          |
| 14  | 05/05/2025 | Amendment big data processing using Pandas                                                | Camily Tang Jia Lei                                       | Updated combine CSV code to insert data into MongoDB and read from MongoDB                   |
| 15  | 05/05/2025 | Perform Big data processing using Modin                                                   | Muhammad Luqman Hakim                                     | Cleaned and processed dataset using Modin for performance benchmarking                        |
| 16  | 06/05/2025 | Perform Big data processing using Dask                                                    | Goh Jing Yang                                             | Cleaned and processed dataset using Dask for performance benchmarking                         |
| 17  | 08/05/2025 | Second amendment big data processing using Pandas                                         | Camily Tang Jia Lei                                       | Final version of Pandas processing code completed                                              |
| 18  | 08/05/2025 | Second amendment big data processing using Modin                                          | Muhammad Luqman Hakim                                     | Final version of Modin processing code completed                                               |
| 19  | 09/05/2025 | Second amendment big data processing using Dask                                           | Goh Jing Yang                                             | Final version of Dask processing code completed                                                |
| 20  | 12/05/2025 | Perform Big data processing using Polars                                                  | Marcus Joey Sayner                                        | Cleaned and processed dataset using Polars for performance benchmarking                       |
| 21  | 13/05/2025 | Complete report (Chapter 6.0)                                                             | Goh Jing Yang                                             | Chapter 6 drafted and added to report                                                          |
| 22  | 13/05/2025 | Complete report (Chapter 7.0, 8.0, 10.0)                                                       | Muhammad Luqman Hakim                                     | Chapter 7, 8 and 10 drafted and added to report                                                   |
| 23  | 14/05/2025 | Completed big data processing coding                                                      | Camily Tang Jia Lei                                       | Code finalised and structured for all libraries, and errors fixed in Polars                   |
| 24  | 15/05/2025 | Complete report (Chapter 1.0, 2.0, 3.0, 5.0, 7.0)                                          | Camily Tang Jia Lei                                       | Finalised chapters written and inserted into report                                            |
| 25  | 15/05/2025 | Amended Chapter 6.0 report                                                                | Goh Jing Yang                                             | Revised and improved Chapter 6.0 of the report                                                 |
| 26  | 15/05/2025 | Complete report (Chapter 4.0)                                                             | Marcus Joey Sayner                                        | Chapter 4 completed and added                                                                  |
| 27  | 15/05/2025 | Complete report documentation                                                             | Camily Tang Jia Lei                                       | Report formatted, labelled, and finalised                                                      |
| 28  | 16/05/2025 | Complete slides                                                                           | Camily Tang Jia Lei, Muhammad Luqman Hakim, Goh Jing Yang | Slides prepared                                                                                |
| 29  | 16/05/2025 | Documentation and final compilation                                                       | Camily Tang Jia Lei                                       | All work compiled and zipped for submission                                                    |
| 30  | 16/05/2025 | Github submission                                                                         | Muhammad Luqman Hakim                                     | Final version uploaded to GitHub                                                               |
| 31  | 23/05/2025 | Report amendment                                                                          | Marcus Joey Sayner                                        | Added figure descriptions                                                                      |
| 32  | 24/05/2025 | Report amendment                                                                          | Camily Tang Jia Lei                                       | Corrected figure numbering, architecture, and explanations                                    |
| 33  | 25/05/2025 | Report amendment                                                                          | Camily Tang Jia Lei                                       | Moved figures/tables to appendices for clarity                                                 |
| 34  | 25/05/2025 | Report submission                                                                         | Camily Tang Jia Lei                                       | Completed and submitted the final report document                                              |
