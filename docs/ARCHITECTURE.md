# Architecture — fastrag

This document explains how fastrag is structured internally, why each decision was made,
and how the pieces connect. Read this before contributing or building adapters.

---

## The Big Picture

```
User's Documents
      ↓
  [ Loader ]        — extracts raw text from a file
      ↓
  [ Chunker ]       — splits text into pieces
      ↓
  [ Embedder ]      — converts pieces into vectors
      ↓
  [ Store ]         — saves and indexes vectors
      ↓
Queryable Knowledge Base
      ↓
  pipeline.query()  — retrieves relevant chunks for any question
      ↓
  User's App        — does whatever they want with the results
```

Every step is a separate, swappable component. The Pipeline class is the conductor
that wires them together and manages the flow.

---

## The Adapter Pattern

The most important architectural decision in fastrag is the adapter pattern.
Every major component follows the same structure:

1. A base class defines the **contract** — what methods must exist and what they must return
2. Built-in implementations fulfill that contract for common providers
3. Community plugins fulfill the same contract for custom providers
4. The Pipeline works with any implementation identically

This means:
- Switching from ChromaDB to Pinecone is one line change
- A community Notion loader feels identical to the built-in PDF loader
- Adding a new provider never requires touching Pipeline or any other component

---

## Component Breakdown

### Loader

**Job:** Accept a file path, return clean extracted text.

**Base contract:**
```python
class BaseLoader(ABC):
    @abstractmethod
    def load(self, path: Path) -> str:
        # return raw text extracted from the file
        ...

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        # return list like [".pdf"] or [".docx"]
        ...
```

**Auto-detection:** The Pipeline uses `supported_extensions()` from all registered loaders
to automatically pick the right one for each file. The user never has to specify
which loader to use unless they want to override the default.

**Built-in loaders:** PDF, DOCX, TXT, MD

---

### Chunker

**Job:** Accept a long string of text, return a list of smaller string chunks.

**Base contract:**
```python
class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        # return list of text chunks
        ...
```

**Default behavior:** Recursive character splitter. Tries to split on paragraph breaks first,
then sentences, then words, then characters. Produces natural-feeling chunks that don't
cut sentences in half.

**Chunk size:** Configurable. Default is 512 tokens with 50 token overlap between chunks.
Overlap prevents losing context at chunk boundaries.

---

### Embedder

**Job:** Accept a list of text chunks, return a list of vectors (lists of floats).

**Base contract:**
```python
class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, chunks: list[str]) -> list[list[float]]:
        # return one vector per chunk
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        # return the vector size this embedder produces
        ...
```

**Why dimensions matters:** The Store needs to know the vector size upfront.
Different embedding models produce different sized vectors.
Mismatched dimensions cause silent corruption, not loud errors — this property prevents that.

**Default:** sentence-transformers `all-MiniLM-L6-v2` — 384 dimensions, fast, free, local.

---

### Store

**Job:** Save vectors with their source metadata. Search for the most similar vectors
to a query vector. Support deletion by source file for delta sync.

**Base contract:**
```python
class BaseStore(ABC):
    @abstractmethod
    def save(self, chunks: list[str], vectors: list[list[float]], metadata: list[dict]) -> None:
        # persist chunks and their vectors
        # metadata must include at minimum: {"source": "filename.pdf"}
        ...

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        # return top_k most similar chunks with their metadata
        ...

    @abstractmethod
    def delete_by_source(self, source: str) -> None:
        # delete all vectors that came from a specific file
        # required for delta sync to work
        ...
```

**Why delete_by_source is required:** Delta sync needs to remove old vectors when a file
changes before re-ingesting the updated version. Without this, updated files produce
duplicate and contradictory vectors.

---

### Pipeline

**Job:** Orchestrate all components. Provide the main entry point for users.
Handle auto file detection, delta sync checking, and query routing.

**Pipeline is NOT:**
- A place to add business logic
- A place to handle LLM calls
- A place to manage conversation history

It wires the five components together and nothing else.

**Key methods:**
```python
pipeline = Pipeline(loader="auto", embedder="sentence-transformers", store="chroma")
pipeline.ingest("./docs")           # ingest a folder or file
results = pipeline.query("question") # query the knowledge base
Pipeline.load()                      # load an existing store without re-ingesting
```

---

## The Registry System

The registry is a dictionary that maps string names to component classes.
Decorators are the API for adding to it.

```
Registry = {
    "loaders": {
        "pdf": PDFLoader,
        "docx": DocxLoader,
        "notion": NotionLoader,   ← community plugin added this
    },
    "embedders": {
        "sentence-transformers": SentenceTransformersEmbedder,
        "openai": OpenAIEmbedder,
    },
    "stores": {
        "chroma": ChromaStore,
        "pinecone": PineconeStore,
    },
    "chunkers": {
        "recursive": RecursiveChunker,
    }
}
```

When a plugin does `import yourframework_notion`, the `@register_loader("notion")` decorator
fires immediately and adds `NotionLoader` to the registry. From that point, any Pipeline
created with `loader="notion"` will use it automatically.

**Validation at registration time:**
When a class is registered, the registry checks that it actually inherits from the correct
base class. A bad plugin fails immediately with a helpful error, not silently at query time.

---

## Delta Sync — How It Works

The ledger is a JSON file stored at `.fastrag/ledger.json`:

```json
{
  "handbook.pdf": {
    "hash": "a3f5c2...",
    "ingested_at": "2025-01-15T10:30:00",
    "chunk_count": 47
  },
  "faq.docx": {
    "hash": "b8d1e9...",
    "ingested_at": "2025-01-15T10:30:01",
    "chunk_count": 23
  }
}
```

**Ingest flow with delta sync:**

```
For each file in the target folder:
    1. Compute SHA-256 hash of the file
    2. Look up the file in the ledger

    If not in ledger:
        → ingest fresh, add to ledger

    If in ledger and hash matches:
        → skip entirely

    If in ledger and hash differs:
        → call store.delete_by_source(filename)
        → re-ingest, update ledger

After processing all files:
    For each entry in ledger not seen in the folder scan:
        → file was deleted
        → call store.delete_by_source(filename)
        → remove from ledger
```

**Why SHA-256:** Fast enough for large files, collision-resistant enough that false matches
are not a real concern. We're hashing document files, not security-critical data.

---

## The Serve Command — How It Works

`fastrag serve` does the following:

1. Loads the existing Pipeline from the local store (no re-ingestion)
2. Creates a FastAPI app with three routes
3. Starts uvicorn on the specified host and port

The FastAPI app is minimal on purpose:

```
POST /query
    body: { "question": "string", "top_k": 5 }
    returns: { "answer": "string", "sources": [], "chunks": [], "confidence": float }

GET /health
    returns: { "status": "ok", "store": "chroma", "document_count": 183 }

GET /docs
    auto-generated by FastAPI — interactive API documentation
```

The `/query` endpoint embeds the question using the active embedder,
searches the store for the top_k most similar chunks,
and returns those chunks plus their source metadata.

Note: fastrag does not call an LLM to generate a final answer by default.
It returns relevant chunks. The user's app decides how to use them —
pass to OpenAI, pass to a local model, display raw chunks, whatever they need.
An optional `--with-llm` flag on serve can enable LLM answer generation for users who want it.

---

## What Happens on `Pipeline.load()`

When a user calls `Pipeline.load()` without a path, fastrag:

1. Looks for `.fastrag/` in the current working directory
2. Reads the ledger to understand what's been ingested
3. Connects to the existing store (doesn't rebuild it)
4. Returns a ready Pipeline

This is how the serve command works and how users drop fastrag into an existing app
without re-ingesting every time the app starts.

---

## Error Handling Philosophy

- Fail loud and early with helpful messages
- Never silently swallow errors and continue
- When an optional dependency is missing, tell the user exactly what to install
- When a plugin fails validation, name the specific method that's missing
- When a file can't be loaded, log a warning and continue (don't abort the whole ingest)

---

## What Goes in Metadata

Every chunk saved to the store must carry this metadata minimum:

```python
{
    "source": "handbook.pdf",      # filename, used for delta sync deletion
    "chunk_index": 3,              # position in the document
    "total_chunks": 47,            # total chunks from this file
    "loader": "pdf",               # which loader produced this
}
```

Stores can add their own metadata fields but must preserve these.
The query results surface this metadata to the user so they can show sources.
