"""Tests for WeaviateStore — open-source vector database integration.

These tests require a running Weaviate instance and the
``WEAVIATE_URL`` environment variable to be set.
"""
import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("WEAVIATE_URL"),
    reason="WEAVIATE_URL not set — no Weaviate instance available",
)
def test_weaviate_add_and_query() -> None:
    """Integration test: add vectors, query them, verify results."""
    import numpy as np
    from fastrag.stores.weaviate import WeaviateStore

    store = WeaviateStore(url=os.environ["WEAVIATE_URL"], class_name="TestDoc")
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
