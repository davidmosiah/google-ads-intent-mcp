# Google Ads Intent MCP

[![CI](https://github.com/davidmosiah/google-ads-intent-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/davidmosiah/google-ads-intent-mcp/actions/workflows/ci.yml)

Dry-run-first Google Ads search-term intent analyzer for agents. It helps Codex, Claude, Cursor, Hermes, OpenClaw and other MCP clients classify search terms, protect buyer intent and draft negative-keyword plans from CSV exports before any live account change.

## Why It Exists

Google Ads cleanup is risky when agents act directly on accounts. This package makes the safe path the default:

- analyze exported search-term CSVs locally
- classify waste, buyer, research and competitor intent
- draft negative-keyword plans without applying them
- expose `manifest`, `connection_status` and `privacy_audit` before action tools
- keep live mutation out of v0.1

## Install

```bash
pipx install "git+https://github.com/davidmosiah/google-ads-intent-mcp.git"
```

With MCP support:

```bash
pipx install "git+https://github.com/davidmosiah/google-ads-intent-mcp.git#egg=google-ads-intent-mcp[mcp]"
```

PyPI artifacts are build-ready. Registry publish is pending a PyPI API token or trusted-publishing setup.

## CLI

```bash
google-ads-intent manifest --client codex
google-ads-intent doctor
google-ads-intent privacy-audit
google-ads-intent classify "free robux generator no verification"
google-ads-intent analyze-csv --csv examples/search_terms.csv
google-ads-intent plan-negatives --csv examples/search_terms.csv
```

## MCP

```bash
google-ads-intent-mcp
```

Hermes-style config:

```yaml
mcp_servers:
  google_ads_intent:
    command: google-ads-intent-mcp
    args: []
    sampling:
      enabled: false
```

Recommended first calls:

1. `google_ads_connection_status`
2. `google_ads_privacy_audit`
3. `google_ads_analyze_search_terms`
4. `google_ads_build_negative_plan`

## CSV Format

The parser accepts common exported columns such as:

- `search_term`, `Search term`, `Query`
- `cost`, `Cost`, `cost_micros`
- `clicks`, `Clicks`
- `conversions`, `Conversions`, `Conv.`
- `impressions`, `Impr.`, `Impressions`

## Safety Model

- CSV analysis is local.
- Negative plans are dry-run only.
- Buyer/conversion terms are protected from automatic exclusion.
- OAuth tokens, developer tokens and account identifiers should stay in local environment/config files.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m compileall -q src
```
