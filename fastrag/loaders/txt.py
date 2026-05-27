"""Plain-text loader — reads UTF-8 text files as-is."""
from pathlib import Path

from fastrag.loaders.base import BaseLoader
from fastrag.registry import register_loader


@register_loader("txt")
class TxtLoader(BaseLoader):
    """Reads plain-text files as-is."""

    def load(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
