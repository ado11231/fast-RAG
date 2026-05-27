"""Simplest possible fastrag workflow: ingest documents, then ask a question.

No custom components, no configuration — just defaults everywhere.
"""
from pathlib import Path

from fastrag import Pipeline

# Point to the directory containing our sample documents.
DATA_DIR = Path(__file__).parent / "data"

# Create a Pipeline with all default components.
# Defaults: RecursiveChunker, SentenceTransformerEmbedder, ChromaStore.
pipeline = Pipeline()

# Ingest every supported file in the data directory.
# Returns the total number of chunks stored.
count = pipeline.ingest(DATA_DIR)
print(f"Ingested {count} chunks from {DATA_DIR}")

# Ask a question against the knowledge base.
# Each result contains: text, metadata (source file), and similarity score.
results = pipeline.query("What is the fastrag philosophy?", top_k=3)
for hit in results:
    score = hit.get("score", 0.0)
    source = hit.get("metadata", {}).get("source", "unknown")
    text = hit.get("text", "")
    print(f"\n[Score: {score:.3f}] [Source: {source}]")
    print(text[:200])
