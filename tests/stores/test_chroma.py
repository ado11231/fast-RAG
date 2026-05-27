"""Tests for ChromaStore — local, persisted vector store via ChromaDB."""
from pathlib import Path

import numpy as np
import pytest

from fastrag.stores.chroma import ChromaStore


@pytest.fixture
def store(tmp_path: Path) -> ChromaStore:
    """Create an isolated ChromaStore in a temp directory for each test."""
    persist_dir = tmp_path / ".fastrag" / "chroma"
    return ChromaStore(persist_dir=str(persist_dir), collection_name="test")


def test_add_and_count(store: ChromaStore) -> None:
    """Adding vectors should increase the stored count."""
    store.add(
        ids=["1", "2"],
        vectors=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
        texts=["hello", "world"],
        metadatas=[{"source": "a.txt"}, {"source": "b.txt"}],
    )
    assert store.count() == 2


def test_query_returns_results(store: ChromaStore) -> None:
    """Querying should return stored chunks with text, metadata, and score."""
    store.add(
        ids=["1", "2"],
        vectors=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
        texts=["hello world", "goodbye world"],
        metadatas=[{"source": "a.txt"}, {"source": "b.txt"}],
    )
    query_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    results = store.query(query_vector, top_k=5)
    assert len(results) == 2
    assert "text" in results[0]
    assert "metadata" in results[0]
    assert "score" in results[0]


def test_delete_by_source(store: ChromaStore) -> None:
    """Deleting by source should remove only vectors matching that source."""
    store.add(
        ids=["1", "2"],
        vectors=np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
        texts=["hello", "world"],
        metadatas=[{"source": "a.txt"}, {"source": "b.txt"}],
    )
    store.delete_by_source("a.txt")
    assert store.count() == 1


def test_clear(store: ChromaStore) -> None:
    """Clearing the store should remove all vectors."""
    store.add(
        ids=["1"],
        vectors=np.array([[1.0, 0.0, 0.0]], dtype=np.float32),
        texts=["hello"],
        metadatas=[{"source": "a.txt"}],
    )
    store.clear()
    assert store.count() == 0


def test_query_with_no_data(store: ChromaStore) -> None:
    """Querying an empty store should return an empty list."""
    query_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    results = store.query(query_vector, top_k=5)
    assert results == []
