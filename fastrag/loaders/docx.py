"""DOCX loader — uses python-docx to read Word document paragraphs."""
from pathlib import Path

import docx

from fastrag.loaders.base import BaseLoader
from fastrag.registry import register_loader


@register_loader("docx")
class DocxLoader(BaseLoader):
    """Extracts text from .docx files using python-docx."""

    def load(self, path: Path) -> str:
        doc = docx.Document(str(path))
        return "\n".join(para.text for para in doc.paragraphs)
