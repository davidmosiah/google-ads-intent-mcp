"""Brand vs non-brand search-term classification.

A small, deterministic helper that decides whether a search term is a
brand query (mentions the advertiser's brand or a known variant) or a
non-brand query. This is the single most important separator for Google
Ads structure decisions — it gates budget, bidding strategy and match
type choices.

The matcher is intentionally simple and local-first:

- Case-insensitive substring match.
- Punctuation normalization (``.``, ``-``, ``_`` collapse to a space)
  so ``Acme-Co`` matches ``acme co``.
- Multi-word brand keywords are matched as adjacent tokens.
- Optional ``fuzzy=True`` accepts a 1-character typo for brands of
  length ``>= 5`` (cheap Levenshtein-ish check), since typos are
  extremely common in branded queries.

Returns a small dict with the decision, the matched keyword (if any)
and a confidence score in 0..1 so callers can sort or threshold.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

_WORD_BOUNDARY = re.compile(r"[^\w\s]+")
_WHITESPACE = re.compile(r"\s+")


def classify_brand_vs_nonbrand(
    search_term: str,
    brand_keywords: Iterable[str],
    *,
    fuzzy: bool = False,
) -> dict[str, Any]:
    """Classify ``search_term`` as ``"brand"`` or ``"nonbrand"``.

    Parameters
    ----------
    search_term:
        The raw user query (a search term row, an exact keyword, etc.).
    brand_keywords:
        Iterable of brand names, variants and known misspellings to
        check for. Examples: ``["acme", "acme corp", "acmeco"]``.
    fuzzy:
        When True, allow a 1-edit typo on brand keywords of length
        ``>= 5``. Disabled by default to keep the classifier
        deterministic.

    Returns
    -------
    dict
        ``{"label": "brand"|"nonbrand", "matched": str, "confidence": float,
           "fuzzy": bool}``. ``matched`` is the original brand keyword that
        triggered the match, empty when the result is ``"nonbrand"``.
    """

    if not isinstance(search_term, str):
        raise TypeError("search_term must be a string")
    keywords = [str(k) for k in brand_keywords if str(k).strip()]
    if not keywords:
        # No brand vocabulary supplied: by definition nothing can be brand.
        return {"label": "nonbrand", "matched": "", "confidence": 1.0, "fuzzy": False}

    term_norm = _normalize(search_term)
    if not term_norm:
        return {"label": "nonbrand", "matched": "", "confidence": 1.0, "fuzzy": False}
    term_tokens = term_norm.split()

    # Sort longer keywords first so multi-word brands win over generic ones.
    for kw in sorted(keywords, key=lambda k: -len(k)):
        kw_norm = _normalize(kw)
        if not kw_norm:
            continue
        if _tokens_contain(term_tokens, kw_norm.split()):
            return {
                "label": "brand",
                "matched": kw,
                "confidence": 0.97,
                "fuzzy": False,
            }

    if fuzzy:
        for kw in sorted(keywords, key=lambda k: -len(k)):
            kw_norm = _normalize(kw)
            if len(kw_norm) < 5 or " " in kw_norm:
                continue
            for token in term_tokens:
                if _within_one_edit(token, kw_norm):
                    return {
                        "label": "brand",
                        "matched": kw,
                        "confidence": 0.75,
                        "fuzzy": True,
                    }

    return {"label": "nonbrand", "matched": "", "confidence": 0.9, "fuzzy": False}


def _normalize(value: str) -> str:
    text = _WORD_BOUNDARY.sub(" ", str(value).lower())
    return _WHITESPACE.sub(" ", text).strip()


def _tokens_contain(tokens: list[str], needle: list[str]) -> bool:
    if not needle:
        return False
    n = len(needle)
    for i in range(0, len(tokens) - n + 1):
        if tokens[i : i + n] == needle:
            return True
    return False


def _within_one_edit(a: str, b: str) -> bool:
    """Return True if ``a`` and ``b`` differ by at most one substitution,
    insertion, or deletion. Cheap O(len) Levenshtein for distance == 1.
    """
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diffs = sum(1 for x, y in zip(a, b) if x != y)
        return diffs == 1
    # length differs by 1 → check single insert/delete
    shorter, longer = (a, b) if la < lb else (b, a)
    i = j = 0
    found = False
    while i < len(shorter) and j < len(longer):
        if shorter[i] == longer[j]:
            i += 1
            j += 1
        else:
            if found:
                return False
            found = True
            j += 1
    return True


__all__ = ["classify_brand_vs_nonbrand"]
