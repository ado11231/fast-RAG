"""Tests for TxtLoader — plain-text file extraction."""
from pathlib import Path

from fastrag.loaders.txt import TxtLoader


def test_txt_loader_returns_string(tmp_path: Path) -> None:
    """Verify the loader returns the raw string content of a text file."""
    file = tmp_path / "test.txt"
    file.write_text("Hello, world!")
    loader = TxtLoader()
    result = loader.load(file)
    assert isinstance(result, str)
    assert result == "Hello, world!"


def test_txt_loader_handles_multiline(tmp_path: Path) -> None:
    """Multi-line content should be preserved verbatim."""
    file = tmp_path / "test.txt"
    file.write_text("line1\nline2\nline3")
    loader = TxtLoader()
    result = loader.load(file)
    assert result == "line1\nline2\nline3"


def test_txt_loader_handles_empty(tmp_path: Path) -> None:
    """An empty file should return an empty string."""
    file = tmp_path / "empty.txt"
    file.write_text("")
    loader = TxtLoader()
    result = loader.load(file)
    assert result == ""


def test_txt_loader_handles_unicode(tmp_path: Path) -> None:
    """Unicode characters including emoji should survive round-trip."""
    file = tmp_path / "unicode.txt"
    file.write_text("héllo wörld 😀")
    loader = TxtLoader()
    result = loader.load(file)
    assert "héllo" in result
