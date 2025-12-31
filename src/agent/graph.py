# src/agent/graph.py

from typing import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv

# Import nodes from the other file
from .nodes import retrieve, grade_documents, generate, transform_query, web_search, check_topic

load_dotenv()

# Define the state dictionary
class GraphState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    web_search_needed: bool
    is_relevant: bool

# Define the graph
workflow = StateGraph(GraphState)

# Add the nodes (async functions)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)
workflow.add_node("web_search", web_search)
workflow.add_node("check_topic", check_topic)

# Define the edges
workflow.set_entry_point("check_topic")

def check_relevance(state):
    if state.get("is_relevant", True):
        return "retrieve"
    else:
        return "end"

workflow.add_conditional_edges(
    "check_topic",
    check_relevance,
    {"retrieve": "retrieve", "end": END}
)

workflow.add_edge("retrieve", "grade_documents")

def decide_to_generate(state):
    """Conditional edge to decide whether to generate or web search."""
    if state["web_search_needed"]:
        return "transform_query"
    else:
        return "generate"

workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {"transform_query": "transform_query", "generate": "generate"},
)

workflow.add_edge("transform_query", "web_search")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

# Compile the graph into a runnable app
app = workflow.compile()
print("Graph compiled successfully!")