import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

from langchain_postgres.vectorstores import PGVector

from .consts import collection_name, embeddings

port = ""
if os.environ.get("POSTGRES_PORT") and os.environ.get("POSTGRES_PORT") != "":
    port = f":{os.environ.get('POSTGRES_PORT')}"

connection = f"postgresql+psycopg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}{port}/{os.environ.get("POSTGRES_DB")}"  # Uses psycopg3!


def _vector_store() -> PGVector:
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )


def delete_docs(ids: List[str]):
    if ids is None or len(ids) == 0:
        return
    vector_store = _vector_store()
    vector_store.delete(ids=ids)


def clean_store():
    vector_store = _vector_store()
    vector_store.delete_collection()


def store_docs(docs):
    vector_store = _vector_store()

    res = vector_store.add_documents(docs)  # ids=[doc.metadata["id"] for doc in docs]
    return res


def get_retriever():
    vector_store = _vector_store()
    return vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    # return vector_store.as_retriever(
    #     search_type="similarity_score_threshold",
    #     search_kwargs={
    #         "score_threshold": 0.5,
    #         "k": 5
    #     })
