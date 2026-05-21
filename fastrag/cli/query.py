"""fastrag query command."""
import typer
from rich.console import Console
from rich.panel import Panel

from fastrag.pipeline import Pipeline

console = Console()


def query(
    question: str = typer.Argument(..., help="Question to ask the knowledge base"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return"),
) -> None:
    """Query the knowledge base from the terminal."""
    pipeline = Pipeline()
    results = pipeline.query(question, top_k=top_k)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        raise typer.Exit(0)

    for i, result in enumerate(results, 1):
        score = result.get("score", 0.0)
        source = result.get("metadata", {}).get("source", "unknown")
        text = result.get("text", "")
        console.print(
            Panel(
                f"[dim]Source:[/dim] {source}  [dim]Score:[/dim] {score:.3f}\n\n{text}",
                title=f"Result {i}",
                border_style="blue",
            )
        )
