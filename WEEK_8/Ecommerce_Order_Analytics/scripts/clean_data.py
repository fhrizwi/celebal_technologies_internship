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


# --------------------------------------------------
# Validate Emails
# --------------------------------------------------

def validate_emails(customers_df):

    print("\nValidating Emails...")

    invalid_customers = []

    for index, row in customers_df.iterrows():

        email = str(row["email"]).strip()

        valid = True

        # Basic validation
        if "@" not in email:
            valid = False

        elif email.count("@") != 1:
            valid = False

        else:

            username, domain = email.split("@")

            if username == "":
                valid = False

            elif "." not in domain:
                valid = False

        if not valid:

            invalid_customers.append(row["customer_id"])

    issues.append(
        f"Invalid Emails Found : {len(invalid_customers)}"
    )

    print(f"Invalid Emails : {len(invalid_customers)}")
    
    
    customers_df.to_csv(
    CLEAN_DIR / "customers.csv",
    index=False
)

    return invalid_customers


# --------------------------------------------------
# Check Referential Integrity
# --------------------------------------------------

def check_referential_integrity(orders_df, order_items_df):

    print("\nChecking Referential Integrity...")

    valid_orders = set(orders_df["order_id"])

    invalid_records = order_items_df[
        ~order_items_df["order_id"].isin(valid_orders)
    ]

    issues.append(
        f"Invalid Order References : {len(invalid_records)}"
    )

    print(f"Invalid Order References : {len(invalid_records)}")

    if len(invalid_records) > 0:

        invalid_records.to_csv(
            CLEAN_DIR / "invalid_order_references.csv",
            index=False
        )

    return invalid_records

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



# --------------------------------------------------
# Save Issue Report
# --------------------------------------------------

def save_issue_report():

    report_path = CLEAN_DIR / "issues_report.txt"

    with open(report_path, "w") as file:

        file.write("=" * 40 + "\n")

        file.write("DATA CLEANING REPORT\n")

        file.write("=" * 40 + "\n\n")

        for issue in issues:

            file.write(issue + "\n")

    print("\nissues_report.txt generated")
    
    
    


customers, products, orders, order_items = load_data()

orders = clean_orders(orders)

products = clean_products(products)

invalid_emails = validate_emails(customers)




print("\nInvalid Customer IDs")

print(invalid_emails)



invalid_orders = check_referential_integrity(
    orders,
    order_items
)


save_issue_report()
