import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = ROOT_DIR / "database" / "ecommerce.db"

REPORTS_DIR = ROOT_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# SQL Queries
# --------------------------------------------------

TOTAL_REVENUE_PER_CATEGORY = """
SELECT
    p.category,
    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_revenue
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
INNER JOIN orders AS o
    ON oi.order_id = o.order_id
WHERE o.status != 'CANCELLED'
GROUP BY p.category
ORDER BY total_revenue DESC;
"""


TOP_10_CUSTOMERS = """
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_order_value
FROM customers AS c
INNER JOIN orders AS o
    ON c.customer_id = o.customer_id
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE o.status != 'CANCELLED'
  AND c.customer_id != 'C_UNKNOWN'
GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_type
ORDER BY total_order_value DESC
LIMIT 10;
"""


MONTH_WISE_ORDER_COUNT = """
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
WHERE date(order_date) >= date(
    'now',
    'start of month',
    '-11 months'
)
GROUP BY strftime('%Y-%m', order_date)
ORDER BY order_month;
"""


# --------------------------------------------------
# Execute and Export Query
# --------------------------------------------------

def execute_query(
    connection,
    query,
    report_name,
    heading
):
    print("\n" + "=" * 70)
    print(heading)
    print("=" * 70)

    result_df = pd.read_sql_query(
        query,
        connection
    )

    if result_df.empty:
        print("No records found.")
    else:
        print(result_df.to_string(index=False))

    output_path = REPORTS_DIR / report_name

    result_df.to_csv(
        output_path,
        index=False
    )

    print(f"\n✔ Report saved: {output_path}")

    return result_df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run python scripts/load_database.py first."
        )

    connection = None

    try:
        connection = sqlite3.connect(
            DATABASE_PATH
        )

        print("\nConnected to SQLite database:")
        print(DATABASE_PATH)

        execute_query(
            connection,
            TOTAL_REVENUE_PER_CATEGORY,
            "01_total_revenue_per_category.csv",
            "QUERY 1: TOTAL REVENUE PER CATEGORY"
        )

        execute_query(
            connection,
            TOP_10_CUSTOMERS,
            "02_top_10_customers.csv",
            "QUERY 2: TOP 10 CUSTOMERS"
        )

        execute_query(
            connection,
            MONTH_WISE_ORDER_COUNT,
            "03_month_wise_order_count.csv",
            "QUERY 3: LAST 12 MONTHS ORDER COUNT"
        )

        print("\n" + "=" * 70)
        print("BASIC SQL ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except sqlite3.Error as error:
        print(f"\nSQLite Error: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()
            print("\n✔ Database connection closed")


if __name__ == "__main__":
    main()