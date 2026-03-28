import streamlit as st

from login import render_login

st.set_page_config(page_title="Launcher", page_icon=":rocket:", layout="wide")


CARD_COUNT = 5



def _ensure_card_state():
    if "launcher_cards" not in st.session_state:
        st.session_state.launcher_cards = []



def _generate_empty_cards():
    st.session_state.launcher_cards = [
        {"id": card_id, "title": f"Card {card_id}", "content": ""}
        for card_id in range(1, CARD_COUNT + 1)
    ]



def _delete_card(card_id: int):
    st.session_state.launcher_cards = [
        card for card in st.session_state.launcher_cards if card["id"] != card_id
    ]


render_login()
_ensure_card_state()

st.title("Launcher")
st.button("Generate 5 empty cards", on_click=_generate_empty_cards, use_container_width=True)

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
                placeholder="Pulled data will appear here.",
                key=f"card_content_{card['id']}",
                height=120,
            )
else:
    st.info("Generate cards to create empty placeholders for pulled data.")


