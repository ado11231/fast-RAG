"""Tests for OpenAIEmbedder — remote embedding via OpenAI API.

These tests require the ``openai`` package and a valid
``OPENAI_API_KEY`` environment variable to run.
"""
import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)
def test_openai_embed_real() -> None:
    """Integration test: embed two texts and verify the output shape."""
    from fastrag.embedders.openai import OpenAIEmbedder

    embedder = OpenAIEmbedder()
    vectors = embedder.embed(["hello world", "test"])
    assert vectors.shape[0] == 2
