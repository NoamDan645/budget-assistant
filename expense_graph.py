from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from expense_model import SYSTEM_PROMPT, create_model
from expense_tools import TOOLS
from langgraph.checkpoint.memory import InMemorySaver

def create_graph():
    model = create_model()

    def assistant(state: MessagesState):
        response = model.invoke(
            [SystemMessage(content=SYSTEM_PROMPT)]
            + state["messages"]
        )

        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    builder.add_node("assistant", assistant)
    builder.add_node(
        "tools",
        ToolNode(TOOLS, handle_tool_errors=True),
    )

    builder.add_edge(START, "assistant")

    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )

    builder.add_edge("tools", "assistant")

    memory = InMemorySaver()
    return builder.compile(checkpointer=memory)