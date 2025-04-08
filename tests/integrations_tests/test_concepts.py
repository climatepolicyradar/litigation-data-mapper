from litigation_data_mapper.extract_concepts import Concept, ConceptType
from litigation_data_mapper.parsers.family import get_concepts


def test_get_concepts():
    test_case = {
        "id": "1",
        "ids": [],
        "title": "Public Ministry of the State of Sao Paulo v. KLM",
        "jurisdiction": [1, 2, 3],
        "principal_law": [4, 5, 6],
        "case_category": [7, 8, 9, 10, 11, 12],
    }
    test_concepts = {
        1: Concept(
            internal_id=1,
            id="Sao Paulo State Court",
            type=ConceptType.LegalEntity,
            preferred_label="Sao Paulo State Court",
            relation="jurisdiction",
            subconcept_of_labels=["Sao Paulo"],
        ),
        2: Concept(
            internal_id=2,
            id="Brazil",
            type=ConceptType.LegalEntity,
            preferred_label="Brazil",
            relation="jurisdiction",
            subconcept_of_labels=[],
        ),
        3: Concept(
            internal_id=3,
            id="Sao Paulo",
            type=ConceptType.LegalEntity,
            preferred_label="Sao Paulo",
            relation="jurisdiction",
            subconcept_of_labels=["Brazil"],
        ),
        4: Concept(
            internal_id=4,
            id="Brazil",
            type=ConceptType.Law,
            preferred_label="Brazil",
            relation="principal_law",
            subconcept_of_labels=[],
        ),
        5: Concept(
            internal_id=5,
            id="National Climate Change Policy (Law No. 12187 of 2009)",
            type=ConceptType.Law,
            preferred_label="National Climate Change Policy (Law No. 12187 of 2009)",
            relation="principal_law",
            subconcept_of_labels=["Brazil"],
        ),
        6: Concept(
            internal_id=6,
            id="National Environmental Policy Act (Law No. 6.938 of 1981)",
            type=ConceptType.Law,
            preferred_label="National Environmental Policy Act (Law No. 6.938 of 1981)",
            relation="principal_law",
            subconcept_of_labels=["Brazil"],
        ),
        7: Concept(
            internal_id=7,
            id="Constitution of 1988",
            type=ConceptType.Law,
            preferred_label="Constitution of 1988",
            relation="principal_law",
            subconcept_of_labels=["Brazil"],
        ),
        8: Concept(
            internal_id=8,
            id="Climate damage",
            type=ConceptType.LegalCategory,
            preferred_label="Climate damage",
            relation="category",
            subconcept_of_labels=["Corporations"],
        ),
        9: Concept(
            internal_id=9,
            id="Corporations",
            type=ConceptType.LegalCategory,
            preferred_label="Corporations",
            relation="category",
            subconcept_of_labels=["Suits against corporations, individuals"],
        ),
        10: Concept(
            internal_id=10,
            id="Suits against corporations, individuals",
            type=ConceptType.LegalCategory,
            preferred_label="Suits against corporations, individuals",
            relation="category",
            subconcept_of_labels=[],
        ),
        11: Concept(
            internal_id=11,
            id="GHG emissions reduction",
            type=ConceptType.LegalCategory,
            preferred_label="GHG emissions reduction",
            relation="category",
            subconcept_of_labels=["Corporations"],
        ),
    }
    expected_parsed_concepts: list[dict[str, object]] = [
        {
            "id": "Sao Paulo State Court",
            "ids": [],
            "type": "legal_entity",
            "preferred_label": "Sao Paulo State Court",
            "relation": "jurisdiction",
            "subconcept_of_labels": ["Sao Paulo"],
        },
        {
            "id": "Brazil",
            "ids": [],
            "type": "legal_entity",
            "preferred_label": "Brazil",
            "relation": "jurisdiction",
            "subconcept_of_labels": [],
        },
        {
            "id": "Sao Paulo",
            "ids": [],
            "type": "legal_entity",
            "preferred_label": "Sao Paulo",
            "relation": "jurisdiction",
            "subconcept_of_labels": ["Brazil"],
        },
        {
            "id": "Brazil",
            "ids": [],
            "type": "law",
            "preferred_label": "Brazil",
            "relation": "principal_law",
            "subconcept_of_labels": [],
        },
        {
            "id": "National Climate Change Policy (Law No. 12187 of 2009)",
            "ids": [],
            "type": "law",
            "preferred_label": "National Climate Change Policy (Law No. 12187 of 2009)",
            "relation": "principal_law",
            "subconcept_of_labels": ["Brazil"],
        },
        {
            "id": "National Environmental Policy Act (Law No. 6.938 of 1981)",
            "ids": [],
            "type": "law",
            "preferred_label": "National Environmental Policy Act (Law No. 6.938 of 1981)",
            "relation": "principal_law",
            "subconcept_of_labels": ["Brazil"],
        },
        {
            "id": "Constitution of 1988",
            "ids": [],
            "type": "law",
            "preferred_label": "Constitution of 1988",
            "relation": "principal_law",
            "subconcept_of_labels": ["Brazil"],
        },
        {
            "id": "Climate damage",
            "ids": [],
            "type": "legal_category",
            "preferred_label": "Climate damage",
            "relation": "category",
            "subconcept_of_labels": ["Corporations"],
        },
        {
            "id": "Corporations",
            "ids": [],
            "type": "legal_category",
            "preferred_label": "Corporations",
            "relation": "category",
            "subconcept_of_labels": ["Suits against corporations, individuals"],
        },
        {
            "id": "Suits against corporations, individuals",
            "ids": [],
            "type": "legal_category",
            "preferred_label": "Suits against corporations, individuals",
            "relation": "category",
            "subconcept_of_labels": [],
        },
        {
            "id": "GHG emissions reduction",
            "ids": [],
            "type": "legal_category",
            "preferred_label": "GHG emissions reduction",
            "relation": "category",
            "subconcept_of_labels": ["Corporations"],
        },
    ]

    concepts = get_concepts(test_case, test_concepts)
    # Sort by id and relation to make comparison order-independent
    assert sorted(concepts, key=lambda x: (str(x["id"]), str(x["relation"]))) == sorted(
        expected_parsed_concepts, key=lambda x: (str(x["id"]), str(x["relation"]))
    )
