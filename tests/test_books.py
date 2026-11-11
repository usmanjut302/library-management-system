
import mysql.connector
import books

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
    """Simulate user input without typing manually."""

    responses = iter(values)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(responses)
    )


# =====================================================
# ADD BOOK TESTS
# =====================================================

def test_add_book_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.lastrowid = 42

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["Python Basics", "John", "ISBN100", "Programming", "5"]
    )

    books.add_book()

    output = capsys.readouterr().out

    assert "Book added successfully!" in output
    assert "Book ID: 42" in output

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_add_book_empty_title(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["", "John", "ISBN100", "Programming", "5"]
    )

    books.add_book()

    output = capsys.readouterr().out

    assert "Book title cannot be empty." in output
    connection.commit.assert_not_called()


def test_add_book_invalid_copies(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["Python Basics", "John", "ISBN100", "Programming", "abc"]
    )

    books.add_book()

    output = capsys.readouterr().out

    assert "Total copies must be a valid integer." in output
    connection.commit.assert_not_called()


def test_add_book_duplicate_isbn(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.execute.side_effect = mysql.connector.IntegrityError(
        "Duplicate ISBN"
    )

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["Python Basics", "John", "ISBN100", "Programming", "5"]
    )

    books.add_book()

    output = capsys.readouterr().out

    assert "Database Integrity Error" in output
    connection.rollback.assert_called_once()


# =====================================================
# VIEW BOOKS TESTS
# =====================================================

def test_view_books_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Python Basics", "John", "ISBN100",
         "Programming", 5, 5)
    ]

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    books.view_books()

    output = capsys.readouterr().out

    assert "Python Basics" in output
    assert "Total Books: 1" in output

    connection.close.assert_called_once()


def test_view_books_empty(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = []

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    books.view_books()

    output = capsys.readouterr().out

    assert "No books found in the library." in output


# =====================================================
# SEARCH BOOK TESTS
# =====================================================

def test_search_book_by_id(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Python Basics", "John", "ISBN100",
         "Programming", 5, 5)
    ]

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "1"])

    books.search_book()

    output = capsys.readouterr().out

    assert "Python Basics" in output
    assert "Matching Books: 1" in output

    executed_query = cursor.execute.call_args

    assert executed_query[0][1] == (1,)


def test_search_book_by_title(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Python Basics", "John", "ISBN100",
         "Programming", 5, 5)
    ]

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2", "Python"])

    books.search_book()

    output = capsys.readouterr().out

    assert "Python Basics" in output

    executed_query = cursor.execute.call_args

    assert executed_query[0][1] == ("%Python%",)


def test_search_book_by_author(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Python Basics", "John", "ISBN100",
         "Programming", 5, 5)
    ]

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["3", "John"])

    books.search_book()

    output = capsys.readouterr().out

    assert "John" in output

    executed_query = cursor.execute.call_args

    assert executed_query[0][1] == ("%John%",)


def test_search_book_no_results(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = []

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "999"])

    books.search_book()

    output = capsys.readouterr().out

    assert "No matching books found." in output


def test_search_book_invalid_option(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["9"])

    books.search_book()

    output = capsys.readouterr().out

    assert "Invalid option" in output


def test_search_book_back_option(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["4"])

    books.search_book()

    output = capsys.readouterr().out

    assert "Returning to the previous menu." in output


# =====================================================
# UPDATE BOOK TESTS
# =====================================================

def test_update_book_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    # Existing book: 10 total, 8 available, 2 borrowed.
    cursor.fetchone.return_value = (
        "Old Title",
        "Old Author",
        "OLD100",
        "Programming",
        10,
        8
    )

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["1", "New Title", "New Author",
         "NEW100", "Technology", "12"]
    )

    books.update_book()

    output = capsys.readouterr().out

    assert "Book updated successfully!" in output

    connection.commit.assert_called_once()

    # New available copies = 12 total - 2 borrowed.
    update_values = cursor.execute.call_args_list[-1][0][1]

    assert update_values[4] == 12
    assert update_values[5] == 10


def test_update_book_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["999"])

    books.update_book()

    output = capsys.readouterr().out

    assert "Book not found" in output
    connection.commit.assert_not_called()


def test_update_book_total_below_borrowed(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    # 10 total, 8 available = 2 borrowed.
    cursor.fetchone.return_value = (
        "Python Basics",
        "John",
        "ISBN100",
        "Programming",
        10,
        8
    )

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["1", "", "", "", "", "1"]
    )

    books.update_book()

    output = capsys.readouterr().out

    assert "Cannot set total copies below 2" in output
    connection.commit.assert_not_called()


def test_update_book_duplicate_isbn(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        "Python Basics",
        "John",
        "ISBN100",
        "Programming",
        10,
        10
    )

    # First execute = SELECT; second execute = UPDATE.
    cursor.execute.side_effect = [
        None,
        mysql.connector.IntegrityError("Duplicate ISBN")
    ]

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["1", "", "", "DUPLICATE", "", ""]
    )

    books.update_book()

    output = capsys.readouterr().out

    assert "Database Integrity Error" in output
    connection.rollback.assert_called_once()


# =====================================================
# DELETE BOOK TESTS
# =====================================================

def test_delete_book_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        99, "Temporary Test Book", "Test Author",
        "TEMP999", "Testing", 1, 1
    )

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["99", "y"])

    books.delete_book()

    output = capsys.readouterr().out

    assert "Book deleted successfully!" in output

    connection.commit.assert_called_once()


def test_delete_book_cancelled(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        99, "Temporary Test Book", "Test Author",
        "TEMP999", "Testing", 1, 1
    )

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["99", "n"])

    books.delete_book()

    output = capsys.readouterr().out

    assert "Book deletion cancelled." in output
    connection.commit.assert_not_called()


def test_delete_book_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["999"])

    books.delete_book()

    output = capsys.readouterr().out

    assert "Book not found" in output
    connection.commit.assert_not_called()


def test_delete_book_with_borrowing_history(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        1, "usman", "usmanjutt",
        "12", "fiction", 99, 99
    )

    cursor.execute.side_effect = [
        None,
        mysql.connector.IntegrityError(
            "Foreign key constraint fails"
        )
    ]

    monkeypatch.setattr(
        books, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "y"])

    books.delete_book()

    output = capsys.readouterr().out

    assert "borrowing history" in output.lower()
    connection.rollback.assert_called_once()
