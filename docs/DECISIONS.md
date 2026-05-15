# Architecture Decision Records

## Template

### ADR-000: Decision title

**Status:** Proposed

**Context**

Describe the forces, constraints, and tradeoffs behind the decision.

**Decision**

State the chosen approach.

**Consequences**

Describe the benefits, costs, and follow-up implications.

## Decisions

### ADR-001: ChromaDB over FAISS for this scope

**Status:** Accepted

**Context**

The assignment needs a local-first vector store that reviewers can run without Docker or a managed service. The store should persist across restarts, support metadata filtering, and keep setup familiar for a Python RAG application.

**Decision**

Use embedded persistent ChromaDB rather than FAISS.

**Consequences**

Chroma gives a simple persistent client, document metadata, and a friendly local development path. FAISS is excellent for raw vector search performance, but would require more surrounding code for persistence and metadata management in this take-home scope.

### ADR-002: Structure-aware chunking strategy

**Status:** Accepted

**Context**

Technical documentation has natural structure: page title, sections, subsections, prose, and code examples. A naive fixed-window splitter can separate an answer from its heading or split code fences into invalid fragments.

**Decision**

Split first on Markdown `h1`, `h2`, and `h3` headings, preserve the heading path in chunk metadata, then recursively split oversized prose with configurable overlap. Code fences are treated as atomic blocks. If a single code block exceeds the target chunk size, keep it whole and log a warning.

**Consequences**

Retrieval results retain enough section context for citations and trace inspection. Some code-heavy chunks can exceed the nominal size, but that is preferable to corrupting runnable examples.

### ADR-003: Sentence-transformers as the default embedder

**Status:** Accepted

**Context**

Reviewers should be able to run ingestion without an OpenAI key. The assignment also asks for provider-agnostic embeddings and local-first operation.

**Decision**

Default to `sentence-transformers` with `BAAI/bge-small-en-v1.5`, while keeping an OpenAI embedding provider behind the same interface.

**Consequences**

First-run ingestion may download the model into the local Hugging Face cache, but subsequent runs work from cache. OpenAI embeddings remain available by changing `.env` configuration.
