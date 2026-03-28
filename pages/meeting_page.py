import streamlit as st
import websocket
import json
import time

WS_URL = "ws://127.0.0.1:8999/ws/transcript"

st.set_page_config(page_title="Meeting Recommendations", page_icon="🎙️")
st.title("🎙️ Meeting Recommendations")

# Initialize state to hold the cumulative transcript
if "transcript_history" not in st.session_state:
    st.session_state.transcript_history = []

transcript_container = st.empty()
is_listening = st.toggle("Listen to Live Stream", value=True)

def render_transcript():
    if st.session_state.transcript_history:
        # Join all words into a single string for display
        full_transcript = " ".join([word["word"] for word in st.session_state.transcript_history])
        transcript_container.markdown(f"**Transcript:** {full_transcript}")
    else:
        transcript_container.markdown("No transcript data received yet.")

if is_listening:
    try:
        # Connect to the FastAPI WebSocket
        ws = websocket.create_connection(WS_URL)
        # Set a short timeout so the while loop doesn't block the UI toggle completely
        ws.settimeout(1.0) 
        
        status_msg = st.toast("Connected to live stream!", icon="🟢")

        while is_listening:
            print("Waiting for new words...")
            try:
                # Wait for the backend to push new words
                result = ws.recv()
                new_words = json.loads(result)
                
                # Append the newly received words to our history
                st.session_state.transcript_history.extend(new_words)
                print(new_words)
                # Update the UI
                render_transcript()
                
            except websocket.WebSocketTimeoutException:
                # Timeout is normal, just loop back around and check if 'is_listening' is still true
                continue
            except Exception as e:
                st.error(f"Connection lost: {e}")
                break
                
    except Exception as e:
        st.error("Cannot connect to backend. Is FastAPI running on port 8999?")
        time.sleep(2)