import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_server_metadata_matches_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    server = json.loads((ROOT / "server.json").read_text())
    project = pyproject["project"]
    package = server["packages"][0]

    assert server["version"] == project["version"]
    assert package["identifier"] == project["name"]
    assert package["version"] == project["version"]
    assert package["registryType"] == "pypi"


def test_agent_discovery_files_exist():
    assert (ROOT / "llms.txt").is_file()
    assert (ROOT / "examples" / "hermes.yaml").is_file()
    assert (ROOT / "examples" / "claude-desktop.json").is_file()
