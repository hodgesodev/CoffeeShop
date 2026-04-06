import streamlit as st
from drink import Drink
from order import Order
from db import create_order, get_items, get_sizes_for_item

st.set_page_config(page_title="Register", page_icon=":coffee:", layout="wide")

TITLE_HEIGHT       = 70   # st.title
SUBHEADER_HEIGHT   = 50   # st.subheader
DETAIL_PANE_HEIGHT = 280  # detail section when a drink is selected
SUBMIT_BAR_HEIGHT  = 100  # divider + submit row
PADDING            = 40

SCROLL_HEIGHT = 768 - TITLE_HEIGHT - SUBHEADER_HEIGHT - DETAIL_PANE_HEIGHT - SUBMIT_BAR_HEIGHT - PADDING

drinks = get_items()

def init_order():
    st.session_state.order = Order()

if "order" not in st.session_state:
    init_order()

if "selected_drink" not in st.session_state:
    st.session_state.selected_drink = None

# Header
st.title("Register")

# Main columns
item_pane, order_pane = st.columns(2, gap="large")

with item_pane:
    st.subheader("Drinks")
    with st.container(height=SCROLL_HEIGHT + DETAIL_PANE_HEIGHT, border=False):
        for item in drinks:
            c = st.container(border=True)
            name_col, price_col, button_col = c.columns([3, 2, 2])
            is_selected = (
                st.session_state.selected_drink is not None
                and st.session_state.selected_drink["name"] == item["name"]
            )
            name_col.text(item["name"])
            price_col.text(f"${item['price']:.2f}")
            label = "Selected" if is_selected else "Select"
            if button_col.button(label=label, key=f"select_{item['name']}"):
                st.session_state.selected_drink = item
                st.rerun()

with order_pane:
    st.subheader("Order")

    # Detail pane
    with st.container(height=DETAIL_PANE_HEIGHT, border=True):
        selected = st.session_state.selected_drink
        if selected is None:
            st.markdown("*Select a drink to see details*")
        else:
            sizes = get_sizes_for_item(selected["name"])
            st.markdown(f"**{selected["name"]}**")
            st.caption(f"Base price: ${selected["price"]:.2f}")
            if not sizes:
                st.warning("No sizes available for this item.")
            else:
                size_labels = {s["name"].capitalize(): s for s in sizes}
                chosen_label = st.radio(
                    "Size", options=list(size_labels.keys()),
                    horizontal=True,
                    index=1 if len(size_labels) > 1 else 0,
                    key="size_radio",
                )
                chosen_size = size_labels[chosen_label]
                st.markdown(f"**Price: ${chosen_size['computed_price']:.2f}**")
                if st.button("Add to order", key="detail_add"):
                    drink = Drink(selected["name"], selected["price"])
                    st.session_state.order.add_drink(drink, chosen_size["name"], chosen_size["computed_price"])
                    st.rerun()

    # Order contents
    with st.container(height=SCROLL_HEIGHT, border=False):
        ordered_drinks = st.session_state.order.get_drinks()
        if not ordered_drinks:
            st.caption("No drinks added yet.")
        else:
            for (drink, size_name), quantity in ordered_drinks.items():
                unit_price = st.session_state.order.get_unit_price(drink, size_name)
                c = st.container(border=True)
                name_col, size_col, qty_col = c.columns([3, 2, 2])
                name_col.text(drink.get_name())
                size_col.text(size_name.capitalize())
                qty_col.text(f"x{quantity}  ${unit_price:.2f} ea")

# Submit bar
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("Clear Order"):
        init_order()
        st.rerun()
with col2:
    customer_name = st.text_input("Customer name").strip()
with col3:
    st.markdown(f"**Total: ${st.session_state.order.get_price():.2f}**")
    if st.button("Submit") and customer_name:
        create_order(customer_name, st.session_state.order)
        init_order()
        st.session_state.selected_drink = None
        st.rerun()