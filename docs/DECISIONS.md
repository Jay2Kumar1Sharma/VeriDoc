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

### ADR-004: Gemini as the configured Phase 3 LLM provider

**Status:** Accepted

**Context**

The original assignment listed Anthropic as the primary LLM provider with OpenAI as an alternative. The implementation request for Phase 3 changed the target LLM to Gemini Flash-Lite.

**Decision**

Add a Gemini provider using the official `google-genai` SDK and make `LLM_PROVIDER=gemini` the default. The model ID remains environment-driven through `GENERATION_MODEL` and `GRADING_MODEL`. The checked-in example uses the currently documented Flash-Lite model code, while allowing a newer `gemini-3.1-flash-lite` value if enabled for the user's API key.

**Consequences**

This adds a third LLM provider while keeping the provider interface stable. The Google SDK requires `httpx>=0.28.1`, so the backend `httpx` pin was widened from the original `<0.28` constraint.

### ADR-005: Web search only after corpus retries are exhausted

**Status:** Accepted

**Context**

The system should remain documentation-first. Web search is useful when the local corpus cannot answer, but using it too early would weaken the demo's core claim that answers are grounded in indexed docs.

**Decision**

Run Tavily web search only when `ENABLE_WEB_SEARCH_FALLBACK=true`, all rewrite retries are exhausted, and no relevant corpus chunks remain. Web results are converted into the same `RetrievedDoc` shape and pass through the existing grader and generator.

**Consequences**

The fallback reuses the normal trace, grading, citation, and groundedness machinery. Web answers are visibly marked by `web:` citation sources. If Tavily is enabled without an API key, the trace records that condition and the graph falls back honestly.

### ADR-006: SQLite-backed session memory with prompt context

**Status:** Accepted

**Context**

LangGraph's in-memory checkpointer is useful during a process lifetime, but reviewers need chat history to survive server restarts. The project already has SQLite for traces and feedback.

**Decision**

Persist user and assistant turns in the existing `session_messages` table. On a session-scoped query, load the latest configurable number of messages and prepend them as a conversation context block to query analysis.

**Consequences**

This keeps memory local-first and easy to inspect. It deliberately limits memory to query rewriting and classification rather than stuffing the entire conversation into generation, which reduces prompt drift while still resolving follow-up questions.
