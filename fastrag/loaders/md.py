from pathlib import Path

from fastrag.loaders.base import BaseLoader


class MarkdownLoader(BaseLoader):
    """Reads Markdown files as plain text (no rendering)."""

    def load(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
