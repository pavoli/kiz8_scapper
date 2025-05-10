import os
from typing import Dict, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection

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


def get_db_connection(db_params) -> Optional[connection]:
    """
    Connects to PostgreSQL using parameters from .env.

    Returns:
        Optional[connection]: Connection psycopg2 object or None.
    """

    if db_params is None:
        db_params = get_postgres_params()

    try:
        return psycopg2.connect(**db_params)
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
