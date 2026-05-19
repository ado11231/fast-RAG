# CLAUDE.md — fastrag Project Bible

This file is the single source of truth for anyone (human or AI) working on this codebase.
Read this before touching anything.

---

## What This Project Is

fastrag is a focused, minimal RAG (Retrieval-Augmented Generation) pipeline framework in Python.

**One job:** Take raw documents, handle all ingestion, chunking, embedding, and vectorization,
and return a deployable queryable knowledge base the user can drop into any app.

> Raw documents in. Deployable RAG agent out. No bloat, no PhD required.

---

## What This Project Is NOT

fastrag does not and will never handle:

- Multi-turn conversation memory
- AI agents or tool use
- LLM chaining or orchestration
- Frontend UI components
- Authentication or user management
- Anything outside the "data in, queryable knowledge out" loop

If a feature request lives outside that loop, the answer is no. That's the user's app's job.
This boundary is what keeps fastrag from becoming LangChain.

---

## Core Philosophy

**1. Simplicity over flexibility**
A beginner and a senior engineer should both find their comfortable entry point.
The CLI requires zero code. The Python API requires minimal code. Never sacrifice that.

**2. Lean dependencies**
Every dependency is a liability. Hard dependencies must justify their existence.
Optional features use extras (`pip install fastrag[openai]`), never the core install.

**3. Adapters everywhere**
Every major component (Loader, Embedder, Store) is swappable via a one-line change.
Switching providers should never require rewriting application logic.

**4. Plugins are first-class**
A community plugin must feel identical to a built-in one.
The plugin contract must be so simple a developer can implement it in 30 minutes
from reading the docstrings alone — no source code diving required.

**5. No magic the user can't see**
Delta sync, auto file detection, default configs — all of it should be
transparent and debuggable. Hidden behavior must always be logged.

---

## The Five Core Concepts

These are the only five concepts a user needs to understand to use fastrag fully.
Every class, every CLI command, every plugin maps to one of these.

| Concept | Class | Job |
|---|---|---|
| **Loader** | `BaseLoader` | Reads a file type, extracts raw text |
| **Chunker** | `BaseChunker` | Splits text into pieces intelligently |
| **Embedder** | `BaseEmbedder` | Converts chunks into vectors |
| **Store** | `BaseStore` | Saves and searches vectors |
| **Pipeline** | `Pipeline` | Wires all four together into one flow |

---

## Technical Defaults

| Component | Default | Why |
|---|---|---|
| Embedder | `sentence-transformers` | Free, local, no API key, good quality |
| Vector Store | ChromaDB | Local, zero config, no account needed |
| Chunker | Recursive character splitter | Handles most document types well |
| File detection | Automatic by extension | Zero config for the user |

---

## Signature Features

### 1. Delta State Sync
A hidden `.fastrag/ledger.json` tracks SHA-256 hashes of every ingested file.
On every ingest run, hashes are compared against the ledger:
- Hash matches → skip (unchanged)
- Hash changed → delete old vectors, re-ingest
- Hash new → ingest fresh
- Hash missing → file deleted, remove vectors

Vectors must be tagged with their source file at ingest time to support deletion.
The ledger lives at `.fastrag/ledger.json` relative to the user's working directory.

### 2. Zero-to-API CLI (`fastrag serve`)
Wraps the active Pipeline in a pre-built FastAPI server.
Exposes `/query`, `/health`, and `/docs` endpoints automatically.
Supports `--port` and `--host` flags.
Requires no server code from the user.

### 3. Decorator Plugin Registry
`@register_loader`, `@register_embedder`, `@register_store`, `@register_chunker`
decorators let community developers register components without modifying core code.
Plugins register themselves on import.
Name collisions use namespacing: `official/notion` vs `community/notion`.
Validation happens at registration time, not at runtime.

---

## Dependency Rules

### Hard Dependencies (always installed)
```
pdfplumber        # PDF reading
python-docx       # DOCX reading
chromadb          # default vector store
sentence-transformers  # default embedder
numpy             # vector math
typer             # CLI framework
fastapi           # serve command
uvicorn           # ASGI server for serve command
```

### Optional Dependencies (installed via extras)
```
pip install fastrag[openai]     # openai embedder adapter
pip install fastrag[pinecone]   # pinecone store adapter
pip install fastrag[weaviate]   # weaviate store adapter
pip install fastrag[all]        # everything
```

Never import optional dependencies at the top level.
Always wrap them in try/except with a helpful error message pointing to the right extra.

---

## Folder Structure

```
fastrag/
├── fastrag/
│   ├── __init__.py               # public API surface
│   ├── pipeline.py               # Pipeline class — main entry point
│   ├── registry.py               # decorator registry system
│   ├── ledger.py                 # delta sync hash tracking
│   │
│   ├── loaders/
│   │   ├── base.py               # BaseLoader abstract class
│   │   ├── pdf.py                # PDF loader
│   │   ├── docx.py               # DOCX loader
│   │   ├── txt.py                # TXT loader
│   │   └── md.py                 # Markdown loader
│   │
│   ├── chunkers/
│   │   ├── base.py               # BaseChunker abstract class
│   │   └── recursive.py          # default recursive character chunker
│   │
│   ├── embedders/
│   │   ├── base.py               # BaseEmbedder abstract class
│   │   └── sentence_transformers.py  # default local embedder
│   │
│   ├── stores/
│   │   ├── base.py               # BaseStore abstract class
│   │   └── chroma.py             # default ChromaDB store
│   │
│   └── cli/
│       ├── __init__.py
│       ├── main.py               # CLI entry point (typer app)
│       ├── ingest.py             # `fastrag ingest` command
│       ├── serve.py              # `fastrag serve` command
│       └── query.py              # `fastrag query` command
│
├── tests/
├── examples/
├── docs/
├── CLAUDE.md                     # this file
├── README.md
├── pyproject.toml
└── CONTRIBUTING.md
```

---

## CLI Commands

| Command | What it does |
|---|---|
| `fastrag ingest <path>` | Ingest documents from a folder or file |
| `fastrag serve` | Spin up a FastAPI server on the active store |
| `fastrag query "<question>"` | Query from the terminal directly |
| `fastrag status` | Show what's in the current ledger and store |
| `fastrag clear` | Wipe the store and ledger |

---

## API Surface (what users import)

```python
from fastrag import Pipeline
from fastrag import BaseLoader, BaseEmbedder, BaseStore, BaseChunker
from fastrag import register_loader, register_embedder, register_store, register_chunker
```

That is the entire public API. Nothing else should be imported directly by users.
Everything internal is considered private and subject to change.

---

## Development Phases

### Phase 1 — Core Pipeline (build this first)
- Loaders: PDF, DOCX, TXT, MD
- Default chunker (recursive character)
- Default embedder (sentence-transformers)
- Default store (ChromaDB)
- Pipeline class wiring everything together
- Basic CLI: `ingest` and `query`

### Phase 2 — Swappable Adapters
- OpenAI embedder adapter
- Pinecone store adapter
- Weaviate store adapter
- Base classes fully documented for community use

### Phase 3 — Signature Features
- Delta sync ledger
- `fastrag serve` CLI command
- Decorator plugin registry
- `fastrag status` and `fastrag clear` commands

### Phase 4 — Polish and Community
- Full README with real examples
- Docs site
- CONTRIBUTING.md
- Plugin discovery (PLUGINS.md → registry later)
- Example projects

---

## Coding Conventions

- Python 3.10+ minimum
- Type hints on every function signature
- Docstrings on every public class and method
- Abstract base classes use `abc.ABC` and `@abstractmethod`
- No print statements in library code — use `logging`
- CLI output uses `typer.echo` or `rich` for formatting
- All file paths handled with `pathlib.Path`, never raw strings
- Tests live in `tests/` mirroring the `fastrag/` structure

---

## The One Rule

If someone asks "can fastrag do X?" and X is outside the data-in, queryable-knowledge-out loop,
the answer is: "That's your app's job. fastrag gives you the knowledge base.
You decide what to build on top of it."

Repeat this as many times as necessary.
