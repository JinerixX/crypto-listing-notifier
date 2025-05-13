import sqlite3

DB_NAME = "listings.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                market_type TEXT NOT NULL,
                UNIQUE(exchange, symbol)
            )
        """)

def is_db_empty() -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM listings")
        count = cur.fetchone()[0]
        return count == 0

def is_new_listing(exchange: str, symbol: str, market_type: str) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM listings WHERE exchange=? AND symbol=?", (exchange, symbol))
        exists = cur.fetchone()
        if not exists:
            cur.execute("INSERT INTO listings (exchange, symbol, market_type) VALUES (?, ?, ?)",
                        (exchange, symbol, market_type))
            conn.commit()
            return True
        return False
