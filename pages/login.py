from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.meeting_agent import connect_bot, disconnect_bot



def render_login():
    header_col, connect_col, disconnect_col = st.columns([6, 1, 1])

    with header_col:
        st.title("Login")

    with connect_col:
        connect_clicked = st.button("Connect Bot", use_container_width=True)

    with disconnect_col:
        disconnect_clicked = st.button("Disconnect Bot", use_container_width=True)

    if connect_clicked:
        success, message = connect_bot()
        if success:
            st.success(message)
        else:
            st.error(message)

    if disconnect_clicked:
        success, message = disconnect_bot()
        if success:
            st.success(message)
        else:
            st.error(message)

    st.selectbox("Client", options=["Select a client"], index=0)
    st.button("Login")
