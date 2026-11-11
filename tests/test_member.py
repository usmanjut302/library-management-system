
import mysql.connector
import member

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
# REGISTER MEMBER TESTS
# =====================================================

def test_register_member_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.lastrowid = 10

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["Ali", "ali@gmail.com", "03001234567"]
    )

    member.register_member()

    output = capsys.readouterr().out

    assert "Member registered successfully!" in output
    assert "Member ID: 10" in output

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_register_member_empty_name(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["", "ali@gmail.com", "03001234567"]
    )

    member.register_member()

    output = capsys.readouterr().out

    assert "Member name cannot be empty." in output
    connection.commit.assert_not_called()


def test_register_member_invalid_email(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["Ali", "invalid-email", "03001234567"]
    )

    member.register_member()

    output = capsys.readouterr().out

    assert "Please enter a valid email address." in output
    connection.commit.assert_not_called()


def test_register_member_duplicate_email(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.execute.side_effect = mysql.connector.IntegrityError(
        "Duplicate email"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["Ali", "ali@gmail.com", "03001234567"]
    )

    member.register_member()

    output = capsys.readouterr().out

    assert "Database Integrity Error" in output
    connection.rollback.assert_called_once()


# =====================================================
# VIEW MEMBERS TESTS
# =====================================================

def test_view_members_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Ali", "ali@gmail.com", "03001234567",
         "2026-11-11")
    ]

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    member.view_members()

    output = capsys.readouterr().out

    assert "Ali" in output
    assert "ali@gmail.com" in output
    assert "Total Members: 1" in output

    connection.close.assert_called_once()


def test_view_members_empty(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchall.return_value = []

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    member.view_members()

    output = capsys.readouterr().out

    assert "No members registered yet." in output


# =====================================================
# SEARCH MEMBER TESTS
# =====================================================

def test_search_member_by_id(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        1, "Ali", "ali@gmail.com",
        "03001234567", "2026-11-11"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "1"])

    member.search_member()

    output = capsys.readouterr().out

    assert "Ali" in output
    assert "Matching Members: 1" in output

    executed_values = cursor.execute.call_args[0][1]
    assert executed_values == (1,)


def test_search_member_by_name(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Ali", "ali@gmail.com",
         "03001234567", "2026-11-11")
    ]

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2", "Ali"])

    member.search_member()

    output = capsys.readouterr().out

    assert "Ali" in output
    assert "Matching Members: 1" in output

    executed_values = cursor.execute.call_args[0][1]
    assert executed_values == ("%Ali%",)


def test_search_member_by_email(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchall.return_value = [
        (1, "Ali", "ali@gmail.com",
         "03001234567", "2026-11-11")
    ]

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["3", "ali@gmail.com"])

    member.search_member()

    output = capsys.readouterr().out

    assert "ali@gmail.com" in output
    assert "Matching Members: 1" in output

    executed_values = cursor.execute.call_args[0][1]
    assert executed_values == ("%ali@gmail.com%",)


def test_search_member_no_results(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchall.return_value = []

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["2", "Unknown"])

    member.search_member()

    output = capsys.readouterr().out

    assert "No matching members found." in output


def test_search_member_invalid_id(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["1", "abc"])

    member.search_member()

    output = capsys.readouterr().out

    assert "Member ID must be a valid integer." in output


def test_search_member_invalid_option(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["9"])

    member.search_member()

    output = capsys.readouterr().out

    assert "Invalid option." in output


def test_search_member_back_option(monkeypatch, capsys):
    provide_inputs(monkeypatch, ["4"])

    member.search_member()

    output = capsys.readouterr().out

    assert "Returning to the previous menu." in output


# =====================================================
# UPDATE MEMBER TESTS
# =====================================================

def test_update_member_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        1, "Old Name", "old@gmail.com", "03000000000"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["1", "New Name", "new@gmail.com", "03111111111"]
    )

    member.update_member()

    output = capsys.readouterr().out

    assert "Member updated successfully!" in output

    connection.commit.assert_called_once()

    update_values = cursor.execute.call_args_list[-1][0][1]

    assert update_values == (
        "New Name",
        "new@gmail.com",
        "03111111111",
        1
    )


def test_update_member_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["999"])

    member.update_member()

    output = capsys.readouterr().out

    assert "Member not found." in output
    connection.commit.assert_not_called()


def test_update_member_invalid_email(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        1, "Ali", "ali@gmail.com", "03001234567"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["1", "", "invalid-email", ""]
    )

    member.update_member()

    output = capsys.readouterr().out

    assert "Please enter a valid email address." in output
    connection.commit.assert_not_called()


def test_update_member_duplicate_email(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        1, "Ali", "ali@gmail.com", "03001234567"
    )

    cursor.execute.side_effect = [
        None,
        mysql.connector.IntegrityError("Duplicate email")
    ]

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(
        monkeypatch,
        ["1", "", "another@gmail.com", ""]
    )

    member.update_member()

    output = capsys.readouterr().out

    assert "Database Integrity Error" in output
    connection.rollback.assert_called_once()


# =====================================================
# DELETE MEMBER TESTS
# =====================================================

def test_delete_member_success(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        99, "Temporary Member", "temp@gmail.com",
        "03000000000", "2026-11-11"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["99", "y"])

    member.delete_member()

    output = capsys.readouterr().out

    assert "Member deleted successfully!" in output
    connection.commit.assert_called_once()


def test_delete_member_cancelled(monkeypatch, capsys):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        99, "Temporary Member", "temp@gmail.com",
        "03000000000", "2026-11-11"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["99", "n"])

    member.delete_member()

    output = capsys.readouterr().out

    assert "Member deletion cancelled." in output
    connection.commit.assert_not_called()


def test_delete_member_not_found(monkeypatch, capsys):
    connection, cursor = create_database_mock()
    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["999"])

    member.delete_member()

    output = capsys.readouterr().out

    assert "Member not found." in output
    connection.commit.assert_not_called()


def test_delete_member_invalid_confirmation(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        99, "Temporary Member", "temp@gmail.com",
        "03000000000", "2026-11-11"
    )

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["99", "maybe"])

    member.delete_member()

    output = capsys.readouterr().out

    assert "Invalid confirmation." in output
    connection.commit.assert_not_called()


def test_delete_member_with_borrowing_history(
    monkeypatch, capsys
):
    connection, cursor = create_database_mock()

    cursor.fetchone.return_value = (
        1, "Ali", "ali@gmail.com",
        "03001234567", "2026-11-11"
    )

    cursor.execute.side_effect = [
        None,
        mysql.connector.IntegrityError(
            "Foreign key constraint fails"
        )
    ]

    monkeypatch.setattr(
        member, "get_connection", lambda: connection
    )

    provide_inputs(monkeypatch, ["1", "y"])

    member.delete_member()

    output = capsys.readouterr().out

    assert "borrowing history" in output.lower()
    connection.rollback.assert_called_once()
