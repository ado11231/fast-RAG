"""Decorator-based plugin registry for loaders, chunkers, embedders, and stores."""
from __future__ import annotations

import logging
from typing import Callable, TypeVar

from fastrag.chunkers.base import BaseChunker
from fastrag.embedders.base import BaseEmbedder
from fastrag.loaders.base import BaseLoader
from fastrag.stores.base import BaseStore

logger = logging.getLogger(__name__)

T = TypeVar("T")

_LOADERS: dict[str, type[BaseLoader]] = {}
_CHUNKERS: dict[str, type[BaseChunker]] = {}
_EMBEDDERS: dict[str, type[BaseEmbedder]] = {}
_STORES: dict[str, type[BaseStore]] = {}


def _register(registry: dict, name: str, cls: type) -> None:
    if name in registry:
        logger.warning("Name collision in registry: '%s' will be overwritten", name)
    registry[name] = cls
    logger.debug("Registered '%s' -> %s", name, cls.__qualname__)


def register_loader(name: str) -> Callable[[type[BaseLoader]], type[BaseLoader]]:
    """Decorator: register a BaseLoader subclass under *name*."""
    def decorator(cls: type[BaseLoader]) -> type[BaseLoader]:
        _register(_LOADERS, name, cls)
        return cls
    return decorator


def register_chunker(name: str) -> Callable[[type[BaseChunker]], type[BaseChunker]]:
    """Decorator: register a BaseChunker subclass under *name*."""
    def decorator(cls: type[BaseChunker]) -> type[BaseChunker]:
        _register(_CHUNKERS, name, cls)
        return cls
    return decorator


def register_embedder(name: str) -> Callable[[type[BaseEmbedder]], type[BaseEmbedder]]:
    """Decorator: register a BaseEmbedder subclass under *name*."""
    def decorator(cls: type[BaseEmbedder]) -> type[BaseEmbedder]:
        _register(_EMBEDDERS, name, cls)
        return cls
    return decorator


def register_store(name: str) -> Callable[[type[BaseStore]], type[BaseStore]]:
    """Decorator: register a BaseStore subclass under *name*."""
    def decorator(cls: type[BaseStore]) -> type[BaseStore]:
        _register(_STORES, name, cls)
        return cls
    return decorator


def get_loader(name: str) -> type[BaseLoader]:
    if name not in _LOADERS:
        raise KeyError(f"No loader registered under '{name}'")
    return _LOADERS[name]


def get_chunker(name: str) -> type[BaseChunker]:
    if name not in _CHUNKERS:
        raise KeyError(f"No chunker registered under '{name}'")
    return _CHUNKERS[name]


def get_embedder(name: str) -> type[BaseEmbedder]:
    if name not in _EMBEDDERS:
        raise KeyError(f"No embedder registered under '{name}'")
    return _EMBEDDERS[name]


def get_store(name: str) -> type[BaseStore]:
    if name not in _STORES:
        raise KeyError(f"No store registered under '{name}'")
    return _STORES[name]
