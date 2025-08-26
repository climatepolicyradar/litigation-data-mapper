import html
from enum import Enum
from typing import Any, Literal, NamedTuple, cast

import click

from litigation_data_mapper.wordpress import (
    fetch_individual_wordpress_resource,
    fetch_word_press_data,
)

US_ROOT_PRINCIPAL_LAW_ID = -1  # Internal ID for the synthetic US principal law concept
US_ROOT_JURISDICTION_ID = -2  # Internal ID for the synthetic US jurisdiction concept

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
        id=html.unescape(wordpress_data["name"]),
        type=taxonomy_to_concept_type[taxonomy],
        preferred_label=html.unescape(wordpress_data["name"]),
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


def add_synthetic_us_principal_law_concept(
    concepts: dict[int, Concept],
) -> dict[int, Concept]:
    """
    Adds a synthetic concept representing the US principal law to the concepts dictionary.

    This synthetic concept is required because the US principal law is not included
    in the original WordPress data source but is needed for internal processing.

    :param dict[int, Concept] concepts: A dictionary mapping internal concept IDs to Concept objects.

    :return dict[int, Concept]: The updated concepts dictionary with the synthetic US principal law concept added.
    """
    us_principal_law = Concept(
        internal_id=US_ROOT_PRINCIPAL_LAW_ID,
        id="United States of America",
        type=ConceptType.Law,
        preferred_label="United States of America",
        subconcept_of_labels=[],
        relation="principal_law",
    )

    concepts[us_principal_law.internal_id] = us_principal_law

    return concepts


def add_synthetic_us_jurisdiction_concept(
    concepts: dict[int, Concept],
) -> dict[int, Concept]:
    """
    Adds a synthetic concept representing the US jurisdiction to the concepts dictionary.

    This synthetic concept is required because the US jurisdiction is not included
    in the original WordPress data source but is needed for internal processing.

    :param dict[int, Concept] concepts: A dictionary mapping internal concept IDs to Concept objects.

    :return dict[int, Concept]: The updated concepts dictionary with the synthetic US jurisdiction concept added.
    """
    us_jurisdiction = Concept(
        internal_id=US_ROOT_JURISDICTION_ID,
        id="United States of America",
        type=ConceptType.LegalEntity,
        preferred_label="United States of America",
        subconcept_of_labels=[],
        relation="jurisdiction",
    )

    concepts[us_jurisdiction.internal_id] = us_jurisdiction

    return concepts


def extract_concepts() -> dict[int, Concept]:
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
        concepts[concept_with_parent_id.internal_id] = (
            map_concept_with_parent_id_to_concept(
                concept_with_parent_id, concepts_with_parent_id
            )
        )

    concepts_with_synthetic_us_principal_law = add_synthetic_us_principal_law_concept(
        concepts
    )

    concepts_with_synthetic_us_principal_law_and_jurisdiction = (
        add_synthetic_us_jurisdiction_concept(concepts_with_synthetic_us_principal_law)
    )

    return concepts_with_synthetic_us_principal_law_and_jurisdiction


def fetch_individual_concept(
    concept_id: int,
    taxonomy: str,
    concepts: dict[int, Concept],
) -> Concept | None:
    try:
        data = fetch_individual_wordpress_resource(
            f"{wordpress_base_url}/{taxonomy}/{concept_id}"
        )

        if not data:
            return None

        click.echo(f"🔍 Found concept {concept_id} in taxonomy {taxonomy}")

        concept_with_parent_id = map_wordpress_data_to_concept_with_parent_id(
            data, taxonomy
        )

        parent_id = concept_with_parent_id.subconcept_of_id
        parent_labels = []

        if parent_id:
            parent_concept = concepts.get(parent_id)
            if parent_concept:
                parent_labels = [parent_concept.preferred_label]
            else:
                parent_data = fetch_individual_wordpress_resource(
                    f"{wordpress_base_url}/{taxonomy}/{parent_id}"
                )
                if parent_data:
                    parent_labels = [parent_data["name"]]

        concept = Concept(
            internal_id=concept_with_parent_id.internal_id,
            id=concept_with_parent_id.id,
            type=concept_with_parent_id.type,
            preferred_label=concept_with_parent_id.preferred_label,
            subconcept_of_labels=parent_labels,
            relation=concept_with_parent_id.relation,
        )

        return concept

    except Exception as e:
        click.echo(
            f"❌ Error fetching concept {concept_id} from taxonomy {taxonomy}: {str(e)}"
        )
        return None
