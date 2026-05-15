import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.ingestion.loaders import Document

logger = get_logger(__name__)


@dataclass(frozen=True)
class Chunk:
    content: str
    metadata: dict[str, Any]


@dataclass
class _Section:
    content: str
    h1: str | None
    h2: str | None
    h3: str | None


@dataclass(frozen=True)
class _Atom:
    text: str
    has_code: bool


HEADER_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
CODE_FENCE_RE = re.compile(r"(```.*?```)", re.DOTALL)
SLUG_RE = re.compile(r"[^a-z0-9]+")


class StructureAwareChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0:
            msg = "chunk_size must be positive"
            raise ValueError(msg)
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            msg = "chunk_overlap must be non-negative and smaller than chunk_size"
            raise ValueError(msg)
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []
        source_slug = slugify_source(document.source)
        for section in self._split_sections(document.content):
            for text in self._split_section_text(section.content):
                stripped = text.strip()
                if not stripped:
                    continue
                chunk_index = len(chunks)
                metadata: dict[str, Any] = {
                    "chunk_id": f"{source_slug}_{chunk_index:04d}",
                    "source": document.source,
                    "title": document.title,
                    "h1": section.h1 or "",
                    "h2": section.h2 or "",
                    "h3": section.h3 or "",
                    "chunk_index": chunk_index,
                    "has_code": "```" in stripped,
                    "char_count": len(stripped),
                }
                chunks.append(Chunk(content=stripped, metadata=metadata))
        return chunks

    def _split_sections(self, content: str) -> list[_Section]:
        sections: list[_Section] = []
        current_lines: list[str] = []
        h1: str | None = None
        h2: str | None = None
        h3: str | None = None
        current_h1: str | None = None
        current_h2: str | None = None
        current_h3: str | None = None
        in_code = False

        def flush() -> None:
            text = "\n".join(current_lines).strip()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if text and not all(HEADER_RE.match(line) for line in lines):
                sections.append(_Section(text, current_h1, current_h2, current_h3))
            current_lines.clear()

        for line in content.splitlines():
            if line.strip().startswith("```"):
                in_code = not in_code
                current_lines.append(line)
                continue

            match = HEADER_RE.match(line)
            if match and not in_code:
                flush()
                level = len(match.group(1))
                title = match.group(2).strip()
                if level == 1:
                    h1, h2, h3 = title, None, None
                elif level == 2:
                    h2, h3 = title, None
                else:
                    h3 = title
                current_h1, current_h2, current_h3 = h1, h2, h3
            current_lines.append(line)
        flush()
        return sections

    def _split_section_text(self, text: str) -> list[str]:
        atoms = list(self._iter_atoms(text))
        chunks: list[str] = []
        current = ""

        for atom in atoms:
            atom_text = atom.text.strip()
            if not atom_text:
                continue
            if atom.has_code and len(atom_text) > self._chunk_size:
                if current:
                    chunks.extend(self._split_text_preserving_overlap(current))
                    current = ""
                logger.warning(
                    "oversize_code_block_kept_whole",
                    char_count=len(atom_text),
                    chunk_size=self._chunk_size,
                )
                chunks.append(atom_text)
                continue

            candidate = join_blocks(current, atom_text)
            if len(candidate) <= self._chunk_size:
                current = candidate
                continue

            if current:
                chunks.extend(self._split_text_preserving_overlap(current))
            current = atom_text

        if current:
            chunks.extend(self._split_text_preserving_overlap(current))
        return chunks

    def _iter_atoms(self, text: str) -> Iterable[_Atom]:
        parts = CODE_FENCE_RE.split(text)
        for part in parts:
            if not part.strip():
                continue
            if part.startswith("```") and part.endswith("```"):
                yield _Atom(part, True)
                continue
            paragraphs = re.split(r"\n\s*\n", part)
            for paragraph in paragraphs:
                body_lines = [
                    line for line in paragraph.splitlines() if not HEADER_RE.match(line.strip())
                ]
                body = "\n".join(body_lines).strip()
                if body:
                    yield _Atom(body, False)

    def _split_text_preserving_overlap(self, text: str) -> list[str]:
        if "```" in text or len(text) <= self._chunk_size:
            return [text]

        chunks: list[str] = []
        remaining = text.strip()
        while len(remaining) > self._chunk_size:
            split_at = best_split_index(remaining, self._chunk_size)
            piece = remaining[:split_at].strip()
            if piece:
                chunks.append(piece)
            overlap = piece[-self._chunk_overlap :] if self._chunk_overlap else ""
            remaining = f"{overlap}{remaining[split_at:]}".strip()
        if remaining:
            chunks.append(remaining)
        return chunks


def join_blocks(left: str, right: str) -> str:
    if not left:
        return right
    return f"{left}\n\n{right}"


def best_split_index(text: str, max_length: int) -> int:
    separators = ["\n\n", "\n", ". ", " "]
    for separator in separators:
        index = text.rfind(separator, 0, max_length)
        if index > max_length // 2:
            return index + len(separator)
    return max_length


def slugify_source(source: str) -> str:
    name = source
    if "://" not in source:
        name = Path(source).as_posix()
    slug = SLUG_RE.sub("-", name.lower()).strip("-")
    return slug or "document"
