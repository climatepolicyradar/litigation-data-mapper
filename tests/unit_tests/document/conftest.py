import pytest


@pytest.fixture()
def mock_global_case():
    return {
        "id": 1,
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
                    "ccl_nonus_file": 1,
                    "ccl_nonus_document_summary": "Plaintiff's administrative litigation action (official English translation)",
                },
                {
                    "ccl_nonus_document_type": "order",
                    "ccl_nonus_filing_date": "20240704",
                    "ccl_nonus_file": 2,
                    "ccl_nonus_document_summary": "Court order setting the date for the first hearing (unofficial English translation)",
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
        "type": "case",
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
                    "ccl_file": 3,
                    "ccl_document_headline": "Document memorandum",
                    "ccl_document_summary": "",
                    "ccl_outcome": "Memorandum of law filed in support of verified petition.",
                },
                {
                    "ccl_document_type": "outcome",
                    "ccl_filing_date": "20250122",
                    "ccl_file": 4,
                    "ccl_document_headline": "Lawsuit Alleged that New York Renewal of Power Plant Air Permit Violated State Climate Law",
                    "ccl_document_summary": "Summary of the lawsuit that alleged that the New York State Department of Environmental Conservation violated the state's climate law by renewing a power plant air permit.",
                    "ccl_outcome": "Memorandum of law filed in support of verified petition.",
                },
            ],
        },
    }


@pytest.fixture
def mock_pdf_urls():
    return {
        1: "https://energy/case-document.pdf",
        2: "https://adaptation/case-document.pdf",
        3: "https://lawsuit/case-document.pdf",
        4: "https://petition/case-document.pdf",
    }
