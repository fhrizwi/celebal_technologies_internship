-- ============================================================
-- E-COMMERCE ORDER ANALYTICS SYSTEM
-- ADVANCED SQL QUERIES - PART 2
-- Queries 10, 11 and 12
-- ============================================================


-- ============================================================
-- QUERY 10: Multi-Level CTE
--
-- Step 1: Calculate monthly revenue per customer
-- Step 2: Categorize customer revenue
-- Step 3: Count customers in each category per month
--
-- Revenue Categories:
-- High   : Revenue > 10000
-- Medium : Revenue between 5000 and 10000
-- Low    : Revenue < 5000
-- ============================================================

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


-- ============================================================
-- QUERY 11: Customer Lifetime Value Segmentation with NTILE
--
-- Divide customers into four quartiles:
-- Quartile 1 = Platinum
-- Quartile 2 = Gold
-- Quartile 3 = Silver
-- Quartile 4 = Bronze
-- ============================================================

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


-- ============================================================
-- QUERY 12: Year-over-Year Revenue Comparison
--
-- Compare monthly revenue with the same month in previous year.
-- If previous-year data does not exist:
-- prev_year_revenue will be NULL
-- yoy_growth_percent will be NULL
-- ============================================================

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