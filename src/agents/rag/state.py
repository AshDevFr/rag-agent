from typing import List

from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        original_question: Original question
        question: question
        generation: LLM generation
        documents: list of documents
        rewrite_retries: Number of rewrite retries
        generation_retries: Number of generation retries
        is_done: Whether the flow is done
    """

    original_question: str
    question: str
    generation: str
    documents: List[str]
    rewrite_retries: int
    generation_retries: int
    is_done: bool
