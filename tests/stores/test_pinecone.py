"""Tests for PineconeStore — serverless vector database integration.

These tests require the ``pinecone-client`` package and a valid
``PINECONE_API_KEY`` environment variable to run.
"""
from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("PINECONE_API_KEY"),
    reason="PINECONE_API_KEY not set",
)
def test_pinecone_add_and_query() -> None:
    """Integration test: add vectors, query them, verify results."""
    import numpy as np
    from fastrag.stores.pinecone import PineconeStore

    store = PineconeStore(index_name="fastrag-test", dimension=4)
    store.clear()

    store.add(
        ids=["1", "2"],
        vectors=np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], dtype=np.float32),
        texts=["hello", "world"],
        metadatas=[{"source": "a.txt"}, {"source": "b.txt"}],
    )
    assert store.count() >= 2

    query_vector = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    results = store.query(query_vector, top_k=5)
    assert len(results) > 0

    store.clear()
