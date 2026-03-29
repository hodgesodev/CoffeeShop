import streamlit as st
from db import get_pending_orders

st.set_page_config(page_title="Order Queue", page_icon=":coffee:")

pane_height = 600
pending_container = st.container(height=pane_height, width="content", border=False)
pending_container.subheader("Pending Orders")
pending_orders = get_pending_orders()
if not pending_orders:
    pending_container.info("No pending orders right now.")
else:
    pending_container.write(f"Total pending: {len(pending_orders)}")

    for i in range(len(pending_orders)):
        order = pending_orders[i]
        c = pending_container.container(horizontal=True)
        index_col, name_col, status_col, = pending_container.columns(3, vertical_alignment="center")
        index_col.text(f"#{i+1}")
        name_col.text(f"{order.get('customer_name')}")
        status_col.text(f"{order.get('status')}")
