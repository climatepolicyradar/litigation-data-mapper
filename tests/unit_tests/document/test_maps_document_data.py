from datetime import datetime

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.parsers.document import map_documents

mock_context = LitigationContext(
    failures=[],
    debug=False,
    last_import_date=datetime.strptime("2025-01-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    get_all_data=False,
    case_bundles={},
    skipped_documents=[],
    skipped_families=[],
)


def test_skips_mapping_documents_if_data_missing_document_media(capsys):
    document_data = {
        "families": {
            "us_cases": [
                {
                    "id": 1,
                    "title": {
                        "rendered": "Center for Biological Diversity v. Wildlife Service"
                    },
                }
            ],
            "global_cases": [
                {
                    "id": 2,
                    "title": {"rendered": "Department of Energy v. Wildlife Service"},
                }
            ],
        },
        "documents": [],
    }

    mapped_documents = map_documents(document_data, mock_context)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 No document media provided in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_skips_mapping_documents_if_case_id_in_skipped_families_context(
    mock_global_case,
    mock_us_case,
):
    document_data = {
        "families": {
            "us_cases": [mock_us_case],
            "global_cases": [mock_global_case],
        },
        "documents": [
            {"id": 2, "source_url": "https://energy/case-document.pdf"},
            {"id": 3, "source_url": "https://brazil/case-document.pdf"},
            {"id": 4, "source_url": "https://germany/case-document.pdf"},
        ],
    }

    mock_context.skipped_families.append(1)
    mapped_documents = map_documents(document_data, mock_context)
    assert len(mapped_documents) == 2


def test_skips_mapping_documents_if_missing_us_case(capsys):
    document_data = {
        "families": {
            "us_cases": [],
            "global_cases": [
                {
                    "id": 1,
                    "title": {"rendered": "Department of Energy v. Wildlife Service"},
                }
            ],
        },
        "documents": [{"id": 2, "source_url": "https://energy/case-document.pdf"}],
    }
    mapped_documents = map_documents(document_data, mock_context)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 No US cases found in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_skips_mapping_documents_if_missing_global_case(capsys):
    document_data = {
        "families": {
            "us_cases": [
                {
                    "id": 1,
                    "title": {
                        "rendered": "Center for Biological Diversity v. Wildlife Service"
                    },
                }
            ],
            "global_cases": [],
        },
        "documents": [{"id": 1, "source_url": "https://energy/case-document.pdf"}],
    }
    mapped_documents = map_documents(document_data, mock_context)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 No global cases found in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_skips_mapping_documents_if_family_missing_case_id():
    document_data = {
        "families": {
            "us_cases": [
                {
                    "id": None,
                    "title": {
                        "rendered": "Center for Biological Diversity v. Wildlife Service"
                    },
                    "type": "case",
                }
            ],
            "global_cases": [
                {
                    "id": None,
                    "title": {"rendered": "Department of Energy v. Wildlife Service"},
                    "type": "non_us_case",
                }
            ],
        },
        "documents": [{"id": 1, "source_url": "https://energy/case-document.pdf"}],
    }

    mapped_documents = map_documents(document_data, mock_context)
    assert mock_context.failures == [
        Failure(
            id=None,
            type="case",
            reason="Does not contain a case id at index (0). Mapping documents.",
        ),
        Failure(
            id=None,
            type="case",
            reason="Does not contain a case id at index (1). Mapping documents.",
        ),
    ]
    assert mapped_documents == []
