"""Tests for PDFLoader — PDF text extraction via pdfplumber."""
from pathlib import Path

import pytest

from fastrag.loaders.pdf import PDFLoader


def test_pdf_loader_returns_string(pdf_sample: Path) -> None:
    """Verify the loader extracts text from a basic PDF."""
    loader = PDFLoader()
    result = loader.load(pdf_sample)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.fixture
def pdf_sample(tmp_path: Path) -> Path:
    """Generate a minimal single-page PDF for testing."""
    path = tmp_path / "sample.pdf"
    try:
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(path))
        c.drawString(100, 750, "Hello from PDF")
        c.save()
    except ImportError:
        pytest.skip("reportlab not installed — cannot generate PDF fixture")
    return path
