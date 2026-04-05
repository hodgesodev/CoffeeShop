import streamlit as st
from db import get_pending_orders, get_order, complete_order

st.set_page_config(page_title="Barista View", page_icon=":coffee:", layout="wide")

if "selected_order" not in st.session_state:
    st.session_state.selected_order = -1

pane_height = 600
left_column, right_column = st.columns(2)
pending_container = left_column.container(height=pane_height, width="stretch", border=False)
selected_container = right_column.container(height=pane_height, width="stretch", border=False)


pending_container.subheader("Pending Orders")
pending_orders = get_pending_orders()
if not pending_orders:
    pending_container.info("No pending orders right now.")
else:
    pending_container.write(f"Total pending: {len(pending_orders)}")

    with pending_container.container(horizontal=True):
        id_col, name_col, status_col, time_col, button_col = pending_container.columns(5, vertical_alignment="center")
        id_col.subheader("Order Id")
        name_col.subheader("Name")
        status_col.subheader("Status")
        time_col.subheader("Time")

    for order in pending_orders:
        c = pending_container.container(horizontal=True)

        id_col, name_col, status_col, time_col, button_col = pending_container.columns(5, vertical_alignment="center")
        id_col.text(f"{order.get('order_id')}")
        name_col.text(f"{order.get('customer_name')}")
        status_col.text(f"{order.get('status')}")
        time_col.text(f"{order.get('created_at')}")
        if button_col.button("Select", key=f"button_{order.get("order_id")}"):
            st.session_state.selected_order = order.get('order_id')

if st.session_state.selected_order != -1:
    selected_container.text(f"Order #{st.session_state.selected_order}")
    order = get_order(st.session_state.selected_order)
    selected_container.dataframe(order, hide_index=True, width="stretch")
    if selected_container.button("Mark Completed"):
        complete_order(st.session_state.selected_order)
        st.session_state.selected_order = -1
        st.rerun()