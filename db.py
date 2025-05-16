import sqlite3

DB_NAME = "listings.db"

_seen = []    


def init_db():
    """Создаём таблицу (если нужно) и заполняем _seen."""
    with sqlite3.connect(DB_NAME) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS listings (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   exchange TEXT NOT NULL,
                   symbol   TEXT NOT NULL,
                   market_type TEXT NOT NULL,
                   UNIQUE(exchange, symbol)
               )"""
        )
        _seen.extend(con.execute("SELECT exchange, symbol FROM listings"))


def is_db_empty() -> bool:
    return len(_seen) == 0


def is_new_listing(exchange: str, symbol: str, market_type: str) -> bool:
    pair = (exchange, symbol)
    if pair in _seen:
        return False        

    with sqlite3.connect(DB_NAME) as con:
        con.execute(
            "INSERT OR IGNORE INTO listings (exchange, symbol, market_type) "
            "VALUES (?, ?, ?)",
            (exchange, symbol, market_type),
        )
        con.commit()

    _seen.append(pair)        # добавляем
    return True
