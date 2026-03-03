import os
import operator
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import the tools we built in Phase 4
from tools import get_stock_price, get_historical_prices, search_sec_filings

load_dotenv()

# 1. Define the Agent State
# This holds the conversation history. Every node in our graph will read from and write to this state.
class AgentState(TypedDict):
    # 'Annotated' and 'operator.add' mean that whenever new messages are added, 
    # they are appended to the list, not overwritten.
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Initialize the LLM and bind the tools
print("Initializing LLM and Tools...")
tools = [get_stock_price, get_historical_prices, search_sec_filings]

llm = ChatOllama(
    model="llama3.2", # Change this if your cloud provider uses a different model name!
    base_url=os.getenv("OLLAMA_BASE_URL"),
    headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"},
)

# Binding tells the LLM: "Here is the list of tools you are allowed to use."
llm_with_tools = llm.bind_tools(tools)

# 3. Define the Nodes of our Graph

def agent_reasoning_node(state: AgentState):
    """
    The Brain: This node passes the current conversation state to the LLM.
    The LLM will either answer the question OR request to use a tool.
    """
    print("\n[Node] Agent is thinking...")
    messages = state['messages']
    
    # Give the LLM a system prompt to guide its behavior
    system_prompt = (
        "You are a professional AI financial analyst. You provide clear, concise, and accurate answers. "
        "You have access to tools to fetch live stock prices, historical data charts, and SEC 10-K filings. "
        "If a user asks for the current price, live price, or market cap, you MUST use the get_stock_price tool. "
        "If a user asks for a chart or historical trend, you MUST use the get_historical_prices tool. "
        "If a user asks about financial numbers, risks, or strategy, use the search_sec_filings tool. "
        "Do not hallucinate numbers. If a tool returns an error or no data, inform the user."
    )
    
    # We prepend the system prompt to the message history
    messages_with_prompt = [{"role": "system", "content": system_prompt}] + messages
    
    # Call the LLM
    response = llm_with_tools.invoke(messages_with_prompt)
    
    # Return the LLM's response to be added to the state
    return {"messages": [response]}

# The ToolNode is a pre-built LangGraph node that executes the tool requested by the LLM
tool_node = ToolNode(tools)

# 4. Define the Conditional Edge Logic
def should_continue(state: AgentState):
    """
    The Traffic Cop: Looks at the LLM's last response. 
    If the LLM requested a tool call, route to the tool_node.
    If the LLM provided a final answer, route to END.
    """
    last_message = state['messages'][-1]
    
    # If the LLM decided to call a tool, it will attach 'tool_calls' to the message
    if last_message.tool_calls:
        print(f"[Router] Routing to Tools: {last_message.tool_calls[0]['name']}")
        return "tools"
    
    # Otherwise, it's done thinking
    print("[Router] Routing to END.")
    return END

# 5. Build the LangGraph
print("🏗️ Building the Agent Graph...")
workflow = StateGraph(AgentState)

# Add our nodes
workflow.add_node("agent", agent_reasoning_node)
workflow.add_node("tools", tool_node)

# Set the entry point
workflow.set_entry_point("agent")

# Add the conditional routing
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# After tools execute, they MUST report back to the agent so it can read the results
workflow.add_edge("tools", "agent")

# Compile the graph into an executable application
app = workflow.compile()

# --- Quick Test ---
if __name__ == "__main__":
    print("\n--- Testing the LangGraph Agent ---")
    
    # We start the conversation with a HumanMessage
    user_query = "What is the current stock price of Apple?"
    initial_state = {"messages": [HumanMessage(content=user_query)]}
    
    print(f"\nUser: {user_query}")
    
    # Stream the steps as they happen
    for event in app.stream(initial_state):
        for key, value in event.items():
            if key == "agent":
                 # If the agent returned a final answer (no tool calls), print it
                 if not value['messages'][0].tool_calls:
                     print(f"\nAgent Final Answer: {value['messages'][0].content}")
            elif key == "tools":
                 print(f"\n[Tool Result]: {value['messages'][0].content}")