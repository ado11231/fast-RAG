from fastrag.loaders.base import BaseLoader
from fastrag.loaders.docx import DocxLoader
from fastrag.loaders.md import MarkdownLoader
from fastrag.loaders.pdf import PDFLoader
from fastrag.loaders.txt import TxtLoader

EXTENSION_MAP: dict[str, type[BaseLoader]] = {
    ".pdf": PDFLoader,
    ".docx": DocxLoader,
    ".txt": TxtLoader,
    ".md": MarkdownLoader,
    ".markdown": MarkdownLoader,
}


def get_loader(extension: str) -> BaseLoader:
    """Return a loader instance for the given file extension (e.g. '.pdf')."""
    cls = EXTENSION_MAP.get(extension.lower())
    if cls is None:
        raise ValueError(f"No loader registered for extension '{extension}'")
    return cls()
