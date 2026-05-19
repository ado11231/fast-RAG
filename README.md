# fastrag

**Raw documents in. Deployable RAG agent out.**

fastrag is a focused Python framework for building RAG (Retrieval-Augmented Generation)
pipelines without the bloat. Point it at your documents, get back a queryable knowledge
base you can drop into any app or serve as a live REST API instantly.

---

## Why fastrag

LangChain tries to do everything. LlamaIndex has a learning curve that rivals a college
course. Both are overwhelming when all you need is: *take my documents, make them queryable*.

fastrag does one thing and does it well. Five concepts. One pipeline. Zero unnecessary complexity.

---

## Install

```bash
pip install fastrag
```

Want OpenAI embeddings or cloud vector stores?

```bash
pip install fastrag[openai]      # OpenAI embeddings
pip install fastrag[pinecone]    # Pinecone vector store
pip install fastrag[all]         # everything
```

---

## Quickstart — CLI

```bash
# ingest your documents
fastrag ingest ./docs

# query from the terminal
fastrag query "What is the refund policy?"

# or ship a live REST API instantly
fastrag serve
# → running on http://localhost:8000
```

That's it. Your documents are queryable. No code written.

---

## Quickstart — Python

```python
from fastrag import Pipeline

pipeline = Pipeline()
pipeline.ingest("./docs")

results = pipeline.query("What is the refund policy?")
```

Drop the query call into any app — FastAPI, Django, Discord bot, Next.js backend.
fastrag handles the knowledge. Your app handles the rest.

---

## Core Concepts

| Concept | Job |
|---|---|
| **Loader** | Reads a file, extracts raw text |
| **Chunker** | Splits text into smart pieces |
| **Embedder** | Converts pieces into vectors |
| **Store** | Saves and searches vectors |
| **Pipeline** | Wires all four together |

Everything is swappable. Switching from local ChromaDB to Pinecone:

```python
pipeline = Pipeline(embedder="openai", store="pinecone")
```

One line. Nothing else changes.

---

## Smart Re-ingestion (Delta Sync)

fastrag tracks a hash of every ingested file. When you re-run ingest,
only changed, added, or deleted files get processed.

```bash
fastrag ingest ./docs
# → 500 files, all unchanged — done in 1 second

# update one file, add one file, then:
fastrag ingest ./docs
# → skipped 499 files
# → re-ingested 1 modified file
# → ingested 1 new file
# → done in 3 seconds
```

10,000 documents. One file changed. One file processed.

---

## Live REST API in One Command

```bash
fastrag serve --port 8000

# POST /query    → ask a question, get relevant chunks
# GET  /health   → server status
# GET  /docs     → interactive API documentation
```

Point your frontend at `http://localhost:8000/query` and you have a working
RAG backend. No server code. No FastAPI boilerplate.

---

## Plugin System

fastrag uses a decorator registry. Community plugins register themselves on import.

```python
pip install fastrag-notion

import fastrag_notion  # registers @register_loader("notion") automatically

pipeline = Pipeline(loader="notion")
pipeline.ingest(database_id="abc123", notion_token="...")
```

Build your own plugin in 30 minutes by implementing one of the four base classes.
See [PLUGIN_GUIDE.md](docs/PLUGIN_GUIDE.md) for the full guide.

---

## Defaults

| Component | Default | Why |
|---|---|---|
| Embedder | sentence-transformers | Free, local, no API key |
| Vector Store | ChromaDB | Local, zero config |
| File Support | PDF, DOCX, TXT, MD | Covers 80% of real use cases |

---

## Scope

fastrag handles: **data in → queryable knowledge out**

fastrag does not handle: agents, memory, LLM chaining, conversation history, frontend UI.
That's your app's job. fastrag is the engine. You build the car.

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — how it works internally
- [CLI Reference](docs/CLI_REFERENCE.md) — all commands and options
- [Plugin Guide](docs/PLUGIN_GUIDE.md) — build your own loader, embedder, or store
- [CLAUDE.md](CLAUDE.md) — project bible for contributors and AI assistants

---

## Community Plugins

| Plugin | What it adds | Install |
|---|---|---|
| *your plugin here* | *open a PR to PLUGINS.md* | — |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The best first contribution is a plugin
for a data source you actually use.

---

## License

MIT
