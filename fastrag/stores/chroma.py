"""ChromaDB store — local, zero-config, persisted to disk.

The default vector store for fastrag.  Uses cosine distance
(HNSW index) and persists everything under ``.fastrag/chroma/``.
No external services or accounts required.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from fastrag.registry import register_store
from fastrag.stores.base import BaseStore

logger = logging.getLogger(__name__)

_DEFAULT_PERSIST_DIR = ".fastrag/chroma"
_DEFAULT_COLLECTION = "fastrag"


@register_store("chroma")
class ChromaStore(BaseStore):
    """Vector store backed by ChromaDB, persisted to disk."""

    def __init__(
        self,
        persist_dir: str | Path = _DEFAULT_PERSIST_DIR,
        collection_name: str = _DEFAULT_COLLECTION,
    ) -> None:
        try:
            import chromadb
        except ImportError:
            raise ImportError("chromadb is not installed. Run: pip install chromadb")
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.debug("ChromaStore ready — collection '%s' at '%s'", collection_name, persist_dir)

    def add(
        self,
        ids: list[str],
        vectors: np.ndarray,
        texts: list[str],
        metadatas: list[dict],
    ) -> None:
        self._collection.upsert(
            ids=ids,
            embeddings=vectors.tolist(),
            documents=texts,
            metadatas=metadatas,
        )

    def query(self, vector: np.ndarray, top_k: int = 5) -> list[dict]:
        results = self._collection.query(
            query_embeddings=[vector.tolist()],
            n_results=min(top_k, self._collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )
        output = []
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        for doc, meta, dist in zip(docs, metas, dists):
            output.append({"text": doc, "metadata": meta, "score": 1.0 - dist})
        return output

    def delete_by_source(self, source: str) -> None:
        results = self._collection.get(where={"source": source}, include=[])
        ids = results.get("ids", [])
        if ids:
            self._collection.delete(ids=ids)
            logger.debug("Deleted %d vectors for source '%s'", len(ids), source)

    def count(self) -> int:
        return self._collection.count()

    def clear(self) -> None:
        name = self._collection.name
        self._client.delete_collection(name)
        self._collection = self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.debug("Cleared collection '%s'", name)
