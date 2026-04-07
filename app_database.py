import sqlite3
from pathlib import Path


DATABASE_FILE = "app_data.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    Path(DATABASE_FILE).touch(exist_ok=True)

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                request_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comments TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                request_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                intent TEXT NOT NULL,
                rag_used INTEGER NOT NULL
            )
        """)

        connection.commit()