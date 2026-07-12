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
# Query 10: Multi-Level CTE Customer Segmentation
# --------------------------------------------------

MONTHLY_CUSTOMER_SEGMENTATION = """
WITH customer_monthly_revenue AS (
    SELECT
        STRFTIME('%Y-%m', o.order_date) AS revenue_month,
        o.customer_id,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS monthly_revenue

    FROM orders AS o

    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'
      AND o.customer_id IS NOT NULL
      AND o.customer_id != 'C_UNKNOWN'

    GROUP BY
        STRFTIME('%Y-%m', o.order_date),
        o.customer_id
),

customer_segments AS (
    SELECT
        revenue_month,
        customer_id,
        monthly_revenue,

        CASE
            WHEN monthly_revenue > 10000
                THEN 'High'

            WHEN monthly_revenue >= 5000
                 AND monthly_revenue <= 10000
                THEN 'Medium'

            ELSE 'Low'
        END AS revenue_category

    FROM customer_monthly_revenue
),

monthly_segment_counts AS (
    SELECT
        revenue_month,
        revenue_category,
        COUNT(DISTINCT customer_id) AS customer_count,

        ROUND(
            SUM(monthly_revenue),
            2
        ) AS segment_revenue

    FROM customer_segments

    GROUP BY
        revenue_month,
        revenue_category
)

SELECT
    revenue_month,
    revenue_category,
    customer_count,
    segment_revenue

FROM monthly_segment_counts

ORDER BY
    revenue_month,
    CASE revenue_category
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;
"""


# --------------------------------------------------
# Query 11: NTILE Customer Lifetime Value
# --------------------------------------------------

CUSTOMER_LIFETIME_VALUE_QUARTILES = """
WITH customer_lifetime_value AS (
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
        ) AS total_value

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
),

customer_quartiles AS (
    SELECT
        customer_id,
        customer_name,
        customer_type,
        total_value,

        NTILE(4) OVER (
            ORDER BY total_value DESC
        ) AS quartile

    FROM customer_lifetime_value
)

SELECT
    customer_id,
    customer_name,
    customer_type,
    total_value,
    quartile,

    CASE quartile
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
    END AS quartile_label

FROM customer_quartiles

ORDER BY
    quartile,
    total_value DESC;
"""


# --------------------------------------------------
# Query 12: Year-over-Year Revenue
# --------------------------------------------------

YEAR_OVER_YEAR_REVENUE = """
WITH monthly_revenue AS (
    SELECT
        CAST(
            STRFTIME('%Y', o.order_date)
            AS INTEGER
        ) AS revenue_year,

        CAST(
            STRFTIME('%m', o.order_date)
            AS INTEGER
        ) AS revenue_month,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS revenue

    FROM orders AS o

    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY
        STRFTIME('%Y', o.order_date),
        STRFTIME('%m', o.order_date)
)

SELECT
    current_year.revenue_year AS year,
    current_year.revenue_month AS month,
    current_year.revenue,
    previous_year.revenue AS prev_year_revenue,

    CASE
        WHEN previous_year.revenue IS NULL
            THEN NULL

        WHEN previous_year.revenue = 0
            THEN NULL

        ELSE ROUND(
            (
                current_year.revenue
                - previous_year.revenue
            )
            * 100.0
            / previous_year.revenue,
            2
        )
    END AS yoy_growth_percent

FROM monthly_revenue AS current_year

LEFT JOIN monthly_revenue AS previous_year
    ON current_year.revenue_month
        = previous_year.revenue_month

    AND current_year.revenue_year
        = previous_year.revenue_year + 1

ORDER BY
    current_year.revenue_year,
    current_year.revenue_month;
"""


# --------------------------------------------------
# Execute Query and Export Report
# --------------------------------------------------

def execute_query(
    connection,
    query,
    report_name,
    heading,
    preview_rows=20
):

    print("\n" + "=" * 80)
    print(heading)
    print("=" * 80)

    result_df = pd.read_sql_query(
        query,
        connection
    )

    if result_df.empty:

        print("No records found.")

    else:

        print(
            result_df.head(preview_rows).to_string(
                index=False
            )
        )

        if len(result_df) > preview_rows:

            print(
                f"\nShowing first {preview_rows} "
                f"of {len(result_df)} records."
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
            MONTHLY_CUSTOMER_SEGMENTATION,
            "10_monthly_customer_segmentation.csv",
            "QUERY 10: MULTI-LEVEL CTE CUSTOMER SEGMENTATION"
        )

        execute_query(
            connection,
            CUSTOMER_LIFETIME_VALUE_QUARTILES,
            "11_customer_lifetime_value_quartiles.csv",
            "QUERY 11: NTILE CUSTOMER LIFETIME VALUE"
        )

        execute_query(
            connection,
            YEAR_OVER_YEAR_REVENUE,
            "12_year_over_year_revenue.csv",
            "QUERY 12: YEAR-OVER-YEAR REVENUE COMPARISON"
        )

        print("\n" + "=" * 80)
        print("ADVANCED SQL PART 2 COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except sqlite3.Error as error:

        print(f"\nSQLite Error: {error}")

        raise

    finally:

        if connection is not None:

            connection.close()

            print("\n✔ Database connection closed")


if __name__ == "__main__":
    main()