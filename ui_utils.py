import streamlit as st

def apply_custom_theme():
    # Inject CSS
    css = (
        "<style>"

        # Fonts
        "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');"
        "@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');"
        # Ensure background is cream
        ".stApp {"
        "    background-color: #F8F6F0 !important;"
        "}"



        # Banner – fixed to top, wood slats + Leopard Café sign
        ".stApp::before {"
        "    content: 'Leopard Café';"
        "    position: fixed;"
        "    top: 0;"
        "    left: 0;"
        "    right: 0;"
        "    height: 110px;"
        "    background: repeating-linear-gradient("
        "        90deg,"
        "        #b28a60, #b28a60 12px,"
        "        #8b653e 12px, #8b653e 14px,"
        "        #a67c52 14px, #a67c52 26px,"
        "        #7c5633 26px, #7c5633 28px"
        "    );"
        "    border-bottom: 7px solid #3d2009;"
        "    box-shadow: 0 4px 14px rgba(0,0,0,0.35);"
        "    z-index: 9000;"
        "    display: flex;"
        "    align-items: center;"
        "    justify-content: center;"
        "    color: #ffffff;"
        "    font-family: 'Outfit', sans-serif;"
        "    font-weight: 700;"
        "    font-size: 3.5rem;"
        "    letter-spacing: 5px;"
        "    text-shadow: 1px 1px 0 #999, 2px 2px 0 #888, 3px 3px 4px rgba(0,0,0,0.5);"
        "    pointer-events: none;"
        "}"

        # Push content below the banner
        ".block-container {"
        "    padding-top: 115px !important;"
        "    padding-bottom: 0px !important;"
        "    max-width: 100% !important;"
        "}"
        
        # Less aggressive compression so buttons don't overlap text
        "div[data-testid='stVerticalBlock'] { gap: 0.8rem !important; }"
        "div[data-testid='stMarkdownContainer'] p { margin-bottom: 0.5rem !important; }"

        # Sidebar above banner
        "section[data-testid='stSidebar'] {"
        "    background-color: #faf7f2 !important;"
        "    border-right: 2px solid #d4c3a3 !important;"
        "    z-index: 99999 !important;"
        "}"

        # Hide deploy button, keep hamburger
        ".stAppDeployButton { display: none !important; }"

        "header[data-testid='stHeader'] {"
        "    background: transparent !important;"
        "    z-index: 99998 !important;"
        "}"

        # Force Streamlit SVGs (like the sidebar arrow) to be dark coffee
        "button[data-testid='baseButton-header'] svg, "
        "button[data-testid='baseButton-headerNoPadding'] svg, "
        "button[kind='headerNoPadding'] svg, "
        ".stIcon svg, "
        ".material-symbols-rounded {"
        "    font-family: 'Material Symbols Rounded' !important;"
        "    font-variation-settings: 'FILL' 0, 'wght' 600, 'GRAD' 0, 'opsz' 24;"
        "    font-style: normal;"
        "    color: #2c1a0e !important;"
        "    fill: #2c1a0e !important;"
        "}"

        # Typography - completely exclude span so Streamlit can render its internal font-ligatures for icons
        "h1, h2, h3, h4 {"
        "    font-family: 'Outfit', sans-serif !important;"
        "    color: #2c1a0e !important;"
        "    font-weight: 700 !important;"
        "}"
        "p, label, div[data-testid='stMarkdownContainer'], div[data-testid='stText'] {"
        "    font-family: 'Outfit', sans-serif !important;"
        "    color: #1a1512 !important;"
        "}"

        # ── BROWN BORDERS on all bordered Streamlit containers ────────────
        "[data-testid='stVerticalBlockBorderWrapper'], "
        "[data-testid='stScrollableContainer'] {"
        "    border: 2px solid #d4c8bd !important; /* light rounded brown */"
        "    border-radius: 15px !important;"
        "    background-color: #ffffff !important;"
        "    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;"
        "    padding: 1rem !important;"
        "    margin-bottom: 1rem !important;"
        "}"

        # Nested bordered containers (item cards) – subtler inside
        "[data-testid='stVerticalBlockBorderWrapper'] [data-testid='stVerticalBlockBorderWrapper'], "
        "[data-testid='stScrollableContainer'] [data-testid='stVerticalBlockBorderWrapper'] {"
        "    border: 1px solid #e8e2da !important;"
        "    border-radius: 8px !important;"
        "    box-shadow: none !important;"
        "    padding: 0.5rem !important;"
        "}"

        # Buttons – always dark brown + white text
        ".stButton > button {"
        "    background-color: #4a3018 !important;"
        "    border: 2px solid #2c1a0e !important;"
        "    border-radius: 7px !important;"
        "    color: #ffffff !important;"
        "    font-family: 'Outfit', sans-serif !important;"
        "    font-weight: 700 !important;"
        "    box-shadow: 0 3px 6px rgba(0,0,0,0.25) !important;"
        "    transition: background-color 0.15s ease, transform 0.1s ease;"
        "}"
        ".stButton > button *, .stButton > button p {"
        "    color: #ffffff !important;"
        "    font-weight: 700 !important;"
        "}"
        ".stButton > button:hover {"
        "    background-color: #6e4926 !important;"
        "    transform: translateY(-1px);"
        "}"

        # Text inputs
        "div[data-testid='stTextInput'] input {"
        "    border: 2px solid #c4a882 !important;"
        "    border-radius: 7px !important;"
        "    background-color: #ffffff !important;"
        "    color: #1a1512 !important;"
        "    font-weight: 500 !important;"
        "}"

        # DataFrames
        "[data-testid='stDataFrame'] * {"
        "    color: #1a1512 !important;"
        "}"

        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)

    # JS: Rename "App" to "Main" in the sidebar natively without touching the filename
    js_code = """
    <script>
    function renameApp() {
        var elements = window.parent.document.querySelectorAll('[data-testid="stSidebarNav"] span');
        elements.forEach(function(el) {
            if (el.innerText === 'App') {
                el.innerText = 'Main';
            }
        });
    }
    // Run multiple times during load to ensure it catches the sidebar rendering
    renameApp();
    setTimeout(renameApp, 50);
    setTimeout(renameApp, 500);
    setTimeout(renameApp, 1500);
    </script>
    """
    st.html(js_code)


