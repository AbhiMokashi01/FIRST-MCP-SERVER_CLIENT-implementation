from langgraph.graph import StateGraph,add_messages,START,END
from typing import Annotated,TypedDict
from llm import model
import uuid
import re
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core._api import LangChainBetaWarning
import asyncio
import warnings

warnings.filterwarnings(
    "ignore",
    category=LangChainBetaWarning
)

from langchain.mcp import MCPAdapter

import json

class MessageState(TypedDict):
    messages : Annotated[list,add_messages]







async def main():

    ###Creating mcp adapters
    adapter=MCPAdapter("http://127.0.0.1:8000/mcp")

    ###listing tools
    tools=await adapter.list_tools()

    #Keeping preference saving tools out of llm tool call because they are only executed if explicity asked by human 
    agent_tools=[]
    for tool in tools:
        if tool.name =="save_preference_tool":
            save_pref=tool
        if tool.name =="list_preferences_tool":
                    list_pref=tool    
        if tool.name != "save_preference_tool":
            agent_tools.append(tool)
            

    # ###binding tools with llm
    # tool_list=[]
    # for tool in tools:
    #     tool_list.append(tool.name)

    

    llm_with_tools=model.bind_tools(agent_tools)

    ###Creating chatbot
    async def chatbot(state:MessageState):
        ###reads preference list stored in database
        preferences = await list_pref.ainvoke({})

        system = SystemMessage(
            content=f"""
    You are AIStudyAssistant.

    Saved preferences: {preferences}

    TOOL SELECTION RULES:

    1. If the user asks to GET, SHOW, READ or
       RETRIEVE notes:
       - FIRST call search_notes_tool.
       - If notes exist, return them.
       - DO NOT call web_search.
       - DO NOT call save_note_tool.

    2. If notes are not found:
       - Inform the user.
       - Offer to search the web.
       - Do not save anything automatically.

    3. If the user asks to SEARCH AND SAVE notes:
       - Call web_search first.
       - Prepare notes from successful results.
       - Call save_note_tool once.
       - Confirm saving using the returned ID.

    4. If the user requests YouTube tutorials:
       - Call get_tutorials.

    5. If the user requests upcoming events:
       - Call get_events.

    Never save notes unless the user requests saving.
    Never repeat successful tool calls unnecessarily.
    """
        )
        messages=[]

        for msg in state["messages"]:
            if isinstance(msg,ToolMessage):
                # print(
                # "Tool:", msg.name,
                # "Status:", msg.status,
                # "Content:", repr(msg.content)[:200]
                # )

                if msg.content is None or msg.content==[] or msg.content=="":
                    msg=msg.model_copy(update={
                    "content": ("tool returned no content" "dont assume it succeded")
                    })

            messages.append(msg)
        last_msg = state["messages"][-1]

        response= await llm_with_tools.ainvoke([system]+messages)
        if isinstance(last_msg, ToolMessage) and last_msg.status == "error":
            return {
            "messages": [
            AIMessage(
                content=(
                    f"The tool {last_msg.name} failed. "
                    "I could not complete the requested research. "
                    "No research notes were saved in this step."
                )
            )
        ]
         }

        # print("Requested tools:", response.tool_calls)

        return {"messages": [response]}
                

    ### Creating graphexit

    graph=StateGraph(MessageState)
    graph.add_node("chatbot",chatbot)
    graph.add_node("tools",ToolNode(agent_tools))
    graph.add_edge(START,"chatbot")
    graph.add_conditional_edges("chatbot",tools_condition)
    graph.add_edge("tools","chatbot")


    

    #Adding memory to the graph

    memory=InMemorySaver()

    config={"configurable":{
        "thread_id":"1"
    }}

    app=graph.compile(checkpointer=memory)

     # Display the available commands to the user
    print("""
========================================
         AI STUDY ASSISTANT
========================================

Available Commands:

1. Ask any study question
   

2. /remember key=value
   

3. /prefs View saved preferences

4. /new Start a new conversation

5. exit
   Exit the application

========================================
""")

    # Keep chatting until the user exits
    while True:

        # Take user input asynchronously
        user_input = input("\nYou: ").strip()

        # Exit the application
        if user_input.lower() == "exit":
            break

        # Start a new thread without deleting PostgreSQL preferences
        if user_input.lower() == "/new":

            config["configurable"]["thread_id"] = str(uuid.uuid4())

            print("New conversation started!")
            continue

        # Save a preference only when the user explicitly
        # uses the /remember command
        if user_input.lower().startswith("/remember "):

            # Extract key=value from the command
            preference = user_input[len("/remember"):]

            if "=" not in preference:
                print("Correct format: /remember key=value")
                continue

            # Separate preference key and value
            key, value = preference.split("=", 1)

            key = key.strip()
            value = value.strip()

            if not key or not value:
                print("Key and value cannot be empty")
                continue

            # Call the MCP tool to save into PostgreSQL
            result = await save_pref.ainvoke({
                "key": key,
                "value": value
            })

            print("Saved preference:", result)
            continue

        # Retrieve all saved preferences from PostgreSQL
        if user_input.lower() == "/prefs":

            preferences = await list_pref.ainvoke({})

            print("Saved preferences:", preferences)
            continue

        # Ignore empty inputs
        if not user_input:
            continue

        # Run the existing LangGraph chatbot
        # The thread ID determines which chat history to use
        result = await app.ainvoke(
            {
                "messages": [
                    ("user", user_input)
                ]
            },
            config=config
        )

        # Display the final response
        print("AI:", result["messages"][-1].content)




if __name__=="__main__":
    asyncio.run(main())