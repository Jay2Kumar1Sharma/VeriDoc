from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True)
class Document:
    content: str
    source: str
    title: str
    fetched_at: datetime


class MarkdownLoader:
    def load(self, path: Path) -> Document:
        content = path.read_text(encoding="utf-8")
        title = self._extract_title(content) or path.stem.replace("-", " ").title()
        return Document(
            content=content,
            source=str(path),
            title=title,
            fetched_at=datetime.now(UTC),
        )

    @staticmethod
    def _extract_title(content: str) -> str | None:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return None


class HTMLLoader:
    def load(self, url: str) -> Document:
        response = httpx.get(url, timeout=20.0, follow_redirects=True)
        response.raise_for_status()
        return self.load_html(response.text, source=url)

    def load_html(self, html: str, source: str) -> Document:
        soup = BeautifulSoup(html, "html.parser")
        for element in soup.select("nav, footer, aside, script, style"):
            element.decompose()

        candidate = soup.find("main") or soup.find("article") or soup.body
        main: Tag | BeautifulSoup = candidate if isinstance(candidate, Tag) else soup
        title = self._extract_title(soup, main, source)
        content = self._to_markdown(main).strip()
        return Document(
            content=content,
            source=source,
            title=title,
            fetched_at=datetime.now(UTC),
        )

    @staticmethod
    def _extract_title(soup: BeautifulSoup, main: Tag | BeautifulSoup, source: str) -> str:
        heading = main.find("h1") if isinstance(main, Tag) else None
        if heading:
            return heading.get_text(" ", strip=True)
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return source.rstrip("/").rsplit("/", maxsplit=1)[-1] or source

    def _to_markdown(self, root: Tag | BeautifulSoup) -> str:
        blocks: list[str] = []
        for element in root.find_all(["h1", "h2", "h3", "p", "pre", "ul", "ol"], recursive=True):
            if not isinstance(element, Tag) or self._has_supported_parent(element):
                continue
            rendered = self._render_block(element)
            if rendered:
                blocks.append(rendered)
        if not blocks:
            text = root.get_text("\n", strip=True)
            return "\n\n".join(line for line in text.splitlines() if line.strip())
        return "\n\n".join(blocks)

    @staticmethod
    def _has_supported_parent(element: Tag) -> bool:
        parent = element.parent
        while isinstance(parent, Tag):
            if parent.name in {"p", "pre", "ul", "ol"}:
                return True
            parent = parent.parent
        return False

    @staticmethod
    def _render_block(element: Tag) -> str:
        name = element.name
        if name in {"h1", "h2", "h3"}:
            level = int(name[1])
            return f"{'#' * level} {element.get_text(' ', strip=True)}"
        if name == "pre":
            code = element.get_text("\n", strip=True)
            return f"```\n{code}\n```"
        if name == "p":
            return element.get_text(" ", strip=True)
        if name in {"ul", "ol"}:
            marker = "-" if name == "ul" else "1."
            items = [
                f"{marker} {item.get_text(' ', strip=True)}"
                for item in element.find_all("li", recursive=False)
            ]
            return "\n".join(item for item in items if item.strip())
        return ""
