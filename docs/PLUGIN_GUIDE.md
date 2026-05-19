# Plugin Development Guide — fastrag

This guide covers everything you need to build a community plugin for fastrag.
If you can implement a Python class, you can build a plugin.

---

## The Core Idea

fastrag uses a decorator-based registry. You write a class that inherits from one of
fastrag's base classes, decorate it with a registration decorator, and it becomes
available in any Pipeline by name.

That's the entire plugin system. No config files. No manual registration steps.
Import the package and it registers itself.

---

## Plugin Types

| Plugin Type | Decorator | Base Class | What It Does |
|---|---|---|---|
| Loader | `@register_loader("name")` | `BaseLoader` | Load a new file or data source type |
| Embedder | `@register_embedder("name")` | `BaseEmbedder` | Add a new embedding model/provider |
| Store | `@register_store("name")` | `BaseStore` | Add a new vector database |
| Chunker | `@register_chunker("name")` | `BaseChunker` | Add a new text splitting strategy |

---

## Building a Loader Plugin

The most common plugin type. Build this when you want to support a new data source.

### The Contract

```python
from fastrag import BaseLoader, register_loader
from pathlib import Path

@register_loader("your-source-name")
class YourLoader(BaseLoader):

    def load(self, path: Path) -> str:
        """
        Accept a path or identifier for your data source.
        Return the full extracted text as a single string.
        """
        ...

    def supported_extensions(self) -> list[str]:
        """
        Return file extensions this loader handles.
        For non-file sources (APIs, databases), return an empty list
        and document that users must specify loader="your-name" explicitly.
        """
        ...
```

### Real Example — Notion Loader

```python
from fastrag import BaseLoader, register_loader
from pathlib import Path

@register_loader("notion")
class NotionLoader(BaseLoader):

    def __init__(self, token: str):
        self.token = token
        # initialize Notion client here

    def load(self, source: Path | str) -> str:
        """
        source is a Notion database ID or page ID.
        Returns all text content from that page/database.
        """
        # call Notion API
        # extract and concatenate all text blocks
        # return as single string
        ...

    def supported_extensions(self) -> list[str]:
        # Notion isn't a file type so no extensions
        return []
```

**Usage after publishing:**
```python
import fastrag_notion  # registers on import

pipeline = Pipeline(
    loader="notion",
    loader_config={"token": "your-token"}
)
pipeline.ingest("your-database-id")
```

---

## Building an Embedder Plugin

Build this when you want to support a new embedding model or provider.

### The Contract

```python
from fastrag import BaseEmbedder, register_embedder

@register_embedder("your-embedder-name")
class YourEmbedder(BaseEmbedder):

    def embed(self, chunks: list[str]) -> list[list[float]]:
        """
        Accept a list of text chunks.
        Return one vector (list of floats) per chunk.
        Order must be preserved — chunk[0] maps to vector[0].
        """
        ...

    @property
    def dimensions(self) -> int:
        """
        Return the number of dimensions in each vector this model produces.
        Must be consistent — same model always returns same dimensions.
        """
        ...
```

### Real Example — Cohere Embedder

```python
from fastrag import BaseEmbedder, register_embedder

@register_embedder("cohere")
class CohereEmbedder(BaseEmbedder):

    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        try:
            import cohere
        except ImportError:
            raise ImportError(
                "Cohere package not found. Install it with: pip install cohere"
            )
        self.client = cohere.Client(api_key)
        self.model = model

    def embed(self, chunks: list[str]) -> list[list[float]]:
        response = self.client.embed(
            texts=chunks,
            model=self.model,
            input_type="search_document"
        )
        return response.embeddings

    @property
    def dimensions(self) -> int:
        return 1024  # embed-english-v3.0 produces 1024-dim vectors
```

---

## Building a Store Plugin

Build this when you want to support a new vector database.

### The Contract

```python
from fastrag import BaseStore, register_store

@register_store("your-store-name")
class YourStore(BaseStore):

    def save(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        metadata: list[dict]
    ) -> None:
        """
        Persist chunks alongside their vectors and metadata.
        metadata[i] always contains at minimum: {"source": "filename"}
        Preserve all metadata fields — they surface in query results.
        """
        ...

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5
    ) -> list[dict]:
        """
        Find the top_k most similar vectors to the query_vector.
        Return a list of dicts, each containing:
          - "text": the original chunk text
          - "score": similarity score (higher = more similar)
          - all original metadata fields
        Results must be ordered by score descending.
        """
        ...

    def delete_by_source(self, source: str) -> None:
        """
        Delete ALL vectors and chunks where metadata["source"] == source.
        This is required for delta sync to work correctly.
        Do not raise an error if source is not found — just do nothing.
        """
        ...
```

---

## Naming Conventions

### Official plugins (maintained by fastrag core team)
Named without namespace: `"chroma"`, `"openai"`, `"pinecone"`

### Community plugins (maintained by you)
Use your package name or a clear identifier: `"notion"`, `"confluence"`, `"ollama"`

### Avoiding conflicts
If a name you want is already taken, use a more specific name:
`"notion-v2"`, `"openai-ada"`, `"cohere-v3"`

Check `PLUGINS.md` in the main repo before publishing to avoid collisions.

---

## Packaging Your Plugin

Your plugin should be a standard Python package published to PyPI.

### Recommended naming convention
`fastrag-{source}` — for example:
- `fastrag-notion`
- `fastrag-confluence`
- `fastrag-ollama`
- `fastrag-qdrant`

This naming makes your plugin discoverable when someone searches PyPI for "fastrag".

### Minimal pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "fastrag-notion"
version = "0.1.0"
description = "Notion loader plugin for fastrag"
dependencies = [
    "fastrag>=0.1.0",
    "notion-client>=2.0.0",
]

[project.urls]
Homepage = "https://github.com/you/fastrag-notion"
```

### Package structure

```
fastrag-notion/
├── fastrag_notion/
│   ├── __init__.py      ← registration decorator fires on import here
│   └── loader.py        ← the actual loader class
├── tests/
├── README.md
└── pyproject.toml
```

### The __init__.py trick

```python
# fastrag_notion/__init__.py
from .loader import NotionLoader  # importing this triggers @register_loader
```

When a user does `import fastrag_notion`, Python runs `__init__.py`,
which imports `NotionLoader`, which fires the decorator, which registers it.
No manual step required.

---

## Testing Your Plugin

Test against the base class contract directly:

```python
def test_loader_returns_string():
    loader = NotionLoader(token="test-token")
    # mock your API calls
    result = loader.load("fake-database-id")
    assert isinstance(result, str)
    assert len(result) > 0

def test_loader_registers_correctly():
    import fastrag_notion
    from fastrag.registry import get_registry
    registry = get_registry()
    assert "notion" in registry["loaders"]

def test_works_in_pipeline():
    import fastrag_notion
    from fastrag import Pipeline
    pipeline = Pipeline(loader="notion")
    # verify pipeline accepts the loader without error
    assert pipeline.loader.__class__.__name__ == "NotionLoader"
```

---

## Getting Listed

Once your plugin is published and working:

1. Open a PR to the main fastrag repo
2. Add your plugin to `PLUGINS.md` in the community section
3. Include: plugin name, PyPI link, what it does, your GitHub handle

That's it. The community will find it there.

---

## Getting Help

If you're stuck on the base class contract or something isn't registering correctly,
open a GitHub Discussion in the main repo tagged `plugin-help`.
Include what you've tried and what error you're seeing.
