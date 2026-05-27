"""Embedder package — text-to-vector conversion."""
from fastrag.embedders.base import BaseEmbedder
from fastrag.embedders.sentence_transformers import SentenceTransformerEmbedder

__all__ = [
    "BaseEmbedder",
    "SentenceTransformerEmbedder",
]
