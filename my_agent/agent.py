from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

# --- QA agent ---
my_agent = Agent(
    name="qa_agent",
    description="Answers general questions and explains things.",
    instruction="Answer the user's question clearly and concisely."
)

# --- Search tool ---
def search_tool(query: str) -> str:
    return f"Search results for: {query}"

# --- Search agent ---
search_agent = Agent(
    name="search_agent",
    description="Finds sources and external information.",
    instruction="Use the search tool to find relevant information.",
    tools=[search_tool],
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Answer questions using Google Search when needed. Always cite sources.",
    instruction="Professional search assistant with Google Search capabilities",
    tools=[google_search]
)

#https://google.github.io/adk-docs/grounding/google_search_grounding/#data-flow-diagram