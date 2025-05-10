import os
import pytest
import sys
from unittest.mock import patch, MagicMock, mock_open

sibling_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
sys.path.append(sibling_dir)

import work_pg

# Patch logger to avoid cluttering test output
@pytest.fixture(autouse=True)
def patch_logger():
    with patch("work_pg.logger") as mock_logger:
        yield mock_logger

def test_read_sql_file_reads_file_content():
    sql_content = "CREATE TABLE test (id SERIAL);"
    with patch("builtins.open", mock_open(read_data=sql_content)) as mock_file:
        result = work_pg.read_sql_file("dummy.sql")
        mock_file.assert_called_once_with("dummy.sql", "r", encoding="utf-8")
        assert result == sql_content

@patch("work_pg.get_db_connection")
@patch("work_pg.get_postgres_params")
@patch("work_pg.read_sql_file")
def test_init_db_success(mock_read_sql, mock_get_params, mock_get_conn):
    # Setup mocks
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn
    mock_get_params.return_value = {"dbname": "test"}
    mock_read_sql.return_value = "CREATE TABLE test (id SERIAL);"

    work_pg.init_db()

    mock_get_conn.assert_called_once()
    mock_read_sql.assert_called_once()
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called_once()

@patch("work_pg.get_db_connection")
@patch("work_pg.get_postgres_params")
def test_init_db_connection_fail(mock_get_params, mock_get_conn):
    mock_get_conn.return_value = None
    mock_get_params.return_value = {"dbname": "test"}
    with pytest.raises(ConnectionError):
        work_pg.init_db()

@patch("work_pg.get_db_connection")
@patch("work_pg.get_postgres_params")
@patch("work_pg.read_sql_file")
def test_init_db_sql_error(mock_read_sql, mock_get_params, mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn
    mock_get_params.return_value = {"dbname": "test"}
    mock_read_sql.return_value = "CREATE TABLE test (id SERIAL);"
    # Simulate DB error
    mock_cursor.execute.side_effect = Exception("DB error")
    with pytest.raises(Exception):
        work_pg.init_db()
    mock_conn.close.assert_called_once()

@patch("work_pg.get_db_connection")
@patch("work_pg.get_postgres_params")
@patch("work_pg.sql.SQL")
@patch("work_pg.sql.Identifier")
def test_insert_many_rows_success(mock_identifier, mock_sql, mock_get_params, mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn
    mock_get_params.return_value = {"dbname": "test"}
    mock_sql.return_value = MagicMock()
    mock_identifier.side_effect = lambda x: x

    # Patch mogrify to return bytes
    mock_cursor.mogrify.side_effect = lambda q, row: f"({','.join(map(str, row))})".encode("utf-8")

    table = "mytable"
    columns = ["id", "name"]
    rows = [(1, "Alice"), (2, "Bob")]

    work_pg.insert_many_rows(table, columns, rows)

    mock_get_conn.assert_called_once()
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_insert_many_rows_no_rows():
    with patch("work_pg.logger") as mock_logger:
        work_pg.insert_many_rows("table", ["id"], [])
        mock_logger.error.assert_called_with("No rows to insert.")

@patch("work_pg.get_db_connection")
@patch("work_pg.get_postgres_params")
@patch("work_pg.sql.SQL")
@patch("work_pg.sql.Identifier")
def test_insert_many_rows_connection_fail(mock_identifier, mock_sql, mock_get_params, mock_get_conn):
    mock_get_conn.return_value = None
    mock_get_params.return_value = {"dbname": "test"}
    mock_sql.return_value = MagicMock()
    mock_identifier.side_effect = lambda x: x
    with pytest.raises(ConnectionError):
        work_pg.insert_many_rows("table", ["id"], [(1,)])

@patch("work_pg.get_db_connection")
@patch("work_pg.get_postgres_params")
@patch("work_pg.sql.SQL")
@patch("work_pg.sql.Identifier")
def test_insert_many_rows_db_error(mock_identifier, mock_sql, mock_get_params, mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn
    mock_get_params.return_value = {"dbname": "test"}
    mock_sql.return_value = MagicMock()
    mock_identifier.side_effect = lambda x: x

    # Patch mogrify to return bytes
    mock_cursor.mogrify.side_effect = lambda q, row: f"({','.join(map(str, row))})".encode("utf-8")
    mock_cursor.execute.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        work_pg.insert_many_rows("table", ["id"], [(1,)])
    mock_conn.close.assert_called_once()
