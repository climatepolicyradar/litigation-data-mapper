import pytest

from litigation_data_mapper.parsers.document import (
    get_document_headline,
    process_family_documents,
)

mock_context = {"skipped_documents": [], "skipped_families": []}


@pytest.fixture()
def mapped_global_case_documents():
    return [
        {
            "family_import_id": "Sabin.family.1.0",
            "import_id": "Sabin.document.1.dummy",
            "metadata": {
                "id": [
                    "dummy",
                ],
            },
            "source_url": None,
            "title": "",
            "variant_name": None,
        },
        {
            "family_import_id": "Sabin.family.1.0",
            "import_id": "Sabin.document.1.1",
            "metadata": {
                "id": [
                    "1",
                ],
            },
            "source_url": "https://energy/case-document.pdf",
            "title": "Center for Biological Diversity v. Wildlife Service - complaint",
            "variant_name": "Original Language",
        },
        {
            "family_import_id": "Sabin.family.1.0",
            "import_id": "Sabin.document.1.2",
            "metadata": {
                "id": [
                    "2",
                ],
            },
            "source_url": "https://adaptation/case-document.pdf",
            "title": "Center for Biological Diversity v. Wildlife Service - order",
            "variant_name": "Original Language",
        },
    ]


def test_maps_global_case_documents(
    mock_global_case: dict, mapped_global_case_documents: dict, mock_pdf_urls: dict
):
    case_id = 1

    mapped_documents = process_family_documents(
        mock_global_case, case_id, mock_pdf_urls, mock_context
    )

    assert mapped_documents is not None
    assert mapped_documents == mapped_global_case_documents
    assert (
        len(mapped_documents)
        == len(mock_global_case.get("acf", {}).get("ccl_nonus_case_documents")) + 1
    )


def test_generate_document_import_ids(mock_global_case: dict, mock_pdf_urls: dict):
    case_id = 1

    mapped_documents = process_family_documents(
        mock_global_case, case_id, mock_pdf_urls, mock_context
    )

    expected_import_ids = set(
        ["Sabin.document.1.dummy", "Sabin.document.1.1", "Sabin.document.1.2"]
    )

    assert mapped_documents is not None
    for mapped_doc in mapped_documents:
        assert mapped_doc.get("import_id") in expected_import_ids


def test_skips_mapping_global_case_documents_if_missing_case_type(
    mock_global_case: dict, capsys, mock_pdf_urls
):
    mock_global_case["type"] = None
    case_id = 2

    mapped_documents = process_family_documents(
        mock_global_case, case_id, mock_pdf_urls, mock_context
    )

    assert mapped_documents is None
    captured = capsys.readouterr()

    assert (
        f"🛑 Skipping document as family with case_id {case_id} is missing case type/title key"
        in captured.out.strip()
    )


def test_skips_mapping_global_case_documents_if_missing_case_title(
    mock_global_case: dict, capsys, mock_pdf_urls
):
    mock_global_case["title"]["rendered"] = None
    case_id = 2
    mapped_documents = process_family_documents(
        mock_global_case, case_id, mock_pdf_urls, mock_context
    )

    assert mapped_documents is None
    captured = capsys.readouterr()

    assert (
        f"🛑 Skipping document as family with case_id {case_id} is missing case type/title key"
        in captured.out.strip()
    )


def test_skips_mapping_document_if_it_does_not_have_corresponding_source_url(
    capsys, mock_pdf_urls
):
    invalid_file_id = 1234
    case_id = 1

    test_global_case = {
        "id": case_id,
        "title": {"rendered": "Center for Biological Diversity v. Wildlife Service"},
        "jurisdiction": [2],
        "type": "non_us_case",
        "acf": {
            "ccl_nonus_case_name": "Center for Biological Diversity v. Wildlife Service",
            "ccl_nonus_summary": "Summary of the challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "ccl_nonus_reporter_info": "1:20-cv-12345",
            "ccl_nonus_status": "Pending",
            "ccl_nonus_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "ccl_nonus_case_country": "US",
            "ccl_nonus_case_documents": [
                {
                    "ccl_nonus_document_type": "complaint",
                    "ccl_nonus_filing_date": "20230718",
                    "ccl_nonus_file": invalid_file_id,
                    "ccl_nonus_document_summary": "Plaintiff's administrative litigation action (official English translation)",
                }
            ],
        },
    }

    assert invalid_file_id not in mock_pdf_urls
    mapped_documents = process_family_documents(
        test_global_case, case_id, mock_pdf_urls, mock_context
    )

    assert mapped_documents is not None
    assert len(mapped_documents) == 1
    assert mapped_documents[0]["import_id"] == f"Sabin.document.{case_id}.dummy"
    captured = capsys.readouterr()
    assert (
        f"🛑 Skipping document in non_us_case ({case_id}): the document ({invalid_file_id}) is missing a source URL."
        in captured.out.strip()
    )


def test_skips_mapping_document_if_it_does_not_have_a_file_id(
    mock_global_case, capsys, mock_pdf_urls
):
    mock_file_id = None

    case_id = 2
    mock_global_case["acf"]["ccl_nonus_case_documents"][0][
        "ccl_nonus_file"
    ] = mock_file_id
    mapped_documents = process_family_documents(
        mock_global_case, case_id, mock_pdf_urls, mock_context
    )

    assert mapped_documents is not None
    assert len(mapped_documents) == 2
    captured = capsys.readouterr()
    assert (
        f"🛑 Skipping document in non_us_case({case_id}): the document ID is missing."
        in captured.out.strip()
    )


def test_skips_mapping_document_if_source_url_does_not_have_supported_file_extension(
    mock_global_case, capsys, mock_pdf_urls
):
    case_id = 2
    mock_file_id = 123
    mock_pdf_urls[mock_file_id] = "https://energy/case-document.csv"
    mock_global_case["acf"]["ccl_nonus_case_documents"][0][
        "ccl_nonus_file"
    ] = mock_file_id
    mapped_documents = process_family_documents(
        mock_global_case, case_id, mock_pdf_urls, mock_context
    )

    assert mapped_documents is not None
    assert len(mapped_documents) == 2
    captured = capsys.readouterr()
    assert (
        f"🛑 Skipping document as [.csv] is not a valid file ext. document_id: {mock_file_id}"
        in captured.out.strip()
    )


def test_generates_global_case_document_title(mock_global_case):
    case_document = mock_global_case.get("acf", {}).get("ccl_nonus_case_documents")[0]
    case_type = "non_us_case"
    case_title = "Federal Court of Brazil vs Amazon Representatives"

    document_title = get_document_headline(case_document, case_type, case_title)

    assert document_title is not None
    assert (
        document_title == f"{case_title} - {case_document['ccl_nonus_document_type']}"
    )


def test_generates_us_case_document_title_from_document_headline(mock_us_case):
    case_document = mock_us_case.get("acf", {}).get("ccl_case_documents")[0]
    case_type = "case"
    case_title = "Department of Energy vs National Parks"

    document_title = get_document_headline(case_document, case_type, case_title)

    assert document_title is not None
    assert document_title == case_document.get("ccl_document_headline")


def test_generates_us_case_document_title_if_document_headline_is_missing(mock_us_case):
    mock_us_case["acf"]["ccl_case_documents"][0]["ccl_document_headline"] = None
    case_document = mock_us_case.get("acf", {}).get("ccl_case_documents")[0]
    case_type = "case"
    case_title = "Department of Energy vs National Parks"

    document_title = get_document_headline(case_document, case_type, case_title)

    assert document_title is not None
    assert document_title == f"{case_title} - {case_document['ccl_document_type']}"
