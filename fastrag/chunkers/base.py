"""Abstract base class for all chunkers.

Every chunker must implement ``chunk()`` to split a long string into
smaller pieces.  The Pipeline calls this after loading and before
embedding.
"""
from abc import ABC, abstractmethod


class BaseChunker(ABC):
    """Splits a string of text into smaller chunks."""

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Return a list of text chunks derived from *text*."""
        ...
