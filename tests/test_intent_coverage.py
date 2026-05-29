"""Cross-vertical intent classifier coverage + optional LLM path tests.

These tests assert the heuristic classifies real, diverse Google Ads search
terms sensibly (not just gaming/Roblox), and that the optional LLM/embeddings
path is strictly opt-in with a clean heuristic fallback.
"""

from google_ads_intent_mcp.intent import classify_search_term


def _intent(term: str, **kwargs) -> str:
    return classify_search_term(term, **kwargs)["intent"]


def test_cross_vertical_buyer_intent_coverage():
    buyer_terms = [
        # ecommerce / retail
        "buy running shoes online",
        "cheap office chair free shipping",
        "where to buy organic coffee",
        # B2B / SaaS
        "crm software pricing",
        "book a demo project management tool",
        "enterprise plan email marketing platform",
        # local services
        "emergency plumber near me",
        "hire electrician in my area",
        "car detailing appointment booking",
        # health
        "dermatology clinic near me",
        # finance
        "best mortgage rates apply now",
        "personal loan calculator",
        # education
        "data science bootcamp tuition",
    ]
    labels = [_intent(t) for t in buyer_terms]
    buyer_hits = sum(1 for l in labels if l == "buyer")
    # The whole point of the broadening: the vast majority of these obvious
    # commercial queries must land on "buyer", not on a gaming-biased default.
    assert buyer_hits >= len(buyer_terms) - 2, dict(zip(buyer_terms, labels))


def test_cross_vertical_research_intent_coverage():
    research_terms = [
        "how to start a podcast",
        "what is content marketing",
        "best practices for email deliverability",
        "types of life insurance explained",
        "step by step sourdough recipe",
        "seo tips for beginners",
        "remote work productivity ideas",
    ]
    labels = [_intent(t) for t in research_terms]
    research_hits = sum(1 for l in labels if l == "research")
    assert research_hits >= len(research_terms) - 2, dict(zip(research_terms, labels))


def test_cross_vertical_waste_intent_coverage():
    waste_terms = [
        "free pdf marketing ebook download",
        "crm software free download cracked",
        "is acme corp a scam",
        "project manager jobs salary",
        "free certification answer key",
    ]
    labels = [_intent(t) for t in waste_terms]
    waste_hits = sum(1 for l in labels if l == "waste")
    assert waste_hits >= len(waste_terms) - 1, dict(zip(waste_terms, labels))


def test_cross_vertical_competitor_intent_coverage():
    competitor_terms = [
        "salesforce vs hubspot",
        "mailchimp alternative",
        "best project management software comparison",
        "notion or obsidian",
    ]
    labels = [_intent(t) for t in competitor_terms]
    comp_hits = sum(1 for l in labels if l in {"competitor", "buyer"})
    # competitor terms are acceptable as competitor (preferred) and not as waste
    assert all(l != "waste" for l in labels), dict(zip(competitor_terms, labels))
    assert comp_hits >= len(competitor_terms) - 1, dict(zip(competitor_terms, labels))


def test_classification_exposes_source_field():
    result = classify_search_term("buy crm software pricing")
    assert result["source"] == "heuristic"


def test_llm_path_is_optional_and_defaults_off(monkeypatch):
    # No env vars, no injected classifier: must use heuristic and never touch
    # any external backend.
    monkeypatch.delenv("GOOGLE_ADS_INTENT_LLM", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = classify_search_term("buy running shoes online", llm=True)
    # llm=True is requested but no backend is configured → graceful fallback.
    assert result["source"] == "heuristic"
    assert result["intent"] == "buyer"


def test_llm_path_uses_injected_classifier_when_enabled():
    calls = {}

    def fake_llm(value: str):
        calls["value"] = value
        return {"intent": "competitor", "confidence": 0.91}

    result = classify_search_term(
        "free robux generator", llm=True, llm_classifier=fake_llm
    )
    assert result["source"] == "llm"
    assert result["intent"] == "competitor"
    assert result["confidence"] == 0.91
    assert calls["value"] == "free robux generator"


def test_llm_path_falls_back_when_classifier_raises():
    def broken_llm(value: str):
        raise RuntimeError("backend exploded")

    result = classify_search_term(
        "buy crm software pricing", llm=True, llm_classifier=broken_llm
    )
    # On any backend error we keep the deterministic heuristic result.
    assert result["source"] == "heuristic"
    assert result["intent"] == "buyer"


def test_llm_never_overrides_conversion_protected_buyer():
    def steer_to_waste(value: str):
        return "waste"

    result = classify_search_term(
        "premium yoga mat",
        metrics={"conversions": 3, "cost": 40},
        llm=True,
        llm_classifier=steer_to_waste,
    )
    # A converting buyer term must stay protected even if the LLM disagrees.
    assert result["intent"] == "buyer"
    assert result["should_add_negative"] is False


def test_llm_ignores_invalid_label():
    def junk_llm(value: str):
        return "not_a_real_intent"

    result = classify_search_term(
        "how to start a podcast", llm=True, llm_classifier=junk_llm
    )
    assert result["source"] == "heuristic"
    assert result["intent"] == "research"


def test_llm_enabled_via_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_ADS_INTENT_LLM", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fake_llm(value: str):
        return "buyer"

    result = classify_search_term(
        "what is content marketing", llm_classifier=fake_llm
    )
    # Env flag turns the path on; injected classifier overrides heuristic.
    assert result["source"] == "llm"
    assert result["intent"] == "buyer"
