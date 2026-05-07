<!-- delx header v2 -->
<h1 align="center">Google Ads Intent MCP</h1>

<div align="center">
  <img src="assets/banner.png" alt="Google Ads Intent MCP" width="85%" />
</div>

<h3 align="center">
  Dry-run-first Google Ads search-term intent analyzer + negative-keyword MCP for agents.<br>Look at search terms safely before spending budget.
</h3>

<p align="center">
  <a href="https://www.npmjs.com/package/google-ads-intent-mcp"><img src="https://img.shields.io/npm/v/google-ads-intent-mcp?style=for-the-badge&labelColor=0F172A&color=10B981&logo=npm&logoColor=white" alt="npm version" /></a>
  <a href="https://www.npmjs.com/package/google-ads-intent-mcp"><img src="https://img.shields.io/npm/dm/google-ads-intent-mcp?style=for-the-badge&labelColor=0F172A&color=0EA5A3&logo=npm&logoColor=white" alt="npm downloads" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-22C55E?style=for-the-badge&labelColor=0F172A" alt="License MIT" /></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/BUILT_FOR-MCP-7C3AED?style=for-the-badge&labelColor=0F172A" alt="Built for MCP" /></a>
</p>

<p align="center">
  <a href="https://github.com/davidmosiah/google-ads-intent-mcp/stargazers"><img src="https://img.shields.io/github/stars/davidmosiah/google-ads-intent-mcp?style=for-the-badge&labelColor=0F172A&color=FBBF24&logo=github" alt="GitHub stars" /></a>
  <a href="https://github.com/davidmosiah/google-ads-intent-mcp/actions/workflows/ci.yml"><img src="https://github.com/davidmosiah/google-ads-intent-mcp/actions/workflows/ci.yml/badge.svg" alt="CI status" /></a>
  <a href="https://github.com/davidmosiah"><img src="https://img.shields.io/badge/PART_OF-Delx_Agent_Stack-0EA5A3?style=for-the-badge&labelColor=0F172A" alt="Part of the Delx agent stack" /></a>
  <a href="https://github.com/davidmosiah/google-ads-intent-mcp"><img src="https://img.shields.io/badge/CATEGORY-Reach-4285F4?style=for-the-badge&labelColor=0F172A" alt="Category" /></a>
</p>

> ⭐ **If this agent-first tool helps your workflow, please star the repo.** Stars make this tooling easier for other builders to discover and help Delx keep shipping open infrastructure.<br>
> 🧱 Part of the [Delx agent stack](https://github.com/davidmosiah) &mdash; 15 open-source MCP servers across **body, reach and coordination**.

---

<!-- /delx header v2 -->

Dry-run-first Google Ads search-term intent analyzer for agents. It helps Codex, Claude, Cursor, Hermes, OpenClaw and other MCP clients classify search terms, protect buyer intent and draft negative-keyword plans from CSV exports before any live account change.

Use it when an agent needs to reduce wasted spend without accidentally excluding buyer-intent queries.

## Why It Exists

Google Ads cleanup is risky when agents act directly on accounts. This package makes the safe path the default:

- analyze exported search-term CSVs locally
- classify waste, buyer, research and competitor intent
- draft negative-keyword plans without applying them
- expose `manifest`, `connection_status` and `privacy_audit` before action tools
- keep live mutation out of v0.1

## Install

```bash
pipx install google-ads-intent-mcp
```

With MCP support:

```bash
pipx install "google-ads-intent-mcp[mcp]"
```

Published on PyPI: [`google-ads-intent-mcp`](https://pypi.org/project/google-ads-intent-mcp/). Release automation uses PyPI Trusted Publishing, so GitHub Actions can publish future versions without long-lived PyPI tokens. See [docs/pypi-publishing.md](docs/pypi-publishing.md).

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

## Agent Surfaces

| Tool | Purpose |
|---|---|
| `google_ads_agent_manifest` | Install/runtime guidance for agent clients |
| `google_ads_connection_status` | CSV/API readiness without credentials |
| `google_ads_privacy_audit` | Dry-run, account and export boundaries |
| `google_ads_classify_search_term` | Single-query intent classification |
| `google_ads_analyze_search_terms` | Batch CSV-style analysis |
| `google_ads_build_negative_plan` | Dry-run negative keyword plan |

## Copy-Paste Agent Prompt

```text
Use google-ads-intent-mcp. First call google_ads_connection_status and google_ads_privacy_audit.
Analyze the search terms, protect buyer/conversion queries, and return a dry-run negative plan only.
```

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
