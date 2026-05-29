from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Intent signal vocabulary
# ---------------------------------------------------------------------------
# The classifier is a deterministic, local-first heuristic. The signal lists
# below are deliberately broad and cross-vertical so that real, diverse Google
# Ads search-term exports classify sensibly — not just gaming/Roblox traffic.
#
# Each list maps to one of four intents:
#   - waste:      junk / freebie-seeker / fraud / off-target traffic
#   - buyer:      commercial / transactional / high-purchase-intent
#   - competitor: comparison / alternative / switching research
#   - research:   informational / educational / top-of-funnel
#
# Signals are matched as case-insensitive substrings against the normalized
# query. Multi-word signals match as substrings too, which keeps the matcher
# cheap and predictable.

WASTE_SIGNALS = [
    # gaming / freebie-seeker / fraud (original niche, kept for back-compat)
    "free robux", "generator", "hack", "cheat", "crack", "apk", "mod menu",
    "no verification", "exploit", "script executor", "bot traffic", "torrent",
    "keygen", "serial key", "license key free", "activation code free",
    # generic freebie / no-intent-to-pay seekers across verticals
    "free download", "download free", "for free", "100% free", "totally free",
    "no cost", "without paying", "without payment", "free trial hack",
    "free version", "freeware", "cracked", "pirated", "nulled",
    # job / employee / DIY seekers (rarely buyers of the product)
    "jobs", "job openings", "career", "careers", "salary", "internship",
    "resume", "cv example", "work from home job", "hiring near me",
    # academic / homework / answer-leeching
    "free pdf", "pdf download", "answers", "answer key", "cheat sheet free",
    "solutions manual", "free course", "free certification",
    # adult / irrelevant / obvious off-target
    "porn", "xxx", "nude", "lyrics", "wikipedia", "reddit",
    "youtube", "meme", "gif", "wallpaper", "clip art",
    # support / existing-customer (not new acquisition)
    "login", "log in", "sign in", "customer service phone number",
    "complaint", "is it a scam", "refund", "cancel subscription",
]

RESEARCH_SIGNALS = [
    # original informational signals
    "how to", "what is", "guide", "tutorial", "examples", "template", "learn",
    # broad informational / educational phrasing
    "what are", "why", "when to", "where to", "tips", "ideas", "checklist",
    "explained", "meaning", "definition", "benefits of", "types of",
    "step by step", "for beginners", "beginner", "guide to", "how does",
    "how do", "diy", "do it yourself", "course", "class", "training",
    "certification", "tutorials", "ebook", "whitepaper", "case study",
    "statistics", "trends", "report", "research", "vs which", "best practices",
    "checklist for", "framework", "blog", "article", "infographic",
]

BUYER_SIGNALS = [
    # original commercial signals
    "pricing", "price", "cost", "hire", "agency", "consultant", "demo", "quote",
    "buy", "service", "software", "platform", "near me", "for business",
    # ecommerce / retail purchase intent
    "buy online", "shop", "store", "for sale", "order", "purchase", "checkout",
    "discount", "coupon", "promo code", "deal", "deals", "sale", "cheap",
    "affordable", "best price", "lowest price", "in stock", "free shipping",
    "shipping", "delivery", "where to buy", "online shop", "outlet",
    # B2B / SaaS commercial intent
    "subscription", "plans", "enterprise plan", "free trial", "sign up",
    "get started", "book a demo", "request a demo", "schedule a demo",
    "request a quote", "get a quote", "talk to sales", "contact sales",
    "vendor", "provider", "supplier", "solution", "tool", "api", "integration",
    # local services / professional services
    "company", "companies", "contractor", "specialist", "expert", "professional",
    "appointment", "booking", "reserve", "reservation", "rental", "rent",
    "installation", "repair", "installer", "open now", "open near me",
    "in my area", "local", "phone number", "address", "directions",
    # health / wellness commercial
    "clinic", "doctor near me", "treatment", "therapy near me", "supplement",
    "prescription", "buy medication", "where to get",
    # finance commercial
    "loan", "mortgage rates", "insurance quote", "credit card offer",
    "open account", "interest rate", "calculator", "apply for", "apply now",
    "best rates", "compare quotes",
    # education commercial
    "enroll", "admission", "tuition", "apply university", "bootcamp",
    "paid course", "buy course", "certification cost",
]

COMPETITOR_SIGNALS = [
    # original
    "alternative", "vs", "versus", "compare", "competitor", "similar",
    # broadened comparison / switching language
    "alternatives", "alternatives to", "comparison", "compared to", "or",
    "better than", "instead of", "switch from", "migrate from", "replace",
    "replacement for", "review", "reviews", "best", "top 10", "top 5",
    "rated", "ranking", "vs.", "competitors", "rivals", "like",
]


def classify_search_term(
    term: str,
    metrics: dict[str, Any] | None = None,
    *,
    llm: bool | None = None,
    llm_classifier: Callable[[str], dict[str, Any] | str | None] | None = None,
) -> dict[str, Any]:
    """Classify a single search term into waste/buyer/research/competitor intent.

    The default path is a deterministic, dependency-free heuristic. An optional
    LLM/embeddings-backed path can be enabled to refine ambiguous results; it
    is OFF by default and always falls back to the heuristic when unavailable,
    so no API keys or extra dependencies are required for normal use.

    Parameters
    ----------
    term:
        The raw search-term string.
    metrics:
        Optional performance metrics (``cost``, ``conversions``, ...). Used to
        protect converting queries and escalate zero-conversion spend.
    llm:
        Enable the optional LLM/embeddings refinement path. When ``None`` the
        value is read from the ``GOOGLE_ADS_INTENT_LLM`` environment variable
        (truthy values: ``1``/``true``/``yes``/``on``). Defaults to disabled.
    llm_classifier:
        Optional callable that receives the normalized term and returns either
        an intent string (one of the four labels) or a dict with an ``intent``
        key (and optional ``confidence``). Injectable for testing and for
        custom embeddings/LLM backends. When omitted, a built-in resolver is
        used that only activates if a backend is actually configured.
    """

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
    source = "heuristic"

    # Optional LLM/embeddings refinement. Strictly opt-in and best-effort:
    # any failure or missing backend leaves the heuristic result untouched.
    if _llm_enabled(llm):
        refined = _refine_with_llm(value, scores, llm_classifier)
        if refined is not None:
            new_intent, new_conf = refined
            # Never override a conversion-protected buyer signal.
            if not (conversions > 0 and intent == "buyer"):
                intent = new_intent
                if new_conf is not None:
                    confidence = new_conf
            source = "llm"

    should_negative = intent == "waste" and conversions == 0
    return {
        "term": term,
        "intent": intent,
        "confidence": round(confidence, 2),
        "scores": scores,
        "source": source,
        "should_add_negative": should_negative,
        "negative_match_type": "phrase" if should_negative else "",
        "reason": _reason(intent, should_negative),
    }


def analyze_search_terms(
    rows: list[dict[str, Any]],
    *,
    llm: bool | None = None,
    llm_classifier: Callable[[str], dict[str, Any] | str | None] | None = None,
) -> dict[str, Any]:
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
        classification = classify_search_term(
            term, metrics, llm=llm, llm_classifier=llm_classifier
        )
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


# ---------------------------------------------------------------------------
# Optional LLM / embeddings path (opt-in, dependency-free fallback)
# ---------------------------------------------------------------------------

_VALID_INTENTS = {"waste", "buyer", "research", "competitor"}


def _llm_enabled(flag: bool | None) -> bool:
    if flag is not None:
        return bool(flag)
    return str(os.environ.get("GOOGLE_ADS_INTENT_LLM", "")).strip().lower() in {
        "1", "true", "yes", "on",
    }


def _refine_with_llm(
    value: str,
    scores: dict[str, int],
    llm_classifier: Callable[[str], dict[str, Any] | str | None] | None,
) -> tuple[str, float | None] | None:
    """Best-effort LLM/embeddings refinement.

    Returns ``(intent, confidence|None)`` when a backend produces a usable
    label, otherwise ``None`` (caller keeps the heuristic result). This never
    raises and never imports a hard dependency at module import time.
    """

    resolver = llm_classifier or _default_llm_classifier()
    if resolver is None:
        return None
    try:
        result = resolver(value)
    except Exception:
        return None
    return _coerce_llm_result(result)


def _coerce_llm_result(result: Any) -> tuple[str, float | None] | None:
    if result is None:
        return None
    if isinstance(result, str):
        label = result.strip().lower()
        return (label, None) if label in _VALID_INTENTS else None
    if isinstance(result, dict):
        label = str(result.get("intent", "")).strip().lower()
        if label not in _VALID_INTENTS:
            return None
        conf = result.get("confidence")
        try:
            conf_val = float(conf) if conf is not None else None
        except (TypeError, ValueError):
            conf_val = None
        if conf_val is not None:
            conf_val = max(0.0, min(0.99, conf_val))
        return label, conf_val
    return None


def _default_llm_classifier() -> Callable[[str], dict[str, Any] | str | None] | None:
    """Resolve a built-in LLM backend only if one is actually configured.

    This intentionally returns ``None`` unless an OpenAI-compatible key is
    present AND the ``openai`` package is importable, so the default heuristic
    path has zero hard dependencies and needs no credentials.
    """

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:  # pragma: no cover - exercised only when a real backend is present
        from openai import OpenAI  # type: ignore
    except Exception:  # pragma: no cover
        return None

    model = os.environ.get("GOOGLE_ADS_INTENT_LLM_MODEL", "gpt-4o-mini")

    def _classify(value: str) -> dict[str, Any] | None:  # pragma: no cover
        client = OpenAI(api_key=api_key)
        prompt = (
            "Classify this Google Ads search term into exactly one intent: "
            "waste, buyer, research, or competitor. "
            "Reply with only the single word.\n\n"
            f"Search term: {value}"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=4,
        )
        return {"intent": resp.choices[0].message.content}

    return _classify


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
