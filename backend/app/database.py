import sqlite3
from contextlib import contextmanager

DATABASE = "hexdocs.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Drop existing tables (optional, for development)
    cursor.executescript("""
        DROP TABLE IF EXISTS examples;
        DROP TABLE IF EXISTS parameters;
        DROP TABLE IF EXISTS functions;
        DROP TABLE IF EXISTS modules;
        DROP TABLE IF EXISTS applications;
    """)
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            version TEXT,
            description TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            name TEXT,
            url TEXT,
            description TEXT,
            FOREIGN KEY(application_id) REFERENCES applications(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            name TEXT,
            arity INTEGER,
            return_type TEXT,
            summary TEXT,
            description TEXT,
            FOREIGN KEY(module_id) REFERENCES modules(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function_id INTEGER,
            name TEXT,
            type TEXT,
            default_value TEXT,
            description TEXT,
            FOREIGN KEY(function_id) REFERENCES functions(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function_id INTEGER,
            code TEXT,
            description TEXT,
            FOREIGN KEY(function_id) REFERENCES functions(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            title TEXT,
            url TEXT,
            content TEXT,
            FOREIGN KEY(application_id) REFERENCES applications(id)
        )
    """)
    # Create other tables as needed (types, callbacks, structs, guides)
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()
