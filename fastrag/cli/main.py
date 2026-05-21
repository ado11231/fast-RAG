"""fastrag CLI entry point."""
import typer

from fastrag.cli.clear import clear
from fastrag.cli.ingest import ingest
from fastrag.cli.query import query
from fastrag.cli.serve import serve
from fastrag.cli.status import status

app = typer.Typer(
    name="fastrag",
    help="Minimal RAG pipeline — raw documents in, queryable knowledge out.",
    no_args_is_help=True,
)

app.command()(ingest)
app.command()(query)
app.command()(serve)
app.command()(status)
app.command()(clear)
