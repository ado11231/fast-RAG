import builtins
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class FakeEmbedding:
    def __init__(self, embedding):
        self.embedding = embedding


class FakeEmbeddingsResponse:
    def __init__(self, data):
        self.data = data


@pytest.fixture(autouse=True)
def mock_openai_module():
    mock_openai = MagicMock()
    with patch.dict("sys.modules", {"openai": mock_openai}):
        yield mock_openai


def test_openai_embedder_embeds_texts(mock_openai_module):
    mock_client = MagicMock()
    mock_openai_module.OpenAI.return_value = mock_client

    fake_vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_client.embeddings.create.return_value = FakeEmbeddingsResponse(
        data=[FakeEmbedding(v) for v in fake_vectors]
    )

    from fastrag.embedders.openai import OpenAIEmbedder

    embedder = OpenAIEmbedder(api_key="test-key")
    result = embedder.embed(["hello", "world"])

    assert isinstance(result, np.ndarray)
    assert result.shape == (2, 3)
    assert result.dtype == np.float32
    np.testing.assert_allclose(result, fake_vectors)


def test_openai_embedder_passes_dimensions(mock_openai_module):
    mock_client = MagicMock()
    mock_openai_module.OpenAI.return_value = mock_client
    mock_client.embeddings.create.return_value = FakeEmbeddingsResponse(data=[])

    from fastrag.embedders.openai import OpenAIEmbedder

    embedder = OpenAIEmbedder(api_key="test-key", model="text-embedding-3-small", dimensions=256)
    embedder.embed(["test"])

    kwargs = mock_client.embeddings.create.call_args[1]
    assert kwargs.get("dimensions") == 256
    assert kwargs.get("model") == "text-embedding-3-small"


@patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"})
def test_openai_embedder_reads_key_from_env(mock_openai_module):
    from fastrag.embedders.openai import OpenAIEmbedder

    OpenAIEmbedder()
    _, kwargs = mock_openai_module.OpenAI.call_args
    assert kwargs["api_key"] == "env-key"


def test_openai_embedder_raises_without_key(mock_openai_module):
    from fastrag.embedders.openai import OpenAIEmbedder

    with pytest.raises(ValueError, match="OpenAI API key is required"):
        OpenAIEmbedder(api_key=None)


def test_openai_embedder_raises_without_openai_package():
    orig_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ImportError("No module named openai")
        return orig_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(ImportError, match="pip install openai"):
            from fastrag.embedders.openai import OpenAIEmbedder

            OpenAIEmbedder(api_key="test-key")
