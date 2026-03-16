from pathlib import Path
import sqlite3
from typing import Any

DEFAULT_DB_PATH = Path("coffeeshop.db")


def _connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                item TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def create_order(
    customer_name: str, item: str, db_path: str | Path = DEFAULT_DB_PATH
) -> int:
    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO orders (customer_name, item, status)
            VALUES (?, ?, 'pending')
            """,
            (customer_name, item),
        )
        return int(cursor.lastrowid)


def get_pending_orders(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, customer_name, item, status, created_at
            FROM orders
            WHERE status = 'pending'
            ORDER BY id ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_queue_position(
    order_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> int | None:
    with _connect(db_path) as conn:
        order = conn.execute(
            """
            SELECT id
            FROM orders
            WHERE id = ? AND status = 'pending'
            """,
            (order_id,),
        ).fetchone()

        if order is None:
            return None

        row = conn.execute(
            """
            SELECT COUNT(*) AS position
            FROM orders
            WHERE status = 'pending' AND id <= ?
            """,
            (order_id,),
        ).fetchone()
    return int(row["position"])
