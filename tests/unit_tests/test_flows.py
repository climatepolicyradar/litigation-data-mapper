from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from prefect.testing.utilities import prefect_test_harness

from litigation_data_mapper.extract_concepts import Concept, ConceptType
from litigation_data_mapper.flows import sync_concepts_to_s3, sync_wordpress_to_s3
from litigation_data_mapper.wordpress_data import endpoints


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


def test_sync_concepts_to_s3(mock_s3_client):
    mock_s3_client.create_bucket(
        Bucket="cpr-cache",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )
    test_concepts = {
        1: Concept(
            internal_id=2,
            id="Brazil",
            type=ConceptType.LegalEntity,
            preferred_label="Brazil",
            relation="jurisdiction",
            subconcept_of_labels=[],
        ),
        2: Concept(
            internal_id=3,
            id="Sao Paulo",
            type=ConceptType.LegalEntity,
            preferred_label="Sao Paulo",
            relation="jurisdiction",
            subconcept_of_labels=["Brazil"],
        ),
    }

    # Ensure files are not there
    with pytest.raises(ClientError):
        mock_s3_client.head_object(
            Bucket="cpr-cache", Key="litigation/concepts/legal_entity__Brazil.json"
        )

    # Upload, now they should be there
    sync_concepts_to_s3(test_concepts)

    # Upload, now they should be there
    assert mock_s3_client.head_object(
        Bucket="cpr-cache", Key="litigation/concepts/legal_entity__Brazil.json"
    )

    # resyncing should have emptied the bucket
    sync_concepts_to_s3({})
    with pytest.raises(ClientError):
        mock_s3_client.head_object(
            Bucket="cpr-cache", Key="litigation/concepts/legal_entity__Brazil.json"
        )


@pytest.mark.parametrize(
    "endpoint",
    endpoints,
)
@patch("litigation_data_mapper.flows.fetch_word_press_data", return_value=[1, 2, 3])
def test_sync_wordpress_to_s3(mock_fetch_word_press_data, mock_s3_client, endpoint):
    mock_s3_client.create_bucket(
        Bucket="cpr-cache",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )

    sync_wordpress_to_s3()

    # Upload, now they should be there
    assert mock_s3_client.head_object(
        Bucket="cpr-cache", Key=f"litigation/wordpress/{endpoint}.json"
    )
