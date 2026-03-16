from db import create_order, get_pending_orders, get_queue_position, init_db


def test_create_order_and_queue_position(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    first_order_id = create_order("Ava", "Latte", db_path)
    second_order_id = create_order("Noah", "Mocha", db_path)

    pending_orders = get_pending_orders(db_path)
    assert [order["id"] for order in pending_orders] == [first_order_id, second_order_id]

    assert get_queue_position(first_order_id, db_path) == 1
    assert get_queue_position(second_order_id, db_path) == 2
    assert get_queue_position(9999, db_path) is None
