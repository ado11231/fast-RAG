import builtins
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def mock_pinecone_module():
    mock_pinecone = MagicMock()
    mock_pinecone.list_indexes.return_value = ["fastrag"]
    mock_pinecone.Index.return_value = MagicMock()
    with patch.dict("sys.modules", {"pinecone": mock_pinecone}):
        yield mock_pinecone


def test_pinecone_store_add_vectors(mock_pinecone_module):
    from fastrag.stores.pinecone import PineconeStore

    store = PineconeStore(api_key="test-key")
    mock_index = mock_pinecone_module.Index.return_value

    ids = ["id1", "id2"]
    vectors = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    texts = ["hello", "world"]
    metadatas = [{"source": "a.txt"}, {"source": "b.txt"}]

    store.add(ids, vectors, texts, metadatas)

    mock_index.upsert.assert_called_once()
    args = mock_index.upsert.call_args[1]["vectors"]
    assert len(args) == 2
    assert args[0][0] == "id1"
    assert args[0][2]["text"] == "hello"
    assert args[0][2]["source"] == "a.txt"


def test_pinecone_store_query(mock_pinecone_module):
    from fastrag.stores.pinecone import PineconeStore

    store = PineconeStore(api_key="test-key")
    mock_index = mock_pinecone_module.Index.return_value
    mock_index.query.return_value = {
        "matches": [
            {"id": "id1", "metadata": {"text": "doc1", "source": "a.txt"}, "score": 0.95},
            {"id": "id2", "metadata": {"text": "doc2", "source": "b.txt"}, "score": 0.80},
        ]
    }

    results = store.query(np.array([0.1, 0.2], dtype=np.float32), top_k=2)

    assert len(results) == 2
    assert results[0]["text"] == "doc1"
    assert results[0]["score"] == 0.95
    assert results[0]["metadata"]["source"] == "a.txt"


def test_pinecone_store_delete_by_source(mock_pinecone_module):
    from fastrag.stores.pinecone import PineconeStore

    store = PineconeStore(api_key="test-key")
    mock_index = mock_pinecone_module.Index.return_value

    store.delete_by_source("a.txt")

    mock_index.delete.assert_called_once_with(filter={"source": {"$eq": "a.txt"}})


def test_pinecone_store_clear(mock_pinecone_module):
    from fastrag.stores.pinecone import PineconeStore

    store = PineconeStore(api_key="test-key")
    mock_index = mock_pinecone_module.Index.return_value

    store.clear()

    mock_index.delete.assert_called_once_with(delete_all=True)


def test_pinecone_store_count(mock_pinecone_module):
    from fastrag.stores.pinecone import PineconeStore

    store = PineconeStore(api_key="test-key")
    mock_index = mock_pinecone_module.Index.return_value
    mock_index.describe_index_stats.return_value = {"total_vector_count": 42}

    assert store.count() == 42


def test_pinecone_store_raises_without_key(mock_pinecone_module):
    from fastrag.stores.pinecone import PineconeStore

    with pytest.raises(ValueError, match="Pinecone API key is required"):
        PineconeStore(api_key=None)


def test_pinecone_store_raises_without_pinecone_package():
    orig_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pinecone":
            raise ImportError("No module named pinecone")
        return orig_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(ImportError, match="pip install pinecone-client"):
            from fastrag.stores.pinecone import PineconeStore

            PineconeStore(api_key="test-key")
