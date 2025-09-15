from unittest.mock import patch

from litigation_data_mapper.extract_concepts import (
    US_ROOT_JURISDICTION_ID,
    US_ROOT_PRINCIPAL_LAW_ID,
    Concept,
    ConceptType,
    extract_concepts,
)


@patch("litigation_data_mapper.extract_concepts.fetch_word_press_data")
def test_extract_concepts_adds_synthetic_us_principal_law_and_jurisdiction_concepts(
    mock_fetch_word_press_data,
):
    mock_fetch_word_press_data.return_value = []

    concepts = extract_concepts()

    assert concepts == {
        -1: Concept(
            internal_id=US_ROOT_PRINCIPAL_LAW_ID,
            id="United States",
            type=ConceptType.Law,
            preferred_label="United States",
            subconcept_of_labels=[],
            relation="principal_law",
        ),
        -2: Concept(
            internal_id=US_ROOT_JURISDICTION_ID,
            id="United States",
            type=ConceptType.LegalEntity,
            preferred_label="United States",
            subconcept_of_labels=[],
            relation="jurisdiction",
        ),
    }
