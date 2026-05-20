from pathlib import Path

import pdfplumber

from fastrag.loaders.base import BaseLoader


class PDFLoader(BaseLoader):
    """Extracts text from PDF files using pdfplumber."""

    def load(self, path: Path) -> str:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
