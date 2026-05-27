"""PDF loader — uses pdfplumber to extract text from every page."""
from pathlib import Path

import pdfplumber

from fastrag.loaders.base import BaseLoader
from fastrag.registry import register_loader


@register_loader("pdf")
class PDFLoader(BaseLoader):
    """Extracts text from PDF files using pdfplumber."""

    def load(self, path: Path) -> str:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
