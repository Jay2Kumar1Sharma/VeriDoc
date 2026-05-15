from pathlib import Path

from app.ingestion.loaders import HTMLLoader, MarkdownLoader


def test_markdown_loader_extracts_first_h1(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text("# Project Guide\n\nBody text", encoding="utf-8")

    document = MarkdownLoader().load(path)

    assert document.title == "Project Guide"
    assert document.content.startswith("# Project Guide")


def test_html_loader_cleans_layout_chrome() -> None:
    html = """
    <html>
      <head><title>Fallback title</title></head>
      <body>
        <nav>Navigation</nav>
        <main>
          <h1>Clean Docs</h1>
          <p>Useful content.</p>
          <pre><code>print("ok")</code></pre>
        </main>
        <footer>Footer text</footer>
      </body>
    </html>
    """

    document = HTMLLoader().load_html(html, source="https://example.test/docs")

    assert document.title == "Clean Docs"
    assert "Navigation" not in document.content
    assert "Footer text" not in document.content
    assert "# Clean Docs" in document.content
    assert 'print("ok")' in document.content

