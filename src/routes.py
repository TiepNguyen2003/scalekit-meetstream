import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks
from scalekit.client import ScalekitClient

load_dotenv()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        data = {}
        
    print(data)

    if data and data.get("event", "").startswith("transcription."):
        event = data.get("event", "unknown")
        bot_id = data.get("bot_id", "unknown")

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
        print(f"\n📄 Notion page created: {page_url}\n")

    return {"status": "received"}