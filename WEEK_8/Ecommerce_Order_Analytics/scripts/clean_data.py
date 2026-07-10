from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

CLEAN_DIR = ROOT_DIR / "cleaned_data"

CLEAN_DIR.mkdir(exist_ok=True)

def load_data():

    customers = pd.read_csv(DATA_DIR / "customers.csv")

    products = pd.read_csv(DATA_DIR / "products.csv")

    orders = pd.read_csv(DATA_DIR / "orders.csv")

    order_items = pd.read_csv(DATA_DIR / "order_items.csv")

    return customers, products, orders, order_items


issues = []

# --------------------------------------------------
# Clean Orders
# --------------------------------------------------

def clean_orders(orders_df):

    print("\nCleaning Orders...")
    
    
# --------------------------------------------------
# Clean Products
# --------------------------------------------------

def clean_products(products_df):

    print("\nCleaning Products...")

    fixed_names = 0

    cleaned_names = []

    for name in products_df["product_name"]:

        original = str(name)

        cleaned = original.strip().title()

        if original != cleaned:
            fixed_names += 1

        cleaned_names.append(cleaned)

    products_df["product_name"] = cleaned_names

    issues.append(f"Product Names Fixed : {fixed_names}")

    products_df.to_csv(
        CLEAN_DIR / "products.csv",
        index=False
    )

    print("products.csv cleaned")

    return products_df

    # ----------------------------
    # Handle NULL customer_id
    # ----------------------------

    null_count = orders_df["customer_id"].isnull().sum()

    issues.append(f"NULL customer_id found : {null_count}")

    orders_df["customer_id"] = orders_df["customer_id"].fillna("UNKNOWN")

    # ----------------------------
    # Fix Date Format
    # ----------------------------

    fixed_dates = 0

    cleaned_dates = []

    for value in orders_df["order_date"]:

        try:
            dt = pd.to_datetime(
                value,
                format="%Y-%m-%d %H:%M:%S"
            )

        except:

            try:

                dt = pd.to_datetime(
                    value,
                    format="%d-%m-%Y %H:%M:%S"
                )

                fixed_dates += 1

            except:

                dt = pd.NaT

        cleaned_dates.append(dt)

    orders_df["order_date"] = cleaned_dates

    issues.append(f"Wrong Date Formats Fixed : {fixed_dates}")

    orders_df.to_csv(

        CLEAN_DIR / "orders.csv",

        index=False

    )

    print("orders.csv cleaned")

    return orders_df


customers, products, orders, order_items = load_data()

orders = clean_orders(orders)

products = clean_products(products)

