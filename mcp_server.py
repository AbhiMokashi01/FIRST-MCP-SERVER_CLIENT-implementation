from mcp.server import MCPServer
from db import *
from external_tools import *

mcp=MCPServer("AIStudybuddy")

@mcp.tool()
def web_search(query:str)->list[dict]:
    """Recieves a query and uses tavily search to retrieve resuls"""
    return tavily_search(query)

@mcp.tool()
def get_events()->list[dict]:
    """Receieves list of events from google calender"""
    return list_upcoming_events()

@mcp.tool()
def get_tutorials(query:str)->list[dict]:
    """recieves a query to find tutorial details using youtube data api"""
    return find_tutorials(query)

@mcp.tool()
def calculate_percentage(total:int,percentage:float):
    """Accepts total and percentage as parameters and returns calculated percentage"""
    if total < 0:
        raise ValueError("Total cannot be negative")

    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    result = (total * percentage) / 100
    return result

@mcp.tool()
def save_note_tool(topic: str, content: str):
    """Accepts topic and content as parameters to save them in database"""
    print(f"INSIDE SAVE NOTE TOOL with topic:{topic} and content {content}")
    # save_note(topic,content)

@mcp.tool()
def search_notes_tool(keyword: str):
    """Accepts Keyword to search for a book in database"""
    print(f"Inside search notes tool with keyword {keyword}")
    # search_notes(keyword)

@mcp.tool()
def save_preference_tool(key: str, value: str) -> dict:
    """Save a learning preference explicitly requested by the user."""
    return save_preference(key, value)

@mcp.tool()
def list_preferences_tool() -> list[dict]:
    """Retrieve previously saved learning preferences."""
    return list_preferences()

@mcp.resource("study://guide/{topic}")
def study_guide(topic:str)->str:
    """Return a beginer friendly study guide on the topic passed as argument"""
    print("inside study guide tool")
    return f"Generate and return a beginer friendly guide for learning {topic}"

@mcp.prompt()
def explain_topic(topic:str)->str:
    "Generates prompt template to send it to llm to get explaination of the topic"

    return "You are a helpful AI study assistant. Explain the topic: {topic} Follow these instructions: 1. Explain the topic in simple language. 2. Provide a real-world example. 3. Include a small code example if applicable. 4. Explain why the topic is useful. 5. End with one practice question. "



if __name__== "__main__":
    mcp.run(transport="streamable-http")

