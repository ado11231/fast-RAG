# fastRAG

Deploy RAG models fast and easy.

fastRAG is a minimal Python library for building RAG pipelines.
Point it at your documents and get back a queryable knowledge base you can drop into any app.

---

## Install

```bash
pip install fastrag
```

---

## Quickstart

```python
from fastrag import Pipeline

pipeline = Pipeline()
pipeline.ingest("./docs")

results = pipeline.query("What is the refund policy?")
for hit in results:
    print(hit["text"])
    print(hit["metadata"]["source"])
```

That's it. `Pipeline` handles loading, chunking, embedding, and storing automatically.

---

## Examples

Ready-to-run examples in the [`examples/`](./examples) directory:

| # | Example | What it shows |
|---|---|---|
| 01 | [`basic-ingest-query`](./examples/01-basic-ingest-query) | Simplest possible ingest + query |
| 02 | [`custom-loader`](./examples/02-custom-loader) | Building a custom CSV loader |
| 03 | [`custom-pipeline`](./examples/03-custom-pipeline) | Configuring every component explicitly |
| 04 | [`api-integration`](./examples/04-api-integration) | Embedding fastrag in a FastAPI app |

---

## Full Documentation

Read the [full docs site](https://anomalyco.github.io/fastrag) for architecture, CLI reference,
plugin development guide, and contributing information.

---

## Supported File Types

| Format | Extension |
|---|---|
| PDF | `.pdf` |
| Word | `.docx` |
| Plain text | `.txt` |
| Markdown | `.md`, `.markdown` |

---

## Defaults

| Component | Default |
|---|---|
| Embedder | `sentence-transformers/all-MiniLM-L6-v2` — free, local, no API key |
| Vector Store | ChromaDB — persisted to `.fastrag/chroma` |
| Chunker | Recursive character splitter — 512 chars, 64 overlap |

---

## Swapping Components

Every component is replaceable. Pass your own into `Pipeline`:

```python
from fastrag import Pipeline
from fastrag.chunkers import RecursiveChunker
from fastrag.embedders import SentenceTransformerEmbedder
from fastrag.stores import ChromaStore

pipeline = Pipeline(
    chunker=RecursiveChunker(chunk_size=256, overlap=32),
    embedder=SentenceTransformerEmbedder(model_name="all-mpnet-base-v2"),
    store=ChromaStore(persist_dir="./my-store"),
)
```

---

## Custom Components

Implement one of the four base classes to add your own loader, chunker, embedder, or store:

```python
from fastrag import BaseLoader, register_loader
from pathlib import Path

@register_loader("csv")
class CSVLoader(BaseLoader):
    def load(self, path: Path) -> str:
        return path.read_text()
```

Registering with a decorator makes the component available across your project on import.

---

## Scope

fastrag handles: **documents in → queryable knowledge out.**

It does not handle agents, memory, LLM chaining, or conversation history.
That's your app's job. fastrag gives you the knowledge base.

---

## License

MIT
