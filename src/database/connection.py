import sqlite3
from contextlib import contextmanager
from src.config.settings import DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@contextmanager
def session():
    """Commit/rollback and always close a connection around one operation."""
    conn = connect()
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def initialize():
    with session() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS businesses (id TEXT PRIMARY KEY, profile_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS quotes (id TEXT PRIMARY KEY, business_id TEXT NOT NULL, quote_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Saved', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS quote_revisions (id INTEGER PRIMARY KEY AUTOINCREMENT, quote_id TEXT NOT NULL, revision INTEGER NOT NULL, quote_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(quote_id, revision));
        CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, business_id TEXT NOT NULL, quote_id TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS order_events (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS consents (id INTEGER PRIMARY KEY AUTOINCREMENT, business_id TEXT NOT NULL, purpose TEXT NOT NULL, granted INTEGER NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS kyc_results (id INTEGER PRIMARY KEY AUTOINCREMENT, business_id TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
