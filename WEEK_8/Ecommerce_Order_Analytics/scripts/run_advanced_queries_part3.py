import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = ROOT_DIR / "database" / "ecommerce.db"

REPORTS_DIR = ROOT_DIR / "reports"

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Query 13:
# First and Most Recent Purchased Category
# --------------------------------------------------

FIRST_AND_RECENT_CATEGORY = """
WITH customer_purchases AS (
    SELECT
        o.customer_id,
        o.order_id,
        DATE(o.order_date) AS order_date,
        p.category,

        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY
                DATETIME(o.order_date),
                o.order_id,
                oi.item_id
        ) AS first_purchase_rank,

        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY
                DATETIME(o.order_date) DESC,
                o.order_id DESC,
                oi.item_id DESC
        ) AS recent_purchase_rank

    FROM orders AS o

    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id

    INNER JOIN products AS p
        ON oi.product_id = p.product_id

    WHERE o.customer_id IS NOT NULL
      AND o.customer_id != 'C_UNKNOWN'
      AND o.status != 'CANCELLED'
      AND oi.quantity > 0
),

customer_categories AS (
    SELECT
        customer_id,

        MAX(
            CASE
                WHEN first_purchase_rank = 1
                THEN category
            END
        ) AS first_category,

        MAX(
            CASE
                WHEN recent_purchase_rank = 1
                THEN category
            END
        ) AS recent_category

    FROM customer_purchases

    GROUP BY customer_id
)

SELECT
    cc.customer_id,
    c.customer_name,
    cc.first_category,
    cc.recent_category,

    CASE
        WHEN cc.first_category != cc.recent_category
            THEN 'Yes'
        ELSE 'No'
    END AS category_shift

FROM customer_categories AS cc

INNER JOIN customers AS c
    ON cc.customer_id = c.customer_id

ORDER BY cc.customer_id;
"""


# --------------------------------------------------
# Query 14:
# Cumulative Customer Revenue Distribution
# --------------------------------------------------

CUMULATIVE_REVENUE_DISTRIBUTION = """
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.customer_name,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS revenue

    FROM customers AS c

    INNER JOIN orders AS o
        ON c.customer_id = o.customer_id

    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE c.customer_id != 'C_UNKNOWN'
      AND o.status != 'CANCELLED'

    GROUP BY
        c.customer_id,
        c.customer_name
),

customer_distribution AS (
    SELECT
        customer_id,
        customer_name,
        revenue,

        ROUND(
            SUM(revenue) OVER (
                ORDER BY revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING
                AND CURRENT ROW
            ),
            2
        ) AS cumulative_revenue,

        SUM(revenue) OVER () AS total_revenue

    FROM customer_revenue
)

SELECT
    customer_id,
    customer_name,
    revenue,
    cumulative_revenue,

    ROUND(
        cumulative_revenue
        * 100.0
        / NULLIF(total_revenue, 0),
        2
    ) AS cumulative_percent

FROM customer_distribution

ORDER BY revenue DESC;
"""


# --------------------------------------------------
# Query 15:
# Cohort Retention Analysis
# --------------------------------------------------

COHORT_RETENTION_ANALYSIS = """
WITH customer_cohorts AS (
    SELECT
        customer_id,
        STRFTIME(
            '%Y-%m-01',
            registration_date
        ) AS cohort_month

    FROM customers

    WHERE customer_id != 'C_UNKNOWN'
      AND registration_date IS NOT NULL
),

customer_order_months AS (
    SELECT DISTINCT
        customer_id,

        STRFTIME(
            '%Y-%m-01',
            order_date
        ) AS order_month

    FROM orders

    WHERE customer_id IS NOT NULL
      AND customer_id != 'C_UNKNOWN'
),

cohort_activity AS (
    SELECT
        cc.customer_id,
        cc.cohort_month,
        com.order_month,

        (
            (
                CAST(
                    STRFTIME('%Y', com.order_month)
                    AS INTEGER
                )
                -
                CAST(
                    STRFTIME('%Y', cc.cohort_month)
                    AS INTEGER
                )
            ) * 12
            +
            (
                CAST(
                    STRFTIME('%m', com.order_month)
                    AS INTEGER
                )
                -
                CAST(
                    STRFTIME('%m', cc.cohort_month)
                    AS INTEGER
                )
            )
        ) AS month_number

    FROM customer_cohorts AS cc

    INNER JOIN customer_order_months AS com
        ON cc.customer_id = com.customer_id

    WHERE DATE(com.order_month)
        >= DATE(cc.cohort_month)
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size

    FROM customer_cohorts

    GROUP BY cohort_month
),

cohort_retention AS (
    SELECT
        cohort_month,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 0
                THEN customer_id
            END
        ) AS month_0_customers,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 1
                THEN customer_id
            END
        ) AS month_1_customers,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 2
                THEN customer_id
            END
        ) AS month_2_customers,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 3
                THEN customer_id
            END
        ) AS month_3_customers

    FROM cohort_activity

    GROUP BY cohort_month
)

SELECT
    cs.cohort_month,
    cs.cohort_size,

    COALESCE(
        cr.month_0_customers,
        0
    ) AS month_0_customers,

    COALESCE(
        cr.month_1_customers,
        0
    ) AS month_1_customers,

    COALESCE(
        cr.month_2_customers,
        0
    ) AS month_2_customers,

    COALESCE(
        cr.month_3_customers,
        0
    ) AS month_3_customers,

    ROUND(
        COALESCE(cr.month_0_customers, 0)
        * 100.0
        / NULLIF(cs.cohort_size, 0),
        2
    ) AS month_0_retention_percent,

    ROUND(
        COALESCE(cr.month_1_customers, 0)
        * 100.0
        / NULLIF(cs.cohort_size, 0),
        2
    ) AS month_1_retention_percent,

    ROUND(
        COALESCE(cr.month_2_customers, 0)
        * 100.0
        / NULLIF(cs.cohort_size, 0),
        2
    ) AS month_2_retention_percent,

    ROUND(
        COALESCE(cr.month_3_customers, 0)
        * 100.0
        / NULLIF(cs.cohort_size, 0),
        2
    ) AS month_3_retention_percent

FROM cohort_sizes AS cs

LEFT JOIN cohort_retention AS cr
    ON cs.cohort_month = cr.cohort_month

ORDER BY cs.cohort_month;
"""


# --------------------------------------------------
# Query 16:
# Frequently Bought Together Products
# --------------------------------------------------

FREQUENTLY_BOUGHT_TOGETHER = """
WITH valid_order_products AS (
    SELECT DISTINCT
        oi.order_id,
        oi.product_id

    FROM order_items AS oi

    INNER JOIN orders AS o
        ON oi.order_id = o.order_id

    WHERE o.status != 'CANCELLED'
      AND oi.quantity > 0
),

product_pairs AS (
    SELECT
        first_item.order_id,
        first_item.product_id AS product_a_id,
        second_item.product_id AS product_b_id

    FROM valid_order_products AS first_item

    INNER JOIN valid_order_products AS second_item
        ON first_item.order_id
            = second_item.order_id

        AND first_item.product_id
            < second_item.product_id
)

SELECT
    product_a.product_name AS product_a,
    product_b.product_name AS product_b,
    COUNT(*) AS times_bought_together

FROM product_pairs AS pp

INNER JOIN products AS product_a
    ON pp.product_a_id = product_a.product_id

INNER JOIN products AS product_b
    ON pp.product_b_id = product_b.product_id

GROUP BY
    pp.product_a_id,
    pp.product_b_id,
    product_a.product_name,
    product_b.product_name

ORDER BY
    times_bought_together DESC,
    product_a,
    product_b

LIMIT 50;
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

    print("\n" + "=" * 85)
    print(heading)
    print("=" * 85)

    result_df = pd.read_sql_query(
        query,
        connection
    )

    if result_df.empty:

        print("No matching records found.")

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
            FIRST_AND_RECENT_CATEGORY,
            "13_first_and_recent_category.csv",
            "QUERY 13: FIRST AND MOST RECENT PURCHASED CATEGORY"
        )

        execute_query(
            connection,
            CUMULATIVE_REVENUE_DISTRIBUTION,
            "14_cumulative_revenue_distribution.csv",
            "QUERY 14: CUMULATIVE CUSTOMER REVENUE DISTRIBUTION"
        )

        execute_query(
            connection,
            COHORT_RETENTION_ANALYSIS,
            "15_cohort_retention_analysis.csv",
            "QUERY 15: CUSTOMER COHORT RETENTION ANALYSIS"
        )

        execute_query(
            connection,
            FREQUENTLY_BOUGHT_TOGETHER,
            "16_frequently_bought_together.csv",
            "QUERY 16: PRODUCTS FREQUENTLY BOUGHT TOGETHER"
        )

        print("\n" + "=" * 85)
        print("ADVANCED SQL PART 3 COMPLETED SUCCESSFULLY")
        print("=" * 85)

    except sqlite3.Error as error:

        print(f"\nSQLite Error: {error}")

        raise

    finally:

        if connection is not None:

            connection.close()

            print("\n✔ Database connection closed")


if __name__ == "__main__":
    main()