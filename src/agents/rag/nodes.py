### Nodes

from dotenv import load_dotenv
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException
from langchain_core.documents import Document

from .generate import rag_chain
from .question_rewriter import question_rewriter
from .retrieval_grader import retrieval_grader
from .tools import retriever

load_dotenv()


def init(state):
    """
    Initialize the state to save the original question
    """

    print("---INIT---")
    question = state["question"]

    state.update(
        {
            "original_question": question,
            "rewrite_retries": 0,
            "generation_retries": 0,
            "is_done": False,
        }
    )
    return state


def reset(state):
    """
    Reset the question to the original question
    """

    print("---RESET---")
    original_question = state["original_question"]

    state.update({"question": original_question})
    return state


def no_result(state):
    """
    Return the result if no relevant documents are found
    """

    print("---NO RESULT---")
    original_question = state["original_question"]

    state.update(
        {
            "question": original_question,
            "documents": [],
            "generation": "No relevant documents found in the context for this query.",
            "is_done": True,
        }
    )
    return state


def result(state):
    """
    Return the result
    """

    print("---RESULT---")

    state.update({"is_done": True})
    return state


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """

    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    state.update(
        {"documents": documents, "generation": f"Retrieved {len(documents)} documents."}
    )
    return state


def web_search(state):
    """
    Web search based on the question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Appended web results to documents
    """

    print("---WEB SEARCH---")
    question = state["question"]
    documents = []

    with DDGS() as ddgs:
        results = []
        try:
            results = ddgs.text(question, max_results=5)
        except DuckDuckGoSearchException as e:
            print(f"Duck Duck go search error occurred during search: {e}")
        except (Exception) as e:
            print(e.__str__())

        for i, r in enumerate(results):
            documents.append(
                Document(
                    id=f"ddg-{i}",
                    page_content=r["body"],
                    metadata={
                        "title": r["title"],
                        "url": r["href"],
                    },
                )
            )

    state.update(
        {
            "documents": documents,
            "generation": f"Search the web and found {len(documents)} documents.",
        }
    )
    return state


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """

    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    generation_retries = state["generation_retries"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    state.update(
        {"generation": generation, "generation_retries": generation_retries + 1}
    )
    return state


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    irrelevant_docs_count = 0
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score["score"]
        if grade == "yes":
            filtered_docs.append(d)
        else:
            irrelevant_docs_count += 1
            continue

    generation = f"Found {irrelevant_docs_count} irrelevant document{'s' if irrelevant_docs_count > 1 else ''}."
    if len(filtered_docs) == 0:
        generation += " No relevant documents found."
    elif irrelevant_docs_count == 0:
        generation = "No irrelevant documents found."

    state.update({"documents": filtered_docs, "generation": generation})
    return state


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    rewrite_retries = state["rewrite_retries"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    state.update(
        {
            "question": better_question,
            "generation": "Re-phrased question.",
            "rewrite_retries": rewrite_retries + 1,
            "generation_retries": 0,
        }
    )
    return state
