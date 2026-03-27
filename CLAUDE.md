# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`meet-stream` is a Python 3.11 project managed with [uv](https://github.com/astral-sh/uv). It depends on `scalekit-sdk-python` for Scalekit integration.

## Commands

```bash
# Install dependencies
uv sync

# Run the app
uv run python main.py

# Add a dependency
uv add <package>
```

## Structure

- `main.py` — entry point
- `pyproject.toml` — project metadata and dependencies
- `uv.lock` — locked dependency versions (commit this file)
