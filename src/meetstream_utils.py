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