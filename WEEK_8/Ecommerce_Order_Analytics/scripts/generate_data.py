import random
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

random.seed(42)
Faker.seed(42)

fake = Faker("en_IN")

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

NUM_CUSTOMERS = 500
NUM_PRODUCTS = 500
NUM_ORDERS = 500
NUM_ORDER_ITEMS = 1000

CUSTOMER_TYPES = [
    "REGULAR",
    "PREMIUM",
    "VIP"
]

ORDER_STATUS = [
    "PLACED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED"
]

REGIONS = [
    "North",
    "South",
    "East",
    "West"
]

PRODUCT_CATEGORIES = {
    "Electronics": [
        "Laptop",
        "Phone",
        "Tablet",
        "Mouse",
        "Keyboard",
        "Monitor",
        "Camera",
        "Speaker"
    ],

    "Clothing": [
        "Shirt",
        "Jeans",
        "Jacket",
        "Shoes",
        "T-Shirt",
        "Sweater"
    ],

    "Books": [
        "Programming",
        "History",
        "Science",
        "Novel",
        "Mathematics",
        "Biography"
    ],

    "Home": [
        "Chair",
        "Table",
        "Fan",
        "Sofa",
        "Lamp",
        "Curtain"
    ]
}

# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------

def random_datetime():
    start = datetime.now() - timedelta(days=730)

    end = datetime.now()

    delta = end - start

    random_days = random.randint(0, delta.days)

    random_seconds = random.randint(0, 86400)

    return start + timedelta(
        days=random_days,
        seconds=random_seconds
    )


def random_order_date():

    dt = random_datetime()

    # 5% wrong format
    if random.random() < 0.05:

        return dt.strftime("%d-%m-%Y %H:%M:%S")

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def random_registration_date():

    dt = datetime.now() - timedelta(
        days=random.randint(30, 1200)
    )

    return dt.strftime("%Y-%m-%d")


def random_product_name(name):

    style = random.randint(1, 5)

    if style == 1:
        return name.upper()

    elif style == 2:
        return name.lower()

    elif style == 3:
        return "   " + name + "   "

    elif style == 4:
        return name.title()

    return name


def random_email():

    email = fake.email()

    # 2% invalid emails

    if random.random() < 0.02:

        mode = random.randint(1, 3)

        if mode == 1:

            email = email.replace("@", "")

        elif mode == 2:

            email = email.split("@")[0] + "@"

        else:

            email = email.replace(".com", "")

    return email


# ----------------------------------------------------
# Customers
# ----------------------------------------------------

def generate_customers():

    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):

        customers.append({

            "customer_id": f"C{i:04d}",

            "customer_name": fake.name(),

            "email": random_email(),

            "registration_date": random_registration_date(),

            "customer_type": random.choice(CUSTOMER_TYPES)

        })

    df = pd.DataFrame(customers)

    df.to_csv(
        DATA_DIR / "customers.csv",
        index=False
    )

    print("customers.csv generated")

    return df

# ----------------------------------------------------
# Products
# ----------------------------------------------------

SUBCATEGORIES = {
    "Electronics": [
        "Laptop",
        "Phone",
        "Tablet",
        "Keyboard",
        "Mouse",
        "Monitor",
        "Camera",
        "Speaker"
    ],

    "Clothing": [
        "Men",
        "Women",
        "Kids",
        "Winter",
        "Sports"
    ],

    "Books": [
        "Programming",
        "Science",
        "History",
        "Novel",
        "Education"
    ],

    "Home": [
        "Furniture",
        "Kitchen",
        "Lighting",
        "Decor",
        "Appliances"
    ]
}


BRANDS = {
    "Electronics": [
        "Samsung",
        "Apple",
        "Dell",
        "HP",
        "Lenovo",
        "Sony",
        "Boat",
        "LG"
    ],

    "Clothing": [
        "Nike",
        "Adidas",
        "Puma",
        "Levis",
        "Zara",
        "H&M"
    ],

    "Books": [
        "Oxford",
        "Pearson",
        "McGraw",
        "Packt",
        "OReilly"
    ],

    "Home": [
        "Godrej",
        "Ikea",
        "Milton",
        "Prestige",
        "Cello"
    ]
}


def generate_products():

    products = []

    for i in range(1, NUM_PRODUCTS + 1):

        category = random.choice(list(PRODUCT_CATEGORIES.keys()))

        product = random.choice(PRODUCT_CATEGORIES[category])

        brand = random.choice(BRANDS[category])

        subcategory = random.choice(SUBCATEGORIES[category])

        product_name = f"{brand} {product}"

        # 10% intentionally dirty names
        if random.random() < 0.10:
            product_name = random_product_name(product_name)

        cost_price = round(random.uniform(100, 50000), 2)

        products.append({

            "product_id": f"P{i:04d}",

            "product_name": product_name,

            "category": category,

            "subcategory": subcategory,

            "cost_price": cost_price

        })

    df = pd.DataFrame(products)

    df.to_csv(
        DATA_DIR / "products.csv",
        index=False
    )

    print("products.csv generated")

    return df

# ----------------------------------------------------
# Orders
# ----------------------------------------------------

def generate_orders(customers_df):

    orders = []

    customer_ids = customers_df["customer_id"].tolist()

    for i in range(1, NUM_ORDERS + 1):

        # 5% NULL customer_id
        if random.random() < 0.05:
            customer_id = None
        else:
            customer_id = random.choice(customer_ids)

        orders.append({

            "order_id": f"O{i:04d}",

            "customer_id": customer_id,

            "order_date": random_order_date(),

            "status": random.choice(ORDER_STATUS),

            "region_code": random.choice(REGIONS)

        })

    df = pd.DataFrame(orders)

    df.to_csv(
        DATA_DIR / "orders.csv",
        index=False
    )

    print("orders.csv generated")

    return df

# ----------------------------------------------------
# Order Items
# ----------------------------------------------------

def generate_order_items(orders_df, products_df):

    order_items = []

    order_ids = orders_df["order_id"].tolist()

    product_lookup = products_df.set_index("product_id")["cost_price"].to_dict()

    product_ids = list(product_lookup.keys())

    for i in range(1, NUM_ORDER_ITEMS + 1):

        order_id = random.choice(order_ids)

        product_id = random.choice(product_ids)

        # 3% negative quantity (returns)
        if random.random() < 0.03:
            quantity = -random.randint(1, 3)
        else:
            quantity = random.randint(1, 5)

        cost_price = product_lookup[product_id]

        # Selling price = cost + 10% to 50%
        unit_price = round(
            cost_price * random.uniform(1.10, 1.50),
            2
        )

        discount_percent = random.randint(0, 100)

        order_items.append({

            "item_id": f"I{i:04d}",

            "order_id": order_id,

            "product_id": product_id,

            "quantity": quantity,

            "unit_price": unit_price,

            "discount_percent": discount_percent

        })

    df = pd.DataFrame(order_items)

    df.to_csv(
        DATA_DIR / "order_items.csv",
        index=False
    )

    print("order_items.csv generated")

    return df


# ----------------------------------------------------
# Main
# ----------------------------------------------------

def main():

    print("=" * 50)
    print("Generating Dataset...")
    print("=" * 50)

    customers_df = generate_customers()

    products_df = generate_products()

    orders_df = generate_orders(customers_df)

    generate_order_items(
        orders_df,
        products_df
    )

    print("\nDataset Generated Successfully!")
    print(f"Location : {DATA_DIR}")


if __name__ == "__main__":
    main()