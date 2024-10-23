import os

from dotenv import load_dotenv

load_dotenv()

from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    base_url=os.environ.get("OLLAMA_HOST"),
    model=os.environ.get("OLLAMA_EMBEDDING"),
)

collection_name = "rag"
