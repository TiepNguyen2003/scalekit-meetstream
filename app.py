import streamlit as st
import websocket
import json
import time

import os
os.environ["GEMINI_API_KEY"] = "AIzaSyCioawiho6x4cj1nnHachZYrAXhxmY_3iY"
WS_URL = "ws://127.0.0.1:8999/ws/transcript"

from google.adk.agents import Agent
import asyncio # Ensure asyncio is imported
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from my_agent.agent import root_agent

agent = root_agent

# Setup runner
session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="app", session_service=session_service)
response_container = st.empty()


# Create session once
if "session_created" not in st.session_state:
    asyncio.run(session_service.create_session(
        app_name="app",
        user_id="u1",
        session_id="s1"
    ))
    st.session_state.session_created = True

async def call_agent(query: str):
    content = types.Content(role='user', parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id="u1",
        session_id="s1",
        new_message=content
    ):
        if event.is_final_response():
            print("Final")
            return event.content.parts[0].text

st.set_page_config(page_title="Live Transcript", page_icon="🎙️")
st.title("🎙️ Live Agent Transcript")

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

        # --- SINGLE QUERY ---
        response = asyncio.run(call_agent(full_transcript))
        st.markdown(f"**Agent Response:** {response}")
        response_container.markdown(f"**Agent Response:** {response}")
        print("AGENT RESPONSE:", response)
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