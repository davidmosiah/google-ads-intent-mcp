from __future__ import annotations

from collections.abc import Mapping

SUPPORTED_CLIENTS = ["generic", "claude", "codex", "cursor", "windsurf", "hermes", "openclaw"]


def _safe_client(client: str = "generic") -> str:
    return client if client in SUPPORTED_CLIENTS else "generic"


def _present(env: Mapping[str, str], key: str) -> bool:
    return bool(str(env.get(key, "")).strip())


def build_agent_manifest(client: str = "generic") -> dict:
    return {
        "project": "google-ads-intent-mcp",
        "mcp_name": "io.github.davidmosiah/google-ads-intent-mcp",
        "client": _safe_client(client),
        "default_mode": "dry_run",
        "package": {
            "pip": "pipx install google-ads-intent-mcp[mcp]",
            "cli": "google-ads-intent",
            "mcp": "google-ads-intent-mcp",
        },
        "supported_clients": SUPPORTED_CLIENTS,
        "standard_tools": [
            "google_ads_agent_manifest",
            "google_ads_connection_status",
            "google_ads_privacy_audit",
            "google_ads_classify_search_term",
            "google_ads_analyze_search_terms",
            "google_ads_build_negative_plan",
        ],
        "recommended_first_calls": ["google_ads_connection_status", "google_ads_privacy_audit"],
        "hermes": {
            "config_path": "~/.hermes/config.yaml",
            "tool_name_prefix": "mcp_google_ads_",
            "recommended_config": (
                "mcp_servers:\n"
                "  google_ads_intent:\n"
                "    command: google-ads-intent-mcp\n"
                "    args: []\n"
                "    sampling:\n"
                "      enabled: false"
            ),
        },
        "agent_rules": [
            "Analyze exported search-term CSVs before live Google Ads API work.",
            "Never apply negatives automatically; build a plan and ask for confirmation.",
            "Protect buyer-intent terms even when they have low clicks.",
            "Prioritize wasted cost, zero-conversion spend and obvious junk traffic.",
        ],
    }


def build_connection_status(env: Mapping[str, str] | None = None) -> dict:
    env = env or {}
    configured = {
        "developer_token": _present(env, "GOOGLE_ADS_DEVELOPER_TOKEN"),
        "customer_id": _present(env, "GOOGLE_ADS_CUSTOMER_ID"),
        "oauth_refresh": _present(env, "GOOGLE_ADS_REFRESH_TOKEN"),
        "oauth_client": _present(env, "GOOGLE_ADS_CLIENT_ID") and _present(env, "GOOGLE_ADS_CLIENT_SECRET"),
    }
    ready_live = all(configured.values()) and str(env.get("GOOGLE_ADS_DRY_RUN", "true")).lower() in {"0", "false", "no"}
    return {
        "ok": True,
        "mode": "api_ready" if ready_live else "csv_dry_run",
        "configured": configured,
        "ready_for_csv_analysis": True,
        "ready_for_live_apply": ready_live,
        "next_steps": [
            "Export Google Ads search terms as CSV and run analyze-csv.",
            "Review the negative plan manually before applying changes in Google Ads.",
        ],
    }


def build_privacy_audit() -> dict:
    return {
        "project": "google-ads-intent-mcp",
        "secrets_returned_to_agent": False,
        "local_files_ignored": [".env", "credentials/", "google-ads.yaml", "token.json", "node_modules/", "coverage/"],
        "external_services": ["optional: Google Ads API"],
        "data_boundary": "CSV analysis is local. API apply flows should stay dry-run until explicit user approval.",
        "safety_rules": [
            "Dry-run is the default.",
            "Never add negative keywords without human confirmation.",
            "Do not print OAuth tokens, developer tokens or customer account identifiers in logs.",
            "Keep raw search-term exports local unless the user asks to share them.",
        ],
    }
