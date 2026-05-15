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

