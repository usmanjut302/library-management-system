
from datetime import date, timedelta

import mysql.connector
import borrowing

from unittest.mock import MagicMock


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def create_database_mock():
    """Create a simulated database connection and cursor."""

    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value = cursor
    connection.is_connected.return_value = True

    return connection, cursor


def provide_inputs(monkeypatch, values):
    """Simulate user input."""

    responses = iter(values)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(responses)
    )


# =====================================================
# BORROW BOOK TESTS
# =====================================================

def test_borrow_book_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (1, "Python Basics", 10, 8),
        (1, "Ali", "ali@gmail.com")
    ]

    cursor.lastrowid = 25
    cursor.rowcount = 1

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "1", "2"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "BORROWING SUCCESSFUL" in output
    assert "Borrowing ID: 25" in " ".join(output.split())
    assert "Python Basics" in output
    assert "Ali" in output
    assert "Quantity Borrowed:  2" in output
    assert "Remaining Copies:   6" in output

    connection.start_transaction.assert_called_once()
    connection.commit.assert_called_once()
    connection.close.assert_called_once()

    # Verify the borrowing dates.
    insert_values = cursor.execute.call_args_list[2][0][1]

    assert insert_values[0] == 1
    assert insert_values[1] == 1
    assert insert_values[2] == 2
    assert insert_values[3] == date.today()
    assert insert_values[4] == date.today() + timedelta(days=14)


def test_borrow_book_invalid_book_id(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["abc"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "Book ID must be a valid integer." in output


def test_borrow_book_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["999", "1", "1"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "Book not found." in output
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_borrow_book_member_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (1, "Python Basics", 10, 8),
        None
    ]

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "999", "1"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "Member not found." in output
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_borrow_book_insufficient_copies(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (1, "Python Basics", 10, 3),
        (1, "Ali", "ali@gmail.com")
    ]

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "1", "5"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "Insufficient book copies." in output
    assert "Available copies: 3" in output
    assert "Requested copies: 5" in output

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_borrow_book_integrity_error(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (1, "Python Basics", 10, 8),
        (1, "Ali", "ali@gmail.com")
    ]

    cursor.execute.side_effect = [
        None,
        None,
        mysql.connector.IntegrityError("Foreign key error")
    ]

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "1", "2"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "Database Integrity Error" in output
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_borrow_book_inventory_update_failure(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (1, "Python Basics", 10, 8),
        (1, "Ali", "ali@gmail.com")
    ]

    # The guarded UPDATE affects zero rows.
    cursor.rowcount = 0

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "1", "2"])

    borrowing.borrow_book()

    output = capsys.readouterr().out

    assert "Book availability could not be updated." in output

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


# =====================================================
# VIEW BORROWINGS TESTS
# =====================================================

def test_view_borrowings_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (
            1,
            "Python Basics",
            "Ali",
            2,
            "2026-11-11",
            "2026-11-25",
            None,
            "borrowed"
        )
    ]

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    borrowing.view_borrowings()

    output = capsys.readouterr().out

    assert "Python Basics" in output
    assert "Ali" in output
    assert "Quantity:        2" in output
    assert "Status:          Borrowed" in output
    assert "Not returned" in output
    assert "Total Borrowing Records: 1" in output

    connection.close.assert_called_once()


def test_view_borrowings_empty(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchall.return_value = []

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    borrowing.view_borrowings()

    output = capsys.readouterr().out

    assert "No borrowing records found." in output


# =====================================================
# RETURN BOOK TESTS
# =====================================================

def test_return_book_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (2, 1, 1, 2, "borrowed"),
        (1, "Python Basics", 10, 6)
    ]

    cursor.rowcount = 1

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "BOOK RETURNED SUCCESSFULLY" in output
    assert "Borrowing ID:       2" in output
    assert "Python Basics" in output
    assert "Quantity Returned:  2" in output
    assert "Available Copies:   8" in output

    connection.start_transaction.assert_called_once()
    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_return_book_invalid_id(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["abc"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "Borrowing ID must be a valid integer." in output


def test_return_book_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["999"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "Borrowing record not found." in output
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_return_book_already_returned(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        2, 1, 1, 2, "returned"
    )

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "already been returned" in output.lower()

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_return_book_missing_book(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (2, 1, 1, 2, "borrowed"),
        None
    ]

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "could not be found" in output.lower()

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_return_book_inventory_limit_exceeded(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (2, 1, 1, 2, "borrowed"),
        (1, "Python Basics", 10, 9)
    ]

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "exceed the" in output.lower()
    assert "total inventory" in output.lower()

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_return_book_inventory_update_failure(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (2, 1, 1, 2, "borrowed"),
        (1, "Python Basics", 10, 6)
    ]

    # Simulate the guarded book UPDATE affecting zero rows.
    cursor.rowcount = 0

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "Book availability could not be updated." in output

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_return_book_borrowing_update_failure(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.side_effect = [
        (2, 1, 1, 2, "borrowed"),
        (1, "Python Basics", 10, 6)
    ]

    # The book UPDATE succeeds, but the borrowing UPDATE fails.
    rowcount_values = iter([1, 0])

    type(cursor).rowcount = property(
        lambda self: next(rowcount_values)
    )

    monkeypatch.setattr(
        borrowing, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2"])

    borrowing.return_book()

    output = capsys.readouterr().out

    assert "Borrowing record could not be updated." in output

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
