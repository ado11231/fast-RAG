"""Demonstrates building a custom loader using the base class and decorator.

The CSVLoader registers itself under the name "csv" via @register_loader,
making it available to any Pipeline by name.
"""
from pathlib import Path

from fastrag import BaseLoader, Pipeline, register_loader

DATA_DIR = Path(__file__).parent / "data"


@register_loader("csv")
class CSVLoader(BaseLoader):
    """Reads CSV files and concatenates columns into a descriptive string per row."""

    def load(self, path: Path) -> str:
        import csv
        import io

        text = path.read_text(encoding="utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        for row in reader:
            rows.append(" | ".join(f"{k}: {v}" for k, v in row.items()))
        return "\n".join(rows)


pipeline = Pipeline()
count = pipeline.ingest(DATA_DIR)
print(f"Ingested {count} chunks")

results = pipeline.query("What is the Q4 revenue?", top_k=2)
for hit in results:
    print(f"  Score: {hit.get('score', 0.0):.3f}")
    print(f"  Text: {hit.get('text', '')[:200]}")
    print()
