import streamlit as st
from drink import Drink
from order import Order

drinks = [
    {
        "name": "Coffee",
        "price": 2.50,
    },
    {
        "name": "Tea",
        "price": 1.50,
    },
    {
        "name": "Hot Chocolate",
        "price": 2.25,
    },
]

order = Order()
item_pane, order_pane = st.columns(
    spec=2,
    width="stretch",
)
with item_pane:
    st.header("Drinks")
    for item in drinks:
        c = st.container(
            width="stretch",
            horizontal=True,
            horizontal_alignment="left",
            vertical_alignment="center",
        )
        c.text(item["name"])
        c.text(f"${item["price"]: .2f}")
        if c.button(
            label="Add",
            key=f"add_{item['name']}",
        ):
            order.add_drink(Drink(item["name"], item["price"]))

with order_pane:
    st.header("Order")
    ordered_drinks = order.get_drinks()
    for drink in ordered_drinks:
        c = st.container(
            width="stretch",
            horizontal=True,
            horizontal_alignment="left",
            vertical_alignment="center",
        )
        c.text(drink.get_name())
        c.text(f"${drink.get_price(): .2f}")
        c.text(f"x{ordered_drinks.get(drink)}")


submit_container = st.container(
    width="stretch",
    height="stretch",
    horizontal=True,
    horizontal_alignment="center",
    vertical_alignment="center",
)

submit_container.text(f"${order.get_price(): .2f}")

submit_container.button(
    label="Submit",
)

