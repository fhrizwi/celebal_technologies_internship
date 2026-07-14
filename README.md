# Celebal Technologies Internship

A data engineering and analytics internship repository covering Python, SQL, Azure, Apache Spark, Delta Lake, and Databricks. Weekly assignments build core skills step by step, and two capstone projects demonstrate end-to-end pipeline development.

## Overview

This repository documents weekly assignments and major projects completed during the Celebal Technologies internship. Work progresses from foundational data cleaning in Python to advanced SQL analytics, cloud ETL on Azure, distributed processing with PySpark, and production-style pipelines on Databricks.

## Tech Stack

| Category | Tools & Technologies |
|----------|---------------------|
| Languages | Python, SQL |
| Data Libraries | Pandas, PySpark, Delta Lake |
| Databases | MySQL, SQLite |
| Cloud | Microsoft Azure, Azure Blob Storage, Azure Data Factory, Databricks |
| Concepts | Medallion Architecture, CDC, SCD Type 2, Window Functions, CTEs |
| Tools | Jupyter Notebook, MySQL Workbench, Unity Catalog, Git, GitHub |

## Repository Structure

```
CT INTERNSHIP/
├── WEEK_1/                              # Python & Pandas — data exploration and cleaning
├── WEEK_2/                              # SQL — e-commerce sales analysis
├── WEEK_3/                              # SQL — Superstore analytics (subqueries, CTEs, windows)
├── WEEK_4/                              # Azure — end-to-end ADF data pipeline
├── WEEK_5/                              # PySpark — data cleaning and transformation
├── WEEK_6/                              # PySpark — CSV/Parquet pipeline and Spark concepts
├── WEEK_7/                              # Pandas — Superstore data cleaning
├── WEEK_8/                              # E-Commerce Order Analytics (capstone)
└── Customer_Sentiment_Analysis_Project/ # Databricks Medallion Architecture (capstone)
```

---

## Weekly Assignments

### Week 1 — Data Exploration and Cleaning

**Objective:** Learn Python basics and perform data exploration and cleaning using Pandas.

- **Dataset:** Myntra product records (`Combined_dataset.csv` — 1,000 rows, 24 columns)
- **Output:** `cleaned_dataset.csv` (1,000 rows, 27 columns with `price`, `quantity`, `total_amount`)
- **Key tasks:** Load CSV, explore data, handle missing values, remove duplicates, filter rows, create derived columns, export cleaned data
- **Files:** `WEEK_1/notebook/data_cleaning.ipynb`, `WEEK_1/data/`
- **Details:** [WEEK_1/SUMMARY.md](WEEK_1/SUMMARY.md)

---

### Week 2 — SQL E-Commerce Analysis

**Objective:** Analyze e-commerce sales data using SQL.

- **Tools:** MySQL Workbench, SQL
- **Topics covered:** Filtering, aggregation, joins, transactions
- **Includes:** SQL queries, screenshots, theoretical answers, business insights
- **Details:** [WEEK_2/SQL_Ecommerce_Analysis/README.md](WEEK_2/SQL_Ecommerce_Analysis/README.md)

**Key insights:**
- Electronics products generate high revenue
- Delivered orders contribute the highest sales
- JOIN queries help analyze customer buying patterns

---

### Week 3 — Superstore SQL Analysis

**Objective:** Analyze Superstore sales data using advanced SQL techniques.

- **Dataset:** [Superstore Dataset (Kaggle)](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- **Topics covered:** Subqueries, CTEs, window functions (ROW_NUMBER, DENSE_RANK)
- **Business queries:** Above-average sales, customer ranking, top/bottom customers, single-order customers
- **Files:** `WEEK_3/Superstore-SQL-Analysis/sql/`, `screenshots/`
- **Details:** [WEEK_3/Superstore-SQL-Analysis/README.md](WEEK_3/Superstore-SQL-Analysis/README.md)

---

### Week 4 — Azure Data Pipeline (ADF)

**Objective:** Build an end-to-end data pipeline using Azure Blob Storage and Azure Data Factory.

**Pipeline flow:**

```
Source Blob → Get Metadata → Copy Data → Destination Blob
```

- **Tasks completed:** Resource group, storage account, blob container, linked service, source/destination datasets, Get Metadata activity, Copy Data activity, IAM roles
- **Output:** Pipeline executed successfully with metadata validation and CSV copied to destination
- **Details:** [WEEK_4/Azure-ADF-Data-Pipeline/README.md](WEEK_4/Azure-ADF-Data-Pipeline/README.md)

---

### Week 5 — Apache Spark Assignment

**Objective:** Perform data cleaning, transformation, aggregation, and schema modification using PySpark.

- **Technologies:** Python, PySpark
- **Topics covered:** Filtering, GroupBy operations, schema modification
- **Run locally:**

```bash
cd WEEK_5/Spark-Assignment
pip install -r requirements.txt
python spark_assignment.py
```

- **Details:** [WEEK_5/Spark-Assignment/README.md](WEEK_5/Spark-Assignment/README.md)

---

### Week 6 — Spark Architecture & Data Pipeline

**Objective:** Build a PySpark data pipeline with CSV and Parquet operations.

- **Topics covered:** Spark architecture, lazy evaluation, transformations, actions, filtering, column rename, casting, predicate pushdown
- **Pipeline:** Read CSV → transform → save Parquet → read Parquet → filter nulls → save CSV
- **Files:** `WEEK_6/Spark_Assignment/main.py`, `data/source.csv`, `output/`
- **Details:** [WEEK_6/Spark_Assignment/README.md](WEEK_6/Spark_Assignment/README.md)

**Run locally:**

```bash
cd WEEK_6/Spark_Assignment
python main.py
```

---

### Week 7 — Superstore Data Cleaning (Pandas)

**Objective:** Perform data exploration and cleaning on the Superstore dataset using Pandas.

- **Dataset:** `data/sample-store.csv`
- **Key tasks:** Load CSV, explore data, handle missing values, remove duplicates, filter rows, select columns, create `total_amount`, save cleaned CSV
- **Output:** `output/cleaned_store.csv`
- **Files:** `WEEK_7/DeltaLakeAssignment/notebook/DeltaLakeAssignment.ipynb`
- **Details:** [WEEK_7/DeltaLakeAssignment/README.md](WEEK_7/DeltaLakeAssignment/README.md)

---

### Week 8 — E-Commerce Order Analytics System

**Objective:** Build a complete end-to-end analytics system from messy data generation to SQL reporting.

**Pipeline:**

```
Generate Raw Data → Clean & Validate → Load SQLite → SQL Analysis → Reports → Edge-Case Tests
```

- **Technologies:** Python, Pandas, Faker, SQLite, SQL
- **Features:** Data generation with intentional quality issues, cleaning/validation, 16 SQL queries (basic to advanced), CTEs, window functions, CLI report generator, automated edge-case testing
- **Reports:** Daily/weekly/monthly reports, revenue analysis, cohort retention, frequently bought together products
- **Details:** [WEEK_8/Ecommerce_Order_Analytics/README.md](WEEK_8/Ecommerce_Order_Analytics/README.md)

**Run locally:**

```bash
cd WEEK_8/Ecommerce_Order_Analytics
pip install -r requirements.txt
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/load_database.py
```

---

## Major Projects

### Customer Sentiment Analysis (Databricks Medallion Architecture)

**Objective:** Build an end-to-end Databricks pipeline using Bronze → Silver → Gold architecture.

- **Technologies:** Databricks, PySpark, Delta Lake, Unity Catalog, Structured Streaming
- **Concepts:** CDC, SCD Type 2, watermarking, nested JSON flattening, Gold KPI tables, Databricks Workflows, interactive dashboard
- **Layers:**
  - **Bronze:** Raw customer and call data ingestion
  - **Silver:** Flattening, deduplication, CDC, SCD Type 2, watermarking
  - **Gold:** Daily call volume, sentiment distribution, agent performance, high-risk customers
- **Details:** [Customer_Sentiment_Analysis_Project/README.md](Customer_Sentiment_Analysis_Project/README.md)

---

## Skills Gained

- **Data wrangling** — loading, exploring, cleaning, and exporting datasets with Pandas
- **SQL analytics** — filtering, joins, aggregations, subqueries, CTEs, and window functions
- **Cloud ETL** — designing and executing data pipelines on Azure Data Factory
- **Big data processing** — distributed data operations with Apache Spark and PySpark
- **Data lakehouse** — Medallion Architecture, Delta Lake, CDC, and SCD Type 2 on Databricks
- **End-to-end analytics** — data generation, validation, SQLite storage, reporting, and testing
- **Documentation** — weekly summaries, READMEs, screenshots, and project reports

## Author

**Faizul Haque Rizwi** — Celebal Technologies Internship

- GitHub: [fhrizwi](https://github.com/fhrizwi)
- LinkedIn: [fhrizwi](https://www.linkedin.com/in/fhrizwi/)
- Email: [faizulhaque2002@gmail.com](mailto:faizulhaque2002@gmail.com)
