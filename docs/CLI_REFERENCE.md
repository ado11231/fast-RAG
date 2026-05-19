# CLI Reference — fastrag

fastrag ships with a full CLI so you can go from raw documents to a live queryable
knowledge base without writing a single line of Python.

---

## Installation

```bash
pip install fastrag
```

Verify the CLI is available:

```bash
fastrag --version
```

---

## Commands Overview

| Command | What it does |
|---|---|
| `fastrag ingest <path>` | Ingest documents from a folder or single file |
| `fastrag query "<question>"` | Query your knowledge base from the terminal |
| `fastrag serve` | Spin up a live REST API on top of your knowledge base |
| `fastrag status` | Show what's currently in your ledger and store |
| `fastrag clear` | Wipe your store and ledger (start fresh) |

---

## fastrag ingest

Takes a folder or file path and runs the full ingestion pipeline:
load → chunk → embed → store. Handles delta sync automatically.

### Basic usage

```bash
# Ingest an entire folder
fastrag ingest ./docs

# Ingest a single file
fastrag ingest ./handbook.pdf
```

### Output

```
fastrag — ingesting ./docs

  ✓ handbook.pdf          47 chunks   (new)
  ✓ api-reference.pdf     89 chunks   (new)
  ✓ faq.docx              23 chunks   (new)
  ✓ notes.txt              8 chunks   (new)
  → release-notes.pdf              —  (unchanged, skipped)

  4 files ingested  |  167 chunks stored  |  1 skipped
  Ledger → .fastrag/ledger.json
  Store  → .fastrag/chroma/
```

### Options

```bash
fastrag ingest ./docs --embedder openai
fastrag ingest ./docs --store pinecone --store-config pinecone.json
fastrag ingest ./docs --chunk-size 256 --chunk-overlap 25
fastrag ingest ./docs --force   # ignore ledger, re-ingest everything
fastrag ingest ./docs --dry-run # show what would be ingested without doing it
```

### Options reference

| Option | Default | Description |
|---|---|---|
| `--embedder` | `sentence-transformers` | Which embedder to use |
| `--store` | `chroma` | Which vector store to use |
| `--store-config` | none | Path to a JSON file with store credentials |
| `--chunk-size` | `512` | Target chunk size in tokens |
| `--chunk-overlap` | `50` | Token overlap between consecutive chunks |
| `--force` | false | Re-ingest all files even if unchanged |
| `--dry-run` | false | Preview what would happen without doing it |
| `--verbose` | false | Show detailed output for each file |

### Supported file types (built-in)

| Extension | Loader |
|---|---|
| `.pdf` | PDF loader (pdfplumber) |
| `.docx` | DOCX loader (python-docx) |
| `.txt` | Plain text loader |
| `.md` | Markdown loader |

Additional file types available via community plugins — see `PLUGINS.md`.

---

## fastrag query

Ask a question against your knowledge base directly from the terminal.
Useful for testing your ingestion before building an app around it.

### Basic usage

```bash
fastrag query "What is the refund policy?"
```

### Output

```
Question: What is the refund policy?

Answer:
  Customers may request a refund within 30 days of purchase. Refunds are
  processed within 5-7 business days to the original payment method...

Sources:
  → handbook.pdf  (chunk 12 of 47)
  → faq.docx      (chunk 3 of 23)
```

### Options

```bash
fastrag query "What is the refund policy?" --top-k 10
fastrag query "What is the refund policy?" --show-chunks
fastrag query "What is the refund policy?" --json
```

| Option | Default | Description |
|---|---|---|
| `--top-k` | `5` | Number of relevant chunks to retrieve |
| `--show-chunks` | false | Display the raw chunk text alongside the answer |
| `--json` | false | Output results as raw JSON |

---

## fastrag serve

Wraps your knowledge base in a FastAPI server instantly.
No server code required.

### Basic usage

```bash
fastrag serve
```

### Output

```
fastrag — starting server

  Store    chroma  (167 chunks across 4 documents)
  Embedder sentence-transformers

  Running on http://localhost:8000

  POST  /query    — ask a question
  GET   /health   — server status
  GET   /docs     — interactive API documentation

  Press CTRL+C to stop
```

### Options

```bash
fastrag serve --port 3001
fastrag serve --host 0.0.0.0    # expose to network, not just localhost
fastrag serve --port 8080 --host 0.0.0.0
fastrag serve --reload          # auto-restart when store changes
```

| Option | Default | Description |
|---|---|---|
| `--port` | `8000` | Port to run on |
| `--host` | `127.0.0.1` | Host to bind to |
| `--reload` | false | Watch for store changes and restart |
| `--workers` | `1` | Number of worker processes |

### API Endpoints

**POST /query**

Request:
```json
{
  "question": "What is the refund policy?",
  "top_k": 5
}
```

Response:
```json
{
  "question": "What is the refund policy?",
  "chunks": [
    {
      "text": "Customers may request a refund within 30 days...",
      "source": "handbook.pdf",
      "score": 0.91,
      "chunk_index": 12,
      "total_chunks": 47
    }
  ],
  "sources": ["handbook.pdf", "faq.docx"],
  "top_score": 0.91
}
```

**GET /health**

Response:
```json
{
  "status": "ok",
  "store": "chroma",
  "embedder": "sentence-transformers",
  "document_count": 4,
  "chunk_count": 167
}
```

**GET /docs**

Opens FastAPI's interactive Swagger documentation in the browser.
Try queries directly from the browser UI — no extra tooling needed.

---

## fastrag status

Shows a summary of what's currently in your ledger and store.

### Basic usage

```bash
fastrag status
```

### Output

```
fastrag — current status

  Store     chroma  (.fastrag/chroma/)
  Embedder  sentence-transformers
  Ledger    .fastrag/ledger.json

  Documents (4 files, 167 total chunks)

  handbook.pdf          47 chunks   last ingested 2025-01-15 10:30
  api-reference.pdf     89 chunks   last ingested 2025-01-15 10:30
  faq.docx              23 chunks   last ingested 2025-01-15 10:31
  notes.txt              8 chunks   last ingested 2025-01-15 10:31
```

---

## fastrag clear

Wipes your vector store and ledger. Useful when you want to start fresh
or switch to a different embedding model (vectors from different models
are not compatible and must be rebuilt).

### Basic usage

```bash
fastrag clear
```

### Output

```
This will delete all vectors and the ingestion ledger.
Are you sure? [y/N]: y

  ✓ Store cleared
  ✓ Ledger cleared

  Run `fastrag ingest <path>` to start fresh.
```

### Options

```bash
fastrag clear --yes    # skip confirmation prompt (useful in scripts)
```

---

## Using a Config File

For repeated use with the same settings, create a `fastrag.toml` in your project root:

```toml
[fastrag]
embedder = "openai"
store = "pinecone"
chunk_size = 256
chunk_overlap = 25

[embedder.openai]
model = "text-embedding-3-small"

[store.pinecone]
index = "my-index"
```

fastrag automatically picks this up. CLI flags override config file values.

Store credentials (API keys) should go in environment variables, not the config file:

```bash
export OPENAI_API_KEY=sk-...
export PINECONE_API_KEY=...
```

---

## Common Workflows

### Start fresh with a new project

```bash
pip install fastrag
fastrag ingest ./my-documents
fastrag query "test question"     # verify it worked
fastrag serve                     # ship it
```

### Update documents after changes

```bash
# just re-run ingest — delta sync handles the rest
fastrag ingest ./my-documents
```

### Switch from local to OpenAI embeddings

```bash
pip install fastrag[openai]
export OPENAI_API_KEY=sk-...

fastrag clear                     # must rebuild — different vector dimensions
fastrag ingest ./my-documents --embedder openai
fastrag serve
```

### Deploy to a server

```bash
# on your server
pip install fastrag
# copy your .fastrag/ folder to the server, then:
fastrag serve --host 0.0.0.0 --port 8000
```

Or if you're embedding in an existing app, skip `serve` entirely
and import `Pipeline` directly in your Python code.
