import sqlite3
import os

import sys

# Path to the local SQLite database file
if getattr(sys, 'frozen', False):
    # If running as a bundle, use the parent directory of the .exe folder
    # to prevent data loss during rebuilds.
    _base_dir = os.path.dirname(os.path.dirname(sys.executable))
else:
    # If running as a script, use the project root
    _base_dir = os.path.dirname(os.path.dirname(__file__))

_db_path = os.path.join(_base_dir, "tally.db")

def get_db_path():
    return _db_path


class SQLiteCursorWrapper:
    """
    A wrapper around an sqlite3 cursor that transparently converts
    MySQL-style %s parameter placeholders to SQLite-style ?.
    Also wraps the connection so db.commit() works as expected.
    """
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def execute(self, query, params=None):
        # Convert MySQL %s parameter syntax to SQLite ? syntax
        query = query.replace('%s', '?')
        if params is not None:
            return self._cursor.execute(query, params)
        else:
            return self._cursor.execute(query)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def commit(self):
        self._conn.commit()


# ---------------------------------------------------------------------------
# Module-level db and cursor used by models.py (schema creation only)
# For request handling, app.py imports `db` and `cursor` which are replaced
# per-request via the `get_connection()` helper below.
# ---------------------------------------------------------------------------
db = sqlite3.connect(_db_path, check_same_thread=False)
cursor = SQLiteCursorWrapper(db)


def get_connection():
    """
    Returns a fresh (conn, wrapped_cursor) pair for use in a single request.
    Each Flask request should call this to get its own connection, preventing
    thread-safety issues with a single shared cursor.
    """
    conn = sqlite3.connect(_db_path)
    return conn, SQLiteCursorWrapper(conn)