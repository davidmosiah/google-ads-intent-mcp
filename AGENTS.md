# Agent Development Notes

## Scope

This repo is a Python CLI plus optional MCP server for dry-run Google Ads search-term intent analysis and negative-keyword planning.

## Commands

- Install dev deps: `pip install -e ".[dev]"`
- Test: `pytest`
- Build package: `python -m build`
- Check dist: `twine check dist/*`
- CLI smoke: `google-ads-intent doctor`

## Rules

- Never commit Google Ads credentials, OAuth tokens, customer IDs, real search-term exports, or private campaign data.
- Keep live mutation out of the default path; v0.1 should remain dry-run first.
- Keep buyer/conversion intent protected in negative-keyword logic.
- Keep PyPI publishing on Trusted Publishing; do not add long-lived PyPI tokens.
