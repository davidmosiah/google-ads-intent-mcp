"""Verify resources in the installed distribution, not the source tree."""
from importlib.metadata import distribution
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist = distribution("google-ads-intent-mcp")
for source, resource in (("skill/SKILL.md", "google_ads_intent_mcp/skill/SKILL.md"), ("MIGRATION.md", "google_ads_intent_mcp/MIGRATION.md")):
    files = {str(path): path for path in dist.files or []}
    assert resource in files, f"missing installed resource: {resource}"
    assert dist.locate_file(files[resource]).read_bytes() == (root / source).read_bytes(), resource
print("installed wheel resources match source")
