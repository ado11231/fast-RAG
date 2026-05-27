"""Tests for the decorator-based plugin registry."""
from fastrag.chunkers.recursive import RecursiveChunker
from fastrag.registry import (
    _CHUNKERS,
    _EMBEDDERS,
    _LOADERS,
    _STORES,
    get_chunker,
    get_embedder,
    get_loader,
    get_store,
    register_chunker,
    register_embedder,
    register_loader,
    register_store,
)
from fastrag.stores.chroma import ChromaStore


def test_register_and_get_loader() -> None:
    """A class decorated with @register_loader should be retrievable by name."""
    @register_loader("test-loader")
    class FakeLoader:
        pass
    cls = get_loader("test-loader")
    assert cls is FakeLoader
    _LOADERS.pop("test-loader", None)


def test_register_and_get_embedder() -> None:
    """A class decorated with @register_embedder should be retrievable by name."""
    @register_embedder("test-embedder")
    class FakeEmbedder:
        pass
    cls = get_embedder("test-embedder")
    assert cls is FakeEmbedder
    _EMBEDDERS.pop("test-embedder", None)


def test_register_and_get_store() -> None:
    """A class decorated with @register_store should be retrievable by name."""
    @register_store("test-store")
    class FakeStore:
        pass
    cls = get_store("test-store")
    assert cls is FakeStore
    _STORES.pop("test-store", None)


def test_register_and_get_chunker() -> None:
    """A class decorated with @register_chunker should be retrievable by name."""
    @register_chunker("test-chunker")
    class FakeChunker:
        pass
    cls = get_chunker("test-chunker")
    assert cls is FakeChunker
    _CHUNKERS.pop("test-chunker", None)


def test_get_nonexistent_loader_raises() -> None:
    """Requesting an unregistered loader should raise KeyError."""
    try:
        get_loader("nonexistent-loader")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_get_nonexistent_store_raises() -> None:
    """Requesting an unregistered store should raise KeyError."""
    try:
        get_store("nonexistent-store")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_get_nonexistent_embedder_raises() -> None:
    """Requesting an unregistered embedder should raise KeyError."""
    try:
        get_embedder("nonexistent-embedder")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_get_nonexistent_chunker_raises() -> None:
    """Requesting an unregistered chunker should raise KeyError."""
    try:
        get_chunker("nonexistent-chunker")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_builtins_are_registered() -> None:
    """The built-in recursive chunker and Chroma store should be pre-registered."""
    assert "recursive" in _CHUNKERS
    assert _CHUNKERS["recursive"] is RecursiveChunker
    assert "chroma" in _STORES
