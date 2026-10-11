from langgraph.graph import StateGraph,add_messages,START,END
from typing import Annotated,TypedDict
from llm import model
import json

class MessageState(TypedDict):
    messages : Annotated[list,add_messages]


graph=StateGraph(MessageState)

##Chatbot Node Definition

def chatbot(state:MessageState)->MessageState:
    return {"messages":[model.invoke(state["messages"])]}


## defining graph
graph.add_node("chatbot",chatbot)
graph.add_edge(START,"chatbot")
graph.add_edge("chatbot",END)

app=graph.compile()

result=app.invoke({"messages":"Hi"})
 