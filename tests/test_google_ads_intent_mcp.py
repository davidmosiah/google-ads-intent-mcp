from google_ads_intent_mcp.agent import build_agent_manifest, build_connection_status, build_privacy_audit
from google_ads_intent_mcp.intent import analyze_search_terms, classify_search_term
from google_ads_intent_mcp.negatives import build_negative_plan


def test_agent_manifest_is_dry_run_first_and_secret_free():
    manifest = build_agent_manifest(client="codex")

    assert manifest["project"] == "google-ads-intent-mcp"
    assert manifest["client"] == "codex"
    assert manifest["default_mode"] == "dry_run"
    assert "google_ads_analyze_search_terms" in manifest["standard_tools"]
    assert "secret" not in str(manifest).lower()


def test_connection_status_supports_csv_mode_without_credentials():
    status = build_connection_status(env={})

    assert status["ok"] is True
    assert status["mode"] == "csv_dry_run"
    assert status["ready_for_live_apply"] is False


def test_privacy_audit_never_returns_tokens():
    audit = build_privacy_audit()

    assert audit["secrets_returned_to_agent"] is False
    assert ".env" in audit["local_files_ignored"]
    assert any("dry-run" in rule.lower() for rule in audit["safety_rules"])


def test_classify_search_term_detects_waste_and_buyer_intent():
    waste = classify_search_term("free robux generator no verification")
    buyer = classify_search_term("hire ai automation agency pricing")

    assert waste["intent"] == "waste"
    assert waste["should_add_negative"] is True
    assert buyer["intent"] == "buyer"
    assert buyer["should_add_negative"] is False


def test_analyze_search_terms_builds_budget_weighted_summary():
    rows = [
        {"search_term": "free robux generator", "cost": "12.50", "clicks": "8", "conversions": "0"},
        {"search_term": "ai automation agency pricing", "cost": "20", "clicks": "2", "conversions": "1"},
    ]

    result = analyze_search_terms(rows)

    assert result["summary"]["total_terms"] == 2
    assert result["summary"]["wasted_cost"] == 12.5
    assert result["terms"][0]["classification"]["intent"] == "waste"


def test_negative_plan_is_dry_run_and_does_not_include_buyer_terms():
    analysis = analyze_search_terms([
        {"search_term": "free robux generator", "cost": "12.50", "clicks": "8", "conversions": "0"},
        {"search_term": "ai automation agency pricing", "cost": "20", "clicks": "2", "conversions": "1"},
    ])

    plan = build_negative_plan(analysis)

    assert plan["dry_run"] is True
    assert plan["negative_keywords"][0]["text"] == "free robux generator"
    assert all(item["text"] != "ai automation agency pricing" for item in plan["negative_keywords"])
