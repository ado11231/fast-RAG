"""Recursive character chunker — splits text on descending separator priority.

Tries paragraph breaks first, then newlines, then sentence endings,
then spaces, and finally falls back to fixed-length character splits.
This produces natural-feeling chunks that rarely cut a sentence in half.
"""
from fastrag.chunkers.base import BaseChunker
from fastrag.registry import register_chunker


@register_chunker("recursive")
class RecursiveChunker(BaseChunker):
    """Splits text recursively on paragraph, newline, then sentence boundaries."""

    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, text: str) -> list[str]:
        return self._split(text, self._separators)

    def _split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split *text* using the ordered list of *separators*."""
        if len(text) <= self.chunk_size:
            stripped = text.strip()
            return [stripped] if stripped else []

        sep = separators[0]
        next_seps = separators[1:]

        if sep == "":
            return self._fixed_split(text)

        parts = text.split(sep)
        chunks: list[str] = []
        current = ""

        for part in parts:
            candidate = current + (sep if current else "") + part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    sub = (
                        self._split(current, next_seps)
                        if len(current) > self.chunk_size
                        else [current.strip()]
                    )
                    chunks.extend(sub)
                current = part

        if current.strip():
            sub = (
                self._split(current, next_seps)
                if len(current) > self.chunk_size
                else [current.strip()]
            )
            chunks.extend(sub)

        return self._apply_overlap(chunks)

    def _fixed_split(self, text: str) -> list[str]:
        """Fallback: split by exact character count with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end].strip())
            start = end - self.overlap
        return [c for c in chunks if c]

    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        """Add trailing tokens from the previous chunk to the next one."""
        if self.overlap <= 0 or len(chunks) <= 1:
            return chunks
        result = [chunks[0]]
        for i in range(1, len(chunks)):
            tail = chunks[i - 1][-self.overlap:]
            result.append(tail + " " + chunks[i])
        return result
