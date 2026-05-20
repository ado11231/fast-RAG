from pathlib import Path

from fastrag.loaders.base import BaseLoader


class TxtLoader(BaseLoader):
    """Reads plain-text files as-is."""

    def load(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
