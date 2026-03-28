import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv


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


def connect_bot():
    try:
        with open("bot_config.json", "r", encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        return False, "bot_config.json was not found."

    url = "https://api.meetstream.ai/api/v1/bots/create_bot"

    load_dotenv()
    api_key = os.getenv("MEET_STREAM_API_KEY")

    if not api_key:
        return False, "Please add MEET_STREAM_API_KEY to your .env file."

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        data = response.json()
        bot_id = data.get("bot_id")

        with open("last_bot_created.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return True, f"Bot connected successfully. Bot ID: {bot_id}"

    return False, f"Failed to connect bot. Status: {response.status_code}. {response.text}"


def disconnect_bot():
    try:
        with open("last_bot_created.json", "r", encoding="utf-8") as file:
            saved_data = json.load(file)
            bot_id = saved_data.get("bot_id")
    except FileNotFoundError:
        return False, "last_bot_created.json was not found. Connect a bot first."

    if not bot_id:
        return False, "No bot_id was found in last_bot_created.json."

    url = f"https://api.meetstream.ai/api/v1/bots/{bot_id}/remove_bot"

    load_dotenv()
    api_key = os.getenv("MEET_STREAM_API_KEY")

    if not api_key:
        return False, "Please add MEET_STREAM_API_KEY to your .env file."

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "bot_id": bot_id,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return True, f"Successfully removed bot: {bot_id}"

    return False, f"Failed to remove bot. Status: {response.status_code}. {response.text}"

