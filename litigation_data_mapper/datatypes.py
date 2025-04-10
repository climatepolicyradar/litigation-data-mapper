from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Failure:
    id: int | None
    type: str
    reason: str


@dataclass(frozen=True, slots=True)
class LitigationContext:
    failures: list[Failure]
    debug: bool
    get_all_data: bool
    case_bundles: dict[int, dict[str, str]]
    skipped_families: list[int]
    skipped_documents: list[int]
