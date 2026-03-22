from pathlib import Path
import sqlite3
from typing import Any
from order import Order
from streamlit import error

DEFAULT_DB_PATH = Path("coffeeshop.db")

def _connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    conn = _connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(
        """
        PRAGMA foreign_keys = ON;
        
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price DECIMAL NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS order_details (
            order_id INTEGER,
            item_id INTEGER,
            quantity INTEGER NOT NULL,
            CONSTRAINT fk_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id),
            CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items(item_id)
        );
        """
    )
    conn.commit()
    conn.close()

    add_drink_to_db("Coffee", 2.25)
    add_drink_to_db("Cafe au Lait", 3.25)
    add_drink_to_db("Cold Brew", 2.55)
    add_drink_to_db("Double Espresso", 2.45)
    add_drink_to_db("Macchiato", 2.95)
    add_drink_to_db("Mocha", 2.55)
    add_drink_to_db("Chai Latte", 2.55)

def add_drink_to_db(name: str, price: float, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO items (name, price)
            SELECT ?, ?
            WHERE NOT EXISTS(
                Select items.name FROM items WHERE name = ?
            );
            """,
            (name, price, name,),
        )

def create_order(
    customer_name: str, order: Order, db_path: str | Path = DEFAULT_DB_PATH
) -> int:
    conn = _connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders (customer_name, status)
        VALUES (?, 'pending')
        """,
        (customer_name,),
    )
    order_id = cursor.lastrowid
    drinks = order.get_drinks()
    for item in drinks:
        drink_row = cursor.execute(
            """
            SELECT item_id, name, price
            FROM items
            WHERE name = ?
            """,
            (item.get_name(),),
        ).fetchone()
        if drink_row is None:
            error(f"Drink {item.get_name()} not found in database from order: {order_id}")
            return -1
        else:
            cursor.execute(
                """
                INSERT INTO order_details (order_id, item_id, quantity)
                VALUES (?, ?, ?)
                """,
                (order_id, drink_row["item_id"], drinks[item],),
            )
    conn.commit()
    conn.close()

    return order_id

def get_pending_orders(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT order_id, customer_name, status, created_at
            FROM orders
            WHERE status = 'pending'
            ORDER BY order_id ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]

def get_order(order_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT items.name, order_details.quantity
            FROM order_details
            INNER JOIN items ON order_details.item_id = items.item_id
            WHERE order_id = ?;
            """,
            (order_id,),
        ).fetchall()
    return [dict(row) for row in rows]

def get_queue_position(
    order_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> int | None:
    with _connect(db_path) as conn:
        order = conn.execute(
            """
            SELECT order_id
            FROM orders
            WHERE order_id = ? AND status = 'pending'
            """,
            (order_id,),
        ).fetchone()

        if order is None:
            return None

        row = conn.execute(
            """
            SELECT COUNT(*) AS position
            FROM orders
            WHERE status = 'pending' AND order_id <= ?
            """,
            (order_id,),
        ).fetchone()
    return int(row["position"])

def get_items() -> list[dict[str, int]]:
    with _connect(DEFAULT_DB_PATH) as conn:
        items = conn.execute(
            """
            SELECT name, price
            FROM items
            """
        ).fetchall()
    return [dict(row) for row in items]

def complete_order(order_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            UPDATE orders
            SET status = 'completed'
            WHERE order_id = ?
            """,
            (order_id,),
        )