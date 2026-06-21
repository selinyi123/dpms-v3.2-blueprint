from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class StoredEvent:
    symbol: str
    timestamp: int
    event_type: str
    action: str
    strength: float
    confidence: float
    reason: str
    level_price: float | None = None
    invalidation_price: float | None = None
    metadata: dict = field(default_factory=dict)


class EventStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def write(self, events: Iterable[StoredEvent]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(asdict(event), ensure_ascii=False, sort_keys=True) + '\n')

    def read(self) -> list[StoredEvent]:
        if not self.path.exists():
            return []
        out = []
        with self.path.open('r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue
                try:
                    out.append(StoredEvent(**json.loads(raw)))
                except (TypeError, json.JSONDecodeError) as exc:
                    raise ValueError(f'invalid event store line {line_no}: {exc}') from exc
        return out

    @staticmethod
    def fingerprint(events: Iterable[StoredEvent]) -> str:
        rows = [asdict(event) for event in events]
        payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
