import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'learning_platform.db')

def get_db_connection():
    """Returns a SQLite connection with dict-like row access."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    except Exception as e:
        print(f"Error opening SQLite database: {e}")
        return None

def init_db():
    """Initialises the SQLite database schema (safe to run multiple times)."""
    conn = get_db_connection()
    if not conn:
        print("WARNING: Could not open SQLite database.")
        return

    cur = conn.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            email     TEXT    UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            learning_style TEXT,
            streak_count   INTEGER DEFAULT 0,
            last_login     TEXT,
            created_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS quiz_responses (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER REFERENCES users(id) ON DELETE CASCADE,
            question  TEXT NOT NULL,
            answer    TEXT NOT NULL,
            learning_style_weight TEXT
        );

        CREATE TABLE IF NOT EXISTS resources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title       TEXT NOT NULL,
            link        TEXT NOT NULL,
            type        TEXT,
            platform    TEXT,
            description TEXT,
            saved_at    TEXT DEFAULT (datetime('now'))
        );
    ''')

    conn.commit()
    conn.close()
    print(f"SQLite database ready at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
