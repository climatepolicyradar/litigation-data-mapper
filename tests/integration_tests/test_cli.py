import pytest
from click.testing import CliRunner

from litigation_data_mapper.cli import entrypoint


@pytest.mark.skip()
def test_entrypoint_fail():
    runner = CliRunner()
    result = runner.invoke(entrypoint)
    assert result.exit_code == 1
    assert "Failed to map Litigation data to expected JSON" in result.output.strip()


@pytest.mark.skip()
def test_entrypoint_success():
    runner = CliRunner()
    result = runner.invoke(entrypoint)
    assert result.exit_code == 0
    assert all(
        item in result.output.strip()
        for item in [
            "Finished mapping Litigation data",
            "Finished dumping mapped Litigation data",
        ]
    )
