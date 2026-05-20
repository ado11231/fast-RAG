"""fastrag public API."""
from fastrag.chunkers.base import BaseChunker
from fastrag.embedders.base import BaseEmbedder
from fastrag.loaders.base import BaseLoader
from fastrag.pipeline import Pipeline
from fastrag.registry import (
    register_chunker,
    register_embedder,
    register_loader,
    register_store,
)
from fastrag.stores.base import BaseStore

__all__ = [
    "Pipeline",
    "BaseLoader",
    "BaseChunker",
    "BaseEmbedder",
    "BaseStore",
    "register_loader",
    "register_chunker",
    "register_embedder",
    "register_store",
]
