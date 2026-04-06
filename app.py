import os
import streamlit as st

from db import init_db

if "database_initialized" not in st.session_state:
    st.session_state.database_initialized = False

if not st.session_state.database_initialized:
    init_db()
    st.session_state.database_initialized = True

st.set_page_config(page_title="Leopard Cafe", page_icon=":coffee:", layout="wide")

from ui_utils import apply_custom_theme
apply_custom_theme()


col1, col2 = st.columns([1.25, 1.2], gap="large")

with col1:
    if os.path.exists("Menu.png"):
        st.image("Menu.png", use_container_width=True)
    else:
        st.info("Upload Menu.png here")
        
    with st.container(border=True):
        st.markdown("""
        **ℹ️ About Us**<br>
        A grab-and-go coffee shop offering freshly brewed New England coffee, espresso-based drinks, iced beverages, pastries, and sandwiches.
        """, unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown("### Leopard Cafe")
        st.markdown("📍 **Location:** Beatty Hall &nbsp; | &nbsp; **Status:** <span style='color:#a83232; font-weight:bold;'>Closed</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("""
        **🕒 Hours of Operation**<br>
        • &nbsp; **Mon-Fri:** 07:00 AM - 02:00 PM<br>
        • &nbsp; **Mon-Thu (Late):** 08:00 PM - 10:00 PM<br>
        • &nbsp; **Weekend:** Closed
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("💳 **Accepted Tenders:** Dining Points, Flex, Credit, Debit, Cash")

import base64

def get_base64_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

ticket_path = None
for ext in ["png", "jpg", "jpeg"]:
    if os.path.exists(f"ticket.{ext}"):
        ticket_path = f"ticket.{ext}"
        break

if ticket_path:
    b64_img = get_base64_image(ticket_path)
    mime = "image/png" if ticket_path.endswith("png") else "image/jpeg"
    st.markdown(f"""
        <img src="data:{mime};base64,{b64_img}" style="
            position: fixed;
            bottom: -30px;
            right: 60px;
            width: 350px;
            z-index: 99999;
            transform: rotate(-15deg);
            pointer-events: none;
            filter: drop-shadow(0px 8px 16px rgba(0,0,0,0.3));
        ">
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 40px;
            z-index: 9999;
            padding: 1rem;
            border: 2px dashed #a67c52;
            border-radius: 10px;
            color: #4a3018;
            background: rgba(255,255,255,0.8);
        ">
        </div>
    """, unsafe_allow_html=True)