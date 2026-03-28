import json
import os

import requests
from flask import Flask, request

try:
    from pages.scalekit_auth import (
        GMAIL_SEND_SCOPE,
        IDENTIFIER,
        ensure_authenticated,
        scalekit,
    )
except ModuleNotFoundError:
    from scalekit_auth import GMAIL_SEND_SCOPE, IDENTIFIER, ensure_authenticated, scalekit

MEETSTREAM_API_KEY = os.getenv("MEET_STREAM_API_KEY")
MEETSTREAM_BASE_URL = "https://api.meetstream.ai/api/v1"
GMAIL_NOTIFICATION_TO = os.getenv("GMAIL_NOTIFICATION_TO")



def get_bot_details(bot_id):
    resp = requests.get(
        f"{MEETSTREAM_BASE_URL}/bots/{bot_id}/detail",
        headers={"Authorization": f"Token {MEETSTREAM_API_KEY}"},
    )
    resp.raise_for_status()
    return resp.json().get("bot_details", {})



def build_email_subject(event: str, meeting_link: str):
    return f"MeetStream transcription update: {event}"



def build_email_body(event: str, bot: dict, payload: dict):
    meeting_link = bot.get("MeetingLink", "N/A")
    platform = bot.get("Platform", "N/A")
    bot_name = bot.get("BotUsername", "N/A")
    start_time = bot.get("StartTime", "N/A")
    end_time = bot.get("EndTime", "N/A")
    duration = bot.get("Duration")
    duration_str = f"{duration}s ({duration // 60}m {duration % 60}s)" if duration else "N/A"
    status = bot.get("Status", "N/A")

    return "\n".join(
        [
            f"Event: {event}",
            f"Platform: {platform}",
            f"Bot Name: {bot_name}",
            f"Meeting Link: {meeting_link}",
            f"Start Time: {start_time}",
            f"End Time: {end_time}",
            f"Duration: {duration_str}",
            f"Status: {status}",
            "",
            "Webhook Payload:",
            json.dumps(payload, indent=2),
        ]
    )



def send_transcription_email(event: str, bot: dict, payload: dict):
    if not GMAIL_NOTIFICATION_TO:
        raise RuntimeError(
            "GMAIL_NOTIFICATION_TO is not set. Add a recipient email address to .env "
            "before using the Gmail notification webhook."
        )

    ensure_authenticated(required_scopes=[GMAIL_SEND_SCOPE])

    subject = build_email_subject(event, bot.get("MeetingLink", "N/A"))
    body = build_email_body(event, bot, payload)

    result = scalekit.actions.execute_tool(
        tool_name="gmail_send_email",
        identifier=IDENTIFIER,
        tool_input={
            "to": GMAIL_NOTIFICATION_TO,
            "subject": subject,
            "body": body,
        },
    )
    return getattr(result, "data", result)


app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print(data)

    if data and data.get("event", "").startswith("transcription."):
        event = data.get("event", "unknown")
        bot_id = data.get("bot_id", "unknown")
        bot = get_bot_details(bot_id)
        email_result = send_transcription_email(event, bot, data)
        print(f"Gmail notification sent: {email_result}")

    return "", 200


if __name__ == "__main__":
    ensure_authenticated(required_scopes=[GMAIL_SEND_SCOPE])
    app.run(port=8999, debug=True)
