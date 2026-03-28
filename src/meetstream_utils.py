import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks

from scalekit.client import ScalekitClient
import scalekit
from globals import CONNECTION_NAME, IDENTIFIER

load_dotenv()
def ensure_authenticated():
    # Get or create a connected account for this user+connector pair.
    # A connected account represents a user's authorized connection to a third-party app (Notion here).
    try:
        response = scalekit.actions.get_or_create_connected_account(
            connection_name=CONNECTION_NAME,
            identifier=IDENTIFIER,
        )
    except Exception as e:
        print(e)
        raise RuntimeError(
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Error: {e}\n\n"
            "  Have you created a Notion connection in Scalekit?\n\n"
            "  app.scalekit.com → Agent Auth → Connections → + Create Connection\n\n"
            "  Then update CONNECTION_NAME in main.py with your connection name.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        ) from e
    connected_account = response.connected_account


def get_bot_details(bot_id):
    # Fetch full bot metadata from MeetStream — includes meeting link, platform,
    # duration, start/end times, and status timeline
    resp = requests.get(
        f"{MEETSTREAM_BASE_URL}/bots/{bot_id}/detail",
        headers={"Authorization": f"Token {MEETSTREAM_API_KEY}"},
    )
    resp.raise_for_status()
    return resp.json().get("bot_details", {})