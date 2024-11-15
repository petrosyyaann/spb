from .base import clickhouse_session
from traceback import format_exc
from settings import settings
import logging


def create_tables():
    client = clickhouse_session()
    try:
        # Create database
        client.query(f"CREATE DATABASE IF NOT EXISTS {settings.CLICKHOUSE_DB_NAME}")
        # Switch to the specified database
        client.query(f"USE {settings.CLICKHOUSE_DB_NAME}")
        # Create `users` table if it does not exist
        client.query("""
            CREATE TABLE IF NOT EXISTS users
            (
                id UInt32,
                name String,
                email String,
                created_at DateTime
            ) ENGINE = MergeTree()
            ORDER BY id;
        """)
        logging.error("Table for clickhouse created")

    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        logging.error(format_exc())
    finally:
        client.close()
