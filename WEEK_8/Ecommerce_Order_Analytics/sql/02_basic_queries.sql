-- ============================================================
-- E-COMMERCE ORDER ANALYTICS SYSTEM
-- BASIC SQL QUERIES
-- ============================================================


-- ============================================================
-- QUERY 1: Total Revenue per Category
--
-- Revenue Formula:
-- quantity * unit_price * (1 - discount_percent / 100)
-- ============================================================

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


-- ============================================================
-- QUERY 2: Top 10 Customers by Total Order Value
-- ============================================================

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


-- ============================================================
-- QUERY 3: Month-wise Order Count for Last 12 Months
-- ============================================================

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