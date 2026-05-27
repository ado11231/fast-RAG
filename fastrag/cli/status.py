"""fastrag status command.

Displays the current ingestion ledger and vector store statistics
so the user can see what has been ingested without digging into
``.fastrag/`` directly.
"""
import typer
from rich.console import Console
from rich.table import Table

from fastrag.ledger import Ledger
from fastrag.stores.chroma import ChromaStore

console = Console()


def status() -> None:
    """Show what's in the current ledger and store."""
    ledger = Ledger()
    entries = ledger.entries()

    if not entries:
        console.print("[yellow]Nothing ingested yet. Run: fastrag ingest <path>[/yellow]")
        return

    table = Table(title="Ingested Files", show_header=True, header_style="bold")
    table.add_column("Source", style="cyan")
    table.add_column("SHA-256", style="dim", width=14)
    for source, sha in entries.items():
        table.add_row(source, sha[:12] + "...")
    console.print(table)

    store = ChromaStore()
    vector_count = store.count()
    console.print(f"\n[green]{len(entries)} file(s)  ·  {vector_count} vectors[/green]")
