from unittest.mock import patch

import pytest
import requests
from prefect.testing.utilities import prefect_test_harness

from litigation_data_mapper.datatypes import Failure
from litigation_data_mapper.extract_concepts import (
    fetch_individual_concept,
    transform_wordpress_concepts_data,
)
from litigation_data_mapper.flows import report_concept_fetch_failures
from litigation_data_mapper.parsers.family import get_concepts


@pytest.fixture(autouse=True, scope="module")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


def test_records_a_failure_when_a_missing_concept_cannot_be_refetched():
    concepts = transform_wordpress_concepts_data(
        data=[{"id": 1, "name": "Argentina", "parent": 0}], taxonomy="jurisdiction"
    )
    case = {"id": 100, "type": "non_us_case", "jurisdiction": [1, 2]}
    failures: list[Failure] = []

    with patch(
        "litigation_data_mapper.parsers.family.fetch_individual_concept",
        side_effect=requests.HTTPError("404 Client Error: Not Found for url: x"),
    ):
        mapped = get_concepts(case, concepts, failures)

    assert [c["id"] for c in mapped] == ["Argentina"]
    assert failures == [
        Failure(
            id=2,
            type="jurisdiction",
            reason=(
                "Could not fetch jurisdiction concept 2 referenced by non_us_case "
                "100: 404 Client Error: Not Found for url: x"
            ),
        )
    ]


def test_records_a_failure_when_refetch_returns_nothing():
    case = {"id": 100, "type": "case_bundle", "entity": [5]}
    failures: list[Failure] = []

    with patch(
        "litigation_data_mapper.parsers.family.fetch_individual_concept",
        return_value=None,
    ):
        get_concepts(case, {}, failures)

    assert len(failures) == 1
    assert failures[0].reason.endswith("WordPress returned no data")


@patch("litigation_data_mapper.extract_concepts.fetch_individual_wordpress_resource")
def test_refetched_concept_gets_its_parent_with_html_unescaped(mock_fetch):
    mock_fetch.side_effect = [
        {"id": 2, "name": "Court of Azul", "parent": 1},
        {"id": 1, "name": "Bosnia &amp; Herzegovina", "parent": 0},
    ]

    concept = fetch_individual_concept(2, "jurisdiction", {})

    assert concept is not None
    assert concept.subconcept_of_labels == ["Bosnia & Herzegovina"]


@patch("litigation_data_mapper.extract_concepts.fetch_individual_wordpress_resource")
def test_refetch_raises_when_a_parent_cannot_be_fetched(mock_fetch):
    mock_fetch.side_effect = [
        {"id": 2, "name": "Court of Azul", "parent": 1},
        requests.HTTPError("404"),
    ]

    with pytest.raises(requests.HTTPError):
        fetch_individual_concept(2, "jurisdiction", {})


@patch("litigation_data_mapper.flows.SlackNotify.send_text")
@patch("litigation_data_mapper.flows.create_table_artifact")
def test_reports_and_alerts_on_concept_fetch_failures(mock_artifact, mock_send):
    mock_artifact.return_value = "artifact-uuid"
    concept_failures = [
        Failure(id=2, type="jurisdiction", reason="concept 2 a"),
        Failure(id=2, type="jurisdiction", reason="concept 2 b"),
        Failure(id=3, type="principal_law", reason="concept 3"),
    ]

    report_concept_fetch_failures(concept_failures)

    table = mock_artifact.call_args.kwargs["table"]
    assert mock_artifact.call_args.kwargs["key"] == "concept-fetch-failures"
    assert [row["reason"] for row in table] == [
        "concept 2 a",
        "concept 2 b",
        "concept 3",
    ]
    message = mock_send.call_args.args[0]
    assert message.startswith("⚠️ 2 litigation concept(s) could not be fetched")
    assert "/artifacts/artifact/artifact-uuid|View the failures>" in message


@patch("litigation_data_mapper.flows.SlackNotify.send_text")
@patch("litigation_data_mapper.flows.create_table_artifact")
def test_does_not_alert_when_every_concept_was_fetched(mock_artifact, mock_send):
    report_concept_fetch_failures([])

    mock_artifact.assert_not_called()
    mock_send.assert_not_called()
