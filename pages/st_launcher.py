import json
from pathlib import Path

import streamlit as st

from login import render_login
from src.meeting_agent import connect_bot, disconnect_bot
from src.transcript_manager import TranscriptManager

st.set_page_config(page_title="Launcher", page_icon=":rocket:", layout="wide")


CARD_COUNT = 5
WORDS_PER_CARD = 10
BOT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "src" / "bot_config.json"



def _ensure_card_state():
    if "launcher_cards" not in st.session_state:
        st.session_state.launcher_cards = []



def _ensure_bot_status_state():
    if "bot_status" not in st.session_state:
        st.session_state.bot_status = None



def _load_bot_config() -> dict:
    if not BOT_CONFIG_PATH.exists():
        return {}

    with BOT_CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)



def _save_meeting_link():
    bot_config = _load_bot_config()
    bot_config["meeting_link"] = st.session_state.meeting_link

    with BOT_CONFIG_PATH.open("w", encoding="utf-8") as config_file:
        json.dump(bot_config, config_file, indent=2)
        config_file.write("\n")



def _ensure_meeting_link_state():
    if "meeting_link" not in st.session_state:
        bot_config = _load_bot_config()
        st.session_state.meeting_link = bot_config.get("meeting_link", "")



def _connect_bot():
    success, message = connect_bot()
    st.session_state.bot_status = (success, message)



def _disconnect_bot():
    success, message = disconnect_bot()
    st.session_state.bot_status = (success, message)



def _build_card_content(card_index: int) -> str:
    transcript_manager = TranscriptManager()
    start_index = card_index * WORDS_PER_CARD
    end_index = start_index + WORDS_PER_CARD
    words = transcript_manager.get_words(start_index, end_index)
    return " ".join(word.word for word in words)



def _generate_cards_from_transcript():
    st.session_state.launcher_cards = [
        {
            "id": card_id,
            "title": f"Card {card_id}",
            "content": _build_card_content(card_id - 1),
        }
        for card_id in range(1, CARD_COUNT + 1)
    ]



def _delete_card(card_id: int):
    st.session_state.launcher_cards = [
        card for card in st.session_state.launcher_cards if card["id"] != card_id
    ]


render_login()
_ensure_card_state()
_ensure_bot_status_state()
_ensure_meeting_link_state()

st.title("Launcher")
st.text_input(
    "Meeting link",
    key="meeting_link",
    on_change=_save_meeting_link,
    placeholder="https://meet.google.com/...",
)

connect_col, disconnect_col = st.columns(2)
connect_col.button("Connect bot", on_click=_connect_bot, use_container_width=True)
disconnect_col.button("Disconnect bot", on_click=_disconnect_bot, use_container_width=True)

if st.session_state.bot_status is not None:
    success, message = st.session_state.bot_status
    if success:
        st.success(message)
    else:
        st.error(message)

st.button(
    "Generate 5 cards from transcript",
    on_click=_generate_cards_from_transcript,
    use_container_width=True,
)

if st.session_state.launcher_cards:
    for card in st.session_state.launcher_cards:
        with st.container(border=True):
            header_col, delete_col = st.columns([6, 1])
            header_col.subheader(card["title"])
            delete_col.button(
                "Delete",
                key=f"delete_card_{card['id']}",
                on_click=_delete_card,
                args=(card["id"],),
                use_container_width=True,
            )
            st.text_area(
                "Pulled data",
                value=card["content"],
                placeholder="Transcript data will appear here.",
                key=f"card_content_{card['id']}",
                height=120,
            )
else:
    st.info("Generate cards to pull 10 transcript words into each placeholder.")
