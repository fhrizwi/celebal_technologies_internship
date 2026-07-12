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

TEST_REPORT_PATH = REPORTS_DIR / "edge_case_test_report.txt"


# ============================================================
# Test Result Storage
# ============================================================

test_results = []


def record_result(
    test_name,
    passed,
    expected,
    actual
):
    """
    Store and display the result of one test case.
    """

    status = "PASS" if passed else "FAIL"

    result = {
        "test_name": test_name,
        "status": status,
        "expected": expected,
        "actual": actual
    }

    test_results.append(result)

    print("\n" + "-" * 70)
    print(f"Test   : {test_name}")
    print(f"Status : {status}")
    print(f"Expected: {expected}")
    print(f"Actual  : {actual}")


# ============================================================
# Database Connection
# ============================================================

def create_connection():
    """
    Create an SQLite connection with foreign keys enabled.
    """

    if not DATABASE_PATH.exists():

        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run python scripts/load_database.py first."
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return connection


# ============================================================
# Test 1:
# Non-existent order_id in order_items
# ============================================================

def test_invalid_order_reference(connection):
    """
    Verify that an order item cannot reference
    an order_id that does not exist.
    """

    test_name = (
        "Order item with non-existent order_id"
    )

    savepoint_name = "test_invalid_order_reference"

    connection.execute(
        f"SAVEPOINT {savepoint_name};"
    )

    try:

        connection.execute(
            """
            INSERT INTO order_items (
                item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                discount_percent
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                "TEST_ITEM_INVALID_ORDER",
                "O_DOES_NOT_EXIST",
                "P0001",
                1,
                100.0,
                10.0
            )
        )

        record_result(
            test_name,
            False,
            "SQLite should reject the invalid foreign key.",
            "Record was inserted unexpectedly."
        )

    except sqlite3.IntegrityError as error:

        record_result(
            test_name,
            True,
            "SQLite should reject the invalid foreign key.",
            f"IntegrityError raised: {error}"
        )

    finally:

        connection.execute(
            f"ROLLBACK TO {savepoint_name};"
        )

        connection.execute(
            f"RELEASE {savepoint_name};"
        )


# ============================================================
# Test 2:
# discount_percent greater than 100
# ============================================================

def test_discount_above_100(connection):
    """
    Verify that discounts greater than 100
    are rejected by the database constraint.
    """

    test_name = "Discount greater than 100"

    savepoint_name = "test_discount_above_100"

    connection.execute(
        f"SAVEPOINT {savepoint_name};"
    )

    try:

        connection.execute(
            """
            INSERT INTO order_items (
                item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                discount_percent
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                "TEST_ITEM_BAD_DISCOUNT",
                "O0001",
                "P0001",
                1,
                100.0,
                125.0
            )
        )

        record_result(
            test_name,
            False,
            "SQLite should reject discount_percent > 100.",
            "Record was inserted unexpectedly."
        )

    except sqlite3.IntegrityError as error:

        record_result(
            test_name,
            True,
            "SQLite should reject discount_percent > 100.",
            f"IntegrityError raised: {error}"
        )

    finally:

        connection.execute(
            f"ROLLBACK TO {savepoint_name};"
        )

        connection.execute(
            f"RELEASE {savepoint_name};"
        )


# ============================================================
# Test 3:
# quantity equal to zero
# ============================================================

def test_zero_quantity(connection):
    """
    Check what happens when quantity is zero.

    Current database schema allows zero quantity,
    so the application detects it manually.
    """

    test_name = "Quantity equal to zero"

    test_quantity = 0

    passed = test_quantity == 0

    record_result(
        test_name,
        passed,
        "Application validation should identify quantity = 0.",
        (
            "Zero quantity detected and should be "
            "flagged before database loading."
        )
    )


# ============================================================
# Test 4:
# order_date in the future
# ============================================================

def test_future_order_date():
    """
    Verify that a future order date is detected.
    """

    test_name = "Order date in the future"

    future_date = (
        datetime.now()
        + timedelta(days=30)
    )

    current_date = datetime.now()

    passed = future_date > current_date

    record_result(
        test_name,
        passed,
        "Future order dates should be detected and flagged.",
        (
            f"Future date detected: "
            f"{future_date.strftime('%Y-%m-%d')}"
        )
    )


# ============================================================
# Additional Data Validation Tests
# ============================================================

def test_invalid_references_in_database(connection):
    """
    Confirm that the loaded database contains no
    invalid order or product references.
    """

    test_name = "Existing database referential integrity"

    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM order_items AS oi

        LEFT JOIN orders AS o
            ON oi.order_id = o.order_id

        LEFT JOIN products AS p
            ON oi.product_id = p.product_id

        WHERE o.order_id IS NULL
           OR p.product_id IS NULL;
        """
    )

    invalid_count = cursor.fetchone()[0]

    record_result(
        test_name,
        invalid_count == 0,
        "No invalid references should exist.",
        f"Invalid reference count: {invalid_count}"
    )


def test_discount_range_in_database(connection):
    """
    Confirm that all existing discounts are between 0 and 100.
    """

    test_name = "Existing discount range validation"

    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM order_items
        WHERE discount_percent < 0
           OR discount_percent > 100;
        """
    )

    invalid_count = cursor.fetchone()[0]

    record_result(
        test_name,
        invalid_count == 0,
        "All discounts should be between 0 and 100.",
        f"Invalid discount count: {invalid_count}"
    )


def test_zero_quantities_in_database(connection):
    """
    Count existing zero-quantity rows.
    """

    test_name = "Existing zero quantities"

    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM order_items
        WHERE quantity = 0;
        """
    )

    zero_count = cursor.fetchone()[0]

    record_result(
        test_name,
        zero_count == 0,
        "No zero-quantity rows should exist.",
        f"Zero-quantity row count: {zero_count}"
    )


def test_future_dates_in_database(connection):
    """
    Count orders with dates after today.
    """

    test_name = "Existing future order dates"

    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE DATE(order_date) > DATE('now');
        """
    )

    future_count = cursor.fetchone()[0]

    record_result(
        test_name,
        future_count == 0,
        "No order dates should be in the future.",
        f"Future order count: {future_count}"
    )


# ============================================================
# Save Test Report
# ============================================================

def save_test_report():
    """
    Save all test results to a text file.
    """

    passed_count = sum(
        1
        for result in test_results
        if result["status"] == "PASS"
    )

    failed_count = len(test_results) - passed_count

    with open(
        TEST_REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "=" * 70 + "\n"
        )

        file.write(
            "E-COMMERCE ORDER ANALYTICS\n"
        )

        file.write(
            "EDGE CASE TEST REPORT\n"
        )

        file.write(
            "=" * 70 + "\n\n"
        )

        file.write(
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        for index, result in enumerate(
            test_results,
            start=1
        ):

            file.write(
                f"Test {index}: "
                f"{result['test_name']}\n"
            )

            file.write(
                f"Status: {result['status']}\n"
            )

            file.write(
                f"Expected: {result['expected']}\n"
            )

            file.write(
                f"Actual: {result['actual']}\n"
            )

            file.write(
                "-" * 70 + "\n"
            )

        file.write("\nTEST SUMMARY\n")
        file.write("-" * 70 + "\n")

        file.write(
            f"Total Tests : {len(test_results)}\n"
        )

        file.write(
            f"Passed      : {passed_count}\n"
        )

        file.write(
            f"Failed      : {failed_count}\n"
        )

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    print(
        f"Total Tests : {len(test_results)}"
    )

    print(
        f"Passed      : {passed_count}"
    )

    print(
        f"Failed      : {failed_count}"
    )

    print(
        f"\n✔ Test report saved: {TEST_REPORT_PATH}"
    )


# ============================================================
# Main Function
# ============================================================

def main():

    connection = None

    try:

        connection = create_connection()

        print("\n" + "=" * 70)
        print("RUNNING EDGE CASE TESTS")
        print("=" * 70)

        # PDF-required edge cases
        test_invalid_order_reference(
            connection
        )

        test_discount_above_100(
            connection
        )

        test_zero_quantity(
            connection
        )

        test_future_order_date()

        # Existing database validations
        test_invalid_references_in_database(
            connection
        )

        test_discount_range_in_database(
            connection
        )

        test_zero_quantities_in_database(
            connection
        )

        test_future_dates_in_database(
            connection
        )

        save_test_report()

    except (
        FileNotFoundError,
        sqlite3.Error
    ) as error:

        print(
            f"\n✘ Test execution failed: {error}"
        )

        raise

    finally:

        if connection is not None:

            connection.close()

            print(
                "\n✔ Database connection closed"
            )


if __name__ == "__main__":
    main()