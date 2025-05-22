
# 🚗 Carlist.my Web Crawler & Big Data Processing Project

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


---

## 🗓️ Project Logbook

### 📅 Week 1: Setup & Team Coordination
- Held initial group meeting to distribute roles:
  - Marcus & Goh focused on crawler logic and fetching URLs
  - Luqman & Camily focused on HTML parsing and selector analysis
- Finalized target website: **Carlist.my**
- Identified key data fields: car name, price, location, mileage, year, etc.
- Chose suitable crawler/scraper libraries for each member’s stack
- Designed folder structure and created GitHub repository
- Got verbal confirmation from lecturer on scope and dataset plan

---

### 🧰 Week 2: Crawler Implementation
- Built individual scrapers using different stacks (`httpx + parsel`, `urllib + Selectolax`, etc.)
- Validated data selectors using browser dev tools (e.g., inspect element)
- Wrote modular Python scripts to handle pagination and auto-retry
- Ensured robots.txt compliance and polite scraping delays (1–2 sec)
- Saved first batch of data (~10,000 rows) in JSON format for validation
- Team tested and compared scraper performance and accuracy

---

### ⚙️ Week 3: Data Processing & Optimization
- Cleaned combined dataset:
  - Removed duplicates and null values
  - Standardized price and mileage formats
  - Merged data from all scrapers into a single schema
- Switched from pandas to `Modin`, `Dask`, or `Polars` for performance testing
- Benchmarked:
  - Runtime for merging & cleaning (before vs after optimization)
  - CPU and memory usage
- Saved clean dataset as Part 1 and continued scraping to complete 100k records

---

### 📈 Week 4: Final Report & Submission
- Finalized full dataset (Part 1 & Part 2), confirmed 100k+ records
- Completed report with:
  - Architecture diagram
  - Comparison of scraper stacks
  - Optimization techniques and performance charts
- Created presentation slides summarizing workflow and findings
- Submitted:
  - ✅ Report (Turnitin)
  - ✅ Dataset (JSON files on GitHub)
  - ✅ GitHub repo with code and readme
  - ✅ Presentation slides
