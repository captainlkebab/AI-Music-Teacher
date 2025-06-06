import sqlite3
import os

DATABASE_NAME = 'sheet_music.db'

def initialize_db():
    """
    Initializes the SQLite database and creates the sheet_music table
    if it doesn't already exist.
    """
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sheet_music (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            piece_name TEXT NOT NULL,
            difficulty_level TEXT,
            composer_name TEXT,
            pdf_file_reference TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' initialized successfully.")

def get_db_connection():
    """
    Establishes and returns a connection to the database.
    """
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

if __name__ == '__main__':
    initialize_db()
