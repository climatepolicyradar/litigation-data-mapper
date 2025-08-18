from datetime import datetime
from unittest.mock import patch

import pytest

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.extract_concepts import Concept, ConceptType
from litigation_data_mapper.parsers.family import process_us_case_data


@pytest.fixture()
def mapped_us_family():
    yield {
        "category": "Litigation",
        "collections": [
            "Sabin.collection.1.0",
            "Sabin.collection.2.0",
        ],
        "concepts": [],
        "geographies": ["USA", "US-NY"],
        "import_id": "Sabin.family.1.0",
        "metadata": {
            "case_number": [
                "1:20-cv-12345",
            ],
            "core_object": [],
            "id": [
                "1",
            ],
            "original_case_name": [],
            "status": [
                "Memorandum of law filed in support of verified petition.",
            ],
            "concept_preferred_label": [],
        },
        "summary": "The description of cases relating to litigation of the Sierra Club",
        "title": "Sierra Club v. New York State Department of Environmental Conservation",
    }


@patch("litigation_data_mapper.parsers.family.fetch_individual_concept")
def test_maps_us_cases(
    mock_fetch_individual_concept,
    mock_us_case: dict,
    mapped_us_family: dict,
    mock_context: LitigationContext,
):
    mock_fetch_individual_concept.return_value = None

    case_id = mock_us_case.get("id", 1)
    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )

    assert not isinstance(mapped_family, Failure)
    assert mapped_family == mapped_us_family


def test_generates_family_import_id(mock_us_case: dict, mock_context):
    case_id = 1000
    mock_us_case["id"] = case_id

    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["import_id"] == f"Sabin.family.{case_id}.0"


def test_maps_collections_to_family(
    mock_us_case: dict, mock_context: LitigationContext
):
    case_id = 1
    mock_us_case["acf"]["ccl_case_bundle"] = [34, 45]

    mock_context.case_bundles[34] = {"description": "Case relating to case bundle 34"}
    mock_context.case_bundles[45] = {"description": "Case relating to case bundle 45"}

    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert mapped_family is not None
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["collections"] == [
        "Sabin.collection.34.0",
        "Sabin.collection.45.0",
    ]


def test_returns_generic_response_if_no_documents_available_to_calculate_status(
    mock_us_case: dict, mock_context: LitigationContext
):
    empty_documents = []
    mock_us_case["acf"]["ccl_case_documents"] = empty_documents
    case_id = 1

    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert mapped_family is not None
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["metadata"].get("status") == ["Status Pending"]


def test_skips_processing_us_case_data_if_docket_number_is_missing(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["acf"]["ccl_docket_number"] = ""
    case_id = 1
    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert mapped_family == Failure(
        id=1, type="us_case", reason="Missing the following values: docket_number"
    )


def test_skips_processing_us_case_data_if_bundle_id_is_missing(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["acf"]["ccl_case_bundle"] = []
    case_id = 1

    family_data = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert family_data == Failure(
        id=1, type="us_case", reason="Missing the following values: bundle_ids"
    )


def test_skips_processing_us_case_data_if_bundle_id_is_not_in_context_bundle_ids(
    mock_us_case: dict,
):
    mock_us_case["acf"]["ccl_case_bundle"] = [1, 2]
    case_id = 1
    context = LitigationContext(
        failures=[],
        debug=False,
        last_import_date=datetime.strptime("2025-01-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
        get_modified_data=False,
        case_bundles={
            99: {"description": "The description"},
            100: {"description": "The description"},
        },
        skipped_documents=[],
        skipped_families=[],
    )

    family_data = process_us_case_data(
        mock_us_case, case_id, context, concepts={}, collections=[]
    )
    assert family_data == Failure(
        id=1, type="us_case", reason="Does not have a valid case bundle"
    )


def test_skips_processing_us_case_data_if_title_is_missing(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["title"]["rendered"] = ""
    case_id = 1
    family_data = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert family_data == Failure(
        id=1, type="us_case", reason="Missing the following values: title"
    )


def test_skips_processing_us_case_data_if_case_has_invalid_state_code(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["acf"]["ccl_state"] = "XXX"
    case_id = 1
    family_data = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert family_data == Failure(
        id=1, type="us_case", reason="Does not have a valid ccl state code (XXX)"
    )


def tests_gets_the_latest_document_status_when_there_is_one_document(
    mock_us_case: dict, mock_context: LitigationContext
):
    documents = [
        {
            "ccl_filing_date": "20230101",
            "ccl_outcome": "Filed",
        }
    ]
    mock_us_case["acf"]["ccl_case_documents"] = documents
    case_id = 1
    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["metadata"].get("status") == ["Filed"]


def tests_gets_the_latest_document_status(
    mock_us_case: dict, mock_context: LitigationContext
):
    documents = [
        {
            "ccl_filing_date": "20230101",
            "ccl_outcome": "Filed",
        },
        {
            "ccl_filing_date": "20240101",
            "ccl_outcome": "Pending",
        },
    ]
    mock_us_case["acf"]["ccl_case_documents"] = documents
    case_id = 1

    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}, collections=[]
    )
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["metadata"].get("status") == ["Pending"]


@patch("litigation_data_mapper.parsers.family.fetch_individual_concept")
def tests_gets_concepts_from_case_bundles(
    mock_fetch_individual_concept, mock_us_case: dict, mock_context: LitigationContext
):
    mock_fetch_individual_concept.return_value = None
    case_id = 1

    # collections = bundles
    case_bundles_on_case = [1, 2]
    collections = [
        # should match
        {"id": 1, "case_category": [1, 2, 3]},
        {"id": 2, "case_category": [4, 5, 6], "principal_law": [10, 11, 12]},
        # shouldn't match
        {"id": 3, "case_category": [7, 8, 9], "principal_law": [13, 14, 15]},
    ]
    mock_us_case["acf"]["ccl_case_bundle"] = case_bundles_on_case

    matching_concepts = {
        1: Concept(
            internal_id=1,
            id="Concept 1",
            type=ConceptType.LegalCategory,
            preferred_label="Concept 1",
        ),
        2: Concept(
            internal_id=2,
            id="Concept 2",
            type=ConceptType.LegalCategory,
            preferred_label="Concept 2",
        ),
        3: Concept(
            internal_id=3,
            id="Concept 3",
            type=ConceptType.LegalCategory,
            preferred_label="Concept 3",
        ),
        4: Concept(
            internal_id=4,
            id="Concept 4",
            type=ConceptType.LegalCategory,
            preferred_label="Concept 4",
        ),
        5: Concept(
            internal_id=5,
            id="Concept 5",
            type=ConceptType.LegalCategory,
            preferred_label="Concept 5",
        ),
        6: Concept(
            internal_id=6,
            id="Concept 6",
            type=ConceptType.LegalCategory,
            preferred_label="Concept 6",
        ),
        10: Concept(
            internal_id=10,
            id="Concept 10",
            type=ConceptType.Law,
            preferred_label="Concept 10",
        ),
        11: Concept(
            internal_id=11,
            id="Concept 11",
            type=ConceptType.Law,
            preferred_label="Concept 11",
        ),
        12: Concept(
            internal_id=12,
            id="Concept 12",
            type=ConceptType.Law,
            preferred_label="Concept 12",
        ),
    }
    non_matching_concepts = {
        7: Concept(
            internal_id=7,
            id="Concept 7",
            type=ConceptType.Law,
            preferred_label="Concept 7",
        ),
        8: Concept(
            internal_id=8,
            id="Concept 8",
            type=ConceptType.Law,
            preferred_label="Concept 8",
        ),
        9: Concept(
            internal_id=9,
            id="Concept 9",
            type=ConceptType.Law,
            preferred_label="Concept 9",
        ),
        13: Concept(
            internal_id=13,
            id="Concept 13",
            type=ConceptType.Law,
            preferred_label="Concept 13",
        ),
        14: Concept(
            internal_id=14,
            id="Concept 14",
            type=ConceptType.Law,
            preferred_label="Concept 14",
        ),
        15: Concept(
            internal_id=15,
            id="Concept 15",
            type=ConceptType.Law,
            preferred_label="Concept 15",
        ),
    }

    mapped_family = process_us_case_data(
        mock_us_case,
        case_id,
        mock_context,
        concepts={**matching_concepts, **non_matching_concepts},
        collections=collections,
    )
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["concepts"] == [
        {
            "id": c.id,
            "ids": [],
            "type": c.type.value if hasattr(c.type, "value") else str(c.type),
            "preferred_label": c.preferred_label,
            "relation": c.relation,
            "subconcept_of_labels": c.subconcept_of_labels,
        }
        for c in matching_concepts.values()
    ]
