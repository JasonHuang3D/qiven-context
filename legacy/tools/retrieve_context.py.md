# [SEALED] tools/retrieve_context.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/retrieve_context.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from retrieval_candidate_bundle import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    build_candidate_bundle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve a small provenance-preserving Qiven candidate-evidence bundle. "
            "Candidates are not selected truth; cognition must decide answerability."
        )
    )
    parser.add_argument(
        "--query",
        required=True,
        type=Path,
        help="Path to a context-query JSON file.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
        help=f"Maximum candidate records to return (default: {DEFAULT_MAX_CANDIDATES}).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    query_path = args.query if args.query.is_absolute() else ROOT / args.query

    try:
        query = json.loads(query_path.read_text(encoding="utf-8"))
        if not isinstance(query, dict):
            raise ValueError("query JSON must be an object")
        bundle = build_candidate_bundle(
            query,
            root=ROOT,
            max_candidates=args.max_candidates,
        )
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

````
