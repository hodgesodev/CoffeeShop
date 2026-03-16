import streamlit as st

from db import create_order, get_pending_orders, get_queue_position, init_db

init_db()

st.set_page_config(page_title="Coffee Shop MVP", page_icon=":coffee:")
st.title("Coffee Shop MVP")
st.caption("Sprint 1 only: cashier, barista, and customer queue.")

view = st.sidebar.radio("Choose view", ["Cashier", "Barista", "Customer"])

if view == "Cashier":
    st.subheader("Create Order")
    with st.form("order_form", clear_on_submit=True):
        customer_name = st.text_input("Customer name")
        item = st.selectbox(
            "Drink",
            ["Latte", "Americano", "Cappuccino", "Mocha", "Tea"],
        )
        submitted = st.form_submit_button("Create order")

    if submitted:
        name = customer_name.strip()
        if not name:
            st.error("Please enter a customer name.")
        else:
            order_id = create_order(name, item)
            st.success(f"Order #{order_id} created for {name} ({item}).")

elif view == "Barista":
    st.subheader("Pending Orders")
    pending_orders = get_pending_orders()
    if not pending_orders:
        st.info("No pending orders right now.")
    else:
        st.dataframe(pending_orders, use_container_width=True, hide_index=True)
        st.write(f"Total pending: {len(pending_orders)}")

else:
    st.subheader("Check Queue Position")
    order_id = st.number_input("Enter your order number", min_value=1, step=1)
    if st.button("Check position"):
        position = get_queue_position(int(order_id))
        if position is None:
            st.warning("Order not found in pending queue.")
        else:
            st.success(f"You are #{position} in the queue.")
