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
            price DECIMAL NOT NULL,
            is_food BOOLEAN NOT NULL DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS item_sizes (
            size_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            size_name TEXT NOT NULL,
            price DECIMAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        );
        
        CREATE TABLE IF NOT EXISTS order_details (
            order_id INTEGER,
            item_id INTEGER,
            quantity INTEGER NOT NULL,
            size TEXT,
            CONSTRAINT fk_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id),
            CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items(item_id)
        );
        """
    )
    
    # Add is_food column if it doesn't exist (for migration)
    try:
        cursor.execute("ALTER TABLE items ADD COLUMN is_food BOOLEAN NOT NULL DEFAULT 0;")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add size column to order_details if it doesn't exist
    try:
        cursor.execute("ALTER TABLE order_details ADD COLUMN size TEXT;")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

    add_product_to_db("Coffee", 2.25)
    add_item_size("Coffee", "Small", 2.00)
    add_item_size("Coffee", "Medium", 2.25)
    add_item_size("Coffee", "Large", 2.50)
    add_product_to_db("Cafe au Lait", 3.25)
    add_item_size("Cafe au Lait", "Small", 3.00)
    add_item_size("Cafe au Lait", "Medium", 3.25)
    add_item_size("Cafe au Lait", "Large", 3.50)
    add_product_to_db("Cold Brew", 2.55)
    add_item_size("Cold Brew", "Small", 2.30)
    add_item_size("Cold Brew", "Medium", 2.55)
    add_item_size("Cold Brew", "Large", 2.80)
    add_product_to_db("Double Espresso", 2.45)
    add_item_size("Double Espresso", "Small", 2.20)
    add_item_size("Double Espresso", "Medium", 2.45)
    add_item_size("Double Espresso", "Large", 2.70)
    add_product_to_db("Macchiato", 2.95)
    add_item_size("Macchiato", "Small", 2.70)
    add_item_size("Macchiato", "Medium", 2.95)
    add_item_size("Macchiato", "Large", 3.20)
    add_product_to_db("Mocha", 2.55)
    add_item_size("Mocha", "Small", 2.30)
    add_item_size("Mocha", "Medium", 2.55)
    add_item_size("Mocha", "Large", 2.80)
    add_product_to_db("Chai Latte", 2.55)
    add_item_size("Chai Latte", "Small", 2.30)
    add_item_size("Chai Latte", "Medium", 2.55)
    add_item_size("Chai Latte", "Large", 2.80)
    add_product_to_db("Matcha Latte", 2.55)
    add_item_size("Matcha Latte", "Small", 2.30)
    add_item_size("Matcha Latte", "Medium", 2.55)
    add_item_size("Matcha Latte", "Large", 2.80)
    add_product_to_db("Bacon, Egg & Cheese", 2.75, True)
    add_product_to_db("Sausage, Egg & Cheese", 2.75, True)
    add_product_to_db("Ham, Egg & Cheese", 2.75, True)
    add_product_to_db("Spinach, Egg & Cheese", 2.75, True)
    add_product_to_db("Bagel with Cream Cheese", 1.75, True)


def add_product_to_db(name: str, price: float, is_food: bool = False, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO items (name, price, is_food)
            SELECT ?, ?, ?
            WHERE NOT EXISTS(
                Select items.name FROM items WHERE name = ?
            );
            """,
            (name, price, is_food, name,),
        )

def add_item_size(item_name: str, size_name: str, price: float, db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO item_sizes (item_id, size_name, price)
            SELECT item_id, ?, ?
            FROM items
            WHERE name = ? AND NOT EXISTS(
                SELECT 1 FROM item_sizes WHERE item_id = items.item_id AND size_name = ?
            )
            """,
            (size_name, price, item_name, size_name),
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
        # Parse base name and size from drink name (e.g., "Coffee (Medium)" -> "Coffee", "Medium")
        full_name = item.get_name()
        if ' (' in full_name and full_name.endswith(')'):
            base_name = full_name.split(' (')[0]
            size = full_name.split(' (')[1][:-1]  # Remove closing )
        else:
            base_name = full_name
            size = None
        drink_row = cursor.execute(
            """
            SELECT item_id
            FROM items
            WHERE name = ?
            """,
            (base_name,),
        ).fetchone()
        if drink_row is None:
            error(f"Drink {base_name} not found in database from order: {order_id}")
            return -1
        else:
            cursor.execute(
                """
                INSERT INTO order_details (order_id, item_id, quantity, size)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, drink_row["item_id"], drinks[item], size),
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
            SELECT items.name, order_details.quantity, order_details.size
            FROM order_details
            INNER JOIN items ON order_details.item_id = items.item_id
            WHERE order_id = ?;
            """,
            (order_id,),
        ).fetchall()
        # Construct full name with size if present
        result = []
        for row in rows:
            name = row['name']
            if row['size']:
                name += f" ({row['size']})"
            result.append({'name': name, 'quantity': row['quantity']})
        return result

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

def get_items() -> list[dict[str, Any]]:
    with _connect(DEFAULT_DB_PATH) as conn:
        # Get base items
        items = conn.execute(
            """
            SELECT item_id, name, price, is_food
            FROM items
            """
        ).fetchall()
        
        result = []
        for item in items:
            item_dict = dict(item)
            if not item_dict['is_food']:
                # Get sizes for drinks
                sizes = conn.execute(
                    """
                    SELECT size_name, price
                    FROM item_sizes
                    WHERE item_id = ?
                    ORDER BY price ASC
                    """,
                    (item_dict['item_id'],)
                ).fetchall()
                item_dict['sizes'] = [dict(size) for size in sizes]
            else:
                item_dict['sizes'] = []
            result.append(item_dict)
    return result

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