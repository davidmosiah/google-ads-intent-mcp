from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

WASTE_SIGNALS = [
    "free robux", "generator", "hack", "cheat", "crack", "apk", "mod menu",
    "no verification", "exploit", "script executor", "bot traffic", "torrent",
]
RESEARCH_SIGNALS = ["how to", "what is", "guide", "tutorial", "examples", "template", "learn"]
BUYER_SIGNALS = [
    "pricing", "price", "cost", "hire", "agency", "consultant", "demo", "quote",
    "buy", "service", "software", "platform", "near me", "for business",
]
COMPETITOR_SIGNALS = ["alternative", "vs", "versus", "compare", "competitor", "similar"]


def classify_search_term(term: str, metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    value = " ".join(str(term or "").lower().split())
    metrics = metrics or {}
    conversions = _number(metrics.get("conversions", 0))
    cost = _money(metrics.get("cost", metrics.get("cost_micros", 0)))

    scores = {
        "waste": _score(value, WASTE_SIGNALS, 4),
        "buyer": _score(value, BUYER_SIGNALS, 3),
        "research": _score(value, RESEARCH_SIGNALS, 2),
        "competitor": _score(value, COMPETITOR_SIGNALS, 2),
    }
    if conversions > 0:
        scores["buyer"] += 5
        scores["waste"] = max(0, scores["waste"] - 4)
    if cost >= 10 and conversions == 0 and scores["waste"] > 0:
        scores["waste"] += 2

    intent = max(scores.items(), key=lambda item: item[1])[0]
    confidence = min(0.98, 0.45 + (scores[intent] * 0.08))
    should_negative = intent == "waste" and conversions == 0
    return {
        "term": term,
        "intent": intent,
        "confidence": round(confidence, 2),
        "scores": scores,
        "should_add_negative": should_negative,
        "negative_match_type": "phrase" if should_negative else "",
        "reason": _reason(intent, should_negative),
    }


def analyze_search_terms(rows: list[dict[str, Any]]) -> dict[str, Any]:
    terms = []
    wasted_cost = Decimal("0")
    protected_cost = Decimal("0")

    for row in rows:
        term = _pick(row, "search_term", "Search term", "search term", "Query", "query")
        metrics = {
            "cost": _pick(row, "cost", "Cost", "cost_micros", "Cost micros", default=0),
            "clicks": _pick(row, "clicks", "Clicks", default=0),
            "conversions": _pick(row, "conversions", "Conversions", "Conv.", default=0),
            "impressions": _pick(row, "impressions", "Impr.", "Impressions", default=0),
        }
        classification = classify_search_term(term, metrics)
        cost = _money(metrics["cost"])
        if classification["should_add_negative"]:
            wasted_cost += cost
        else:
            protected_cost += cost
        terms.append({
            "search_term": term,
            "metrics": {
                "cost": float(cost),
                "clicks": int(_number(metrics["clicks"])),
                "conversions": float(_number(metrics["conversions"])),
                "impressions": int(_number(metrics["impressions"])),
            },
            "classification": classification,
        })

    terms.sort(key=lambda item: (item["classification"]["should_add_negative"], item["metrics"]["cost"]), reverse=True)
    return {
        "summary": {
            "total_terms": len(terms),
            "negative_candidates": sum(1 for item in terms if item["classification"]["should_add_negative"]),
            "wasted_cost": float(round(wasted_cost, 2)),
            "protected_cost": float(round(protected_cost, 2)),
        },
        "terms": terms,
    }


def _score(text: str, signals: list[str], weight: int) -> int:
    return sum(weight for signal in signals if signal in text)


def _reason(intent: str, should_negative: bool) -> str:
    if should_negative:
        return "Matches junk or low-value query patterns and has no conversion protection."
    if intent == "buyer":
        return "Contains purchase, pricing or service-evaluation language."
    if intent == "competitor":
        return "Looks like comparison or alternative research; review before excluding."
    if intent == "research":
        return "Educational query. Keep or route to content/remarketing depending on campaign goal."
    return "No strong exclusion signal detected."


def _pick(row: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def _number(value: Any) -> Decimal:
    try:
        return Decimal(str(value).replace(",", "").replace("$", "").strip() or "0")
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _money(value: Any) -> Decimal:
    number = _number(value)
    if abs(number) > Decimal("100000"):
        return number / Decimal("1000000")
    return number
