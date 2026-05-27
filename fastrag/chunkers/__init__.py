"""Chunker package — text splitting strategies."""
from fastrag.chunkers.base import BaseChunker
from fastrag.chunkers.recursive import RecursiveChunker

__all__ = [
    "BaseChunker",
    "RecursiveChunker",
]
