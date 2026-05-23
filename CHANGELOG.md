# Changelog

## 0.1.1 - 2026-05-22
- Add `classify_brand_vs_nonbrand(search_term, brand_keywords)` returning `{label, matched, confidence, fuzzy}`. Multi-word brand keywords match adjacency only, punctuation is normalized, longer brands win when both match, and optional `fuzzy=True` accepts 1-edit typos on brands of length 5+.
- Exposes `classify_brand_vs_nonbrand` from package root.

## 0.1.0
- Initial release.
