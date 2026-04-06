import streamlit as st
from db import get_pending_orders

st.set_page_config(page_title="Order Queue", page_icon=":coffee:", layout="wide")

from ui_utils import apply_custom_theme
apply_custom_theme()


pending_container = st.container(border=True)
pending_container.subheader("Pending Orders")
pending_orders = get_pending_orders()
if not pending_orders:
    pending_container.info("No orders in the system right now.")
else:
    pending_container.markdown(f"**Total pending: {len(pending_orders)}**")

    col_widths = [1, 3, 2]
    header_c = pending_container.container()
    index_col, name_col, status_col = header_c.columns(col_widths, vertical_alignment="center")
    index_col.markdown("**Order**")
    name_col.markdown("**Name**")
    status_col.markdown("**Status**")

    for i in range(len(pending_orders)):
        order = pending_orders[i]
        c = pending_container.container(border=True)
        index_col, name_col, status_col = c.columns(col_widths, vertical_alignment="center")
        index_col.markdown(f"**#{i+1}**")
        name_col.markdown(f"**{order.get('customer_name')}**")
        status_col.markdown(f"{order.get('status')}")
