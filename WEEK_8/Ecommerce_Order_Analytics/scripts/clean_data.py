from pathlib import Path
import pandas as pd
import re
from datetime import datetime

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


# -----------------------------
# Check Referential Integrity
# -----------------------------

def check_referential_integrity(orders, products, order_items):

    print("\n" + "=" * 60)
    print("Checking Referential Integrity")
    print("=" * 60)

    valid_order_ids = set(orders["order_id"])

    valid_product_ids = set(products["product_id"])

    invalid_records = order_items[
        (~order_items["order_id"].isin(valid_order_ids)) |
        (~order_items["product_id"].isin(valid_product_ids))
    ]

    issues.append(
        f"Invalid Referential Records : {len(invalid_records)}"
    )

    print(f"✔ Invalid Records Found : {len(invalid_records)}")

    if len(invalid_records) > 0:

        invalid_records.to_csv(
            REPORT_DIR / "invalid_references.csv",
            index=False
        )

        print("Invalid records saved.")

    return order_items, invalid_records


# -----------------------------
# Clean Order Items
# -----------------------------

def clean_order_items(order_items):

    print("\n" + "=" * 60)
    print("Cleaning Order Items")
    print("=" * 60)

    # Remove duplicate rows
    before = len(order_items)

    order_items = order_items.drop_duplicates()

    duplicates = before - len(order_items)

    issues.append(
        f"Duplicate Order Items Removed : {duplicates}"
    )

    # Quantity should not be zero
    zero_quantity = (order_items["quantity"] == 0).sum()

    issues.append(
        f"Zero Quantity Records : {zero_quantity}"
    )

    # Discount should be between 0 and 100
    invalid_discount = (
        (order_items["discount_percent"] < 0) |
        (order_items["discount_percent"] > 100)
    ).sum()

    issues.append(
        f"Invalid Discount Records : {invalid_discount}"
    )

    order_items.to_csv(
        CLEAN_DIR / "order_items.csv",
        index=False
    )

    print("✔ Order Items Cleaned Successfully")

    return order_items


# -----------------------------
# Save Issue Report
# -----------------------------

def save_issue_report():

    print("\n" + "=" * 60)
    print("Saving Issue Report")
    print("=" * 60)

    report_path = REPORT_DIR / "issues_report.txt"

    try:
        with open(report_path, "w", encoding="utf-8") as file:

            file.write("=" * 50 + "\n")
            file.write("DATA CLEANING REPORT\n")
            file.write("=" * 50 + "\n\n")
            file.write(f"Generated: {datetime.utcnow().isoformat()}Z\n\n")

            if not issues:
                file.write("No issues found.\n")
            else:
                for issue in issues:
                    file.write(issue + "\n")

            file.write("\nCleaning completed successfully.\n")

        print(f"\n✔ issues_report.txt generated: {report_path}")
        return report_path

    except Exception as e:
        print(f"Failed to write issue report: {e}")
        return None

customers, products, orders, order_items = load_data()

orders = clean_orders(orders)

products = clean_products(products)

customers, invalid_customers = validate_emails(customers)

order_items, invalid_records = check_referential_integrity(
    orders,
    products,
    order_items
)

order_items = clean_order_items(order_items)

save_issue_report()