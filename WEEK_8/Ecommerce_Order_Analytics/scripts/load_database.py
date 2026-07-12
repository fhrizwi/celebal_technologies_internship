import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

CLEAN_DIR = ROOT_DIR / "cleaned_data"

DATABASE_DIR = ROOT_DIR / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "ecommerce.db"


# --------------------------------------------------
# Required Input Files
# --------------------------------------------------

REQUIRED_FILES = {
    "customers": CLEAN_DIR / "customers.csv",
    "products": CLEAN_DIR / "products.csv",
    "orders": CLEAN_DIR / "orders.csv",
    "order_items": CLEAN_DIR / "order_items.csv",
}


# --------------------------------------------------
# Validate Cleaned CSV Files
# --------------------------------------------------

def validate_input_files():

    print("\n" + "=" * 60)
    print("Checking Cleaned CSV Files")
    print("=" * 60)

    missing_files = []

    for table_name, file_path in REQUIRED_FILES.items():

        if file_path.exists():
            print(f"✔ {table_name}: {file_path.name}")
        else:
            print(f"✘ Missing: {file_path.name}")
            missing_files.append(file_path.name)

    if missing_files:

        raise FileNotFoundError(
            "Missing cleaned CSV files: "
            + ", ".join(missing_files)
            + ". Run clean_data.py first."
        )


# --------------------------------------------------
# Load Cleaned CSV Files
# --------------------------------------------------

def load_cleaned_data():

    print("\n" + "=" * 60)
    print("Loading Cleaned CSV Files")
    print("=" * 60)

    customers = pd.read_csv(REQUIRED_FILES["customers"])

    products = pd.read_csv(REQUIRED_FILES["products"])

    orders = pd.read_csv(REQUIRED_FILES["orders"])

    order_items = pd.read_csv(REQUIRED_FILES["order_items"])

    print(f"✔ Customers loaded: {len(customers)} rows")
    print(f"✔ Products loaded: {len(products)} rows")
    print(f"✔ Orders loaded: {len(orders)} rows")
    print(f"✔ Order items loaded: {len(order_items)} rows")

    return customers, products, orders, order_items


# --------------------------------------------------
# Create Database Connection
# --------------------------------------------------

def create_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.execute("PRAGMA foreign_keys = ON;")

    print("\n" + "=" * 60)
    print("SQLite Database Connection")
    print("=" * 60)

    print(f"✔ Connected to database: {DB_PATH}")

    return connection


# --------------------------------------------------
# Prepare Data Before Database Loading
# --------------------------------------------------

def prepare_data(customers, products, orders, order_items):

    print("\n" + "=" * 60)
    print("Preparing Data for SQLite")
    print("=" * 60)

    # SQLite stores Boolean values as 0 and 1.
    if "email_valid" in customers.columns:

        customers["email_valid"] = (
            customers["email_valid"]
            .astype(str)
            .str.lower()
            .map({"true": 1, "false": 0})
            .fillna(0)
            .astype(int)
        )

    # Store dates as standard text values.
    customers["registration_date"] = (
        pd.to_datetime(
            customers["registration_date"],
            errors="coerce"
        )
        .dt.strftime("%Y-%m-%d")
    )

    orders["order_date"] = (
        pd.to_datetime(
            orders["order_date"],
            errors="coerce"
        )
        .dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    print("✔ Data prepared successfully")

    return customers, products, orders, order_items


# --------------------------------------------------
# Create Database Tables
# --------------------------------------------------

def create_tables(connection):

    print("\n" + "=" * 60)
    print("Creating Database Tables")
    print("=" * 60)

    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS order_items;")
    cursor.execute("DROP TABLE IF EXISTS orders;")
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS customers;")

    cursor.execute(
        """
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT,
            registration_date TEXT,
            customer_type TEXT
                CHECK (
                    customer_type IN (
                        'REGULAR',
                        'PREMIUM',
                        'VIP'
                    )
                ),
            email_valid INTEGER DEFAULT 0
                CHECK (email_valid IN (0, 1))
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            cost_price REAL NOT NULL
                CHECK (cost_price >= 0)
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK (
                    status IN (
                        'PLACED',
                        'SHIPPED',
                        'DELIVERED',
                        'CANCELLED',
                        'RETURNED'
                    )
                ),
            region_code TEXT,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE order_items (
            item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL
                CHECK (unit_price >= 0),
            discount_percent REAL NOT NULL
                CHECK (
                    discount_percent >= 0
                    AND discount_percent <= 100
                ),
            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),
            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        );
        """
    )

    connection.commit()

    print("✔ customers table created")
    print("✔ products table created")
    print("✔ orders table created")
    print("✔ order_items table created")


# --------------------------------------------------
# Insert Data into Database
# --------------------------------------------------

def insert_data(
    connection,
    customers,
    products,
    orders,
    order_items
):

    print("\n" + "=" * 60)
    print("Inserting Data into SQLite")
    print("=" * 60)

    customers.to_sql(
        "customers",
        connection,
        if_exists="append",
        index=False
    )

    products.to_sql(
        "products",
        connection,
        if_exists="append",
        index=False
    )

    orders.to_sql(
        "orders",
        connection,
        if_exists="append",
        index=False
    )

    order_items.to_sql(
        "order_items",
        connection,
        if_exists="append",
        index=False
    )

    connection.commit()

    print("✔ Customer data inserted")
    print("✔ Product data inserted")
    print("✔ Order data inserted")
    print("✔ Order item data inserted")


# --------------------------------------------------
# Create Helpful Indexes
# --------------------------------------------------

def create_indexes(connection):

    print("\n" + "=" * 60)
    print("Creating Database Indexes")
    print("=" * 60)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_orders_customer_id
        ON orders(customer_id);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_orders_order_date
        ON orders(order_date);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_orders_status
        ON orders(status);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_order_items_order_id
        ON order_items(order_id);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_order_items_product_id
        ON order_items(product_id);
        """
    )

    connection.commit()

    print("✔ Database indexes created")


# --------------------------------------------------
# Verify Database Tables and Records
# --------------------------------------------------

def verify_database(connection):

    print("\n" + "=" * 60)
    print("Database Verification")
    print("=" * 60)

    cursor = connection.cursor()

    table_names = [
        "customers",
        "products",
        "orders",
        "order_items"
    ]

    for table_name in table_names:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name};"
        )

        row_count = cursor.fetchone()[0]

        print(f"✔ {table_name}: {row_count} rows")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL;
        """
    )

    invalid_order_references = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL;
        """
    )

    invalid_product_references = cursor.fetchone()[0]

    print(
        "✔ Invalid order references:",
        invalid_order_references
    )

    print(
        "✔ Invalid product references:",
        invalid_product_references
    )


# --------------------------------------------------
# Main Function
# --------------------------------------------------

def main():

    connection = None

    try:

        validate_input_files()

        customers, products, orders, order_items = (
            load_cleaned_data()
        )

        customers, products, orders, order_items = (
            prepare_data(
                customers,
                products,
                orders,
                order_items
            )
        )

        connection = create_connection()

        create_tables(connection)

        insert_data(
            connection,
            customers,
            products,
            orders,
            order_items
        )

        create_indexes(connection)

        verify_database(connection)

        print("\n" + "=" * 60)
        print("DATABASE LOADING COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(f"\nDatabase file: {DB_PATH}")

    except Exception as error:

        print("\n✘ Database loading failed")
        print(f"Error: {error}")

        raise

    finally:

        if connection is not None:

            connection.close()

            print("\n✔ Database connection closed")


if __name__ == "__main__":
    main()