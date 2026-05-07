# Contributing

Contributions are welcome around search-term classification, negative-keyword planning, dry-run safety, MCP ergonomics, tests and docs.

## Local development

```bash
pip install -e ".[dev]"
pytest
python -m build
twine check dist/*
```

## Design rules

- Keep live mutation out of the default path.
- Never commit Google Ads credentials, OAuth tokens, customer IDs, real search-term exports or private campaign data.
- Protect buyer/conversion intent in negative-keyword logic.
- Keep PyPI publishing on Trusted Publishing; do not add long-lived PyPI tokens.

## Pull request checklist

- `pytest` passes.
- Package builds successfully when packaging metadata changes.
- README, `llms.txt` and examples are updated when commands or tools change.
