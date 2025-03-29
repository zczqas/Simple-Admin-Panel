from typing import Dict, List, Tuple, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from app.config.db.base import DB_CONFIG, DB_MAX_CONNECTIONS, DB_MIN_CONNECTIONS

connection_pool = SimpleConnectionPool(
    DB_MIN_CONNECTIONS, DB_MAX_CONNECTIONS, **DB_CONFIG
)


@contextmanager
def get_connection():
    """
    Context manager for database connections.
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            connection_pool.putconn(conn)


@contextmanager
def get_cursor():
    """
    Context manager for database cursors.
    """
    with get_connection() as conn:
        cursor = None
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()


def execute_query(query: str, params: Optional[Tuple] = None) -> None:
    """
    Execute a SQL query without returning results (for INSERT, UPDATE, DELETE).
    """
    with get_cursor() as cursor:
        cursor.execute(query, params or ())


def fetch_one(query: str, params: Optional[Tuple] = None) -> Dict:
    """
    Execute a query and fetch a single result row.
    """
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchone()


def fetch_all(query: str, params: Optional[Tuple] = None) -> List[Dict]:
    """
    Execute a query and fetch all result rows.
    """
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()


def fetch_paginated(
    query: str, params: Optional[Tuple] = None, page: int = 1, page_size: int = 10
) -> Tuple[List[Dict], int]:
    """
    Execute a query with pagination support.
    """
    offset = (page - 1) * page_size

    paginated_query = f"{query} LIMIT %s OFFSET %s"

    paginated_params = list(params or ())
    paginated_params.extend([page_size, offset])

    try:
        from_part = query.split("FROM")[1]
        if "ORDER BY" in from_part.upper():
            from_part = from_part.split("ORDER BY")[0]

        count_query = f"SELECT COUNT(*) as total FROM {from_part}"
    except (IndexError, AttributeError):
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_query"

    with get_cursor() as cursor:
        cursor.execute(count_query, params or ())
        total = cursor.fetchone()["total"]

        cursor.execute(paginated_query, tuple(paginated_params))
        results = cursor.fetchall()

    return results, total


def transaction():
    """
    Context manager for transactions.
    Commits if no exceptions, rolls back if there are any.
    """

    @contextmanager
    def transaction_context():
        conn = connection_pool.getconn()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            connection_pool.putconn(conn)

    return transaction_context()
