import time
import streamlit as st
from drink import Drink
from order import Order
from db import create_order, get_items, get_sizes_for_item

st.set_page_config(page_title="Register", page_icon=":coffee:", layout="wide")

from ui_utils import apply_custom_theme
apply_custom_theme()

# Layout math updated for no-scroll:
# Banner: 110px. Dropped st.title to save 60px.
MENU_SCROLL_HEIGHT  = 400   # Drink cards scroll inside here
# Order Detail Pane dynamically sizes! 
ORDER_SCROLL_HEIGHT = 120   # Added items list

drinks = get_items()

def init_order():
    st.session_state.order = Order()

if "order" not in st.session_state:
    init_order()

if "selected_drink" not in st.session_state:
    st.session_state.selected_drink = None

# Success banner
if st.session_state.get("submit_success"):
    elapsed = time.time() - st.session_state.submit_success
    if elapsed < 1:
        st.success("Order placed successfully!")
        st.html(
            "<script>setTimeout(() => window.parent.location.reload(), 1000);</script>"
        )
    else:
        st.session_state.submit_success = None
        st.rerun()

# Removed st.title completely to save vertical space. The huge banner already says Leopard Cafe.

# ── Main two-column layout ─────────────────────────────────────────────────
item_pane, order_pane = st.columns(2, gap="large")

with item_pane:
    st.markdown("### Menu")
    # Brown-bordered outer box; only the drink cards inside scroll
    with st.container(height=MENU_SCROLL_HEIGHT, border=True):
        for item in drinks:
            c = st.container(border=False)
            name_col, price_col, button_col = c.columns([3, 2, 2])
            is_selected = (
                st.session_state.selected_drink is not None
                and st.session_state.selected_drink["name"] == item["name"]
            )
            name_col.markdown(f"**{item['name']}**")
            price_col.markdown(f"${item['price']:.2f}")
            label = "✔ Selected" if is_selected else "Select"
            if button_col.button(label=label, key=f"select_{item['name']}"):
                st.session_state.selected_drink = item
                st.rerun()

with order_pane:
    st.markdown("### Order")

    # ── Item detail / size picker ──────────────────────────────────────────
    with st.container(border=True): # NO fixed height, meaning NO CLIPPING ever!
        selected = st.session_state.selected_drink
        if selected is None:
            st.markdown("*Select a menu item to see options*")
        else:
            sizes = get_sizes_for_item(selected["name"])
            st.markdown(f"**{selected['name']}**")
            st.caption(f"Base price: ${selected['price']:.2f}")

            if not sizes:
                st.warning("No sizes available for this item.")
            else:
                one_size = len(sizes) == 1 and sizes[0]["name"] == "one_size"
                if one_size:
                    chosen_size = sizes[0]
                    st.markdown(f"**${chosen_size['computed_price']:.2f}**")
                    if st.button("Add to order", key="detail_add"):
                        drink = Drink(selected["name"], selected["price"])
                        st.session_state.order.add_drink(drink, chosen_size["name"], chosen_size["computed_price"])
                        st.rerun()
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

    # ── Current order items (scrollable) ─────────────────────────────────
    with st.container(height=ORDER_SCROLL_HEIGHT, border=True):
        ordered_drinks = st.session_state.order.get_drinks()
        if not ordered_drinks:
            st.caption("No items added yet.")
        else:
            for (drink, size_name), quantity in ordered_drinks.items():
                unit_price = st.session_state.order.get_unit_price(drink, size_name)
                col_name, col_size, col_qty = st.columns([3, 2, 2])
                col_name.markdown(f"**{drink.get_name()}**")
                col_size.markdown("" if size_name == "one_size" else size_name.capitalize())
                col_qty.markdown(f"x{quantity} &nbsp; **${unit_price:.2f} ea**")

# ── Submit bar (always visible at the bottom) ──────────────────────────────
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("🗑 Clear Order"):
        init_order()
        st.rerun()
with col2:
    if not st.session_state.get("submit_success"):
        customer_name = st.text_input("Customer name").strip()
    else:
        customer_name = ""
with col3:
    total = st.session_state.order.get_price()
    st.markdown(f"**Total: ${total:.2f}**")
    cannot_submit = not customer_name or total == 0.0
    if st.button("✔ Submit Order", disabled=cannot_submit):
        create_order(customer_name, st.session_state.order)
        init_order()
        st.session_state.selected_drink = None
        st.session_state.submit_success = time.time()
        st.rerun()
