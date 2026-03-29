from pathlib import Path
import sqlite3
from typing import Any
from order import Order

DEFAULT_DB_PATH = Path("coffeeshop.db")
SCHEMA_VERSION = 2

SEED_ITEMS = [
    ("Coffee", 2.25),
    ("Cafe au Lait", 3.25),
    ("Cold Brew", 2.55),
    ("Double Espresso", 2.45),
    ("Macchiato", 2.95),
    ("Mocha", 2.55),
    ("Chai Latte", 2.55),
]

SEED_SIZES = [
    ("small", 0.85),
    ("medium", 1.0),
    ("large", 1.2),
]


def _connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _get_version(conn: sqlite3.Connection) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def _set_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(f"PRAGMA user_version = {version}")


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        version = _get_version(conn)

        if version < 1:
            _migrate_v1(conn)
            _set_version(conn, 1)

        if version < 2:
            _migrate_v2(conn)
            _set_version(conn, 2)

    for name, price in SEED_ITEMS:
        add_drink_to_db(name, price, db_path)

    for name, multiplier in SEED_SIZES:
        add_size_to_db(name, multiplier, db_path)

    _seed_item_sizes(db_path)


def _migrate_v1(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name   TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'pending'
                                    CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
            created_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS items (
            item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    UNIQUE NOT NULL,
            price       DECIMAL NOT NULL CHECK(price >= 0),
            available   INTEGER NOT NULL DEFAULT 1 CHECK(available IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS order_details (
            order_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id        INTEGER NOT NULL,
            item_id         INTEGER NOT NULL,
            quantity        INTEGER NOT NULL CHECK(quantity > 0),
            unit_price      DECIMAL NOT NULL CHECK(unit_price >= 0),
            CONSTRAINT  uq_order_item UNIQUE (order_id, item_id),
            CONSTRAINT  fk_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id)  ON DELETE CASCADE,
            CONSTRAINT  fk_item_id  FOREIGN KEY (item_id)  REFERENCES items(item_id)    ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_orders_status          ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_order_details_order_id ON order_details(order_id);
        """
    )


def _migrate_v2(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sizes (
            size_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    UNIQUE NOT NULL,
            multiplier  REAL    NOT NULL DEFAULT 1.0 CHECK(multiplier > 0)
        );

        CREATE TABLE IF NOT EXISTS item_sizes (
            item_id     INTEGER NOT NULL,
            size_id     INTEGER NOT NULL,
            PRIMARY KEY (item_id, size_id),
            FOREIGN KEY (item_id) REFERENCES items(item_id)  ON DELETE CASCADE,
            FOREIGN KEY (size_id) REFERENCES sizes(size_id)  ON DELETE CASCADE
        );

        ALTER TABLE order_details ADD COLUMN size_id INTEGER REFERENCES sizes(size_id) ON DELETE RESTRICT;
        """
    )


def add_drink_to_db(name: str, price: float, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO items (name, price)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM items WHERE name = ?
            )
            """,
            (name, price, name),
        )


def add_size_to_db(name: str, multiplier: float, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sizes (name, multiplier)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM sizes WHERE name = ?
            )
            """,
            (name, multiplier, name),
        )


def _seed_item_sizes(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO item_sizes (item_id, size_id)
            SELECT items.item_id, sizes.size_id
            FROM items
            CROSS JOIN sizes
            """
        )


def get_sizes(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT size_id, name, multiplier
            FROM sizes
            ORDER BY multiplier ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_sizes_for_item(item_name: str, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT sizes.size_id, sizes.name, sizes.multiplier,
                   ROUND(items.price * sizes.multiplier, 2) AS computed_price
            FROM item_sizes
            INNER JOIN items ON item_sizes.item_id = items.item_id
            INNER JOIN sizes ON item_sizes.size_id = sizes.size_id
            WHERE items.name = ? AND items.available = 1
            ORDER BY sizes.multiplier ASC
            """,
            (item_name,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_order(
    customer_name: str, order: Order, db_path: str | Path = DEFAULT_DB_PATH
) -> int:
    with _connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO orders (customer_name, status)
            VALUES (?, 'pending')
            """,
            (customer_name,),
        )
        order_id = cursor.lastrowid

        for (item, size_name), quantity in order.get_drinks().items():
            drink_row = cursor.execute(
                """
                SELECT items.item_id, items.price, sizes.size_id, sizes.multiplier
                FROM items
                INNER JOIN item_sizes ON items.item_id = item_sizes.item_id
                INNER JOIN sizes ON item_sizes.size_id = sizes.size_id
                WHERE items.name = ? AND sizes.name = ? AND items.available = 1
                """,
                (item.get_name(), size_name),
            ).fetchone()

            if drink_row is None:
                raise ValueError(
                    f"Drink '{item.get_name()}' with size '{size_name}' not found (order {order_id})"
                )

            unit_price = round(drink_row["price"] * drink_row["multiplier"], 2)

            cursor.execute(
                """
                INSERT INTO order_details (order_id, item_id, size_id, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, drink_row["item_id"], drink_row["size_id"], quantity, unit_price),
            )

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
            SELECT items.name, sizes.name AS size, order_details.quantity, order_details.unit_price
            FROM order_details
            INNER JOIN items ON order_details.item_id = items.item_id
            INNER JOIN sizes ON order_details.size_id = sizes.size_id
            WHERE order_details.order_id = ?
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


def get_items(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT name, price
            FROM items
            WHERE available = 1
            """
        ).fetchall()
    return [dict(row) for row in rows]


def complete_order(order_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            UPDATE orders
            SET status = 'completed', updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
            """,
            (order_id,),
        )