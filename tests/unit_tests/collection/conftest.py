import pytest

from litigation_data_mapper.datatypes import LitigationContext


@pytest.fixture()
def mock_context():
    yield LitigationContext(
        failures=[],
        debug=False,
        get_all_data=True,
        case_bundles={},
        skipped_documents=[],
        skipped_families=[],
    )


@pytest.fixture()
def mock_collection_data():
    yield [
        {
            "id": 1,
            "date": "2021-01-01T00:00:00",
            "modified_gmt": "2025-02-01T12:00:00",
            "type": "case_bundle",
            "title": {
                "rendered": "Center for Biological Diversity v. Wildlife Service"
            },
            "slug": "center-biological-diversity-v-wildlife-service",
            "status": "publish",
            "case_category": [422, 423],
            "principal_law": [4, 42],
            "acf": {
                "ccl_cases": [1],
                "ccl_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
                "ccl_case_categories": [422, 423],
                "ccl_principal_law": [4, 42],
            },
            "yoast_head": "",
        },
        {
            "id": 2,
            "date": "2021-01-01T00:00:00",
            "modified_gmt": "2025-02-01T12:00:00",
            "type": "case_bundle",
            "title": {"rendered": "Matter of project approvals approved by DOE"},
            "slug": "center-biological-diversity-v-wildlife-service",
            "status": "publish",
            "case_category": [10, 11],
            "principal_law": [1, 2],
            "acf": {
                "ccl_cases": [1],
                "ccl_core_object": "Challenge to to project approvals issued by Department of Environmental Protection.",
                "ccl_case_categories": [10, 11],
                "ccl_principal_law": [1, 2],
            },
            "yoast_head": "",
        },
    ]


@pytest.fixture
def parsed_collection_data():
    yield [
        {
            "import_id": "Sabin.collection.1.0",
            "description": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "title": "Center for Biological Diversity v. Wildlife Service",
            "metadata": {"id": ["1"]},
        },
        {
            "import_id": "Sabin.collection.2.0",
            "description": "Challenge to to project approvals issued by Department of Environmental Protection.",
            "title": "Matter of project approvals approved by DOE",
            "metadata": {"id": ["2"]},
        },
    ]
