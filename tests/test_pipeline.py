"""Tests for Pipeline — end-to-end ingest and query orchestration."""
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from fastrag.chunkers.base import BaseChunker
from fastrag.embedders.base import BaseEmbedder
from fastrag.ledger import Ledger
from fastrag.pipeline import Pipeline
from fastrag.stores.base import BaseStore


class DummyStore(BaseStore):
    """In-memory store that returns constant scores — no external deps needed."""

    def __init__(self) -> None:
        self.data: list[dict[str, Any]] = []

    def add(
        self,
        ids: list[str],
        vectors: np.ndarray,
        texts: list[str],
        metadatas: list[dict],
    ) -> None:
        for i in range(len(texts)):
            self.data.append({
                "id": ids[i],
                "text": texts[i],
                "metadata": metadatas[i],
            })

    def query(self, vector: np.ndarray, top_k: int = 5) -> list[dict]:
        return [
            {"text": d["text"], "metadata": d["metadata"], "score": 0.5}
            for d in self.data[:top_k]
        ]

    def delete_by_source(self, source: str) -> None:
        self.data = [d for d in self.data if d["metadata"].get("source") != source]

    def clear(self) -> None:
        self.data = []

    def count(self) -> int:
        return len(self.data)


class DummyEmbedder(BaseEmbedder):
    """Returns zero vectors — no model loading required."""

    def embed(self, texts: list[str]) -> np.ndarray:
        return np.zeros((len(texts), 4), dtype=np.float32)


class DummyChunker(BaseChunker):
    """Splits on exact character count — deterministic and fast."""

    def __init__(self, chunk_size: int = 10) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        result = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i : i + self.chunk_size].strip()
            if chunk:
                result.append(chunk)
        return result


@pytest.fixture
def pipeline() -> Pipeline:
    return Pipeline(chunker=DummyChunker(), embedder=DummyEmbedder(), store=DummyStore())


def test_ingest_txt_file(pipeline: Pipeline, tmp_path: Path) -> None:
    """Ingesting a single .txt file should produce chunks."""
    file = tmp_path / "test.txt"
    file.write_text("Hello world. This is a test document.")
    count = pipeline.ingest(file)
    assert count > 0
    assert pipeline.store.count() > 0


def test_ingest_directory(pipeline: Pipeline, tmp_path: Path) -> None:
    """Ingesting a directory should process every supported file inside."""
    (tmp_path / "a.txt").write_text("File A content here")
    (tmp_path / "b.txt").write_text("File B content here")
    count = pipeline.ingest(tmp_path)
    assert count > 0


def test_query_returns_results(pipeline: Pipeline, tmp_path: Path) -> None:
    """After ingestion, querying should return stored chunks."""
    file = tmp_path / "test.txt"
    file.write_text("The refund policy allows returns within 30 days.")
    pipeline.ingest(file)
    results = pipeline.query("What is the refund policy?", top_k=3)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "text" in results[0]
    assert "metadata" in results[0]


def test_ingest_skips_unsupported(pipeline: Pipeline, tmp_path: Path) -> None:
    """Files with unsupported extensions should be silently skipped."""
    file = tmp_path / "test.xyz"
    file.write_text("unsupported")
    count = pipeline.ingest(file)
    assert count == 0


def test_ingest_with_ledger_skips_unchanged(pipeline: Pipeline, tmp_path: Path) -> None:
    """An unchanged file tracked by the ledger should not be re-ingested."""
    ledger = Ledger(path=tmp_path / "ledger.json")
    file = tmp_path / "doc.txt"
    file.write_text("content")
    count = pipeline.ingest(file, ledger=ledger)
    assert count > 0
    count = pipeline.ingest(file, ledger=ledger)
    assert count == 0


def test_ingest_with_ledger_detects_changes(pipeline: Pipeline, tmp_path: Path) -> None:
    """A modified file tracked by the ledger should be re-ingested."""
    ledger = Ledger(path=tmp_path / "ledger.json")
    file = tmp_path / "doc.txt"
    file.write_text("version 1")
    pipeline.ingest(file, ledger=ledger)
    file.write_text("version 2")
    count = pipeline.ingest(file, ledger=ledger)
    assert count > 0


def test_pipeline_empty_query(pipeline: Pipeline) -> None:
    """Querying a store with no data should return an empty list."""
    results = pipeline.query("anything", top_k=5)
    assert results == []
