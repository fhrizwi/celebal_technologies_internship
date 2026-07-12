import sqlite3
from pathlib import Path
import pandas as pd


# -----------------------------
# Project Paths
# -----------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

CLEAN_DIR = ROOT_DIR / "cleaned_data"

DATABASE_DIR = ROOT_DIR / "database"

DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "ecommerce.db"



# -----------------------------
# Create SQLite Connection
# -----------------------------

def create_connection():

    connection = sqlite3.connect(DB_PATH)

    print(f"Database Created : {DB_PATH}")

    return connection


# -----------------------------
# Load CSV Files
# -----------------------------

def load_cleaned_data():

    customers = pd.read_csv(CLEAN_DIR / "customers.csv")

    products = pd.read_csv(CLEAN_DIR / "products.csv")

    orders = pd.read_csv(CLEAN_DIR / "orders.csv")

    order_items = pd.read_csv(CLEAN_DIR / "order_items.csv")

    return customers, products, orders, order_items

