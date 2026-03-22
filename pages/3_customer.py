import streamlit as st
from db import get_queue_position

st.set_page_config(page_title="Order Queue", page_icon=":coffee:")

st.subheader("Check Queue Position")
order_id = st.number_input("Enter your order number", min_value=1, step=1)
if st.button("Check position"):
    position = get_queue_position(int(order_id))
    if position is None:
        st.warning("Order not found in pending queue.")
    else:
        st.success(f"You are #{position} in the queue.")