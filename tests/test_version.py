import tomllib
from pathlib import Path

from typer.testing import CliRunner

from fcm_console_receiver.show_notifications import app


def test_version_matches():
    # when
    result = CliRunner().invoke(app, ["--version"])
    # then
    print(result.output)
    assert result.exit_code == 0
    assert get_version() in result.stdout


def get_version():
    path = Path(__file__).parent.parent / "pyproject.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]
