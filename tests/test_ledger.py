"""Tests for Ledger — delta-sync hash tracking."""
from pathlib import Path

from fastrag.ledger import Ledger


def test_ledger_tracks_hash(tmp_path: Path) -> None:
    """A new file should be reported as changed; after update it should not."""
    ledger = Ledger(path=tmp_path / ".fastrag" / "ledger.json")
    file = tmp_path / "doc.txt"
    file.write_text("hello")
    assert ledger.is_changed(file)
    ledger.update(file)
    assert not ledger.is_changed(file)


def test_ledger_detects_change(tmp_path: Path) -> None:
    """Modifying a tracked file should flip is_changed back to True."""
    ledger = Ledger(path=tmp_path / ".fastrag" / "ledger.json")
    file = tmp_path / "doc.txt"
    file.write_text("version 1")
    ledger.update(file)
    file.write_text("version 2")
    assert ledger.is_changed(file)


def test_ledger_remove(tmp_path: Path) -> None:
    """Removing a file from the ledger should drop it from all_sources."""
    ledger = Ledger(path=tmp_path / "ledger.json")
    file = tmp_path / "doc.txt"
    file.write_text("data")
    ledger.update(file)
    assert len(ledger.all_sources()) == 1
    ledger.remove(file)
    assert len(ledger.all_sources()) == 0


def test_ledger_clear(tmp_path: Path) -> None:
    """Clearing the ledger should remove all entries."""
    ledger = Ledger(path=tmp_path / "ledger.json")
    for i in range(3):
        f = tmp_path / f"doc{i}.txt"
        f.write_text(f"data{i}")
        ledger.update(f)
    assert len(ledger.entries()) == 3
    ledger.clear()
    assert len(ledger.entries()) == 0


def test_ledger_persistence(tmp_path: Path) -> None:
    """Data written by one Ledger instance should be visible to another."""
    ledger_path = tmp_path / "ledger.json"
    ledger1 = Ledger(path=ledger_path)
    file = tmp_path / "doc.txt"
    file.write_text("persistent data")
    ledger1.update(file)

    ledger2 = Ledger(path=ledger_path)
    assert str(file) in ledger2.all_sources()
    assert not ledger2.is_changed(file)


def test_ledger_handles_missing_file(tmp_path: Path) -> None:
    """A ledger path whose parent does not exist should not crash."""
    ledger = Ledger(path=tmp_path / "nonexistent" / "ledger.json")
    assert ledger.entries() == {}


def test_ledger_entries_returns_copy(tmp_path: Path) -> None:
    """entries() should return a copy so mutation does not affect internal state."""
    ledger = Ledger(path=tmp_path / "ledger.json")
    file = tmp_path / "doc.txt"
    file.write_text("data")
    ledger.update(file)
    entries = ledger.entries()
    entries.pop(str(file), None)
    assert str(file) in ledger.entries()
