from click.testing import CliRunner

from litigation_data_mapper.cli import entrypoint


def test_version():
    runner = CliRunner()
    result = runner.invoke(entrypoint, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.strip()


def test_help():
    runner = CliRunner()
    result = runner.invoke(entrypoint, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output.strip()
    assert "Options" in result.output.strip()
