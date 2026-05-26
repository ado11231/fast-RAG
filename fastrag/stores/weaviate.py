from __future__ import annotations

import logging
import os
from urllib.parse import urlparse

import numpy as np

from fastrag.registry import register_store
from fastrag.stores.base import BaseStore

logger = logging.getLogger(__name__)

_DEFAULT_CLASS = "Document"
_DEFAULT_URL = "http://localhost:8080"


@register_store("weaviate")
class WeaviateStore(BaseStore):
    """Vector store backed by Weaviate.

    Requires the ``weaviate-client`` package (``pip install fastrag[weaviate]``).
    The API key is read from the ``WEAVIATE_API_KEY`` environment variable by default.
    """

    def __init__(
        self,
        url: str = _DEFAULT_URL,
        api_key: str | None = None,
        class_name: str = _DEFAULT_CLASS,
    ) -> None:
        try:
            import weaviate
        except ImportError:
            raise ImportError(
                "weaviate-client is not installed. Run: pip install weaviate-client"
            )

        self._class_name = class_name
        auth = None
        key = api_key or os.environ.get("WEAVIATE_API_KEY")
        if key:
            auth = weaviate.classes.init.Auth.api_key(key)

        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        http_port = parsed.port or 8080
        grpc_port = 50051
        secure = parsed.scheme == "https"

        self._client = weaviate.connect_to_custom(
            http_host=host,
            http_port=http_port,
            http_secure=secure,
            grpc_host=host,
            grpc_port=grpc_port,
            grpc_secure=secure,
            auth_credentials=auth,
        )

        self._ensure_class()
        logger.debug("WeaviateStore ready — class='%s' at '%s'", class_name, url)

    def _ensure_class(self) -> None:
        if self._client.collections.exists(self._class_name):
            self._collection = self._client.collections.get(self._class_name)
        else:
            self._collection = self._client.collections.create(
                name=self._class_name,
                properties=[
                    {"name": "text", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                ],
            )
            logger.debug("Created Weaviate class '%s'", self._class_name)

    def add(
        self,
        ids: list[str],
        vectors: np.ndarray,
        texts: list[str],
        metadatas: list[dict],
    ) -> None:
        with self._collection.batch.fixed_size(batch_size=100) as batch:
            for i in range(len(vectors)):
                props = {"text": texts[i], **metadatas[i]}
                batch.add_object(
                    uuid=ids[i],
                    properties=props,
                    vector=vectors[i].tolist(),
                )

    def query(self, vector: np.ndarray, top_k: int = 5) -> list[dict]:
        response = self._collection.query.near_vector(
            near_vector=vector.tolist(),
            limit=top_k,
            return_metadata=["distance"],
        )
        output = []
        for obj in response.objects:
            meta = {k: v for k, v in obj.properties.items() if k != "text"}
            output.append({
                "text": obj.properties.get("text", ""),
                "metadata": meta,
                "score": 1.0 - obj.metadata.distance if obj.metadata.distance is not None else 0.0,
            })
        return output

    def delete_by_source(self, source: str) -> None:
        self._collection.data.delete_many(
            where={"path": ["source"], "operator": "Equal", "valueText": source}
        )
        logger.debug("Deleted vectors for source '%s'", source)

    def clear(self) -> None:
        self._collection.data.delete_many(
            where={"path": ["source"], "operator": "Like", "valueText": "*"}
        )
        logger.debug("Cleared Weaviate collection '%s'", self._class_name)

    def count(self) -> int:
        response = self._collection.aggregate.over_all(total_count=True)
        return response.total_count if response else 0
