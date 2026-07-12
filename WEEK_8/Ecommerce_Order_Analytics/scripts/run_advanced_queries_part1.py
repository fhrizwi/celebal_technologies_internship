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
# Query 7: Running Revenue Total per Region
# --------------------------------------------------

RUNNING_REVENUE_PER_REGION = """
WITH daily_region_revenue AS (
    SELECT
        o.region_code,
        DATE(o.order_date) AS order_date,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS daily_revenue

    FROM orders AS o

    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY
        o.region_code,
        DATE(o.order_date)
)

SELECT
    region_code,
    order_date,
    daily_revenue,

    ROUND(
        SUM(daily_revenue) OVER (
            PARTITION BY region_code
            ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ),
        2
    ) AS running_total

FROM daily_region_revenue

ORDER BY
    region_code,
    order_date;
"""


# --------------------------------------------------
# Query 8: Product Ranking by Category
# --------------------------------------------------

PRODUCT_RANKING_BY_CATEGORY = """
WITH product_revenue AS (
    SELECT
        p.category,
        p.product_id,
        p.product_name,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS total_revenue

    FROM products AS p

    INNER JOIN order_items AS oi
        ON p.product_id = oi.product_id

    INNER JOIN orders AS o
        ON oi.order_id = o.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY
        p.category,
        p.product_id,
        p.product_name
)

SELECT
    category,
    product_id,
    product_name,
    total_revenue,

    DENSE_RANK() OVER (
        PARTITION BY category
        ORDER BY total_revenue DESC
    ) AS rank_in_category

FROM product_revenue

ORDER BY
    category,
    rank_in_category,
    product_name;
"""


# --------------------------------------------------
# Query 9: Customer Order Gap Analysis
# --------------------------------------------------

CUSTOMER_ORDER_GAP_ANALYSIS = """
WITH customer_order_history AS (
    SELECT
        customer_id,
        order_id,
        DATE(order_date) AS order_date,

        LAG(DATE(order_date)) OVER (
            PARTITION BY customer_id
            ORDER BY DATE(order_date), order_id
        ) AS previous_order_date

    FROM orders

    WHERE customer_id IS NOT NULL
      AND customer_id != 'C_UNKNOWN'
),

order_gaps AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        previous_order_date,

        CASE
            WHEN previous_order_date IS NULL
                THEN NULL
            ELSE CAST(
                JULIANDAY(order_date)
                - JULIANDAY(previous_order_date)
                AS INTEGER
            )
        END AS days_gap

    FROM customer_order_history
),

customer_average_gap AS (
    SELECT
        customer_id,
        ROUND(AVG(days_gap), 2) AS average_gap

    FROM order_gaps

    WHERE days_gap IS NOT NULL

    GROUP BY customer_id
)

SELECT
    og.customer_id,
    og.order_date,
    og.previous_order_date,
    og.days_gap,
    cag.average_gap,

    CASE
        WHEN cag.average_gap > 30
            THEN 'At Risk'
        ELSE 'Active'
    END AS customer_risk

FROM order_gaps AS og

LEFT JOIN customer_average_gap AS cag
    ON og.customer_id = cag.customer_id

ORDER BY
    og.customer_id,
    og.order_date;
"""


# --------------------------------------------------
# Execute Query and Export CSV
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
                f"\nShowing first {preview_rows} of "
                f"{len(result_df)} records."
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
            RUNNING_REVENUE_PER_REGION,
            "07_running_revenue_per_region.csv",
            "QUERY 7: RUNNING REVENUE TOTAL PER REGION"
        )

        execute_query(
            connection,
            PRODUCT_RANKING_BY_CATEGORY,
            "08_product_ranking_by_category.csv",
            "QUERY 8: PRODUCT RANKING WITH DENSE_RANK"
        )

        execute_query(
            connection,
            CUSTOMER_ORDER_GAP_ANALYSIS,
            "09_customer_order_gap_analysis.csv",
            "QUERY 9: CUSTOMER ORDER GAP AND RISK ANALYSIS"
        )

        print("\n" + "=" * 80)
        print("ADVANCED SQL PART 1 COMPLETED SUCCESSFULLY")
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