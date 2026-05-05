from __future__ import annotations

import csv
from pathlib import Path


def read_search_terms_csv(path: str | Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))
