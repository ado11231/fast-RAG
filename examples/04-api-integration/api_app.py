"""Demonstrates embedding fastrag into an existing FastAPI application.

Ingests documents at startup, then exposes a POST /ask endpoint
that accepts a question and returns relevant chunks.
"""
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from fastrag import Pipeline

DATA_DIR = Path(__file__).parent / "data"

# Ingest once at module load time.
pipeline = Pipeline()
pipeline.ingest(DATA_DIR)

app = FastAPI(title="My Knowledge API", version="0.1.0")


class QueryRequest(BaseModel):
    """Request body for the /ask endpoint."""
    question: str = Field(..., description="Natural language question")
    top_k: int = Field(default=5, ge=1, le=50)


class QueryResponse(BaseModel):
    """Response body containing matched chunks."""
    question: str
    results: list[dict]


@app.post("/ask", response_model=QueryResponse)
def ask(req: QueryRequest) -> QueryResponse:
    """Handle a question by searching the knowledge base."""
    results = pipeline.query(req.question, top_k=req.top_k)
    return QueryResponse(question=req.question, results=results)


@app.get("/health")
def health() -> dict:
    """Report server status and the number of stored chunks."""
    return {"status": "ok", "chunk_count": pipeline.store.count()}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
