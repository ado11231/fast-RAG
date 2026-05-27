"""Abstract base class for all vector stores.

Every store must implement five methods covering upsert, similarity
search, source-tracked deletion, full clear, and counting.
The Pipeline depends on every one of these.
"""
from abc import ABC, abstractmethod

import numpy as np


class BaseStore(ABC):
    """Persists vectors with metadata and supports similarity search."""

    @abstractmethod
    def add(
        self,
        ids: list[str],
        vectors: np.ndarray,
        texts: list[str],
        metadatas: list[dict],
    ) -> None:
        """Upsert *vectors* with associated *texts* and *metadatas*."""
        ...

    @abstractmethod
    def query(self, vector: np.ndarray, top_k: int = 5) -> list[dict]:
        """Return the *top_k* closest stored chunks as dicts with 'text' and 'metadata'."""
        ...

    @abstractmethod
    def delete_by_source(self, source: str) -> None:
        """Remove all vectors whose metadata['source'] equals *source*."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Delete every vector in the store."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the number of vectors currently in the store."""
        ...
