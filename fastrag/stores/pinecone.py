"""Pinecone store adapter — serverless vector database.

Requires the ``pinecone-client`` package (``pip install fastrag[pinecone]``).
The API key is read from ``PINECONE_API_KEY`` by default.
Creates the index automatically if it does not exist.
"""
from __future__ import annotations

import logging
import os
import uuid

import numpy as np

from fastrag.registry import register_store
from fastrag.stores.base import BaseStore

logger = logging.getLogger(__name__)

_DEFAULT_INDEX = "fastrag"
_DEFAULT_METRIC = "cosine"


@register_store("pinecone")
class PineconeStore(BaseStore):
    """Vector store backed by Pinecone serverless index.

    Requires the ``pinecone-client`` package (``pip install fastrag[pinecone]``).
    The API key is read from the ``PINECONE_API_KEY`` environment variable by default.
    """

    def __init__(
        self,
        index_name: str = _DEFAULT_INDEX,
        api_key: str | None = None,
        environment: str | None = None,
        dimension: int = 384,
        metric: str = _DEFAULT_METRIC,
    ) -> None:
        try:
            import pinecone
        except ImportError:
            raise ImportError(
                "pinecone-client is not installed. Run: pip install pinecone-client"
            )
        self._api_key = api_key or os.environ.get("PINECONE_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Pinecone API key is required. Set the PINECONE_API_KEY "
                "environment variable or pass api_key to the constructor."
            )
        init_kwargs = {"api_key": self._api_key}
        if environment is not None:
            init_kwargs["environment"] = environment
        pinecone.init(**init_kwargs)

        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
            )
            logger.debug("Created Pinecone index '%s'", index_name)

        self._index = pinecone.Index(index_name)
        self._index_name = index_name
        logger.debug("PineconeStore ready — index='%s', dimension=%d", index_name, dimension)

    def add(
        self,
        ids: list[str],
        vectors: np.ndarray,
        texts: list[str],
        metadatas: list[dict],
    ) -> None:
        records = [
            (
                ids[i] if ids[i] else str(uuid.uuid4()),
                vectors[i].tolist(),
                {**metadatas[i], "text": texts[i]},
            )
            for i in range(len(vectors))
        ]
        self._index.upsert(vectors=records)

    def query(self, vector: np.ndarray, top_k: int = 5) -> list[dict]:
        results = self._index.query(
            vector=vector.tolist(),
            top_k=top_k,
            include_metadata=True,
        )
        output = []
        for match in results.get("matches", []):
            meta = dict(match.get("metadata", {}))
            text = meta.pop("text", "")
            output.append({
                "text": text,
                "metadata": meta,
                "score": match.get("score", 0.0),
            })
        return output

    def delete_by_source(self, source: str) -> None:
        self._index.delete(filter={"source": {"$eq": source}})
        logger.debug("Deleted vectors for source '%s'", source)

    def clear(self) -> None:
        self._index.delete(delete_all=True)
        logger.debug("Cleared Pinecone index '%s'", self._index_name)

    def count(self) -> int:
        stats = self._index.describe_index_stats()
        return stats.get("total_vector_count", 0)
