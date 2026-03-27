import os
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request
from scalekit.client import ScalekitClient

load_dotenv()

# Scalekit connection name for the Notion integration configured in the Scalekit dashboard
CONNECTION_NAME = "your-connection-name"
# Unique identifier for the user/account in Scalekit — used to scope connected accounts
IDENTIFIER = "your-identifier"

MEETSTREAM_API_KEY = os.getenv("MEET_STREAM_API_KEY")
MEETSTREAM_BASE_URL = "https://api.meetstream.ai/api/v1"

# Initialize the Scalekit client — handles OAuth token management and tool execution
# for third-party integrations (Notion, Gmail, etc.) on behalf of users
# Quickstart: https://docs.scalekit.com/quickstart/
scalekit = ScalekitClient(
    env_url=os.getenv("SCALEKIT_ENV_URL"),
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
)


def ensure_authenticated():
    # Get or create a connected account for this user+connector pair.
    # A connected account represents a user's authorized connection to a third-party app (Notion here).
    try:
        response = scalekit.actions.get_or_create_connected_account(
            connection_name=CONNECTION_NAME,
            identifier=IDENTIFIER,
        )
    except Exception as e:
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

    if connected_account.status != "ACTIVE":
        # Generate a one-time OAuth authorization link.
        # User must visit this link to grant our app access to their Notion workspace.
        # Scalekit handles the full OAuth 2.0 flow and stores the token securely.
        link_response = scalekit.actions.get_authorization_link(
            connection_name=CONNECTION_NAME,
            identifier=IDENTIFIER,
        )
        print(f"Notion is not connected (status: {connected_account.status})")
        print(f"\n🔗 Authorize here:\n\n    {link_response.link}\n")
        input("⎆ Press Enter after authorizing...")

        # Re-check status after user completes authorization
        recheck = scalekit.actions.get_or_create_connected_account(
            connection_name=CONNECTION_NAME,
            identifier=IDENTIFIER,
        )
        if recheck.connected_account.status != "ACTIVE":
            raise RuntimeError(
                f"Authorization incomplete (status: {recheck.connected_account.status}). "
                "Please restart and complete the authorization flow."
            )
        print(f"✓ Connected account is active: {recheck.connected_account.id}")
    else:
        print(f"✓ Connected account is active: {connected_account.id}")


def get_bot_details(bot_id):
    # Fetch full bot metadata from MeetStream — includes meeting link, platform,
    # duration, start/end times, and status timeline
    resp = requests.get(
        f"{MEETSTREAM_BASE_URL}/bots/{bot_id}/detail",
        headers={"Authorization": f"Token {MEETSTREAM_API_KEY}"},
    )
    resp.raise_for_status()
    return resp.json().get("bot_details", {})


def rich_text(content):
    # Notion API requires text content wrapped in a rich_text array
    return [{"type": "text", "text": {"content": str(content)}}]


def info_row(label, value):
    # Creates a Notion paragraph block with a bold label and plain value
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": f"{label}: "}, "annotations": {"bold": True}},
                {"type": "text", "text": {"content": str(value)}},
            ]
        },
    }


ensure_authenticated()

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print(data)

    # Only process transcription events — MeetStream sends various event types
    # (audio.processed, bot.joined, etc.) but we only care about transcription.*
    if data and data.get("event", "").startswith("transcription."):
        event = data.get("event", "unknown")
        bot_id = data.get("bot_id", "unknown")

        # Enrich the event with full meeting context from MeetStream
        bot = get_bot_details(bot_id)
        meeting_link = bot.get("MeetingLink", "N/A")
        platform = bot.get("Platform", "N/A")
        bot_name = bot.get("BotUsername", "N/A")
        start_time = bot.get("StartTime", "N/A")
        end_time = bot.get("EndTime", "N/A")
        duration = bot.get("Duration")
        duration_str = f"{duration}s ({duration // 60}m {duration % 60}s)" if duration else "N/A"
        status = bot.get("Status", "N/A")

        title = f"[{event}] {meeting_link}"

        # Use Scalekit's execute_tool to create a Notion page
        # Notion tools reference: https://docs.scalekit.com/reference/agent-connectors/notion/
        result = scalekit.actions.execute_tool(
            tool_name="notion_page_create",
            identifier=IDENTIFIER,
            tool_input={
                "properties": {
                    "title": rich_text(title)
                },
                "child_blocks": [
                    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rich_text("Meeting Details")}},
                    info_row("Platform", platform),
                    info_row("Bot Name", bot_name),
                    info_row("Meeting Link", meeting_link),
                    info_row("Start Time", start_time),
                    info_row("End Time", end_time),
                    info_row("Duration", duration_str),
                    info_row("Status", status),
                    {"object": "block", "type": "divider", "divider": {}},
                    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rich_text("Webhook Payload")}},
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "language": "json",
                            "rich_text": rich_text(json.dumps(data, indent=2)),
                        },
                    },
                ],
            },
        )
        page_url = result.data.get("url")
        print(
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📄 Notion page created:\n\n"
            f"     {page_url}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    return "", 200


if __name__ == "__main__":
    app.run(port=8999, debug=True)
