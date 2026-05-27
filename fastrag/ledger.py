"""Delta-sync ledger — tracks SHA-256 hashes of every ingested file.

The ledger lives at ``.fastrag/ledger.json`` relative to the user's
working directory.  On each ingest run, hashes are compared against
the stored values to decide what needs re-ingesting and what can
be skipped.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_LEDGER_PATH = Path(".fastrag/ledger.json")


class Ledger:
    """Tracks SHA-256 hashes of ingested files for delta-sync."""

    def __init__(self, path: Path | str = _DEFAULT_LEDGER_PATH) -> None:
        self._path = Path(path)
        self._data: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        """Read the JSON ledger from disk, handling corruption gracefully."""
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except Exception:
                logger.warning("Corrupt ledger at %s — starting fresh", self._path)
                self._data = {}

    def _save(self) -> None:
        """Persist the in-memory dict to disk as JSON."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    @staticmethod
    def _hash(path: Path) -> str:
        """Return the SHA-256 hex digest of *path*."""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def is_changed(self, path: Path) -> bool:
        """Return True if the file is new or has changed since last ingest."""
        return self._data.get(str(path)) != self._hash(path)

    def update(self, path: Path) -> None:
        """Record the current hash for *path*."""
        self._data[str(path)] = self._hash(path)
        self._save()

    def remove(self, path: Path) -> None:
        """Remove *path* from the ledger."""
        self._data.pop(str(path), None)
        self._save()

    def all_sources(self) -> list[str]:
        """Return all tracked source paths."""
        return list(self._data.keys())

    def clear(self) -> None:
        """Wipe the ledger entirely."""
        self._data = {}
        self._save()

    def entries(self) -> dict[str, str]:
        """Return a snapshot of all ledger entries (path → hash)."""
        return dict(self._data)
