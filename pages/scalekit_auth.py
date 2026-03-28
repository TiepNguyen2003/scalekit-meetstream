import os

from dotenv import load_dotenv
from scalekit.client import ScalekitClient

load_dotenv()

CONNECTION_NAME = os.getenv("SCALEKIT_CONNECTION_NAME", "gmail")
IDENTIFIER = os.getenv("SCALEKIT_IDENTIFIER", "test_identifier")

scalekit = ScalekitClient(
    env_url=os.getenv("SCALEKIT_ENV_URL"),
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
)


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
GMAIL_READ_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_PEOPLE_SCOPE = "https://www.googleapis.com/auth/contacts.readonly"


def _validate_required_scopes(connected_account, required_scopes: list[str] | None):
    if not required_scopes:
        return

    granted_scopes = set(getattr(connected_account, "scopes", []) or [])
    missing_scopes = [scope for scope in required_scopes if scope not in granted_scopes]
    if missing_scopes:
        missing = ", ".join(missing_scopes)
        raise RuntimeError(
            f"Connected Gmail account is missing required scopes: {missing}. "
            "Update the Scalekit Gmail connection scopes and re-authorize the user."
        )



def ensure_authenticated(required_scopes: list[str] | None = None):
    try:
        response = scalekit.actions.get_or_create_connected_account(
            connection_name=CONNECTION_NAME,
            identifier=IDENTIFIER,
        )
    except Exception as exc:
        raise RuntimeError(
            "\n"
            "Scalekit could not load the connected Gmail account.\n\n"
            f"Error: {exc}\n\n"
            "Check the following:\n"
            "- SCALEKIT_ENV_URL, SCALEKIT_CLIENT_ID, and SCALEKIT_CLIENT_SECRET are set\n"
            f"- the Scalekit connection '{CONNECTION_NAME}' exists in the dashboard\n"
            "- the Gmail connection is configured with the required Google scopes\n"
        ) from exc

    connected_account = response.connected_account
    if connected_account.status == "ACTIVE":
        _validate_required_scopes(connected_account, required_scopes)
        print(f"Connected account is active: {connected_account.id}")
        return connected_account

    link_response = scalekit.actions.get_authorization_link(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
    )
    print(f"Scalekit connection '{CONNECTION_NAME}' is not active (status: {connected_account.status})")
    print(f"\nAuthorize here:\n\n    {link_response.link}\n")
    input("Press Enter after authorizing...")

    recheck = scalekit.actions.get_or_create_connected_account(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
    )
    if recheck.connected_account.status != "ACTIVE":
        raise RuntimeError(
            f"Authorization incomplete for '{CONNECTION_NAME}' "
            f"(status: {recheck.connected_account.status})."
        )

    _validate_required_scopes(recheck.connected_account, required_scopes)
    print(f"Connected account is active: {recheck.connected_account.id}")
    return recheck.connected_account
