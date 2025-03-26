from enum import Enum
from pathlib import Path
from typing import Any, Literal, NamedTuple, cast

from litigation_data_mapper.wordpress import fetch_word_press_data

wordpress_base_url = "https://climatecasechart.com/wp-json/wp/v2"
taxonomies = [
    # USA
    "case_category",
    "entity",  # This is like a jurisdiction but for USA
    "principal_law",
    # Non-USA
    "jurisdiction",
    "non_us_principal_law",
    "non_us_case_category",
]


class ConceptType(str, Enum):
    Law = "law"
    LegalCategory = "legal_category"
    Country = "country"
    CountrySubdivision = "country_subdivision"
    LegalEntity = "legal_entity"


taxonomy_to_concept_type = {
    "case_category": ConceptType.LegalCategory,
    "entity": ConceptType.LegalEntity,
    "principal_law": ConceptType.Law,
    "jurisdiction": ConceptType.LegalEntity,
    "non_us_principal_law": ConceptType.Law,
    "non_us_case_category": ConceptType.LegalCategory,
}

Relation = Literal["author", "jurisdiction", "category", "principal_law"]

taxonomies_to_relation: dict[str, Relation] = {
    "case_category": "category",
    "entity": "jurisdiction",
    "principal_law": "principal_law",
    "jurisdiction": "jurisdiction",
    "non_us_principal_law": "principal_law",
    "non_us_case_category": "category",
}


class ConceptWithParentId(NamedTuple):
    """
    This is a concept model from the knowledge graph project.
    @see: https://github.com/climatepolicyradar/knowledge-graph/blob/main/src/concept.py
    """

    internal_id: int
    id: str
    type: ConceptType
    preferred_label: str
    ids: list[str] = []
    subconcept_of_id: int | None = None
    relation: Relation | None = None


class Concept(NamedTuple):
    """
    This is a concept model from the knowledge graph project.
    @see: https://github.com/climatepolicyradar/knowledge-graph/blob/main/src/concept.py
    """

    internal_id: int
    id: str
    type: ConceptType
    preferred_label: str
    ids: list[str] = []
    subconcept_of_labels: list[str] = []
    relation: Relation | None = None


def map_wordpress_data_to_concept_with_parent_id(
    wordpress_data: dict[str, Any],
    taxonomy: str,
) -> ConceptWithParentId:
    parent_id_with_0: int | None = cast(int, wordpress_data["parent"])
    parent_id: int | None = None if parent_id_with_0 == 0 else parent_id_with_0
    return ConceptWithParentId(
        internal_id=wordpress_data["id"],
        id=wordpress_data["name"],
        type=taxonomy_to_concept_type[taxonomy],
        preferred_label=wordpress_data["name"],
        subconcept_of_id=parent_id,
        relation=taxonomies_to_relation.get(taxonomy),
    )


def map_concept_with_parent_id_to_concept(
    concept_with_parent_id: ConceptWithParentId,
    concepts_with_parent_id: dict[int, ConceptWithParentId],
) -> Concept:
    parent_id = concept_with_parent_id.subconcept_of_id
    parent_concept = concepts_with_parent_id.get(parent_id, None) if parent_id else None

    if parent_concept:
        parent_label = parent_concept.preferred_label
        return Concept(
            internal_id=concept_with_parent_id.internal_id,
            id=concept_with_parent_id.id,
            type=concept_with_parent_id.type,
            preferred_label=concept_with_parent_id.preferred_label,
            subconcept_of_labels=[parent_label],
            relation=concept_with_parent_id.relation,
        )
    else:
        return Concept(
            internal_id=concept_with_parent_id.internal_id,
            id=concept_with_parent_id.id,
            type=concept_with_parent_id.type,
            preferred_label=concept_with_parent_id.preferred_label,
            subconcept_of_labels=[],
            relation=concept_with_parent_id.relation,
        )


def extract_concepts() -> dict[int, Concept]:
    dumps_directory = "dist/dumps"
    output_dir = Path(dumps_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in output_dir.glob("*"):
        file.unlink()

    concepts_with_parent_id: dict[int, ConceptWithParentId] = {}
    concepts: dict[int, Concept] = {}

    # create a lookup table of ConceptWithParentId
    for taxonomy in taxonomies:
        data = fetch_word_press_data(f"{wordpress_base_url}/{taxonomy}")
        for item in data:
            concept_with_parent_id: ConceptWithParentId = (
                map_wordpress_data_to_concept_with_parent_id(item, taxonomy)
            )
            concepts_with_parent_id[item["id"]] = concept_with_parent_id

    # generate a lookup table of Concept
    for _, concept_with_parent_id in concepts_with_parent_id.items():
        if concept_with_parent_id.subconcept_of_id:
            concepts[concept_with_parent_id.internal_id] = (
                map_concept_with_parent_id_to_concept(
                    concept_with_parent_id, concepts_with_parent_id
                )
            )

    return concepts
