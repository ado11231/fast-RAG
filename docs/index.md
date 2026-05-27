# fastrag

**Raw documents in → queryable knowledge base out.**

fastrag is a minimal Python library for building RAG pipelines.
Point it at your documents and get back a deployable queryable knowledge base.

---

## Quickstart

```python
from fastrag import Pipeline

pipeline = Pipeline()
pipeline.ingest("./docs")

results = pipeline.query("What is the refund policy?")
for hit in results:
    print(hit["text"])
```

---

## Installation

```bash
pip install fastrag
```

With optional providers:

```bash
pip install fastrag[openai]     # OpenAI embeddings
pip install fastrag[pinecone]   # Pinecone vector store
pip install fastrag[weaviate]   # Weaviate vector store
pip install fastrag[all]        # everything
```

---

## CLI

```bash
fastrag ingest ./docs     # Ingest documents
fastrag query "question"  # Ask a question
fastrag serve             # Start REST API
fastrag status            # Show current state
fastrag clear             # Reset everything
```

---

## Examples

Ready-to-run examples are in the [`examples/`](https://github.com/anomalyco/fastrag/tree/main/examples) directory:

| Example | What it shows |
|---|---|
| `01-basic-ingest-query` | Simplest possible ingest + query |
| `02-custom-loader` | Building a custom CSV loader |
| `03-custom-pipeline` | Configuring every component explicitly |
| `04-api-integration` | Embedding fastrag in a FastAPI app |

---

## Scope

fastrag handles: **documents in → queryable knowledge out.**

It does **not** handle agents, memory, LLM chaining, or conversation history.
That's your app's job. fastrag gives you the knowledge base.

---

## License

MIT
