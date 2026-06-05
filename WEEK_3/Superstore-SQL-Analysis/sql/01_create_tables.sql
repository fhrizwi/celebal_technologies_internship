USE superstore_db;

CREATE TABLE customers AS
SELECT DISTINCT
    `Customer ID` AS Customer_ID,
    `Customer Name` AS Customer_Name,
    Segment
FROM superstore_raw;

CREATE TABLE products AS
SELECT DISTINCT
    `Product ID` AS Product_ID,
    `Product Name` AS Product_Name,
    Category,
    `Sub-Category` AS Sub_Category
FROM superstore_raw;

CREATE TABLE orders AS
SELECT
    `Row ID` AS Row_ID,
    `Order ID` AS Order_ID,
    `Order Date` AS Order_Date,
    `Ship Date` AS Ship_Date,
    `Ship Mode` AS Ship_Mode,
    `Customer ID` AS Customer_ID,
    `Product ID` AS Product_ID,
    Sales,
    Quantity,
    Discount,
    Profit
FROM superstore_raw;