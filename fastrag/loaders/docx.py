from pathlib import Path

import docx

from fastrag.loaders.base import BaseLoader


class DocxLoader(BaseLoader):
    """Extracts text from .docx files using python-docx."""

    def load(self, path: Path) -> str:
        doc = docx.Document(str(path))
        return "\n".join(para.text for para in doc.paragraphs)
