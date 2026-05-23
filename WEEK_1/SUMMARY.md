# Week 1 - Data Exploration and Cleaning Summary

## Objective
Learn Python basics and perform data exploration and cleaning using Pandas.

## Dataset
- Input: data/Combined_dataset.csv (1000 Myntra product records, 24 columns)
- Output: data/cleaned_dataset.csv (1000 rows, 27 columns including price, quantity, total_amount)

## Steps Performed
1. Load - Read CSV into a Pandas DataFrame
2. Explore - head(), tail(), shape, columns, dtypes, describe()
3. Missing values - Filled discount (0), rating (median), seller_name and what_customers_said (defaults)
4. Basic ops - Selected key columns; filtered backpacks with rating >= 4.5 and initial_price > 2000
5. Duplicates - Checked and removed duplicate product_id rows (none found in this dataset)
6. Derived column - price = initial_price, quantity = ratings_count, total_amount = price * quantity
7. Save - Exported to cleaned_dataset.csv

## Files
- notebook/data_cleaning.ipynb
- data/Combined_dataset.csv
- data/cleaned_dataset.csv
