from __future__ import annotations

import logging
import os

import numpy as np

from fastrag.embedders.base import BaseEmbedder
from fastrag.registry import register_embedder

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "text-embedding-3-small"


@register_embedder("openai")
class OpenAIEmbedder(BaseEmbedder):
    """Embedder backed by the OpenAI Embeddings API.

    Requires the ``openai`` package (``pip install fastrag[openai]``).
    The API key is read from the ``OPENAI_API_KEY`` environment variable by default.
    """

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        api_key: str | None = None,
        dimensions: int | None = None,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai is not installed. Run: pip install openai"
            )

        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "OpenAI API key is required. Set the OPENAI_API_KEY environment "
                "variable or pass api_key to the constructor."
            )
        self._client = OpenAI(api_key=self._api_key)
        self._dimensions = dimensions
        logger.debug(
            "OpenAIEmbedder ready — model='%s'%s",
            model,
            f", dimensions={dimensions}" if dimensions else "",
        )

    def embed(self, texts: list[str]) -> np.ndarray:
        kwargs = {"model": self._model, "input": texts}
        if self._dimensions is not None:
            kwargs["dimensions"] = self._dimensions

        response = self._client.embeddings.create(**kwargs)
        vectors = [item.embedding for item in response.data]
        return np.array(vectors, dtype=np.float32)
