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
                    "id": 1,
                    "title": {"rendered": "Department of Energy v. Wildlife Service"},
                }
            ],
        },
        "documents": [],
    }

    mapped_documents = map_documents(document_data, False)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 No document media provided in the data. Skipping document litigation."
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
        "documents": [{"id": 1, "source_url": "https://energy/case-document.pdf"}],
    }

    mapped_documents = map_documents(document_data, False)
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

    mapped_documents = map_documents(document_data, False)
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

    mapped_documents = map_documents(document_data, False)
    assert len(mapped_documents) == 0

    captured = capsys.readouterr()

    assert (
        "🛑 Skipping mapping documents, missing case id at index 0."
        in captured.out.strip()
    )
