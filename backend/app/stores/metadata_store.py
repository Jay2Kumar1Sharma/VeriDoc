from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiosqlite


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

