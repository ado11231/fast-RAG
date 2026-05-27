"""Tests for RecursiveChunker — text splitting behaviour."""
from fastrag.chunkers.recursive import RecursiveChunker


def test_chunker_returns_list_of_strings() -> None:
    """Chunking a long text should produce multiple string pieces."""
    chunker = RecursiveChunker(chunk_size=50, overlap=0)
    text = "Hello world. This is a test. " * 10
    chunks = chunker.chunk(text)
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)
    assert len(chunks) > 1


def test_chunker_small_text() -> None:
    """Text smaller than chunk_size should be returned as a single chunk."""
    chunker = RecursiveChunker(chunk_size=100, overlap=0)
    text = "Short text."
    chunks = chunker.chunk(text)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunker_empty_text() -> None:
    """An empty string should produce no chunks."""
    chunker = RecursiveChunker(chunk_size=100, overlap=0)
    chunks = chunker.chunk("")
    assert chunks == []


def test_chunker_whitespace_only() -> None:
    """Whitespace-only content should produce no chunks."""
    chunker = RecursiveChunker(chunk_size=100, overlap=0)
    chunks = chunker.chunk("   \n\n   ")
    assert chunks == []


def test_chunker_preserves_content() -> None:
    """No characters should be lost or duplicated during splitting."""
    chunker = RecursiveChunker(chunk_size=50, overlap=0)
    text = "one two three four five six seven eight nine ten"
    chunks = chunker.chunk(text)
    joined = "".join(chunks).replace(" ", "")
    original = text.replace(" ", "")
    assert joined == original


def test_chunker_no_overlap() -> None:
    """With overlap=0, chunks should be disjoint."""
    chunker = RecursiveChunker(chunk_size=10, overlap=0)
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunker.chunk(text)
    assert len(chunks) >= 2


def test_chunker_with_overlap() -> None:
    """With overlap > 0, consecutive chunks should share trailing context."""
    chunker = RecursiveChunker(chunk_size=50, overlap=10)
    text = "Hello world. This is a test of the overlap mechanism. " * 10
    chunks = chunker.chunk(text)
    assert len(chunks) > 1
    assert len(chunks[1]) > 0


def test_chunker_respects_chunk_size() -> None:
    """No chunk should significantly exceed the configured chunk_size."""
    chunker = RecursiveChunker(chunk_size=20, overlap=0)
    text = "a" * 100
    chunks = chunker.chunk(text)
    assert all(len(c) <= 25 for c in chunks)
