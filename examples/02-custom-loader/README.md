# Custom Loader

Demonstrates building a custom CSV loader using the base class and
registering it with the decorator.

## Run

```bash
pip install fastrag
python custom_csv_loader.py
```

## What it does

1. Defines a `CSVLoader` that reads CSV files and concatenates columns
2. Registers it with `@register_loader("csv")`
3. Ingests a sample CSV file
4. Queries the knowledge base
