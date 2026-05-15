from time import perf_counter
from typing import Any


class NodeTimer:
    def __init__(self) -> None:
        self._start = perf_counter()

    def elapsed_ms(self) -> int:
        return int((perf_counter() - self._start) * 1000)


def trace_entry(node: str, duration_ms: int, output: dict[str, Any]) -> dict[str, object]:
    return {
        "node": node,
        "duration_ms": duration_ms,
        "output": output,
    }

