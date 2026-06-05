-- ROW_NUMBER()

SELECT
    Customer_ID,
    Sales,

    ROW_NUMBER()
    OVER(
        PARTITION BY Customer_ID
        ORDER BY Sales DESC
    ) AS Row_Num

FROM orders;

-- RANK()

SELECT
    Customer_ID,
    SUM(Sales) AS Total_Sales,

    RANK()
    OVER(
        ORDER BY SUM(Sales) DESC
    ) AS Customer_Rank

FROM orders
GROUP BY Customer_ID;

-- DENSE_RANK()

SELECT
    Customer_ID,
    SUM(Sales) AS Total_Sales,

    DENSE_RANK()
    OVER(
        ORDER BY SUM(Sales) DESC
    ) AS Dense_Rank

FROM orders
GROUP BY Customer_ID;