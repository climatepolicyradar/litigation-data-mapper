from enum import Enum


class CaseStatus(Enum):
    PENDING = "Pending"
    DECIDED = "Decided"
    APPEALED = "Appealed / Under Review"
    ENFORCEMENT = "Enforcement / Implementation Phase"
    SETTLED = "Settled"
    WITHDRAWN = "Withdrawn / Discontinued"


CASE_STATUS_MAPPING = {
    "pen": CaseStatus.PENDING,
    "dec": CaseStatus.DECIDED,
    "app": CaseStatus.APPEALED,
    "enf": CaseStatus.ENFORCEMENT,
    "set": CaseStatus.SETTLED,
    "wit": CaseStatus.WITHDRAWN,
}
