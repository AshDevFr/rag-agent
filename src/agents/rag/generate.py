### Generate

import os

from dotenv import load_dotenv

load_dotenv()
from langchain import hub
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatOllama(
    base_url=os.environ.get("OLLAMA_HOST"),
    model=os.environ.get("OLLAMA_MODEL"),
    temperature=0,
)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = prompt | llm | StrOutputParser()
