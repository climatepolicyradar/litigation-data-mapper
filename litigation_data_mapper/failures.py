from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Failure:
    id: str | None
    type: str
    reason: str
