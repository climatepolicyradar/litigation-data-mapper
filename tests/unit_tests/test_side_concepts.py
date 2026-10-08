from litigation_data_mapper.extract_concepts import transform_wordpress_concepts_data
from litigation_data_mapper.parsers.family import get_concepts

# Shapes from Sabin case 134252 and its plaintiff / defendant terms.
DEFENDANT_TERMS = [
    {"id": 3063, "name": "Governments", "parent": 0},
    {"id": 3136, "name": "National Governments", "parent": 3063},
]
PLAINTIFF_TERMS = [
    {"id": 3074, "name": "NGOs", "parent": 0},
    {"id": 3113, "name": "National NGOs", "parent": 3074},
]


def _concepts():
    concepts = transform_wordpress_concepts_data(
        data=DEFENDANT_TERMS, taxonomy="defendant"
    )
    concepts.update(
        transform_wordpress_concepts_data(data=PLAINTIFF_TERMS, taxonomy="plaintiff")
    )
    return concepts


def _concept(label, relation, parents):
    return {
        "id": label,
        "ids": [],
        "type": "legal_entity",
        "preferred_label": label,
        "relation": relation,
        "subconcept_of_labels": parents,
    }


def test_case_sides_become_legal_concepts():
    case = {
        "id": 134252,
        "type": "case",
        "plaintiff": [3113, 3074],
        "defendant": [3063, 3136],
    }
    concepts = get_concepts(case, _concepts())
    side_concepts = [c for c in concepts if c["relation"] in ("plaintiff", "defendant")]
    assert sorted(side_concepts, key=lambda c: (c["relation"], c["id"])) == [
        _concept("Governments", "defendant", []),
        _concept("National Governments", "defendant", ["Governments"]),
        _concept("NGOs", "plaintiff", []),
        _concept("National NGOs", "plaintiff", ["NGOs"]),
    ]


def test_case_without_sides_gets_no_side_concepts():
    concepts = get_concepts({"id": 1, "type": "non_us_case"}, _concepts())
    assert concepts == []
