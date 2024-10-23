import json
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from langgraph.pregel import GraphRecursionError
from pydantic import BaseModel, Field

from src.agents.rag.graph import graph

load_dotenv()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

# declare origin/s for local dev
origins = ["http://localhost:5173", "localhost:5173"]

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class SearchInput(BaseModel):
    query: str = Field(..., description="The query to search for")


def search(query: str):
    try:
        for output in graph.stream(
            {"question": query},
        ):
            for key, value in output.items():
                if value == None:
                    continue
                print(value)
                documents = []
                if len(value.get("documents", [])) > 0:
                    for doc in value["documents"]:
                        documents.append(
                            {
                                "id": doc.id,
                                "metadata": doc.metadata,
                                "page_content": doc.page_content,
                            }
                        )
                yield json.dumps(
                    {
                        "node": key,
                        "question": value.get("question"),
                        "generation": value.get("generation"),
                        "documents": documents,
                        "is_done": value.get("is_done"),
                    }
                )
    except GraphRecursionError:
        print("GraphRecursionError: Graph recursion error. No results found.")
        yield json.dumps(
            {"error": "Graph recursion error. No results found.", "is_done": True}
        )
    except Exception as err:
        print("Shit happened!")
        yield json.dumps({"error": err, "is_done": True})


@app.post(
    "/search",
    summary="Search for an answer using self corrective RAG",
)
async def stream(r: SearchInput) -> StreamingResponse:
    return StreamingResponse(search(r.query), media_type="text/event-stream")


app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "web" / "dist", html=True),
    name="spa",
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
