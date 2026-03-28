from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="Answer questions using Google Search when needed. Always cite sources.",
    instruction="Professional search assistant with Google Search capabilities",
    tools=[google_search]
)

#https://google.github.io/adk-docs/grounding/google_search_grounding/#data-flow-diagram