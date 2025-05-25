<h1 align="center"> 
  Group 3 -Utusan Malaysia
  <br>
</h1>

<table border="solid" align="center">
  <tr>
    <th>Name</th>
    <th>Matric Number</th>
  </tr>
  <tr>
    <td width=80%>MUHAMMAD DANIEL HAKIM BIN SYAHRULNIZAM</td>
    <td>A22EC0207</td>
  </tr>
  <tr>
    <td width=80%>WONG KHAI SHIAN NICHOLAS</td>
    <td>A22EC0292</td>
  </tr>
  <tr>
    <td width=80%>NICOLE LIM TZE YEE </td>
    <td>A22EC0123</td>
  </tr>
  <tr>
    <td width=80%>NUR ALEYSHA QURRATU'AINI BINTI MAT SALLEH</td>
    <td>A22EC0241</td>
  </tr>
</table>
<!-- <br>
<div align='center'>
<img src='https://www.jeveuxetredatascientist.fr/wp-content/uploads/2022/06/BeautifulSoup.jpg' height=200 width=300 alt='beautiful soup'>
</div>
<br> -->

## 🔍 Project Overview

The objective of this project is to develop a high-performance data pipeline capable of extracting and processing **at least 100,000 structured records** from a dynamic web source. Our selected website is **[Utusan Malaysia](https://www.utusan.com.my/)**.

We designed a system that:
- Crawls and scrapes data using `BeautifulSoup`, `Request`, `Asyncio`, `Selenium`, and `Selectolax`.
- Stores raw and cleaned data in a **MongoDB Atlas** database.
- Performs cleaning using **Pandas (baseline)**, **Polars (optimized)**, **Modin**, **Dask** and **Swifter** methods.
- Evaluates and compares performance improvements.

---

## 🌐 Target Website

**Website**: [Utusan Malaysia](https://www.utusan.com.my/)  
**Description**: Utusan Malaysia is a Malaysian online news portal that publishes articles on current events, politics, business, and entertainment. It serves as the target website for this project due to its structured layout and regularly updated content, making it suitable for web scraping and data analysis.

### 📊 Data Fields Extracted

| Attribute        | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Article Title    | The headline or title of the news article.  |
| Publication Date | The date on which the article was published on the Utusan Malaysia website, used to track content chronology. |
| Article Category | The classification of the article based on its subject matter, such as politics, business, or entertainment.  |
| Article URL | The direct web address (link) to the full article, allowing access to the original source for reference or validation. |

---

## 🎯 Goals and Deliverables

- ✅ Collect large-scale Utusan Malaysia news data
- ✅ Clean and transform datasets using Python tools
- ✅ Apply high-performance techniques 
- ✅ Compare all libraries for cleaning in terms of speed and efficiency
- ✅ Submit a full report, cleaned dataset, source code, and performance analysis

📄 **Report, code, and results** are organized in the respective subfolders.

---

## 📄 Project Documentation

You can view our final deliverables here:

- 📘 [Final Report (PDF)](https://github.com/Jingyong14/HPDP02/blob/main/2425/project/p1/Group%203/report/Group%203_Project%201_Report.pdf)
- 🖥️ [Presentation Slides (PPTX)](report/Presentation_Slides.pptx)

---
