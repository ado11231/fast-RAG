"""fastrag CLI entry point — typer app that registers all subcommands.

Commands:
  ingest   — ingest documents into the vector store
  query    — ask a question against the knowledge base
  serve    — spin up a FastAPI server on the active store
  status   — show ledger and store contents
  clear    — wipe everything and start fresh
"""
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
