from mcp.server import MCPServer
from fastmcp import FastMCP
from db import save_note,list_notes,search_notes

mcp=FastMCP("AIStudybuddy")

@mcp.tool()
def calculate_percentage(total:int,percentage:float):
    if total < 0:
        raise ValueError("Total cannot be negative")

    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    result = (total * percentage) / 100
    return result

@mcp.tool()
def save_note_tool(topic: str, content: str):
    save_note(topic,content)

@mcp.tool()
def search_notes_tool(keyword: str):
    search_notes(keyword)

@mcp.resource("study://guide/{topic}")
def study_guide(topic:str)->str:
    """Return a beginer friendly study guide on the topic passed as argument"""
    return f"Generate and return a beginer friendly guide for learning {topic}"

@mcp.prompt()
def explain_topic(topic:str)->str:
    "Generates prompt template to send it to llm to get explaination of the topic"

    return "You are a helpful AI study assistant. Explain the topic: {topic} Follow these instructions: 1. Explain the topic in simple language. 2. Provide a real-world example. 3. Include a small code example if applicable. 4. Explain why the topic is useful. 5. End with one practice question. "
    

mcp.run(transport="streamable-http")