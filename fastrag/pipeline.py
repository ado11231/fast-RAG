"""Pipeline — the main entry point that wires Loader, Chunker, Embedder, and Store together."""
from __future__ import annotations

import hashlib
import logging
import uuid
from pathlib import Path

from fastrag.chunkers.base import BaseChunker
from fastrag.chunkers.recursive import RecursiveChunker
from fastrag.embedders.base import BaseEmbedder
from fastrag.embedders.sentence_transformers import SentenceTransformerEmbedder
from fastrag.loaders import get_loader
from fastrag.stores.base import BaseStore
from fastrag.stores.chroma import ChromaStore

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Orchestrates ingestion and querying.

    Usage::

        pipeline = Pipeline()
        pipeline.ingest("docs/")
        results = pipeline.query("What is the refund policy?")
    """

    def __init__(
        self,
        chunker: BaseChunker | None = None,
        embedder: BaseEmbedder | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self.chunker = chunker or RecursiveChunker()
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.store = store or ChromaStore()

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, path: str | Path) -> int:
        """
        Ingest a file or every supported file under a directory.

        Returns the number of chunks stored.
        """
        target = Path(path)
        if target.is_dir():
            files = [f for f in target.rglob("*") if f.is_file()]
        else:
            files = [target]

        total = 0
        for file in files:
            total += self._ingest_file(file)
        return total

    def _ingest_file(self, path: Path) -> int:
        suffix = path.suffix.lower()
        try:
            loader = get_loader(suffix)
        except ValueError:
            logger.info("Skipping unsupported file type: %s", path)
            return 0

        logger.info("Ingesting %s", path)
        text = loader.load(path)
        if not text.strip():
            logger.warning("No text extracted from %s", path)
            return 0

        chunks = self.chunker.chunk(text)
        if not chunks:
            return 0

        vectors = self.embedder.embed(chunks)
        source = str(path)
        ids = [f"{hashlib.md5(source.encode()).hexdigest()}-{i}" for i in range(len(chunks))]
        metadatas = [{"source": source} for _ in chunks]

        self.store.add(ids=ids, vectors=vectors, texts=chunks, metadatas=metadatas)
        logger.info("Stored %d chunks from %s", len(chunks), path)
        return len(chunks)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        """
        Search the store for chunks most relevant to *question*.

        Returns a list of dicts with 'text', 'metadata', and 'score'.
        """
        vector = self.embedder.embed([question])[0]
        return self.store.query(vector, top_k=top_k)
