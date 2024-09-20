import sqlite3
from contextlib import contextmanager

DATABASE = "hexdocs.db"


def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag TEXT,
        text TEXT,
        link TEXT,
        embedding BLOB
    )
    """
    )
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()
