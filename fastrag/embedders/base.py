"""Abstract base class for all embedders.

Every embedder must implement ``embed()`` to convert a list of text
strings into a 2-D numpy array where each row is a vector.
"""
from abc import ABC, abstractmethod

import numpy as np


class BaseEmbedder(ABC):
    """Converts a list of text strings into a 2-D numpy array of vectors."""

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        """Return an (N, D) float32 array — one row per input text."""
        ...
