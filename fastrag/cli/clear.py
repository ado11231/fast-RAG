"""fastrag clear command.

Wipes the vector store and delta-sync ledger.
Useful when switching embedding models (different dimensions require
a fresh index) or resetting a project entirely.
"""
import typer
from rich.console import Console

from fastrag.ledger import Ledger
from fastrag.stores.chroma import ChromaStore

console = Console()


def clear(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Wipe the vector store and ledger."""
    if not yes:
        confirmed = typer.confirm("Delete all ingested vectors and ledger entries?")
        if not confirmed:
            console.print("Aborted.")
            raise typer.Exit(0)

    ChromaStore().clear()
    Ledger().clear()
    console.print("[green]Store and ledger cleared.[/green]")
