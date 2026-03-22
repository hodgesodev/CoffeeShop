import streamlit as st
from drink import Drink
from order import Order

st.set_page_config(page_title="Register", page_icon=":coffee:", layout="wide")

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

pane_height = 600

def init_order():
    st.session_state.order = Order()

if "order" not in st.session_state: ## doing this here is fine, it can happen later, but must be before use
    init_order()

item_pane, order_pane = st.columns(
    spec=2,
    width="stretch",
    gap="large",
)
item_pane.header("Drinks")
order_pane.header("Order")
menu = item_pane.container(height=pane_height, width="stretch")
order_contents = order_pane.container(width="stretch", height=pane_height)

## We initialize and use this container in between initialization and use of the panes in order to force proper
## function call order
submit_container = st.container(
    width="stretch",
    height="stretch",
    horizontal=True,
    horizontal_alignment="center",
    vertical_alignment="bottom",
)

if submit_container.button(label="Clear Order"):
    init_order()

customer_name = submit_container.text_input("Customer name")

submit_container.text("Price:")
submit_container.text(f"${st.session_state.order.get_price(): .2f}")

submit_container.button(label="Submit")

with menu: ## This pane should hold all the available drinks that can be added to the order
    for item in drinks:
        c = st.container(
            width="stretch",
            horizontal=True,
            horizontal_alignment="left",
            vertical_alignment="center",
            border=True,
        )
        name_col = c.container(
            vertical_alignment="center",
            horizontal_alignment="left",
        )
        price_col = c.container(
            vertical_alignment="center",
            horizontal_alignment="center",
        )
        button_col = c.container(
            vertical_alignment="center",
            horizontal_alignment="right",
        )

        name_col.text(item['name'])
        price_col.text(f"${item['price']: .2f}")
        if button_col.button(label="Add to order", key=f"add_{item['name']}", width="stretch"):
            st.session_state.order.add_drink(Drink(item['name'], item['price']))

with (order_contents): ## This pane holds all drinks in the order
    ordered_drinks = st.session_state.order.get_drinks()

    for (drink) in ordered_drinks:
        c = st.container(
            width="stretch",
            horizontal=True,
            horizontal_alignment="left",
            vertical_alignment="bottom",
            border=True,
        )
        name_col = c.container(
            vertical_alignment="center",
            horizontal_alignment="left",
        )
        price_col = c.container(
            vertical_alignment="center",
            horizontal_alignment="center",
        )
        qty_col = c.container(
            vertical_alignment="center",
            horizontal_alignment="right",
        )

        name_col.text(drink.get_name())
        price_col.text(f"${drink.get_price(): .2f}")
        qty_col.text(f"x{ordered_drinks.get(drink)}")



