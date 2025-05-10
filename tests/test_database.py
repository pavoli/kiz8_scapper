import os
import pytest
import sys
from psycopg2.extensions import connection

from src.utils.helper import get_db_connection, get_postgres_params


def test_get_db_connection_success():
    conn = get_db_connection(get_postgres_params())
    assert conn is not None
    assert isinstance(conn, connection)
    conn.close()

def test_get_db_connection_fail(monkeypatch):
    import psycopg2

    def mock_connect(*args, **kwargs):
        raise psycopg2.OperationalError("Mocked connection error")

    monkeypatch.setattr(psycopg2, "connect", mock_connect)

    conn = get_db_connection({
        "dbname": "wrongdb",
        "user": "wronguser",
        "password": "wrongpassword",
        "host": "localhost",
        "port": "5432"
    })
    assert conn is None
