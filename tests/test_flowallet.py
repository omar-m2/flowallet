"""
Unit tests for Flowallet - Personal Finance Manager

This module contains unit tests for key functions of the Flowallet application,
including transaction management, input validation, and user interface handling.
The tests utilize mocks for the SQLite database connection and GUI components
to ensure isolated testing of the application logic.

Tested functionalities include:
- Validating and formatting amount inputs
- Adding transactions to the database
- Handling user input in the amount and category entry fields
"""

import unittest
from unittest.mock import Mock, patch
from flowallet import (
    validate_amount,
    format_amount_input,
    add_transaction,
    on_amount_entry,
    on_category_entry
)

class MockPlaceholderEntry:
    """Simulate the behavior of the PlaceholderEntry used in the main application"""

    def __init__(self, placeholder=""):
        # Initialize with placeholder text
        self.placeholder = placeholder
        self.value = ""

    def get(self):
        """Return entry value, if it's a placeholder text then return an empty string"""
        return self.value if self.value != self.placeholder else ""

    def delete(self, start, end):
        """Simulate deletion of the entry's text by clearing the value"""
        self.value = ""

    def insert(self, index, value):
        """Simulate inserting a value into the entry field"""
        self.value = value

    def set(self, value):
        """Set the entry's value directly"""
        self.value = value

    def focus(self):
        """Simulate the entry getting focus (not used in tests but required for completeness)"""
        pass

class TestPersonalFinanceManager(unittest.TestCase):
    """Main test class for testing the personal finance manager functions"""

    # Setup method that runs before each test
    def setUp(self):
        # Mock the SQLite database connection and cursor
        self.mock_conn = Mock()  # Mocked database connection
        self.mock_cursor = self.mock_conn.cursor.return_value  # Mocked cursor from the connection

        # Mock entries, labels, and other GUI components
        self.amount_entry = MockPlaceholderEntry(placeholder="Enter amount")
        self.category_entry = MockPlaceholderEntry(placeholder="Enter category")
        self.result_label = Mock()  # Mock label for showing results
        self.type_var = Mock()  # Mock variable for the transaction type (e.g., expense or income)

        # Patch global variables and methods from the 'flowallet' module
        self.patcher = patch.multiple('flowallet',
            amount_entry=self.amount_entry,  # Patch the amount entry
            category_entry=self.category_entry,  # Patch the category entry
            result_label=self.result_label,  # Patch the result label
            type_var=self.type_var,  # Patch the type variable
            update_totals=Mock()  # Patch the update_totals function
        )
        self.patcher.start()  # Start the patching

        # Patch the SQLite database connection call
        self.mock_sqlite_connect = patch('flowallet.sqlite3.connect',
                                            Mock(return_value=self.mock_conn)).start()

        # Mock fetchone to return a tuple with the ID
        self.mock_cursor.fetchone.return_value = (1,)  # Simulating that the available ID is 1

    # Tear down method to clean up after each test
    def tearDown(self):
        # Stop all patches after the test finishes
        patch.stopall()

    # Test the validate_amount function
    def test_validate_amount(self):
        """Test valid amounts"""

        self.assertEqual(validate_amount("1000"), 1000.0)  # Normal integer
        self.assertEqual(validate_amount("1,000"), 1000.0)  # Comma-separated integer
        self.assertEqual(validate_amount("10.50"), 10.5)  # Decimal number

        # Test invalid amounts
        self.assertIsNone(validate_amount("0"))  # Amount should be greater than 0
        self.assertIsNone(validate_amount("-100"))  # Negative amounts are invalid
        self.assertIsNone(validate_amount("abc"))  # Non-numeric input
        self.assertIsNone(validate_amount(""))  # Empty input

    # Test the format_amount_input function
    def test_format_amount_input(self):
        """Mock the event argument, even though it's not used in the function"""

        mock_event = Mock()

        # Test valid input
        self.amount_entry.set("1000")
        format_amount_input(mock_event)
        self.assertEqual(self.amount_entry.get(), "1,000")  # Ensure it formats as "1,000"

        # Test invalid input (letters should be cleared)
        self.amount_entry.set("abc")
        format_amount_input(mock_event)
        self.assertEqual(self.amount_entry.get(), "")  # Letters should be cleared

        # Test empty input
        self.amount_entry.set("")
        format_amount_input(mock_event)
        self.assertEqual(self.amount_entry.get(), "")  # Ensure no error with empty input

    # Test the add_transaction function
    def test_add_transaction(self):
        """Set up mock values for the entries"""

        self.amount_entry.set("1000")
        self.category_entry.set("Groceries")
        self.type_var.get.return_value = "expense"  # Mock that the transaction type is "expense"

        # Mock database cursor's execute and commit methods
        self.mock_cursor.execute.return_value = None
        self.mock_conn.commit.return_value = None

        # Call the function and check the result
        add_transaction()
        self.result_label.config.assert_called_with(text="Transaction Added!",
                                                    fg="green")  # Ensure success message displayed

    # Test the on_amount_entry function
    def test_on_amount_entry(self):
        """Test amount field with valid amount input"""
        self.amount_entry.set("1000")
        on_amount_entry(None)  # Call the function with None for the event
        self.assertEqual(self.category_entry.get(), "")  # Category entry should be cleared

        # Test with invalid amount input
        self.amount_entry.set("abc")
        on_amount_entry(None)
        self.result_label.config.assert_called_with(text="Please enter a valid numeric amount.",
                                                    fg="red")  # Error message

    # Test the on_category_entry function
    def test_on_category_entry(self):
        """Test category field with valid input"""

        self.amount_entry.set("1000")
        self.category_entry.set("Groceries")
        self.type_var.get.return_value = "expense"

        # Mock database cursor's execute and commit methods
        self.mock_cursor.execute.return_value = None
        self.mock_conn.commit.return_value = None

        on_category_entry(None)
        self.result_label.config.assert_called_with(text="Transaction Added!",
                                                    fg="green")  # Success message for valid input

        # Test with empty category
        self.category_entry.set("")
        on_category_entry(None)
        self.result_label.config.assert_called_with(text="Please enter a category.",
                                                    fg="red")  # Error message for missing category

# Run the tests.
if __name__ == "__main__":
    unittest.main()
