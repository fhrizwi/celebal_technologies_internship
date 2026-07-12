-- ============================================================
-- E-COMMERCE ORDER ANALYTICS SYSTEM
-- INTERMEDIATE SQL QUERIES
-- ============================================================


-- ============================================================
-- QUERY 4:
-- Customers who placed orders but never had any delivered order
-- ============================================================

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


-- ============================================================
-- QUERY 5:
-- Products ordered but having more returns than purchases
--
-- Negative quantity = returned items
-- Positive quantity = purchased items
-- ============================================================

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


-- ============================================================
-- QUERY 6:
-- Return Rate per Category
--
-- Return Rate =
-- returned quantity / total absolute quantity * 100
-- ============================================================

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