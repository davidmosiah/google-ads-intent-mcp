from __future__ import annotations


def build_negative_plan(analysis: dict, match_type: str = "phrase", level: str = "campaign") -> dict:
    candidates = []
    for item in analysis.get("terms", []):
        classification = item.get("classification", {})
        if not classification.get("should_add_negative"):
            continue
        candidates.append({
            "text": item.get("search_term", ""),
            "match_type": classification.get("negative_match_type") or match_type,
            "level": level,
            "cost": item.get("metrics", {}).get("cost", 0),
            "reason": classification.get("reason", ""),
        })

    return {
        "dry_run": True,
        "apply_supported": False,
        "negative_keywords": candidates,
        "summary": {
            "candidate_count": len(candidates),
            "estimated_wasted_cost": round(sum(float(item.get("cost", 0)) for item in candidates), 2),
        },
        "next_step": "Review candidates in Google Ads before applying. Live mutation is intentionally not automatic in v0.1.",
    }
