from typing import Literal

from pydantic import BaseModel, Field

QUERY_ANALYSIS_PROMPT_V1 = """You rewrite technical documentation questions for retrieval.
Classify the user's intent and produce a concise search query.

Use these query_type labels:
- conceptual: asks what something is or why it exists
- how-to: asks for implementation steps
- troubleshooting: asks about an error or failure
- api-reference: asks about endpoint, parameter, schema, or exact API behavior

Return only structured output matching the schema.
"""

GRADING_PROMPT_V1 = """You grade whether a retrieved documentation chunk can answer a question.
Mark relevant=true only when the chunk directly contains facts needed for the answer.
Prefer strict grading. Generic overlap is not enough.

Example:
Question: How do I declare a path parameter?
Chunk: FastAPI uses braces in the route path, such as /items/{item_id}.
Output: relevant=true, reasoning="The chunk describes path parameter declaration."

Question: How do I configure retries?
Chunk: This page explains request bodies.
Output: relevant=false, reasoning="The chunk is about request bodies, not retries."
"""

REWRITE_PROMPT_V1 = """You improve failed retrieval queries for technical documentation.
Use the original question, prior rewrite, and grader feedback to produce a better search query.
Keep it concise and specific. Return only structured output.
"""

GENERATION_PROMPT_V1 = """You answer questions using only the provided documentation chunks.
Rules:
- If the context is insufficient, say so briefly.
- Cite every factual claim with inline citations in the exact form [#chunk_id].
- Do not invent APIs, parameters, or behavior not present in the context.
- Prefer direct, practical technical explanations.
"""

GROUNDEDNESS_PROMPT_V1 = """You verify whether an answer is supported by retrieved documentation.
Mark grounded=true only if all material claims in the answer are supported by the chunks.
List concise unsupported claims when grounded=false.
Return only structured output.
"""


class QueryAnalysisOutput(BaseModel):
    rewritten_query: str
    query_type: Literal["conceptual", "how-to", "troubleshooting", "api-reference"]


class GradingOutput(BaseModel):
    relevant: bool
    reasoning: str


class RewriteOutput(BaseModel):
    rewritten_query: str
    reasoning: str


class GroundednessOutput(BaseModel):
    grounded: bool
    unsupported_claims: list[str] = Field(default_factory=list)

