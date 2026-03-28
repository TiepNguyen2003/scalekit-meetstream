# Scalekit connection name for the Notion integration configured in the Scalekit dashboard
import os

from dotenv import load_dotenv
from scalekit import ScalekitClient

load_dotenv()

CONNECTION_NAME = "Tiep's Connection name-name"
# Unique identifier for the user/account in Scalekit — used to scope connected accounts
IDENTIFIER = os.getenv("IDENTIFIER")

MEETSTREAM_API_KEY = os.getenv("MEET_STREAM_API_KEY")
MEETSTREAM_BASE_URL = "https://api.meetstream.ai/api/v1"

# Initialize the Scalekit client — handles OAuth token management and tool execution
# for third-party integrations (Notion, Gmail, etc.) on behalf of users
# Quickstart: https://docs.scalekit.com/quickstart/
scalekit_client = ScalekitClient(
    env_url=os.getenv("SCALEKIT_ENV_URL"),
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
)
