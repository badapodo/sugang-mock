from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .random_provider import RandomProvider


@dataclass
class Context:
    scenario: dict[str, Any]
    schema: dict[str, Any]
    seed: int
    output_dir: Path
    data: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.random = RandomProvider(self.seed)

    def rows(self, table: str) -> list[dict[str, Any]]:
        return self.data.setdefault(table, [])

    def table(self, table: str) -> dict[str, Any]:
        return self.schema["tables"][table]

