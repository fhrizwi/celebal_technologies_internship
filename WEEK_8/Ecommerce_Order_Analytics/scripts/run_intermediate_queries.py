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
# Intermediate SQL Queries
# --------------------------------------------------

CUSTOMERS_WITHOUT_DELIVERED_ORDERS = """
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers AS c
INNER JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE c.customer_id != 'C_UNKNOWN'
GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_type
HAVING SUM(
    CASE
        WHEN o.status = 'DELIVERED' THEN 1
        ELSE 0
    END
) = 0
ORDER BY total_orders DESC;
"""


PRODUCTS_WITH_MORE_RETURNS = """
SELECT
    p.product_id,
    p.product_name,
    p.category,

    SUM(
        CASE
            WHEN oi.quantity > 0
            THEN oi.quantity
            ELSE 0
        END
    ) AS purchased_quantity,

    ABS(
        SUM(
            CASE
                WHEN oi.quantity < 0
                THEN oi.quantity
                ELSE 0
            END
        )
    ) AS returned_quantity

FROM products AS p
INNER JOIN order_items AS oi
    ON p.product_id = oi.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category

HAVING returned_quantity > purchased_quantity

ORDER BY returned_quantity DESC;
"""


RETURN_RATE_PER_CATEGORY = """
SELECT
    p.category,

    SUM(
        CASE
            WHEN oi.quantity < 0
            THEN ABS(oi.quantity)
            ELSE 0
        END
    ) AS returned_items,

    SUM(
        ABS(oi.quantity)
    ) AS total_items,

    ROUND(
        100.0
        * SUM(
            CASE
                WHEN oi.quantity < 0
                THEN ABS(oi.quantity)
                ELSE 0
            END
        )
        / NULLIF(
            SUM(ABS(oi.quantity)),
            0
        ),
        2
    ) AS return_rate_percent

FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id

GROUP BY p.category

ORDER BY return_rate_percent DESC;
"""


# --------------------------------------------------
# Execute Query and Export Result
# --------------------------------------------------

def execute_query(
    connection,
    query,
    report_name,
    heading
):

    print("\n" + "=" * 75)
    print(heading)
    print("=" * 75)

    result_df = pd.read_sql_query(
        query,
        connection
    )

    if result_df.empty:

        print("No matching records found.")

    else:

        print(
            result_df.to_string(index=False)
        )

    output_path = REPORTS_DIR / report_name

    result_df.to_csv(
        output_path,
        index=False
    )

    print(f"\n✔ Report saved: {output_path}")

    return result_df


# --------------------------------------------------
# Main Function
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
            CUSTOMERS_WITHOUT_DELIVERED_ORDERS,
            "04_customers_without_delivered_orders.csv",
            "QUERY 4: CUSTOMERS WITHOUT DELIVERED ORDERS"
        )

        execute_query(
            connection,
            PRODUCTS_WITH_MORE_RETURNS,
            "05_products_with_more_returns.csv",
            "QUERY 5: PRODUCTS WITH MORE RETURNS THAN PURCHASES"
        )

        execute_query(
            connection,
            RETURN_RATE_PER_CATEGORY,
            "06_return_rate_per_category.csv",
            "QUERY 6: RETURN RATE PER CATEGORY"
        )

        print("\n" + "=" * 75)
        print("INTERMEDIATE SQL ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 75)

    except sqlite3.Error as error:

        print(f"\nSQLite Error: {error}")

        raise

    finally:

        if connection is not None:

            connection.close()

            print("\n✔ Database connection closed")


if __name__ == "__main__":
    main()