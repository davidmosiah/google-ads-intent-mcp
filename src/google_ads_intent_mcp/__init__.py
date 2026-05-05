"""Agent-first Google Ads intent analysis toolkit."""

from .agent import build_agent_manifest, build_connection_status, build_privacy_audit
from .intent import analyze_search_terms, classify_search_term
from .negatives import build_negative_plan

__all__ = [
    "analyze_search_terms",
    "build_agent_manifest",
    "build_connection_status",
    "build_negative_plan",
    "build_privacy_audit",
    "classify_search_term",
]
