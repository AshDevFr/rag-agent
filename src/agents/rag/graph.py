from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import END, START, StateGraph

from .edges import (decide_the_source, decide_to_generate,
                    grade_generation_v_documents_and_question)
from .nodes import (generate, grade_documents, init, no_result, reset, result,
                    retrieve, transform_query, web_search)
from .state import GraphState

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("init", init)  # init
workflow.add_node("reset", reset)  # reset
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("web_search", web_search)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate
workflow.add_node("transform_query", transform_query)  # transform_query
workflow.add_node("no_result", no_result)  # no_result
workflow.add_node("result", result)  # result

# Build graph
workflow.add_edge(START, "init")
workflow.add_edge("init", "retrieve")
workflow.add_edge("reset", "web_search")
workflow.add_edge("no_result", END)
workflow.add_edge("result", END)
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("web_search", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_conditional_edges(
    "transform_query",
    decide_the_source,
    {
        "reset": "reset",
        "web_search": "web_search",
        "retrieve": "retrieve",
        "no_result": "no_result",
    },
)
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": "result",
        "not useful": "transform_query",
    },
)

# Compile
graph = workflow.compile()

print(graph.get_graph().draw_mermaid())

graph.get_graph().draw_mermaid_png(
    draw_method=MermaidDrawMethod.API, output_file_path="data/graph.png"
)
