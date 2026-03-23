import streamlit as st

from db import init_db

if "database_initialized" not in st.session_state:
    st.session_state.database_initialized = False

if not st.session_state.database_initialized:
    init_db()
    st.session_state.database_initialized = True

st.set_page_config(page_title="Coffee Shop MVP", page_icon=":coffee:")
st.title("Coffee Shop MVP")
st.caption("Sprint 1 only: cashier, barista, and customer queue.")

st.sidebar.title("Coffee Shop")