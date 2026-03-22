import streamlit as st
from db import get_pending_orders

st.set_page_config(page_title="Barista View", page_icon=":coffee:")

st.subheader("Pending Orders")
pending_orders = get_pending_orders()
if not pending_orders:
    st.info("No pending orders right now.")
else:
    st.dataframe(pending_orders, width="stretch", hide_index=True)
    st.write(f"Total pending: {len(pending_orders)}")