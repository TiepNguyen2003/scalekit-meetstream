# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A sample integration that joins Google Meet calls via a [MeetStream](https://meetstream.ai) bot, receives transcription webhook events, and creates Notion pages enriched with meeting details — using [Scalekit](https://scalekit.com) to handle Notion OAuth and tool execution.

Python 3.11, managed with [uv](https://github.com/astral-sh/uv).

## Commands

```bash
# Install dependencies
uv sync

# Run the app
uv run python main.py

# Add a dependency
uv add <package>
```

## Architecture

Everything lives in `main.py`:

- **Scalekit client** — initialized at startup using `SCALEKIT_ENV_URL`, `SCALEKIT_CLIENT_ID`, `SCALEKIT_CLIENT_SECRET` from `.env`
- **`ensure_authenticated()`** — runs at startup; calls `get_or_create_connected_account()` to check if the user has authorized Notion. If not, generates an auth link via `get_authorization_link()` and waits for the user to complete OAuth before continuing
- **`/webhook` (POST)** — receives all MeetStream bot events; only acts on `transcription.*` events
- On a transcription event: fetches bot details from MeetStream API, then calls `scalekit.actions.execute_tool("notion_page_create")` to create a Notion page with meeting metadata and the webhook payload

## Key globals

- `CONNECTION_NAME` — Scalekit connection name for Notion (set in Scalekit dashboard)
- `IDENTIFIER` — unique user identifier scoped to the connected account

## Environment variables

See `.env.example`. Copy to `.env` and fill in values before running.
