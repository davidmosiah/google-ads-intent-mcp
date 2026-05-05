from __future__ import annotations

import argparse
import json
import os

from .agent import build_agent_manifest, build_connection_status, build_privacy_audit
from .csv_io import read_search_terms_csv
from .intent import analyze_search_terms, classify_search_term
from .negatives import build_negative_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="google-ads-intent")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    sub = parser.add_subparsers(dest="command", required=True)

    manifest = sub.add_parser("manifest")
    manifest.add_argument("--client", default="generic")

    sub.add_parser("doctor")
    sub.add_parser("privacy-audit")

    classify = sub.add_parser("classify")
    classify.add_argument("term")

    analyze = sub.add_parser("analyze-csv")
    analyze.add_argument("--csv", required=True)

    plan = sub.add_parser("plan-negatives")
    plan.add_argument("--csv", required=True)
    plan.add_argument("--match-type", choices=["exact", "phrase", "broad"], default="phrase")
    plan.add_argument("--level", choices=["campaign", "ad_group"], default="campaign")

    args = parser.parse_args(argv)

    if args.command == "manifest":
        payload = build_agent_manifest(args.client)
    elif args.command == "doctor":
        payload = build_connection_status(os.environ)
    elif args.command == "privacy-audit":
        payload = build_privacy_audit()
    elif args.command == "classify":
        payload = classify_search_term(args.term)
    elif args.command == "analyze-csv":
        payload = analyze_search_terms(read_search_terms_csv(args.csv))
    elif args.command == "plan-negatives":
        payload = build_negative_plan(
            analyze_search_terms(read_search_terms_csv(args.csv)),
            match_type=args.match_type,
            level=args.level,
        )
    else:
        parser.error("unknown command")

    print(_format(payload, args.format))
    return 0


def _format(payload: dict, response_format: str) -> str:
    if response_format == "markdown":
        return "# Google Ads Intent MCP\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
    return json.dumps(payload, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    raise SystemExit(main())
