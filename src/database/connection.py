import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    settings = {
        "host": os.getenv("DB_HOST") or os.getenv("DB_host"),
        "user": os.getenv("DB_USER") or os.getenv("DB_user"),
        "password": os.getenv("DB_PASSWORD") or os.getenv("DB_password"),
        "database": os.getenv("DB_NAME") or os.getenv("DB_name"),
    }
    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise RuntimeError(
            "MySQL configuration is missing: " + ", ".join(missing)
        )
    try:
        return mysql.connector.connect(**settings)
    except mysql.connector.Error as error:
        raise RuntimeError(f"Could not connect to MySQL: {error}") from error
