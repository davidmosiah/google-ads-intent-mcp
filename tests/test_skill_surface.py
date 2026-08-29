from pathlib import Path
import json
import re

from google_ads_intent_mcp.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_skill_document_is_present_and_safe():
    skill = ROOT / "skill" / "SKILL.md"
    assert skill.is_file()
    text = skill.read_text(encoding="utf-8")
    assert "google_ads_connection_status" in text
    assert re.search(r"[A-Z0-9_]*ALLOW_MUTATIONS\s*=\s*true", text) is None


def test_cli_call_connection_status(capsys):
    code = main(["call", "google_ads_connection_status", "--json", "{}"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, dict)


def test_cli_call_unknown_tool(capsys):
    code = main(["call", "not_a_real_tool", "--json", "{}"])
    assert code == 1
