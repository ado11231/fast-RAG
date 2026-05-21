"""fastrag serve command."""
import typer
from rich.console import Console

console = Console()


def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on"),
) -> None:
    """Spin up a FastAPI server on the active store."""
    try:
        import uvicorn
        from fastapi import FastAPI
    except ImportError:
        console.print("[red]fastapi and uvicorn are required. Run: pip install fastapi 'uvicorn[standard]'[/red]")
        raise typer.Exit(1)

    from fastrag.pipeline import Pipeline

    pipeline = Pipeline()
    api = FastAPI(title="fastrag", description="fastrag query API", version="0.1.0")

    @api.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @api.get("/query")
    def query_endpoint(q: str, top_k: int = 5) -> dict:
        results = pipeline.query(q, top_k=top_k)
        return {"question": q, "results": results}

    console.print(f"[green]fastrag API running → http://{host}:{port}[/green]")
    console.print(f"[dim]Interactive docs  → http://{host}:{port}/docs[/dim]")
    uvicorn.run(api, host=host, port=port)
