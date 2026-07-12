-- ============================================================
-- E-COMMERCE ORDER ANALYTICS SYSTEM
-- ADVANCED SQL QUERIES - PART 1
-- Queries 7, 8 and 9
-- ============================================================


-- ============================================================
-- QUERY 7: Running Total of Revenue per Region
--
-- Output:
-- region_code
-- order_date
-- daily_revenue
-- running_total
-- ============================================================

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


-- ============================================================
-- QUERY 8: Rank Products by Revenue within Each Category
--
-- Products having same revenue receive same rank.
-- DENSE_RANK does not leave gaps in ranking.
-- ============================================================

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


-- ============================================================
-- QUERY 9: Days between Consecutive Customer Orders
--
-- Output:
-- customer_id
-- order_date
-- previous_order_date
-- days_gap
-- average_gap
-- customer_risk
-- ============================================================

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