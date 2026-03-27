# Scalekit x MeetStream

A sample app that joins Google Meet calls using a [MeetStream](https://meetstream.ai) bot, listens for transcription webhook events, and automatically creates a Notion page for each transcription event — enriched with meeting details. Notion is connected and authorized via [Scalekit](https://scalekit.com).

---

## What it does

1. On startup, checks if the Notion account is authorized via Scalekit. If not, prompts you with an authorization link.
2. Runs a webhook server that receives events from MeetStream bots.
3. When a `transcription.*` event arrives, it fetches the full meeting details from MeetStream and creates a Notion page with the meeting info and webhook payload.

---

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — for dependency management
- A [MeetStream](https://meetstream.ai) account and API key
- A [Scalekit](https://scalekit.com) account with a Notion connection set up
- [ngrok](https://ngrok.com) (or similar) to expose your local server for MeetStream webhooks

---

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
MEET_STREAM_API_KEY=your_meetstream_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key

SCALEKIT_ENV_URL=https://your-env.scalekit.dev
SCALEKIT_CLIENT_ID=your_client_id
SCALEKIT_CLIENT_SECRET=your_client_secret
```

#### Getting your MeetStream API key
Sign up at [meetstream.ai](https://meetstream.ai) and grab your API key from the dashboard.

#### Getting your Scalekit credentials
1. Sign up at [app.scalekit.com](https://app.scalekit.com)
2. Go to **Developers → Settings → API Credentials**
3. Copy your `Environment URL`, `Client ID`, and `Client Secret` into `.env`

> Scalekit quickstart: https://docs.scalekit.com/quickstart/

### 3. Create a Notion connection in Scalekit

1. In the Scalekit dashboard, go to **Agent Auth → Connections**
2. Click **+ Create Connection** and select **Notion**
3. Configure it using either Scalekit's built-in credentials (for quick testing) or your own Notion integration credentials
4. Copy the connection name and update `CONNECTION_NAME` and `IDENTIFIER` in `main.py` — these are placeholders that you replace with your own values:

```python
CONNECTION_NAME = "your-connection-name"  # from Scalekit dashboard
IDENTIFIER = "your-identifier"            # unique ID for the user in your system
```

> Notion connector reference: https://docs.scalekit.com/reference/agent-connectors/notion/

---

## Running the app

### 1. Start the server

```bash
uv run python main.py
```

On first run, you'll be prompted with a Notion authorization link. Visit it, grant access, and press Enter to continue.

### 2. Expose it with ngrok

```bash
ngrok http 8999
```

Use the ngrok URL as the `callback_url` when creating a MeetStream bot.

### 3. Send a bot to a meeting

```bash
curl -X POST https://api.meetstream.ai/api/v1/bots/create_bot \
  -H "Authorization: Token YOUR_MEETSTREAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_link": "https://meet.google.com/xxx-xxxx-xxx",
    "bot_name": "MeetStream Bot",
    "callback_url": "https://your-ngrok-url/webhook",
    "recording_config": {
      "transcript": {
        "provider": { "deepgram": { "model": "nova-2", "smart_format": true } }
      }
    }
  }'
```

Once the meeting ends and transcription is processed, a Notion page will be created automatically.
