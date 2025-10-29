import logging
import mysql.connector
from config import Config

_PLACEHOLDER_VALUES = {"your_db_host", "your_db_user", "your_db_password", "your_db_name"}


def _db_configured() -> bool:
    return all([
        Config.DB_HOST,
        Config.DB_USER,
        Config.DB_PASSWORD,
        Config.DB_NAME,
    ]) and Config.DB_HOST not in _PLACEHOLDER_VALUES


def get_customer_info(user_id):
    """Fetch customer info from the database when credentials are configured."""
    if not _db_configured():
        logging.debug("Database credentials not provided; skipping customer lookup.")
        return {}

    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE id=%s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result or {}
    except Exception as e:
        logging.warning(f"Customer DB lookup failed for user {user_id}: {e}")
        return {}
