# E-Commerce Order Analytics System

A complete data analytics project that generates messy e-commerce data, cleans and validates it using Python and Pandas, stores it in SQLite, and performs business analysis using SQL.

The project also includes a command-line report generator and automated edge-case testing.

## Project Overview

Online order data often comes from multiple sources and may contain missing values, inconsistent date formats, invalid email addresses, incorrect product names, invalid references, and other quality issues.

This project demonstrates an end-to-end data pipeline:

```text
Generate Raw Data
        ↓
Clean and Validate Data
        ↓
Load Data into SQLite
        ↓
Perform SQL Analysis
        ↓
Generate Reports
        ↓
Run Edge-Case Tests
```

## Technologies Used

* Python
* Pandas
* Faker
* SQLite
* SQL
* Git
* GitHub
* Visual Studio Code

## Project Features

* Generates realistic e-commerce data
* Creates intentional data-quality issues
* Cleans inconsistent order dates
* Handles missing customer IDs
* Normalizes product names
* Validates customer email addresses
* Checks referential integrity
* Loads cleaned data into SQLite
* Executes basic, intermediate, and advanced SQL queries
* Uses CTEs and window functions
* Generates daily, weekly, and monthly reports
* Compares results with previous periods
* Tests important edge cases
* Exports analysis results as CSV and text reports

## Dataset Structure

The project generates four CSV files.

### Customers

```text
customer_id
customer_name
email
registration_date
customer_type
```

Customer types:

```text
REGULAR
PREMIUM
VIP
```

### Products

```text
product_id
product_name
category
subcategory
cost_price
```

Product categories include:

```text
Electronics
Clothing
Books
Home
```

### Orders

```text
order_id
customer_id
order_date
status
region_code
```

Order statuses:

```text
PLACED
SHIPPED
DELIVERED
CANCELLED
RETURNED
```

### Order Items

```text
item_id
order_id
product_id
quantity
unit_price
discount_percent
```

## Intentional Data Issues

The generated raw data contains intentional issues for cleaning and validation:

* Approximately 5% missing customer IDs
* Approximately 3% negative quantities representing returns
* Some order dates in `DD-MM-YYYY` format
* Product names containing extra spaces or inconsistent capitalization
* Approximately 2% invalid customer emails
* Referential relationships between orders and order items

## Project Structure

```text
Ecommerce_Order_Analytics/
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
│
├── cleaned_data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
│
├── database/
│   └── ecommerce.db
│
├── reports/
│   ├── issues_report.txt
│   ├── edge_case_test_report.txt
│   ├── 01_total_revenue_per_category.csv
│   ├── 02_top_10_customers.csv
│   ├── 03_month_wise_order_count.csv
│   ├── 04_customers_without_delivered_orders.csv
│   ├── 05_products_with_more_returns.csv
│   ├── 06_return_rate_per_category.csv
│   ├── 07_running_revenue_per_region.csv
│   ├── 08_product_ranking_by_category.csv
│   ├── 09_customer_order_gap_analysis.csv
│   ├── 10_monthly_customer_segmentation.csv
│   ├── 11_customer_lifetime_value_quartiles.csv
│   ├── 12_year_over_year_revenue.csv
│   ├── 13_first_and_recent_category.csv
│   ├── 14_cumulative_revenue_distribution.csv
│   ├── 15_cohort_retention_analysis.csv
│   └── 16_frequently_bought_together.csv
│
├── screenshots/
│
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── load_database.py
│   ├── run_basic_queries.py
│   ├── run_intermediate_queries.py
│   ├── run_advanced_queries_part1.py
│   ├── run_advanced_queries_part2.py
│   ├── run_advanced_queries_part3.py
│   ├── report.py
│   └── test_cases.py
│
├── sql/
│   ├── 02_basic_queries.sql
│   ├── 03_intermediate_queries.sql
│   ├── 04_advanced_queries_part1.sql
│   ├── 05_advanced_queries_part2.sql
│   └── 06_advanced_queries_part3.sql
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/fhrizwi/Ecommerce-Order-Analytics-System.git
```

Move into the project directory:

```bash
cd Ecommerce-Order-Analytics-System
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install Required Libraries

```bash
pip install -r requirements.txt
```

The main dependencies are:

```text
pandas
Faker
```

## Running the Project

The scripts should be executed in the following order.

### Step 1: Generate Raw Data

```bash
python scripts/generate_data.py
```

This creates:

```text
data/customers.csv
data/products.csv
data/orders.csv
data/order_items.csv
```

### Step 2: Clean and Validate Data

```bash
python scripts/clean_data.py
```

This creates cleaned CSV files inside:

```text
cleaned_data/
```

It also generates:

```text
reports/issues_report.txt
```

### Step 3: Create and Load the SQLite Database

```bash
python scripts/load_database.py
```

This creates:

```text
database/ecommerce.db
```

### Step 4: Run Basic SQL Queries

```bash
python scripts/run_basic_queries.py
```

### Step 5: Run Intermediate SQL Queries

```bash
python scripts/run_intermediate_queries.py
```

### Step 6: Run Advanced SQL Queries

```bash
python scripts/run_advanced_queries_part1.py
```

```bash
python scripts/run_advanced_queries_part2.py
```

```bash
python scripts/run_advanced_queries_part3.py
```

### Step 7: Generate a Command-Line Report

```bash
python scripts/report.py
```

Available report types:

```text
daily
weekly
monthly
```

The tool asks for:

* Report type
* Start date
* End date

It displays:

* Total orders
* Total revenue
* Unique customers
* Top three products
* Comparison with the previous period

### Step 8: Run Edge-Case Tests

```bash
python scripts/test_cases.py
```

The test report is saved as:

```text
reports/edge_case_test_report.txt
```

## Data Cleaning Operations

The cleaning script performs the following operations:

* Converts order dates into a standard format
* Handles missing customer IDs
* Removes duplicate records
* Normalizes product names
* Trims extra spaces
* Converts product names to title case
* Validates email addresses using regular expressions
* Detects invalid order references
* Detects invalid product references
* Checks zero quantities
* Checks invalid discount percentages
* Saves all detected issues in a report

## SQL Analysis

### Basic Queries

1. Total revenue per category
2. Top 10 customers by total order value
3. Month-wise order count for the last 12 months

### Intermediate Queries

4. Customers who placed orders but never had a delivered order
5. Products with more returns than purchases
6. Return rate per category

### Advanced Queries

7. Running revenue total per region
8. Product ranking using `DENSE_RANK`
9. Customer order-gap analysis using `LAG`
10. Monthly customer segmentation using multi-level CTEs
11. Customer lifetime-value segmentation using `NTILE`
12. Year-over-year revenue comparison
13. First and most recent purchased category
14. Cumulative customer revenue distribution
15. Customer cohort-retention analysis
16. Products frequently bought together

## Revenue Formula

Revenue is calculated using:

```text
Revenue =
quantity × unit_price × (1 - discount_percent / 100)
```

Cancelled orders are excluded from revenue analysis.

Negative quantities represent returned items.

## SQL Concepts Demonstrated

* Joins
* Aggregations
* Subqueries
* Common Table Expressions
* Multi-level CTEs
* Window functions
* `LAG`
* `DENSE_RANK`
* `NTILE`
* Running totals
* Cumulative distribution
* Conditional aggregation
* Cohort analysis
* Self joins

## Edge Cases Tested

The project contains automated tests for:

* Order items referencing non-existent orders
* Discount percentages greater than 100
* Zero quantity
* Future order dates
* Existing invalid foreign-key references
* Existing invalid discounts
* Existing zero-quantity rows
* Existing future-dated orders

## Example Outputs

### Data Cleaning Output

```text
Cleaning Orders
Orders Cleaned Successfully

Cleaning Products
Products Cleaned Successfully

Validating Customer Emails
Invalid Emails Found: 6

Checking Referential Integrity
Invalid Records Found: 0
```

### Database Verification Output

```text
customers: 501 rows
products: 500 rows
orders: 500 rows
order_items: 1000 rows

Invalid order references: 0
Invalid product references: 0
```

### Edge-Case Test Output

```text
Total Tests: 8
Passed: 8
Failed: 0
```

## Business Insights Generated

The project helps identify:

* Highest-revenue product categories
* Most valuable customers
* Monthly order trends
* Category return rates
* Products with high return quantities
* Customers at risk due to long order gaps
* Customer lifetime-value segments
* Year-over-year revenue growth
* Customer category shifts
* Revenue concentration among top customers
* Customer retention by registration cohort
* Products frequently purchased together

## Future Improvements

* Build an interactive dashboard using Power BI or Tableau
* Add visualizations using Matplotlib
* Create a Streamlit web application
* Move the database from SQLite to PostgreSQL
* Schedule automated data pipelines
* Add unit testing using `pytest`
* Add logging instead of terminal print statements
* Use larger real-world e-commerce datasets
* Deploy the analytics system on a cloud platform

## Author

**Faizul Haque Rizwi**

* GitHub: [fhrizwi](https://github.com/fhrizwi)
* LinkedIn: [fhrizwi](https://www.linkedin.com/in/fhrizwi/)
* Email: [faizulhaque2002@gmail.com](mailto:faizulhaque2002@gmail.com)
