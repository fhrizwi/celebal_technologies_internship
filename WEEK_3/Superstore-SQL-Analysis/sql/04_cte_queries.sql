-- Query 1: Total Sales Per Customer

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
ORDER BY Total_Sales DESC;

-- Query 2: Customers Above Average Total Sales

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
WHERE Total_Sales >
(
    SELECT AVG(Total_Sales)
    FROM customer_sales
);