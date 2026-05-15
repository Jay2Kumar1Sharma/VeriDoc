import asyncio
import sys
from pathlib import Path

import typer

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.pipeline import ingest_sources  # noqa: E402


def main(
    replace: bool = typer.Option(True, help="Replace existing chunks for each source."),
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    urls_path = repo_root / "corpus" / "urls.txt"
    local_dir = repo_root / "corpus" / "local"
    urls = [
        line.strip()
        for line in urls_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    local_files = sorted(local_dir.glob("*.md"))
    report = asyncio.run(ingest_sources([*urls, *local_files], replace=replace))

    typer.echo("Source | Status | Chunks | Doc ID | Error")
    typer.echo("-" * 80)
    for result in report.results:
        typer.echo(
            f"{result.source} | {result.status} | {result.chunk_count} | "
            f"{result.doc_id or ''} | {result.error or ''}"
        )


if __name__ == "__main__":
    typer.run(main)
