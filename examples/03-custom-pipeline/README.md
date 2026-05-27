# Custom Pipeline

Shows how to configure every Pipeline component explicitly with
non-default settings.

## Run

```bash
pip install fastrag
python custom_pipeline.py
```

## What it does

1. Creates a custom chunker with smaller chunk size
2. Uses a different sentence-transformers model
3. Stores vectors in a custom directory
4. Ingests and queries
