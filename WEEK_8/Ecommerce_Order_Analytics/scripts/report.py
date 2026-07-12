import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# Project Paths
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = ROOT_DIR / "database" / "ecommerce.db"

REPORTS_DIR = ROOT_DIR / "reports"

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Utility Functions
# ============================================================

def parse_date(date_text):
    """
    Convert YYYY-MM-DD input into a datetime object.
    """

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        )

    except ValueError as error:

        raise ValueError(
            "Invalid date format. Use YYYY-MM-DD."
        ) from error


def format_date(date_value):
    """
    Convert datetime object to YYYY-MM-DD string.
    """

    return date_value.strftime("%Y-%m-%d")


def validate_report_type(report_type):
    """
    Validate daily, weekly or monthly report type.
    """

    valid_types = {
        "daily",
        "weekly",
        "monthly"
    }

    report_type = report_type.strip().lower()

    if report_type not in valid_types:

        raise ValueError(
            "Report type must be daily, weekly or monthly."
        )

    return report_type


# ============================================================
# Date Range Functions
# ============================================================

def calculate_current_period(
    report_type,
    start_date,
    end_date
):
    """
    Validate report period according to report type.
    """

    if start_date > end_date:

        raise ValueError(
            "Start date cannot be after end date."
        )

    period_days = (
        end_date - start_date
    ).days + 1

    if report_type == "daily" and period_days != 1:

        print(
            "Note: Daily report normally covers one day."
        )

    elif report_type == "weekly" and period_days != 7:

        print(
            "Note: Weekly report normally covers seven days."
        )

    elif report_type == "monthly":

        print(
            "Monthly report will use the entered date range."
        )

    return period_days


def calculate_previous_period(
    start_date,
    end_date
):
    """
    Calculate an immediately preceding period
    having the same number of days.
    """

    period_days = (
        end_date - start_date
    ).days + 1

    previous_end = (
        start_date - timedelta(days=1)
    )

    previous_start = (
        previous_end
        - timedelta(days=period_days - 1)
    )

    return previous_start, previous_end


# ============================================================
# Database Connection
# ============================================================

def create_connection():
    """
    Connect to the SQLite database.
    """

    if not DATABASE_PATH.exists():

        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run python scripts/load_database.py first."
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# Summary Metrics
# ============================================================

def get_summary(
    connection,
    start_date,
    end_date
):
    """
    Calculate total orders, revenue and unique customers
    for the selected date range.
    """

    query = """
    SELECT
        COUNT(DISTINCT o.order_id) AS total_orders,

        ROUND(
            COALESCE(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (
                        1
                        - oi.discount_percent / 100.0
                    )
                ),
                0
            ),
            2
        ) AS total_revenue,

        COUNT(
            DISTINCT CASE
                WHEN o.customer_id IS NOT NULL
                 AND o.customer_id != 'C_UNKNOWN'
                THEN o.customer_id
            END
        ) AS unique_customers

    FROM orders AS o

    LEFT JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE DATE(o.order_date)
        BETWEEN DATE(?) AND DATE(?)

      AND o.status != 'CANCELLED';
    """

    cursor = connection.execute(
        query,
        (
            format_date(start_date),
            format_date(end_date)
        )
    )

    row = cursor.fetchone()

    return {
        "total_orders": row["total_orders"] or 0,
        "total_revenue": row["total_revenue"] or 0,
        "unique_customers": row["unique_customers"] or 0
    }


# ============================================================
# Top Three Products
# ============================================================

def get_top_products(
    connection,
    start_date,
    end_date
):
    """
    Return the top three products by revenue.
    """

    query = """
    SELECT
        p.product_id,
        p.product_name,

        SUM(
            CASE
                WHEN oi.quantity > 0
                THEN oi.quantity
                ELSE 0
            END
        ) AS quantity_sold,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (
                    1
                    - oi.discount_percent / 100.0
                )
            ),
            2
        ) AS product_revenue

    FROM orders AS o

    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id

    INNER JOIN products AS p
        ON oi.product_id = p.product_id

    WHERE DATE(o.order_date)
        BETWEEN DATE(?) AND DATE(?)

      AND o.status != 'CANCELLED'

      AND oi.quantity > 0

    GROUP BY
        p.product_id,
        p.product_name

    ORDER BY product_revenue DESC

    LIMIT 3;
    """

    cursor = connection.execute(
        query,
        (
            format_date(start_date),
            format_date(end_date)
        )
    )

    return cursor.fetchall()


# ============================================================
# Percentage Change
# ============================================================

def calculate_percentage_change(
    current_value,
    previous_value
):
    """
    Calculate percentage change.
    """

    if previous_value == 0:

        if current_value == 0:
            return 0.0

        return None

    return round(
        (
            current_value - previous_value
        )
        * 100.0
        / previous_value,
        2
    )


def format_change(change_value):
    """
    Format percentage-change output.
    """

    if change_value is None:

        return "N/A (previous value was zero)"

    if change_value > 0:

        return f"+{change_value:.2f}%"

    return f"{change_value:.2f}%"


# ============================================================
# Report Display
# ============================================================

def display_report(
    report_type,
    start_date,
    end_date,
    current_summary,
    previous_start,
    previous_end,
    previous_summary,
    top_products
):
    """
    Display the complete report in the terminal.
    """

    order_change = calculate_percentage_change(
        current_summary["total_orders"],
        previous_summary["total_orders"]
    )

    revenue_change = calculate_percentage_change(
        current_summary["total_revenue"],
        previous_summary["total_revenue"]
    )

    customer_change = calculate_percentage_change(
        current_summary["unique_customers"],
        previous_summary["unique_customers"]
    )

    print("\n" + "=" * 70)
    print("E-COMMERCE ORDER ANALYTICS REPORT")
    print("=" * 70)

    print(
        f"Report Type     : {report_type.upper()}"
    )

    print(
        "Current Period  : "
        f"{format_date(start_date)} "
        f"to {format_date(end_date)}"
    )

    print(
        "Previous Period : "
        f"{format_date(previous_start)} "
        f"to {format_date(previous_end)}"
    )

    print("\n" + "-" * 70)
    print("SUMMARY")
    print("-" * 70)

    print(
        f"Total Orders      : "
        f"{current_summary['total_orders']}"
    )

    print(
        f"Total Revenue     : "
        f"₹{current_summary['total_revenue']:,.2f}"
    )

    print(
        f"Unique Customers  : "
        f"{current_summary['unique_customers']}"
    )

    print("\n" + "-" * 70)
    print("COMPARISON WITH PREVIOUS PERIOD")
    print("-" * 70)

    print(
        f"Orders Change     : "
        f"{format_change(order_change)}"
    )

    print(
        f"Revenue Change    : "
        f"{format_change(revenue_change)}"
    )

    print(
        f"Customers Change  : "
        f"{format_change(customer_change)}"
    )

    print("\n" + "-" * 70)
    print("TOP 3 PRODUCTS")
    print("-" * 70)

    if not top_products:

        print(
            "No products found for the selected period."
        )

    else:

        print(
            f"{'Rank':<6}"
            f"{'Product':<35}"
            f"{'Qty':<10}"
            f"{'Revenue':>15}"
        )

        print("-" * 70)

        for rank, product in enumerate(
            top_products,
            start=1
        ):

            product_name = (
                product["product_name"][:32]
            )

            print(
                f"{rank:<6}"
                f"{product_name:<35}"
                f"{product['quantity_sold']:<10}"
                f"₹{product['product_revenue']:>13,.2f}"
            )

    print("=" * 70)


# ============================================================
# Save Report to Text File
# ============================================================

def save_report(
    report_type,
    start_date,
    end_date,
    current_summary,
    previous_start,
    previous_end,
    previous_summary,
    top_products
):
    """
    Save the generated report as a text file.
    """

    report_name = (
        f"{report_type}_report_"
        f"{format_date(start_date)}_"
        f"to_{format_date(end_date)}.txt"
    )

    report_path = REPORTS_DIR / report_name

    order_change = calculate_percentage_change(
        current_summary["total_orders"],
        previous_summary["total_orders"]
    )

    revenue_change = calculate_percentage_change(
        current_summary["total_revenue"],
        previous_summary["total_revenue"]
    )

    customer_change = calculate_percentage_change(
        current_summary["unique_customers"],
        previous_summary["unique_customers"]
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "=" * 70 + "\n"
        )

        file.write(
            "E-COMMERCE ORDER ANALYTICS REPORT\n"
        )

        file.write(
            "=" * 70 + "\n\n"
        )

        file.write(
            f"Report Type: {report_type.upper()}\n"
        )

        file.write(
            "Current Period: "
            f"{format_date(start_date)} "
            f"to {format_date(end_date)}\n"
        )

        file.write(
            "Previous Period: "
            f"{format_date(previous_start)} "
            f"to {format_date(previous_end)}\n\n"
        )

        file.write(
            f"Total Orders: "
            f"{current_summary['total_orders']}\n"
        )

        file.write(
            f"Total Revenue: "
            f"{current_summary['total_revenue']:.2f}\n"
        )

        file.write(
            f"Unique Customers: "
            f"{current_summary['unique_customers']}\n\n"
        )

        file.write(
            "Comparison with Previous Period\n"
        )

        file.write(
            "-" * 40 + "\n"
        )

        file.write(
            f"Orders Change: "
            f"{format_change(order_change)}\n"
        )

        file.write(
            f"Revenue Change: "
            f"{format_change(revenue_change)}\n"
        )

        file.write(
            f"Customers Change: "
            f"{format_change(customer_change)}\n\n"
        )

        file.write(
            "Top 3 Products\n"
        )

        file.write(
            "-" * 40 + "\n"
        )

        if not top_products:

            file.write(
                "No products found.\n"
            )

        else:

            for rank, product in enumerate(
                top_products,
                start=1
            ):

                file.write(
                    f"{rank}. "
                    f"{product['product_name']} | "
                    f"Quantity: "
                    f"{product['quantity_sold']} | "
                    f"Revenue: "
                    f"{product['product_revenue']:.2f}\n"
                )

    print(
        f"\n✔ Report saved: {report_path}"
    )

    return report_path


# ============================================================
# User Input
# ============================================================

def get_user_input():
    """
    Take report type and date range from the user.
    """

    print("\n" + "=" * 70)
    print("E-COMMERCE REPORT GENERATOR")
    print("=" * 70)

    print("\nAvailable report types:")

    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")

    report_choice = input(
        "\nSelect report type "
        "(daily/weekly/monthly): "
    )

    report_type = validate_report_type(
        report_choice
    )

    start_text = input(
        "Enter start date (YYYY-MM-DD): "
    )

    end_text = input(
        "Enter end date (YYYY-MM-DD): "
    )

    start_date = parse_date(
        start_text
    )

    end_date = parse_date(
        end_text
    )

    calculate_current_period(
        report_type,
        start_date,
        end_date
    )

    return (
        report_type,
        start_date,
        end_date
    )


# ============================================================
# Main Function
# ============================================================

def main():

    connection = None

    try:

        (
            report_type,
            start_date,
            end_date
        ) = get_user_input()

        (
            previous_start,
            previous_end
        ) = calculate_previous_period(
            start_date,
            end_date
        )

        connection = create_connection()

        current_summary = get_summary(
            connection,
            start_date,
            end_date
        )

        previous_summary = get_summary(
            connection,
            previous_start,
            previous_end
        )

        top_products = get_top_products(
            connection,
            start_date,
            end_date
        )

        display_report(
            report_type,
            start_date,
            end_date,
            current_summary,
            previous_start,
            previous_end,
            previous_summary,
            top_products
        )

        save_report(
            report_type,
            start_date,
            end_date,
            current_summary,
            previous_start,
            previous_end,
            previous_summary,
            top_products
        )

        print(
            "\n✔ Report generated successfully"
        )

    except (
        ValueError,
        FileNotFoundError,
        sqlite3.Error
    ) as error:

        print(
            f"\n✘ Error: {error}"
        )

    finally:

        if connection is not None:

            connection.close()

            print(
                "✔ Database connection closed"
            )


if __name__ == "__main__":
    main()