"""Tests for MarkdownLoader — Markdown file extraction."""
from pathlib import Path

from fastrag.loaders.md import MarkdownLoader


def test_md_loader_returns_string(tmp_path: Path) -> None:
    """Verify the loader returns Markdown content as a plain string."""
    file = tmp_path / "test.md"
    file.write_text("# Heading\n\nSome text.")
    loader = MarkdownLoader()
    result = loader.load(file)
    assert isinstance(result, str)
    assert "# Heading" in result


def test_md_loader_handles_frontmatter(tmp_path: Path) -> None:
    """YAML frontmatter is passed through as raw text (not stripped)."""
    file = tmp_path / "doc.md"
    file.write_text("---\ntitle: Test\n---\n\nBody text here.")
    loader = MarkdownLoader()
    result = loader.load(file)
    assert "Body text here." in result


def test_md_loader_empty(tmp_path: Path) -> None:
    """An empty Markdown file should return an empty string."""
    file = tmp_path / "empty.md"
    file.write_text("")
    loader = MarkdownLoader()
    result = loader.load(file)
    assert result == ""
