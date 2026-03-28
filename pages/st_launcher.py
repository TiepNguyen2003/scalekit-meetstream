import streamlit as st

from login import render_login

st.set_page_config(page_title="Launcher", page_icon=":rocket:", layout="wide")

render_login()
