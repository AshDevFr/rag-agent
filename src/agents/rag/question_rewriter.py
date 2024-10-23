### Question Re-writer
import os

from dotenv import load_dotenv

load_dotenv()
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

# LLM
llm = ChatOllama(
    base_url=os.environ.get("OLLAMA_HOST"),
    model=os.environ.get("OLLAMA_MODEL"),
    temperature=0,
)

# Prompt
re_write_prompt = PromptTemplate(
    template="""You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the initial and formulate an improved question. \n
     Only answer with the reformulated question.\n
     Here is the initial question: \n\n {question}. Improved question with no preamble: \n """,
    input_variables=["generation", "question"],
)

question_rewriter = re_write_prompt | llm | StrOutputParser()
