from dataclasses import dataclass

@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    summary: str | None
    expected_statuses: tuple[int, ...]
