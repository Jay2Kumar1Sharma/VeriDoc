from datetime import UTC, datetime

from app.ingestion.chunker import StructureAwareChunker, slugify_source
from app.ingestion.loaders import Document


def make_document(content: str) -> Document:
    return Document(
        content=content,
        source="docs/sample.md",
        title="Sample",
        fetched_at=datetime.now(UTC),
    )


def test_code_blocks_are_preserved() -> None:
    document = make_document(
        """
# Guide

Intro text.

```python
def hello() -> str:
    return "world"
```

Closing text.
""".strip()
    )
    chunks = StructureAwareChunker(chunk_size=80, chunk_overlap=10).chunk(document)

    code_chunks = [chunk for chunk in chunks if "def hello" in chunk.content]

    assert len(code_chunks) == 1
    assert code_chunks[0].content.count("```") == 2
    assert code_chunks[0].metadata["has_code"] is True


def test_header_metadata_is_preserved() -> None:
    document = make_document(
        """
# API

## Authentication

### API keys

Use bearer tokens.
""".strip()
    )

    chunks = StructureAwareChunker(chunk_size=200, chunk_overlap=20).chunk(document)

    assert chunks[0].metadata["h1"] == "API"
    assert chunks[0].metadata["h2"] == "Authentication"
    assert chunks[0].metadata["h3"] == "API keys"


def test_overlap_exists_for_recursive_splits() -> None:
    content = "# Guide\n\n" + " ".join(f"word{i}" for i in range(60))
    chunks = StructureAwareChunker(chunk_size=90, chunk_overlap=12).chunk(make_document(content))

    assert len(chunks) > 1
    assert chunks[0].content[-12:] in chunks[1].content


def test_oversize_code_block_is_kept_whole() -> None:
    code = "```python\n" + "\n".join(f"line_{index} = {index}" for index in range(10)) + "\n```"
    chunks = StructureAwareChunker(chunk_size=40, chunk_overlap=5).chunk(
        make_document(f"# Big\n\n{code}")
    )

    code_chunks = [chunk for chunk in chunks if "line_9" in chunk.content]

    assert len(code_chunks) == 1
    assert len(code_chunks[0].content) > 40
    assert code_chunks[0].content.count("```") == 2


def test_slug_determinism() -> None:
    source = "https://fastapi.tiangolo.com/tutorial/path-params/"

    assert slugify_source(source) == slugify_source(source)
    assert slugify_source(source) == "https-fastapi-tiangolo-com-tutorial-path-params"
