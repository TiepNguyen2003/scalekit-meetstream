import json
import os
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
BOT_CONFIG_PATH = BASE_DIR / "bot_config.json"
LAST_BOT_CREATED_PATH = BASE_DIR / "last_bot_created.json"
CREATE_BOT_URL = "https://api.meetstream.ai/api/v1/bots/create_bot"
REMOVE_BOT_URL_TEMPLATE = "https://api.meetstream.ai/api/v1/bots/{bot_id}/remove_bot"


def _get_api_key():
    load_dotenv()
    api_key = os.getenv("MEET_STREAM_API_KEY")
    if not api_key:
        return None, "Please add MEET_STREAM_API_KEY to your .env file."

    return api_key, None


def _get_headers():
    api_key, error_message = _get_api_key()
    if error_message:
        return None, error_message

    return {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }, None



def connect_bot():
    try:
        with BOT_CONFIG_PATH.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        return False, f"{BOT_CONFIG_PATH.name} was not found in src/."

    headers, error_message = _get_headers()
    if error_message:
        return False, error_message

    try:
        response = requests.post(CREATE_BOT_URL, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        return False, f"Failed to connect bot: {exc}"

    if response.status_code not in (200, 201):
        return False, f"Failed to connect bot. Status: {response.status_code}. {response.text}"

    data = response.json()
    bot_id = data.get("bot_id")

    with LAST_BOT_CREATED_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return True, f"Bot connected successfully. Bot ID: {bot_id}"



def disconnect_bot():
    try:
        with LAST_BOT_CREATED_PATH.open("r", encoding="utf-8") as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        return False, "last_bot_created.json was not found in src/. Connect a bot first."

    bot_id = saved_data.get("bot_id")
    if not bot_id:
        return False, "No bot_id was found in last_bot_created.json."

    api_key, error_message = _get_api_key()
    if error_message:
        return False, error_message

    command = [
        "curl",
        REMOVE_BOT_URL_TEMPLATE.format(bot_id=bot_id),
        "-H",
        f"Authorization: {api_key}",
    ]

    try:
        response = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"Failed to remove bot: {exc}"

    if response.returncode != 0:
        error_output = response.stderr.strip() or response.stdout.strip()
        return False, f"Failed to remove bot. {error_output}"

    return True, f"Successfully removed bot: {bot_id}"



print(disconnect_bot())
