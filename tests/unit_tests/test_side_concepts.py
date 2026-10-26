from litigation_data_mapper.extract_concepts import transform_wordpress_concepts_data
from litigation_data_mapper.parsers.family import get_concepts


def test_maps_case_sides_to_concepts():
    concepts = transform_wordpress_concepts_data(
        data=[
            {"id": 3063, "name": "Governments", "parent": 0},
            {"id": 3136, "name": "National Governments", "parent": 3063},
        ],
        taxonomy="defendant",
    ) | transform_wordpress_concepts_data(
        data=[
            {"id": 3074, "name": "NGOs", "parent": 0},
            {"id": 3113, "name": "National NGOs", "parent": 3074},
        ],
        taxonomy="plaintiff",
    )
    case = {"id": 134252, "plaintiff": [3113, 3074], "defendant": [3063, 3136]}

    mapped = get_concepts(case, concepts)

    assert sorted(
        (c["relation"], c["id"], c["type"], c["subconcept_of_labels"]) for c in mapped
    ) == [
        ("defendant", "Governments", "side", []),
        ("defendant", "National Governments", "side", ["Governments"]),
        ("plaintiff", "NGOs", "side", []),
        ("plaintiff", "National NGOs", "side", ["NGOs"]),
    ]
