"""Tests for SentenceTransformerEmbedder — local embedding via sentence-transformers."""
import numpy as np
import pytest

from fastrag.embedders.sentence_transformers import SentenceTransformerEmbedder


def test_embed_returns_float32_array() -> None:
    """Verify the embedder returns a float32 numpy array with expected shape."""
    try:
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    vectors = embedder.embed(["hello world", "test document"])
    assert isinstance(vectors, np.ndarray)
    assert vectors.dtype == np.float32
    assert vectors.shape == (2, 384)


def test_embed_single_text() -> None:
    """A single input should produce a single vector row."""
    try:
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    vectors = embedder.embed(["single chunk"])
    assert vectors.shape == (1, 384)


def test_embed_empty_list() -> None:
    """An empty input list should not crash and return a 1-D array."""
    try:
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    vectors = embedder.embed([])
    assert vectors.ndim == 1 or vectors.shape == (0,)
