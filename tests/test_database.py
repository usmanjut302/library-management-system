
import pytest

from database import get_connection


def test_database_connection():
    connection = get_connection()

    try:
        assert connection.is_connected() is True

    finally:
        connection.close()


def test_missing_database_configuration(monkeypatch):
    # Temporarily remove DB_HOST from the environment.
    monkeypatch.delenv("DB_HOST", raising=False)

    # Verify that get_connection raises the expected error.
    with pytest.raises(
        ValueError,
        match="Missing required environment variable: DB_HOST"
    ):
        get_connection()








def test_invalid_database_port(monkeypatch):
    # Replace DB_PORT temporarily with an invalid value.
    monkeypatch.setenv("DB_PORT", "abc")

    with pytest.raises(
        ValueError,
        match="DB_PORT must be a valid number."
    ):
        get_connection()
