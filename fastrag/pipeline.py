"""Pipeline — the main entry point.

Wires a Loader, Chunker, Embedder, and Store together into a single
ingest-and-query workflow.  The user never has to touch the individual
components unless they want custom behaviour.
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from fastrag.chunkers.base import BaseChunker
from fastrag.chunkers.recursive import RecursiveChunker
from fastrag.embedders.base import BaseEmbedder
from fastrag.embedders.sentence_transformers import SentenceTransformerEmbedder
from fastrag.loaders import get_loader
from fastrag.stores.base import BaseStore
from fastrag.stores.chroma import ChromaStore

if TYPE_CHECKING:
    from fastrag.ledger import Ledger

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates ingestion and querying.

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
        """Use defaults (RecursiveChunker, SentenceTransformer, ChromaStore) when
        nothing is provided — zero-config for the common case."""
        self.chunker = chunker or RecursiveChunker()
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.store = store or ChromaStore()

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, path: str | Path, ledger: Ledger | None = None) -> int:
        """Ingest a file or every supported file under a directory.

        When a *ledger* is provided, unchanged files are skipped and
        vectors for deleted files are removed (delta sync).
        Returns the number of chunks stored.
        """
        target = Path(path)
        files = list(target.rglob("*")) if target.is_dir() else [target]
        files = [f for f in files if f.is_file()]
        current_sources = {str(f) for f in files}

        if ledger:
            for source in ledger.all_sources():
                if source not in current_sources:
                    self.store.delete_by_source(source)
                    ledger.remove(Path(source))
                    logger.info("Removed deleted source: %s", source)

        total = 0
        for file in files:
            if ledger and not ledger.is_changed(file):
                logger.debug("Skipping unchanged: %s", file)
                continue
            if ledger and str(file) in ledger.all_sources():
                self.store.delete_by_source(str(file))
            count = self._ingest_file(file)
            total += count
            if ledger and count > 0:
                ledger.update(file)
        return total

    def _ingest_file(self, path: Path) -> int:
        """Run one file through the full pipeline: load → chunk → embed → store."""
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
        ids = [
            f"{hashlib.md5(source.encode()).hexdigest()}-{i}"
            for i in range(len(chunks))
        ]
        metadatas = [{"source": source} for _ in chunks]

        self.store.add(ids=ids, vectors=vectors, texts=chunks, metadatas=metadatas)
        logger.info("Stored %d chunks from %s", len(chunks), path)
        return len(chunks)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        """Search the store for chunks most relevant to *question*.

        Returns a list of dicts with 'text', 'metadata', and 'score'.
        """
        vector = self.embedder.embed([question])[0]
        return self.store.query(vector, top_k=top_k)
