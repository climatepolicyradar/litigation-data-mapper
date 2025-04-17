from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Failure:
    id: int | None
    type: str
    reason: str


@dataclass(frozen=True, slots=True)
class LitigationContext:
    failures: list[Failure]
    debug: bool
    last_import_date: datetime
    get_modified_data: bool
    case_bundles: dict[int, dict[str, str]]
    skipped_families: list[int]
    skipped_documents: list[int]
