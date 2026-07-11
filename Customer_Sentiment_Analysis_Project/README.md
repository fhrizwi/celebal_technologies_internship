# 📞 Customer Call Sentiment Analysis using Databricks Medallion Architecture

## 📌 Project Overview

This project demonstrates an end-to-end Data Engineering pipeline built on **Databricks** using the **Medallion Architecture (Bronze → Silver → Gold)**. The pipeline processes customer information and simulated customer call data to generate business-ready insights for customer support analytics.

The project implements modern Data Engineering concepts including:

* Medallion Architecture
* Delta Lake
* Unity Catalog
* Change Data Capture (CDC)
* Slowly Changing Dimension (SCD Type 2)
* Watermarking
* Structured Streaming
* Gold Layer KPI Aggregations
* Databricks Workflows
* Interactive Dashboard

---

# 🏗️ Architecture

```
                Customer Dataset
                      │
                      ▼
              Bronze Customers
                      │
                      ▼
              Silver Customers
                      │
                CDC + SCD Type 2
                      │
                      ▼

Call JSON Files
      │
      ▼
 Bronze Calls
      │
      ▼
 Silver Calls
(Flatten + Deduplicate + Watermark)
      │
      ▼
 Gold KPI Tables
      │
      ▼
 Dashboard & Reporting
```

---

# 🛠️ Tech Stack

* Databricks
* Apache Spark
* PySpark
* Delta Lake
* Unity Catalog
* Structured Streaming
* SQL
* Python
* Faker
* Git & GitHub

---

# 📂 Project Structure

```
Customer_Call_Sentiment_Project
│
├── bronze
│   ├── 01_bronze_customers
│   └── 02_bronze_calls
│
├── silver
│   ├── 01_silver_calls
│   ├── 02_silver_customers
│   ├── 03_scd_type2_customers
│   └── 04_watermark_calls
│
├── gold
│   └── 01_gold_kpis
│
├── scripts
│   └── generate_call_data.py
│
├── datasets
│   └── customer_cdc_data_final.csv
│
├── screenshots
│
├── README.md
└── requirements.txt
```

---

# 📊 Dataset

## Customer Dataset

The customer dataset contains:

* customer_id
* city
* subscription_type
* age
* signup_date
* operation
* update_ts

The dataset is used to demonstrate:

* Change Data Capture (CDC)
* SCD Type 2 implementation

---

## Call Dataset

Call data is generated using Python.

Each call contains:

* call_id
* customer_id
* call_timestamp
* duration_seconds
* sentiment
* conversation

  * agent
  * customer_text

The call dataset simulates a real-world customer support system.

---

# 🥉 Bronze Layer

The Bronze Layer ingests raw customer and call data.

### Bronze Customers

* Raw customer ingestion
* Metadata columns
* Delta Table

### Bronze Calls

* Raw JSON ingestion
* Nested conversation structure
* Delta Table

---

# 🥈 Silver Layer

The Silver Layer transforms raw data into clean analytical datasets.

Implemented features:

* Nested JSON Flattening
* Duplicate Removal
* Event Time Creation
* Data Cleaning
* CDC Processing
* Watermark Logic

---

# 🔄 Change Data Capture (CDC)

Customer updates are processed using the latest update timestamp.

Latest customer record is selected using Window Functions.

This ensures downstream tables always contain the most recent customer information.

---

# 🕒 Slowly Changing Dimension (SCD Type 2)

SCD Type 2 is implemented to preserve historical customer information.

Additional columns:

* effective_from
* effective_to
* is_current

This enables complete customer history tracking.

---

# 🥇 Gold Layer

Business KPIs are generated for reporting.

Generated Gold Tables:

* Daily Call Volume
* Sentiment Distribution
* Agent Performance
* Subscription-wise Sentiment
* High Risk Customers

---

# 📈 Dashboard

A Databricks dashboard is created using Gold Layer tables.

Dashboard includes:

* Daily Call Volume
* Customer Sentiment Distribution
* Agent Performance
* Subscription-wise Sentiment
* High Risk Customers

---

# ⚙️ Workflow

Databricks Workflow orchestrates the complete pipeline.

Execution Order:

1. Bronze Customers
2. Bronze Calls
3. Silver Calls
4. Silver Customers
5. SCD Type 2
6. Gold KPIs

---

# 📸 Screenshots

Add the following screenshots inside the `screenshots` folder:

* Workspace Structure
* Unity Catalog Tables
* Bronze Layer Output
* Silver Layer Output
* SCD Type 2 Table
* Gold KPI Tables
* Dashboard
* Workflow Success

---

# 🚀 How to Run

1. Upload the customer dataset into Unity Catalog Volume.
2. Execute the Bronze notebooks.
3. Execute the Silver notebooks.
4. Run the SCD Type 2 notebook.
5. Execute the Gold notebook.
6. Open the Dashboard.
7. Run the Databricks Workflow for end-to-end execution.

---

# 📌 Key Features

* Medallion Architecture
* Delta Lake
* Structured Streaming
* Watermarking
* CDC
* SCD Type 2
* Delta Tables
* Databricks Workflows
* Interactive Dashboard
* Business KPI Generation

---

# 📚 Learning Outcomes

This project demonstrates practical implementation of modern Data Engineering concepts including:

* Data Lakehouse Architecture
* Incremental Data Processing
* Customer History Tracking
* Streaming Data Processing
* Business KPI Reporting
* End-to-End Databricks Pipeline Development

---

# 👨‍💻 Author

**Faizul Haque Rizwi**

Data Engineering Project built using Databricks, PySpark and Delta Lake.
