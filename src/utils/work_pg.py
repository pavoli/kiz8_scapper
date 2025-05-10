from typing import List, Tuple

from psycopg2 import (
    sql, 
    Error,
)
from src.utils.helper import (
    get_db_connection, 
    get_postgres_params,
)
from src.utils.logger import setup_logger

logger = setup_logger(level=10)


def read_sql_file(file_path: str) -> str:
    """Read DDL commands from SQL-file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def init_db() -> None:
    """Initializes the database by executing SQL commands from a file."""

    conn = get_db_connection(get_postgres_params())
    
    if conn is None:
        logger.error("Failed to establish a connection to the database.")
        raise ConnectionError("Failed to establish database connection")

    try:
        with conn.cursor() as cur:
            sql_commands = read_sql_file(file_path="src/sql_ddl/init_sql_ddl.sql")
            for command in sql_commands.split(';'):
                command = command.strip()
                logger.debug(f"command={command}")
                if command:
                    cur.execute(command)
            conn.commit()
            logger.debug("DB created.")
    except Error as e:
        logger.error(f"Error initializing the database: {e}")
        raise
    finally:
        conn.close()


def insert_many_rows(
    table_name: str,
    columns: List[str],
    rows: List[Tuple]
) -> None:
    """
    Inserts multiple rows into a PostgreSQL table in a single query.

    Args:
        conn_params (dict): Connection parameters for the database (e.g., dbname, user, password, host, port).
        table_name (str): Name of the target table.
        columns (List[str]): List of column names to insert data into.
        rows (List[Tuple]): List of tuples, each representing a row of data to insert.

    Example:
        insert_many_rows(
            conn_params={'dbname': 'testdb', 'user': 'postgres', 'password': 'pass', 'host': 'localhost'},
            table_name='employees',
            columns=['id', 'name', 'age'],
            rows=[(1, 'John Doe', 30), (2, 'Jane Smith', 25)]
        )
    """
    if not rows:
        logger.error("No rows to insert.")
        return

    # Create the placeholders for each row (%s, %s, ...)
    values_placeholder = ', '.join(['%s'] * len(columns))

    # Create the base INSERT query with placeholders for multiple rows
    insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ").format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
    )

    conn = None
    try:
        conn = get_db_connection(get_postgres_params())
        if conn is None:
            raise ConnectionError("Failed to establish database connection")

        with conn.cursor() as cur:
            args_str = b','.join(
                cur.mogrify(f"({values_placeholder})", row) for row in rows
            )
            cur.execute(insert_query + sql.SQL(args_str.decode('utf-8')))
        conn.commit()
        logger.debug(f"Successfully inserted {len(rows)} rows into '{table_name}'.")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    pass