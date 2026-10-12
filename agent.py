from langgraph.graph import StateGraph,add_messages,START,END
from typing import Annotated,TypedDict
from llm import model

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

        
    ###binding tools with llm
    tool_list=[]
    for tool in tools:
        tool_list.append(tool.name)

    

    llm_with_tools=model.bind_tools(tools)

    ###Creating chatbot
    async def chatbot(state:MessageState):
        response=await llm_with_tools.ainvoke(state["messages"])

        return {"messages":response}

    ### Creating graph

    graph=StateGraph(MessageState)
    graph.add_node("chatbot",chatbot)
    graph.add_node("tools",ToolNode(tools))
    graph.add_edge(START,"chatbot")
    graph.add_conditional_edges("chatbot",tools_condition)
    graph.add_edge("tools","chatbot")


    

    #Adding memory to the graph

    memory=InMemorySaver()

    config={"configurable":{
        "thread_id":"1"
    }}

    app=graph.compile(checkpointer=memory)

    result=await app.ainvoke({"messages":[("user","Get me the tutorials of Python")]},config)

    print(result["messages"][-1].content)

    result=await app.ainvoke({"messages":[("user","What tutorial is best among you recommended")]},config)

    print(result["messages"][-1].content)


if __name__=="__main__":
    asyncio.run(main())