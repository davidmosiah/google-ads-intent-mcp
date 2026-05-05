from __future__ import annotations

import os

from .agent import build_agent_manifest, build_connection_status, build_privacy_audit
from .intent import analyze_search_terms, classify_search_term
from .negatives import build_negative_plan


def create_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install MCP support with: pip install 'google-ads-intent-mcp[mcp]'") from exc

    mcp = FastMCP("google-ads-intent-mcp")

    @mcp.tool()
    def google_ads_agent_manifest(client: str = "generic") -> dict:
        return build_agent_manifest(client)

    @mcp.tool()
    def google_ads_connection_status() -> dict:
        return build_connection_status(os.environ)

    @mcp.tool()
    def google_ads_privacy_audit() -> dict:
        return build_privacy_audit()

    @mcp.tool()
    def google_ads_classify_search_term(term: str) -> dict:
        return classify_search_term(term)

    @mcp.tool()
    def google_ads_analyze_search_terms(rows: list[dict]) -> dict:
        return analyze_search_terms(rows)

    @mcp.tool()
    def google_ads_build_negative_plan(rows: list[dict], match_type: str = "phrase", level: str = "campaign") -> dict:
        return build_negative_plan(analyze_search_terms(rows), match_type=match_type, level=level)

    return mcp


def main() -> None:
    create_mcp().run()


if __name__ == "__main__":
    main()
