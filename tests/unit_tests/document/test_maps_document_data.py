from litigation_data_mapper.parsers.document import map_documents


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

    context = {"debug": False}
    mapped_documents = map_documents(document_data, context)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 No document media provided in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_skips_mapping_documents_if_case_id_in_skipped_families_context(
    capsys, mock_global_case, mock_us_case
):
    document_data = {
        "families": {
            "us_cases": [mock_us_case],
            "global_cases": [mock_global_case],
        },
        "documents": [{"id": 2, "source_url": "https://energy/case-document.pdf"}],
    }

    context = {"debug": False, "skipped_families": [1]}
    mapped_documents = map_documents(document_data, context)
    assert len(mapped_documents) == 1

    captured = capsys.readouterr()

    assert (
        "🛑Skipping mapping documents, case_id 1 in skipped families context"
        in captured.out.strip()
    )


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
    context = {"debug": False}
    mapped_documents = map_documents(document_data, context)
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
    context = {"debug": False}
    mapped_documents = map_documents(document_data, context)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 No Global cases found in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_skips_mapping_documents_if_family_missing_case_id(capsys):
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

    context = {"debug": False}
    mapped_documents = map_documents(document_data, context)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 Skipping mapping documents, missing case id at index 0."
        in captured.out.strip()
    )
