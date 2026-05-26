import builtins
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


def _setup_mock_collection(mock_client):
    collection = MagicMock()
    mock_client.collections.exists.return_value = True
    mock_client.collections.get.return_value = collection
    return collection


@pytest.fixture(autouse=True)
def mock_weaviate_module():
    mock_weaviate = MagicMock()
    mock_weaviate.connect_to_custom.return_value = MagicMock()
    with patch.dict("sys.modules", {"weaviate": mock_weaviate}):
        yield mock_weaviate


def test_weaviate_store_add_vectors(mock_weaviate_module):
    from fastrag.stores.weaviate import WeaviateStore

    mock_client = mock_weaviate_module.connect_to_custom.return_value
    collection = _setup_mock_collection(mock_client)

    store = WeaviateStore(api_key="test-key", url="http://localhost:8080")
    ids = ["id1", "id2"]
    vectors = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    texts = ["hello", "world"]
    metadatas = [{"source": "a.txt"}, {"source": "b.txt"}]

    store.add(ids, vectors, texts, metadatas)

    batch_context = collection.batch.fixed_size.return_value.__enter__.return_value
    assert batch_context.add_object.call_count == 2


def test_weaviate_store_query(mock_weaviate_module):
    from fastrag.stores.weaviate import WeaviateStore

    mock_client = mock_weaviate_module.connect_to_custom.return_value
    collection = _setup_mock_collection(mock_client)

    class FakeMetadata:
        distance = 0.05

    class FakeObject:
        properties = {"text": "doc1", "source": "a.txt"}
        metadata = FakeMetadata()

    collection.query.near_vector.return_value = MagicMock(objects=[FakeObject()])

    store = WeaviateStore(api_key="test-key", url="http://localhost:8080")
    results = store.query(np.array([0.1, 0.2], dtype=np.float32), top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == "doc1"
    assert results[0]["score"] == pytest.approx(0.95)


def test_weaviate_store_delete_by_source(mock_weaviate_module):
    from fastrag.stores.weaviate import WeaviateStore

    mock_client = mock_weaviate_module.connect_to_custom.return_value
    collection = _setup_mock_collection(mock_client)

    store = WeaviateStore(api_key="test-key", url="http://localhost:8080")
    store.delete_by_source("a.txt")

    collection.data.delete_many.assert_called_once_with(
        where={"path": ["source"], "operator": "Equal", "valueText": "a.txt"}
    )


def test_weaviate_store_clear(mock_weaviate_module):
    from fastrag.stores.weaviate import WeaviateStore

    mock_client = mock_weaviate_module.connect_to_custom.return_value
    collection = _setup_mock_collection(mock_client)

    store = WeaviateStore(api_key="test-key", url="http://localhost:8080")
    store.clear()

    collection.data.delete_many.assert_called_once_with(
        where={"path": ["source"], "operator": "Like", "valueText": "*"}
    )


def test_weaviate_store_count(mock_weaviate_module):
    from fastrag.stores.weaviate import WeaviateStore

    mock_client = mock_weaviate_module.connect_to_custom.return_value
    collection = _setup_mock_collection(mock_client)

    class FakeAggregate:
        total_count = 42

    collection.aggregate.over_all.return_value = FakeAggregate()

    store = WeaviateStore(api_key="test-key", url="http://localhost:8080")
    assert store.count() == 42


def test_weaviate_store_raises_without_weaviate_package():
    orig_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "weaviate":
            raise ImportError("No module named weaviate")
        return orig_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(ImportError, match="pip install weaviate-client"):
            from fastrag.stores.weaviate import WeaviateStore

            WeaviateStore()
