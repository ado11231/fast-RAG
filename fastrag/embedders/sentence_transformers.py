from __future__ import annotations

import logging

import numpy as np

from fastrag.embedders.base import BaseEmbedder

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "all-MiniLM-L6-v2"


class SentenceTransformerEmbedder(BaseEmbedder):
    """Local embedder backed by sentence-transformers (no API key required)."""

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. Run: pip install sentence-transformers"
            )
        logger.debug("Loading sentence-transformer model '%s'", model_name)
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return vectors.astype(np.float32)
