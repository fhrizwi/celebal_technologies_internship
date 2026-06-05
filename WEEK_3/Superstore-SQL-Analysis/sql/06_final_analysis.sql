-- Top 10 Customers

WITH customer_sales AS
(
    SELECT
        Customer_ID,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY Customer_ID
)

SELECT *
FROM customer_sales
ORDER BY Total_Sales DESC
LIMIT 10;

-- Bottom 10 Customers

WITH customer_sales AS
(
    SELECT
        Customer_ID,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY Customer_ID
)

SELECT *
FROM customer_sales
ORDER BY Total_Sales ASC
LIMIT 10;

-- Single Order Customers

SELECT
    Customer_ID,
    COUNT(DISTINCT Order_ID) AS Total_Orders
FROM orders
GROUP BY Customer_ID
HAVING COUNT(DISTINCT Order_ID) = 1;

-- Final Analysis Query

WITH customer_sales AS
(
    SELECT
        c.Customer_ID,
        c.Customer_Name,
        SUM(o.Sales) AS Total_Sales

    FROM customers c
    JOIN orders o
        ON c.Customer_ID = o.Customer_ID

    GROUP BY
        c.Customer_ID,
        c.Customer_Name
)

SELECT
    Customer_ID,
    Customer_Name,
    Total_Sales,

    RANK()
    OVER(
        ORDER BY Total_Sales DESC
    ) AS Customer_Rank

FROM customer_sales;