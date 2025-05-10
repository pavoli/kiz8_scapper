import os
from typing import Any, Dict, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection

from src.utils.logger import setup_logger

logger = setup_logger(level=10)


def get_postgres_params() -> Dict[str, str]:
    load_dotenv()

    return {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }


def get_db_connection(db_params: Optional[Dict[str, Any]] = None) -> Optional[_connection]:
    """
    Establishes a connection to a PostgreSQL database using provided parameters.

    Args:
        db_params (Optional[Dict[str, Any]]): Dictionary with connection parameters such as
            host, port, user, password, dbname. If None, attempts to retrieve parameters
            via `get_postgres_params()`.

    Returns:
        Optional[psycopg2.extensions.connection]: psycopg2 connection object if successful, else None.

    Notes:
        - Caller is responsible for closing the connection.
        - Logs an error if connection fails.
    """

    if db_params is None:
        db_params = get_postgres_params()

    try:
        conn = psycopg2.connect(**db_params)
        logger.debug("Database connection established successfully.")
        return conn
    except psycopg2.Error as err:
        logger.error(f"Database connection error: {err}")
        return None


def get_param_from_env(param_name: str) -> Optional[str]:
    """Function to get `PARAMETER` from file .env

    Args:
        param_name (str): parameter name to get from .env

    Returns:
        str: parameter value or None
    """

    return os.getenv(param_name, None)
