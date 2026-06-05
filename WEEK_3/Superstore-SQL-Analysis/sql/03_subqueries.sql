-- Query 1: Orders Above Average Sales

SELECT *
FROM orders
WHERE Sales >
(
    SELECT AVG(Sales)
    FROM orders
);

-- Query 2: Highest Order Per Customer

SELECT *
FROM orders o
WHERE Sales =
(
    SELECT MAX(Sales)
    FROM orders
    WHERE Customer_ID = o.Customer_ID
);