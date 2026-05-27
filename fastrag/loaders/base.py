"""Abstract base class for all loaders.

Every loader must implement ``load()`` to extract text from a file path.
The Pipeline calls this method automatically based on the file extension.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseLoader(ABC):
    """Reads a single file and returns its raw text content."""

    @abstractmethod
    def load(self, path: Path) -> str:
        """Extract and return all text from *path*."""
        ...
