from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime

import aiosqlite


@dataclass(frozen=True)
class DocumentRecord:
    doc_id: str
    source: str
    title: str
    ingested_at: str
    chunk_count: int
    status: str


@dataclass(frozen=True)
class QueryTraceRecord:
    trace_id: str
    question: str
    answer: str
    retries: int
    grounded: bool
    latency_ms: int
    created_at: str
    payload_json: str


@dataclass(frozen=True)
class FeedbackRecord:
    id: int
    trace_id: str
    rating: int
    comment: str | None
    created_at: str


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    created_at: str


@dataclass(frozen=True)
class SessionMessageRecord:
    id: int
    session_id: str
    role: str
    content: str
    created_at: str


class MetadataStore:
    def __init__(self, sqlite_path: str) -> None:
        self._sqlite_path = sqlite_path

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[aiosqlite.Connection]:
        db = await aiosqlite.connect(self._sqlite_path)
        db.row_factory = aiosqlite.Row
        try:
            yield db
        finally:
            await db.close()

    async def migrate(self) -> None:
        async with self.connect() as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    ingested_at TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    status TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS query_traces (
                    trace_id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    retries INTEGER NOT NULL,
                    grounded INTEGER NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (trace_id) REFERENCES query_traces(trace_id)
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
                """
            )
            await db.commit()

    async def upsert_document(
        self,
        doc_id: str,
        source: str,
        title: str,
        chunk_count: int,
        status: str,
        ingested_at: datetime | None = None,
    ) -> None:
        timestamp = (ingested_at or datetime.now(UTC)).isoformat()
        async with self.connect() as db:
            await db.execute(
                """
                INSERT INTO documents (doc_id, source, title, ingested_at, chunk_count, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    source = excluded.source,
                    title = excluded.title,
                    ingested_at = excluded.ingested_at,
                    chunk_count = excluded.chunk_count,
                    status = excluded.status
                """,
                (doc_id, source, title, timestamp, chunk_count, status),
            )
            await db.commit()

    async def get_document_by_source(self, source: str) -> DocumentRecord | None:
        async with self.connect() as db:
            cursor = await db.execute(
                """
                SELECT doc_id, source, title, ingested_at, chunk_count, status
                FROM documents
                WHERE source = ?
                """,
                (source,),
            )
            row = await cursor.fetchone()
            await cursor.close()
        if row is None:
            return None
        return _document_record_from_row(row)

    async def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
        source: str | None = None,
    ) -> list[DocumentRecord]:
        query = """
            SELECT doc_id, source, title, ingested_at, chunk_count, status
            FROM documents
        """
        params: list[str | int] = []
        if source is not None:
            query += " WHERE source = ?"
            params.append(source)
        query += " ORDER BY ingested_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        async with self.connect() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            await cursor.close()
        return [_document_record_from_row(row) for row in rows]

    async def delete_document(self, doc_id: str) -> None:
        async with self.connect() as db:
            await db.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            await db.commit()

    async def delete_document_by_source(self, source: str) -> None:
        async with self.connect() as db:
            await db.execute("DELETE FROM documents WHERE source = ?", (source,))
            await db.commit()

    async def document_count(self) -> int:
        async with self.connect() as db:
            cursor = await db.execute("SELECT COUNT(*) FROM documents")
            row = await cursor.fetchone()
            await cursor.close()
        return int(row[0]) if row is not None else 0

    async def upsert_query_trace(
        self,
        trace_id: str,
        question: str,
        answer: str,
        retries: int,
        grounded: bool,
        latency_ms: int,
        payload_json: str,
        created_at: datetime | None = None,
    ) -> None:
        timestamp = (created_at or datetime.now(UTC)).isoformat()
        async with self.connect() as db:
            await db.execute(
                """
                INSERT INTO query_traces
                    (
                        trace_id, question, answer, retries,
                        grounded, latency_ms, created_at, payload_json
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(trace_id) DO UPDATE SET
                    question = excluded.question,
                    answer = excluded.answer,
                    retries = excluded.retries,
                    grounded = excluded.grounded,
                    latency_ms = excluded.latency_ms,
                    created_at = excluded.created_at,
                    payload_json = excluded.payload_json
                """,
                (
                    trace_id,
                    question,
                    answer,
                    retries,
                    int(grounded),
                    latency_ms,
                    timestamp,
                    payload_json,
                ),
            )
            await db.commit()

    async def get_query_trace(self, trace_id: str) -> QueryTraceRecord | None:
        async with self.connect() as db:
            cursor = await db.execute(
                """
                SELECT
                    trace_id, question, answer, retries,
                    grounded, latency_ms, created_at, payload_json
                FROM query_traces
                WHERE trace_id = ?
                """,
                (trace_id,),
            )
            row = await cursor.fetchone()
            await cursor.close()
        if row is None:
            return None
        return _query_trace_record_from_row(row)

    async def list_query_traces(self, limit: int = 100, offset: int = 0) -> list[QueryTraceRecord]:
        async with self.connect() as db:
            cursor = await db.execute(
                """
                SELECT
                    trace_id, question, answer, retries,
                    grounded, latency_ms, created_at, payload_json
                FROM query_traces
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = await cursor.fetchall()
            await cursor.close()
        return [_query_trace_record_from_row(row) for row in rows]

    async def add_feedback(
        self,
        trace_id: str,
        rating: int,
        comment: str | None = None,
        created_at: datetime | None = None,
    ) -> int:
        timestamp = (created_at or datetime.now(UTC)).isoformat()
        async with self.connect() as db:
            cursor = await db.execute(
                """
                INSERT INTO feedback (trace_id, rating, comment, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (trace_id, rating, comment, timestamp),
            )
            await db.commit()
            if cursor.lastrowid is None:
                msg = "SQLite did not return a feedback row id"
                raise RuntimeError(msg)
            return cursor.lastrowid

    async def list_feedback(self, trace_id: str | None = None) -> list[FeedbackRecord]:
        query = "SELECT id, trace_id, rating, comment, created_at FROM feedback"
        params: tuple[str, ...] = ()
        if trace_id is not None:
            query += " WHERE trace_id = ?"
            params = (trace_id,)
        query += " ORDER BY created_at DESC"
        async with self.connect() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            await cursor.close()
        return [_feedback_record_from_row(row) for row in rows]

    async def create_session(
        self,
        session_id: str,
        created_at: datetime | None = None,
    ) -> None:
        timestamp = (created_at or datetime.now(UTC)).isoformat()
        async with self.connect() as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO sessions (session_id, created_at)
                VALUES (?, ?)
                """,
                (session_id, timestamp),
            )
            await db.commit()

    async def list_sessions(self) -> list[SessionRecord]:
        async with self.connect() as db:
            cursor = await db.execute(
                "SELECT session_id, created_at FROM sessions ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            await cursor.close()
        return [_session_record_from_row(row) for row in rows]

    async def add_session_message(
        self,
        session_id: str,
        role: str,
        content: str,
        created_at: datetime | None = None,
    ) -> int:
        await self.create_session(session_id)
        timestamp = (created_at or datetime.now(UTC)).isoformat()
        async with self.connect() as db:
            cursor = await db.execute(
                """
                INSERT INTO session_messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, timestamp),
            )
            await db.commit()
            if cursor.lastrowid is None:
                msg = "SQLite did not return a session message row id"
                raise RuntimeError(msg)
            return cursor.lastrowid

    async def list_session_messages(self, session_id: str) -> list[SessionMessageRecord]:
        async with self.connect() as db:
            cursor = await db.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM session_messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            )
            rows = await cursor.fetchall()
            await cursor.close()
        return [_session_message_record_from_row(row) for row in rows]


def _document_record_from_row(row: aiosqlite.Row) -> DocumentRecord:
    return DocumentRecord(
        doc_id=str(row["doc_id"]),
        source=str(row["source"]),
        title=str(row["title"]),
        ingested_at=str(row["ingested_at"]),
        chunk_count=int(row["chunk_count"]),
        status=str(row["status"]),
    )


def _query_trace_record_from_row(row: aiosqlite.Row) -> QueryTraceRecord:
    return QueryTraceRecord(
        trace_id=str(row["trace_id"]),
        question=str(row["question"]),
        answer=str(row["answer"]),
        retries=int(row["retries"]),
        grounded=bool(row["grounded"]),
        latency_ms=int(row["latency_ms"]),
        created_at=str(row["created_at"]),
        payload_json=str(row["payload_json"]),
    )


def _feedback_record_from_row(row: aiosqlite.Row) -> FeedbackRecord:
    return FeedbackRecord(
        id=int(row["id"]),
        trace_id=str(row["trace_id"]),
        rating=int(row["rating"]),
        comment=None if row["comment"] is None else str(row["comment"]),
        created_at=str(row["created_at"]),
    )


def _session_record_from_row(row: aiosqlite.Row) -> SessionRecord:
    return SessionRecord(
        session_id=str(row["session_id"]),
        created_at=str(row["created_at"]),
    )


def _session_message_record_from_row(row: aiosqlite.Row) -> SessionMessageRecord:
    return SessionMessageRecord(
        id=int(row["id"]),
        session_id=str(row["session_id"]),
        role=str(row["role"]),
        content=str(row["content"]),
        created_at=str(row["created_at"]),
    )
