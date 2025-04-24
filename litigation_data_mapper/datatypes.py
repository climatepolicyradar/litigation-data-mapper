from dataclasses import dataclass
from datetime import datetime

from pydantic import SecretStr


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


@dataclass(frozen=True, slots=True)
class Credentials:
    superuser_email: SecretStr
    superuser_password: SecretStr


@dataclass(frozen=True, slots=True)
class Config:
    corpus_import_id: str
    app_domain: str
    user_credentials: Credentials
