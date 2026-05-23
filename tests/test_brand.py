import pytest

from google_ads_intent_mcp.brand import classify_brand_vs_nonbrand


def test_simple_brand_match():
    result = classify_brand_vs_nonbrand("acme pricing", ["acme"])
    assert result["label"] == "brand"
    assert result["matched"] == "acme"
    assert result["confidence"] >= 0.9
    assert result["fuzzy"] is False


def test_nonbrand_when_no_keyword_present():
    result = classify_brand_vs_nonbrand("best crm software", ["acme", "acmeco"])
    assert result["label"] == "nonbrand"
    assert result["matched"] == ""


def test_multi_word_brand_matches_only_as_phrase():
    result = classify_brand_vs_nonbrand("acme corp pricing", ["acme corp"])
    assert result["label"] == "brand"
    assert result["matched"] == "acme corp"


def test_multi_word_brand_does_not_match_when_split():
    # tokens "acme ... corp" with another word in between should NOT match
    # the multi-word brand "acme corp" — adjacency required.
    result = classify_brand_vs_nonbrand(
        "acme widget corp", ["acme corp"]
    )
    assert result["label"] == "nonbrand"


def test_punctuation_is_normalized():
    result = classify_brand_vs_nonbrand("Acme-Co reviews", ["acme co"])
    assert result["label"] == "brand"


def test_case_insensitive():
    result = classify_brand_vs_nonbrand("AcMe Pricing", ["acme"])
    assert result["label"] == "brand"


def test_empty_brand_list_returns_nonbrand():
    result = classify_brand_vs_nonbrand("acme reviews", [])
    assert result["label"] == "nonbrand"
    assert result["confidence"] == 1.0


def test_empty_search_term_returns_nonbrand():
    result = classify_brand_vs_nonbrand("", ["acme"])
    assert result["label"] == "nonbrand"


def test_fuzzy_off_does_not_match_typo():
    result = classify_brand_vs_nonbrand("acmee pricing", ["acmee" * 0 or "acme"])
    # "acmee" should NOT match "acme" without fuzzy
    out = classify_brand_vs_nonbrand("acmee pricing", ["acme"])
    assert out["label"] == "nonbrand"


def test_fuzzy_on_matches_one_edit_typo():
    out = classify_brand_vs_nonbrand("hubspott pricing", ["hubspot"], fuzzy=True)
    assert out["label"] == "brand"
    assert out["fuzzy"] is True
    assert out["matched"] == "hubspot"
    assert 0 < out["confidence"] < 0.9


def test_fuzzy_skips_short_brands():
    # 4-char brand "Nike" — typo "nik" would otherwise be 1 edit but length < 5
    out = classify_brand_vs_nonbrand("nik shoes", ["nike"], fuzzy=True)
    assert out["label"] == "nonbrand"


def test_longer_brand_wins_when_both_match():
    out = classify_brand_vs_nonbrand("hello acme corp", ["acme", "acme corp"])
    assert out["matched"] == "acme corp"


def test_non_string_search_term_raises():
    with pytest.raises(TypeError):
        classify_brand_vs_nonbrand(123, ["acme"])  # type: ignore[arg-type]
