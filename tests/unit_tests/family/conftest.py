import pytest


@pytest.fixture()
def mock_context():
    return {
        "debug": False,
        "case_bundle_ids": {
            1: {
                "description": "The description of cases relating to litigation of the Sierra Club"
            },
            2: {
                "description": "The description of cases where jurisdictions lie in the state of New York"
            },
        },
    }


@pytest.fixture()
def mock_global_case():
    return {
        "id": 1,
        "title": {"rendered": "Center for Biological Diversity v. Wildlife Service"},
        "jurisdiction": [2],
        "acf": {
            "ccl_nonus_case_name": "Center for Biological Diversity v. Wildlife Service",
            "ccl_nonus_summary": "Summary of the challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "ccl_nonus_reporter_info": "1:20-cv-12345",
            "ccl_nonus_status": "Pending",
            "ccl_nonus_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "ccl_nonus_case_country": "US",
            "ccl_nonus_case_documents": [
                {
                    "ccl_nonus_document_type": "judgment",
                    "ccl_nonus_filing_date": "20230718",
                    "ccl_nonus_file": 89750,
                    "ccl_nonus_document_summary": "",
                },
                {
                    "ccl_nonus_document_type": "judgment",
                    "ccl_nonus_filing_date": "20240704",
                    "ccl_nonus_file": 89751,
                    "ccl_nonus_document_summary": "",
                },
            ],
        },
    }


@pytest.fixture()
def mock_us_case():
    return {
        "id": 1,
        "title": {
            "rendered": "Sierra Club v. New York State Department of Environmental Conservation"
        },
        "entity": [133, 245],
        "acf": {
            "ccl_case_bundle": [1, 2],
            "ccl_docket_number": "1:20-cv-12345",
            "ccl_entity": 245,
            "ccl_filing_year_for_action": "2025",
            "ccl_state": "NY",
            "ccl_case_documents": [
                {
                    "ccl_document_type": "petition",
                    "ccl_filing_date": "20250122",
                    "ccl_file": 89915,
                    "ccl_document_headline": "",
                    "ccl_document_summary": "",
                    "ccl_outcome": "Memorandum of law filed in support of verified petition.",
                },
                {
                    "ccl_document_type": "petition",
                    "ccl_filing_date": "20250122",
                    "ccl_file": 89916,
                    "ccl_document_headline": "Lawsuit Alleged that New York Renewal of Power Plant Air Permit Violated State Climate Law",
                    "ccl_document_summary": "Summary of the lawsuit that alleged that the New York State Department of Environmental Conservation violated the state's climate law by renewing a power plant air permit.",
                    "ccl_outcome": "Memorandum of law filed in support of verified petition.",
                },
            ],
        },
    }


@pytest.fixture()
def mock_family_data():
    yield {
        "us_cases": [
            {
                "id": 1,
                "title": {
                    "rendered": "Sierra Club v. New York State Department of Environmental Conservation"
                },
                "entity": [133, 245],
                "acf": {
                    "ccl_case_bundle": [1, 2],
                    "ccl_docket_number": "1:20-cv-12345",
                    "ccl_entity": 245,
                    "ccl_state": "AB",
                    "ccl_filing_year_for_action": "2025",
                    "ccl_case_documents": [
                        {
                            "ccl_document_type": "petition",
                            "ccl_filing_date": "20250122",
                            "ccl_file": 89915,
                            "ccl_document_headline": "",
                            "ccl_document_summary": "",
                            "ccl_outcome": "Memorandum of law filed in support of verified petition.",
                        },
                        {
                            "ccl_document_type": "petition",
                            "ccl_filing_date": "20250122",
                            "ccl_file": 89916,
                            "ccl_document_headline": "Lawsuit Alleged that New York Renewal of Power Plant Air Permit Violated State Climate Law",
                            "ccl_document_summary": "Summary of the lawsuit that alleged that the New York State Department of Environmental Conservation violated the state's climate law by renewing a power plant air permit.",
                            "ccl_outcome": "Memorandum of law filed in support of verified petition.",
                        },
                    ],
                },
            },
        ],
        "global_cases": [
            {
                "id": 1,
                "title": {
                    "rendered": "Center for Biological Diversity v. Wildlife Service"
                },
                "jurisdiction": [2],
                "acf": {
                    "ccl_nonus_case_name": "Center for Biological Diversity v. Wildlife Service",
                    "ccl_nonus_summary": "Summary of the challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
                    "ccl_nonus_reporter_info": "1:20-cv-12345",
                    "ccl_nonus_status": "Pending",
                    "ccl_nonus_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
                    "ccl_nonus_case_country": "US",
                    "ccl_nonus_case_documents": [
                        {
                            "ccl_nonus_document_type": "judgment",
                            "ccl_nonus_filing_date": "20230718",
                            "ccl_nonus_file": 89750,
                            "ccl_nonus_document_summary": "",
                        },
                        {
                            "ccl_nonus_document_type": "judgment",
                            "ccl_nonus_filing_date": "20240704",
                            "ccl_nonus_file": 89751,
                            "ccl_nonus_document_summary": "",
                        },
                    ],
                },
            }
        ],
        "jurisdictions": [
            {"id": 1, "name": "United States"},
            {"id": 2, "name": "Canada"},
            {"id": 3, "name": "United Kingdom"},
            {"id": 4, "name": "Australia"},
        ],
    }
