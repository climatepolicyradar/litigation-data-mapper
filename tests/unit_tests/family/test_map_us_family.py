import pytest

from litigation_data_mapper.parsers.family import process_us_case_data


@pytest.fixture()
def mapped_us_family():
    return {
        "category": "Litigation",
        "collections": [
            "Litigation.collection.1.0",
            "Litigation.collection.2.0",
        ],
        "geographies": ["USA", "US-NY"],
        "import_id": "Litigation.family.1.0",
        "metadata": {
            "case_number": [
                "1:20-cv-12345",
            ],
            "core_object": [],
            "id": [
                1,
            ],
            "original_case_name": [],
            "status": [
                "Memorandum of law filed in support of verified petition.",
            ],
        },
        "summary": "",
        "title": "Sierra Club v. New York State Department of Environmental Conservation",
    }


def test_maps_us_cases(mock_us_case: dict, mapped_us_family: dict):
    case_id = mock_us_case.get("id", 1)
    mapped_family = process_us_case_data(mock_us_case, case_id)

    assert mapped_family is not None
    assert mapped_family == mapped_us_family


def test_generates_family_import_id(mock_us_case: dict):
    case_id = 1000
    mock_us_case["id"] = case_id

    mapped_family = process_us_case_data(mock_us_case, case_id)
    assert mapped_family is not None
    assert mapped_family != {}
    assert mapped_family["import_id"] == f"Litigation.family.{case_id}.0"


def test_maps_collections_to_family(mock_us_case: dict):
    case_id = 1
    mock_us_case["acf"]["ccl_case_bundle"] = [34, 45]

    mapped_family = process_us_case_data(mock_us_case, case_id)
    assert mapped_family is not None
    assert mapped_family != {}
    assert mapped_family["collections"] == [
        "Litigation.collection.34.0",
        "Litigation.collection.45.0",
    ]


def test_skips_processing_us_case_data_if_status_is_not_calculated(
    capsys, mock_us_case: dict
):
    empty_documents = []
    mock_us_case["acf"]["ccl_case_documents"] = empty_documents
    case_id = 1

    mapped_family = process_us_case_data(mock_us_case, case_id)
    assert mapped_family is None
    captured = capsys.readouterr()
    assert (
        f"🛑 Skipping US case_id {case_id}, missing family metadata: case documents"
        in captured.out.strip()
    )


def test_skips_processing_us_case_data_if_docket_number_is_missing(
    capsys, mock_us_case: dict
):
    mock_us_case["acf"]["ccl_docket_number"] = ""
    case_id = 1

    mapped_family = process_us_case_data(mock_us_case, case_id)
    assert mapped_family is None
    captured = capsys.readouterr()
    assert (
        "🛑 Skipping US case_id 1, missing family metadata: docket_number"
        in captured.out.strip()
    )


def test_skips_processing_us_case_data_if_bundle_id_is_missing(
    capsys, mock_us_case: dict
):
    mock_us_case["acf"]["ccl_case_bundle"] = []
    case_id = 1

    family_data = process_us_case_data(mock_us_case, case_id)
    assert family_data is None
    captured = capsys.readouterr()
    assert "🛑 Skipping US case_id 1, missing bundle_ids" in captured.out.strip()


def test_skips_processing_us_case_data_if_title_is_missing(capsys, mock_us_case: dict):
    mock_us_case["title"]["rendered"] = ""
    case_id = 1

    family_data = process_us_case_data(mock_us_case, case_id)
    assert family_data is None
    captured = capsys.readouterr()
    assert "🛑 Skipping US case_id 1, missing title" in captured.out.strip()


def tests_gets_the_latest_document_status_when_there_is_one_document(
    mock_us_case: dict,
):
    documents = [
        {
            "ccl_filing_date": "20230101",
            "ccl_outcome": "Filed",
        }
    ]
    mock_us_case["acf"]["ccl_case_documents"] = documents
    case_id = 1

    mapped_family = process_us_case_data(mock_us_case, case_id)
    assert mapped_family is not None
    assert mapped_family != {}
    assert mapped_family["metadata"].get("status") == ["Filed"]


def tests_gets_the_latest_document_status(
    mock_us_case: dict,
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

    mapped_family = process_us_case_data(mock_us_case, case_id)
    assert mapped_family is not None
    assert mapped_family != {}
    assert mapped_family["metadata"].get("status") == ["Pending"]
