"""Markdown loader — reads Markdown as plain text without rendering."""
from pathlib import Path

from fastrag.loaders.base import BaseLoader
from fastrag.registry import register_loader


@register_loader("md")
class MarkdownLoader(BaseLoader):
    """Reads Markdown files as plain text (no rendering)."""

    def load(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
