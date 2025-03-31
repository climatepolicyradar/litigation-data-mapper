from dataclasses import dataclass
from typing import Any

from litigation_data_mapper.failures import Failure


@dataclass(frozen=True, slots=True)
class LitigationContext:
    failures: list[Failure]
    debug: bool
    case_bundles: dict[str, dict[str, Any]]
    skipped_families: list[str | int]
    skipped_documents: list[str | int]
