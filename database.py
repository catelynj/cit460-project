import sqlite3
from datetime import datetime

DB_PATH = "/home/c8win/queries.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            query       TEXT NOT NULL,
            response    TEXT,
            status      TEXT,
            queried_at  TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_query(query: str, response: str, status: str = "success"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO query_history (query, response, status, queried_at) VALUES (?, ?, ?, ?)",
        (query, response, status, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()