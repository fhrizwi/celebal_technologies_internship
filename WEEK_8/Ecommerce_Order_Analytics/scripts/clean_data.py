from pathlib import Path
import pandas as pd
import re

# -----------------------------
# Paths
# -----------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

CLEAN_DIR = ROOT_DIR / "cleaned_data"

REPORT_DIR = ROOT_DIR / "reports"

CLEAN_DIR.mkdir(exist_ok=True)

REPORT_DIR.mkdir(exist_ok=True)

issues = []



# -----------------------------
# Load Data
# -----------------------------

def load_data():

    customers = pd.read_csv(DATA_DIR / "customers.csv")

    products = pd.read_csv(DATA_DIR / "products.csv")

    orders = pd.read_csv(DATA_DIR / "orders.csv")

    order_items = pd.read_csv(DATA_DIR / "order_items.csv")

    return customers, products, orders, order_items


# -----------------------------
# Clean Orders
# -----------------------------

def clean_orders(orders):

    print("\n" + "=" * 60)
    print("Cleaning Orders")
    print("=" * 60)
    
    
# -----------------------------
# Clean Products
# -----------------------------

def clean_products(products):

    print("\n" + "=" * 60)
    print("Cleaning Products")
    print("=" * 60)

    cleaned_names = []
    fixed_names = 0

    for name in products["product_name"]:

        original = str(name)

        # Remove extra spaces
        cleaned = " ".join(original.split())

        # Convert to Title Case
        cleaned = cleaned.title()

        if original != cleaned:
            fixed_names += 1

        cleaned_names.append(cleaned)

    products["product_name"] = cleaned_names

    # Remove duplicate products
    before = len(products)

    products = products.drop_duplicates()

    after = len(products)

    duplicate_products = before - after

    issues.append(f"Product Names Fixed : {fixed_names}")
    issues.append(f"Duplicate Products Removed : {duplicate_products}")

    products.to_csv(
        CLEAN_DIR / "products.csv",
        index=False
    )

    print("✔ Products Cleaned Successfully")

    return products

    # ---------------------------------
    # 1. Handle Missing Customer IDs
    # ---------------------------------

    missing_customer = orders["customer_id"].isna().sum()

    issues.append(f"Missing Customer IDs : {missing_customer}")

    orders["customer_id"] = orders["customer_id"].fillna("UNKNOWN")

    # ---------------------------------
    # 2. Fix Date Formats
    # ---------------------------------

    wrong_dates = 0
    converted_dates = []

    for value in orders["order_date"]:

        parsed = None

        # YYYY-MM-DD HH:MM:SS
        try:
            parsed = pd.to_datetime(
                value,
                format="%Y-%m-%d %H:%M:%S"
            )

        except:
            pass

        # DD-MM-YYYY HH:MM:SS
        if parsed is None:

            try:

                parsed = pd.to_datetime(
                    value,
                    format="%d-%m-%Y %H:%M:%S"
                )

                wrong_dates += 1

            except:

                parsed = pd.NaT

        converted_dates.append(parsed)

    orders["order_date"] = converted_dates

    issues.append(f"Wrong Date Formats Fixed : {wrong_dates}")

    # ---------------------------------
    # 3. Remove Duplicate Orders
    # ---------------------------------

    before = len(orders)

    orders = orders.drop_duplicates()

    after = len(orders)

    duplicates_removed = before - after

    issues.append(
        f"Duplicate Orders Removed : {duplicates_removed}"
    )

    # ---------------------------------
    # 4. Sort Orders
    # ---------------------------------

    orders = orders.sort_values(
        by="order_date"
    )

    # ---------------------------------
    # 5. Save
    # ---------------------------------

    orders.to_csv(
        CLEAN_DIR / "orders.csv",
        index=False
    )

    print("✔ Orders Cleaned Successfully")

    return orders


# -----------------------------
# Validate Emails
# -----------------------------

def validate_emails(customers):

    print("\n" + "=" * 60)
    print("Validating Customer Emails")
    print("=" * 60)

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    invalid_customers = []

    valid_email = []

    for _, row in customers.iterrows():

        email = str(row["email"]).strip()

        if re.match(email_pattern, email):

            valid_email.append(True)

        else:

            valid_email.append(False)

            invalid_customers.append(row["customer_id"])

    customers["email_valid"] = valid_email

    issues.append(
        f"Invalid Emails : {len(invalid_customers)}"
    )

    customers.to_csv(
        CLEAN_DIR / "customers.csv",
        index=False
    )

    print(f"✔ Invalid Emails Found : {len(invalid_customers)}")

    return customers, invalid_customers


customers, products, orders, order_items = load_data()

orders = clean_orders(orders)

products = clean_products(products)

customers, invalid_customers = validate_emails(customers)


print("\nInvalid Customer IDs")

for customer in invalid_customers:

    print(customer)