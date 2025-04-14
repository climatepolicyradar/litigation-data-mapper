import pytest

from litigation_data_mapper.datatypes import Failure, LitigationContext
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
        },
        "summary": "The description of cases relating to litigation of the Sierra Club",
        "title": "Sierra Club v. New York State Department of Environmental Conservation",
    }


def test_maps_us_cases(
    mock_us_case: dict, mapped_us_family: dict, mock_context: LitigationContext
):
    case_id = mock_us_case.get("id", 1)
    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}
    )

    assert not isinstance(mapped_family, Failure)
    assert mapped_family == mapped_us_family


def test_generates_family_import_id(mock_us_case: dict, mock_context):
    case_id = 1000
    mock_us_case["id"] = case_id

    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}
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
        mock_us_case, case_id, mock_context, concepts={}
    )
    assert mapped_family is not None
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["collections"] == [
        "Sabin.collection.34.0",
        "Sabin.collection.45.0",
    ]


def test_skips_processing_us_case_data_if_status_is_not_calculated(
    mock_us_case: dict, mock_context: LitigationContext
):
    empty_documents = []
    mock_us_case["acf"]["ccl_case_documents"] = empty_documents
    case_id = 1

    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}
    )
    assert mapped_family == Failure(
        id=1, type="us_case", reason="Missing the following values: case documents"
    )


def test_skips_processing_us_case_data_if_docket_number_is_missing(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["acf"]["ccl_docket_number"] = ""
    case_id = 1
    mapped_family = process_us_case_data(
        mock_us_case, case_id, mock_context, concepts={}
    )
    assert mapped_family == Failure(
        id=1, type="us_case", reason="Missing the following values: docket_number"
    )


def test_skips_processing_us_case_data_if_bundle_id_is_missing(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["acf"]["ccl_case_bundle"] = []
    case_id = 1

    family_data = process_us_case_data(mock_us_case, case_id, mock_context, concepts={})
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
        get_all_data=False,
        case_bundles={
            99: {"description": "The description"},
            100: {"description": "The description"},
        },
        skipped_documents=[],
        skipped_families=[],
    )

    family_data = process_us_case_data(mock_us_case, case_id, context, concepts={})
    assert family_data == Failure(
        id=1, type="us_case", reason="Does not have a valid case bundle"
    )


def test_skips_processing_us_case_data_if_title_is_missing(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["title"]["rendered"] = ""
    case_id = 1
    family_data = process_us_case_data(mock_us_case, case_id, mock_context, concepts={})
    assert family_data == Failure(
        id=1, type="us_case", reason="Missing the following values: title"
    )


def test_skips_processing_us_case_data_if_case_has_invalid_state_code(
    mock_us_case: dict, mock_context: LitigationContext
):
    mock_us_case["acf"]["ccl_state"] = "XXX"
    case_id = 1
    family_data = process_us_case_data(mock_us_case, case_id, mock_context, concepts={})
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
        mock_us_case, case_id, mock_context, concepts={}
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
        mock_us_case, case_id, mock_context, concepts={}
    )
    assert not isinstance(mapped_family, Failure)
    assert mapped_family["metadata"].get("status") == ["Pending"]
