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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
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

# Add some sample data
def add_sample_blog_posts():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blog_posts")  # Clear existing data
        cursor.execute("INSERT INTO blog_posts (title, content) VALUES (?, ?)",
                       ("First Blog Post", "This is the content of the first blog post."))
        cursor.execute("INSERT INTO blog_posts (title, content) VALUES (?, ?)",
                       ("Second Blog Post", "This is the content of the second blog post."))
        conn.commit()
    print("Sample blog posts added successfully.")

# This function will be called by our new poetry command
def seed_database():
    initialize_database()
    add_sample_blog_posts()
