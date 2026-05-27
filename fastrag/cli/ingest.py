"""fastrag ingest command.

Scans a file or directory, runs every supported file through the full
Pipeline (load → chunk → embed → store), and updates the delta-sync
ledger so unchanged files are skipped on subsequent runs.
"""
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from fastrag.ledger import Ledger
from fastrag.pipeline import Pipeline

console = Console()


def ingest(
    path: Path = typer.Argument(..., help="File or directory to ingest"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show debug logs"),
) -> None:
    """Ingest documents into the vector store."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if not path.exists():
        console.print(f"[red]Error: path not found: {path}[/red]")
        raise typer.Exit(1)

    pipeline = Pipeline()
    ledger = Ledger()

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        progress.add_task("Ingesting documents...", total=None)
        count = pipeline.ingest(path, ledger=ledger)

    if count == 0:
        console.print("[yellow]No new or changed content to store.[/yellow]")
    else:
        console.print(f"[green]Stored {count} chunks.[/green]")
