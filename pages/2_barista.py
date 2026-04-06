import streamlit as st
from db import get_pending_orders, get_order, complete_order

st.set_page_config(page_title="Barista View", page_icon=":coffee:", layout="wide")

from ui_utils import apply_custom_theme
apply_custom_theme()

if "selected_order" not in st.session_state:
    st.session_state.selected_order = -1


left_column, right_column = st.columns(2)
pending_container = left_column.container(border=True)
selected_container = right_column.container(border=True)


pending_container.subheader("Pending Orders")
pending_orders = get_pending_orders()
if not pending_orders:
    pending_container.info("No pending orders right now.")
else:
    pending_container.markdown(f"**Total pending: {len(pending_orders)}**")

    col_widths = [1, 2.5, 2, 2, 1.8]
    header_c = pending_container.container()
    id_col, name_col, status_col, time_col, button_col = header_c.columns(col_widths, vertical_alignment="center")
    id_col.markdown("**ID**")
    name_col.markdown("**Name**")
    status_col.markdown("**Status**")
    time_col.markdown("**Time**")

    for order in pending_orders:
        c = pending_container.container(border=True)
        id_col, name_col, status_col, time_col, button_col = c.columns(col_widths, vertical_alignment="center")
        id_col.markdown(f"**#{order.get('order_id')}**")
        name_col.markdown(f"**{order.get('customer_name')}**")
        status_col.markdown(f"{order.get('status')}")
        
        # Only show time (HH:MM:SS) instead of full datestring to prevent awkward wrapping
        full_time = order.get('created_at', '')
        short_time = full_time.split(' ')[1] if ' ' in full_time else full_time
        time_col.markdown(f"{short_time}")
        if button_col.button("Select", key=f"button_{order.get('order_id')}"):
            st.session_state.selected_order = order.get('order_id')

if st.session_state.selected_order != -1:
    selected_container.markdown(f"### Order #{st.session_state.selected_order}")
    order = get_order(st.session_state.selected_order)
    selected_container.dataframe(order, hide_index=True)
    if selected_container.button("Mark Completed"):
        complete_order(st.session_state.selected_order)
        st.session_state.selected_order = -1
        st.rerun()