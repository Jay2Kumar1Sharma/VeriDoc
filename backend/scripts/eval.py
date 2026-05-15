import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from app.core.config import get_settings
from app.graph.builder import build_graph
from app.graph.state import initial_state
from app.llm.clients import ChatMessage, LLMClient, get_llm_client
from app.llm.prompts import GroundednessOutput

app = typer.Typer(help="Run the local VeriDoc evaluation harness.")


@dataclass(frozen=True)
class GoldenCase:
    question: str
    expected_chunk_id: str
    expected_answer: str


@dataclass(frozen=True)
class EvalRow:
    question: str
    expected_chunk_id: str
    retrieved: bool
    grounded: bool
    correctness: bool


@app.command()
def run(
    golden_path: Annotated[
        Path,
        typer.Option(help="JSONL file with question, expected_chunk_id, expected_answer."),
    ] = Path("tests/eval/golden.jsonl"),
    output_path: Annotated[
        Path,
        typer.Option(help="Markdown report path."),
    ] = Path("../eval-results/REPORT.md"),
) -> None:
    rows = asyncio.run(_run_eval(golden_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_report(rows), encoding="utf-8")
    typer.echo(f"Wrote {output_path}")


async def _run_eval(golden_path: Path) -> list[EvalRow]:
    cases = _load_cases(golden_path)
    settings = get_settings()
    graph = build_graph()
    llm_client = get_llm_client()
    rows: list[EvalRow] = []
    for index, case in enumerate(cases):
        result = await graph.ainvoke(
            initial_state(case.question),
            config={"configurable": {"thread_id": f"eval-{index}"}},
        )
        retrieved_ids = {doc.chunk_id for doc in result.get("retrieved_docs", [])}
        check = result.get("hallucination_check") or {}
        grounded = bool(check.get("grounded", False))
        correctness = await _judge_correctness(
            llm_client,
            settings.grading_model,
            case,
            str(result.get("answer", "")),
        )
        rows.append(
            EvalRow(
                question=case.question,
                expected_chunk_id=case.expected_chunk_id,
                retrieved=case.expected_chunk_id in retrieved_ids,
                grounded=grounded,
                correctness=correctness,
            )
        )
    return rows


async def _judge_correctness(
    llm_client: LLMClient,
    model: str,
    case: GoldenCase,
    answer: str,
) -> bool:
    output = await llm_client.complete(
        messages=[
            ChatMessage(
                role="system",
                content=(
                    "Judge whether the candidate answer covers the expected answer. "
                    "Return grounded=true for correct and grounded=false for incorrect."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    f"Question:\n{case.question}\n\n"
                    f"Expected answer:\n{case.expected_answer}\n\n"
                    f"Candidate answer:\n{answer}"
                ),
            ),
        ],
        model=model,
        response_model=GroundednessOutput,
    )
    return output.grounded


def _load_cases(path: Path) -> list[GoldenCase]:
    cases: list[GoldenCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        cases.append(
            GoldenCase(
                question=str(payload["question"]),
                expected_chunk_id=str(payload["expected_chunk_id"]),
                expected_answer=str(payload["expected_answer"]),
            )
        )
    return cases


def _render_report(rows: list[EvalRow]) -> str:
    total = len(rows)
    recall = _percentage(sum(row.retrieved for row in rows), total)
    grounding = _percentage(sum(row.grounded for row in rows), total)
    correctness = _percentage(sum(row.correctness for row in rows), total)
    lines = [
        "# VeriDoc Eval Report",
        "",
        f"Generated: {datetime.now(UTC).isoformat()}",
        "",
        "| Metric | Score |",
        "| --- | ---: |",
        f"| Retrieval recall@5 | {recall} |",
        f"| Grounding rate | {grounding} |",
        f"| Judge correctness | {correctness} |",
        "",
        "| Question | Expected chunk | Retrieved | Grounded | Correct |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row.question} | {row.expected_chunk_id} | {_mark(row.retrieved)} | "
            f"{_mark(row.grounded)} | {_mark(row.correctness)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _percentage(count: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(count / total) * 100:.1f}%"


def _mark(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    app()
