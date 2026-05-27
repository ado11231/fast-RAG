"""Demonstrates explicit configuration of every Pipeline component.

Shows how to swap in non-default chunk sizes, embedding models,
and storage directories without changing any application logic.
"""
from pathlib import Path

from fastrag import Pipeline
from fastrag.chunkers.recursive import RecursiveChunker
from fastrag.embedders.sentence_transformers import SentenceTransformerEmbedder
from fastrag.stores.chroma import ChromaStore

DATA_DIR = Path(__file__).parent / "data"
PERSIST_DIR = Path(__file__).parent / ".fastrag" / "chroma"

# Smaller chunk size for finer granularity.
chunker = RecursiveChunker(chunk_size=128, overlap=16)

# Explicit model choice — still local, no API key.
embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")

# Store vectors in an example-specific directory so they don't
# conflict with the user's main .fastrag/ working directory.
store = ChromaStore(persist_dir=str(PERSIST_DIR))

pipeline = Pipeline(chunker=chunker, embedder=embedder, store=store)

count = pipeline.ingest(DATA_DIR)
print(f"Ingested {count} chunks (custom config)")

results = pipeline.query("What are the features?", top_k=2)
for hit in results:
    print(f"  Score: {hit.get('score', 0.0):.3f}")
    print(f"  Text: {hit.get('text', '')[:200]}")
