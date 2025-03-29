import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "artist_management"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
}

DB_CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
DB_MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "10"))
DB_MIN_CONNECTIONS = int(os.getenv("DB_MIN_CONNECTIONS", "1"))

SQL_TEMPLATES = {
    "FIND_BY_ID": "SELECT * FROM {table} WHERE id = %s",
    "FIND_ALL": "SELECT * FROM {table}",
    "DELETE_BY_ID": "DELETE FROM {table} WHERE id = %s",
    "COUNT_ALL": "SELECT COUNT(*) as total FROM {table}",
}
