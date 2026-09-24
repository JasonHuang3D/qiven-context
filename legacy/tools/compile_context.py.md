# [SEALED] tools/compile_context.py

> Museum piece (ADR-0040/ADR-0041, sealed 2026-09-21). Original
> location: `tools/compile_context.py`. Do not execute — this is historical text
> only; the `.md` extension makes accidental execution impossible.

````python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_compiler import compile_context_pack  # noqa: E402
from context_pack import write_context_pack  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile a deterministic Qiven task context pack from a JSON query."
    )
    parser.add_argument(
        "--query",
        required=True,
        type=Path,
        help="Path to a context-query JSON file.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        type=Path,
        help="Output path prefix; .json and .md are written beside it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    query_path = args.query if args.query.is_absolute() else ROOT / args.query
    output_prefix = args.output_prefix if args.output_prefix.is_absolute() else ROOT / args.output_prefix

    try:
        query = json.loads(query_path.read_text(encoding="utf-8"))
        if not isinstance(query, dict):
            raise ValueError("query JSON must be an object")
        pack = compile_context_pack(query, ROOT)
        json_path, markdown_path = write_context_pack(pack, output_prefix, ROOT)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Context pack JSON: {json_path.relative_to(ROOT) if json_path.is_relative_to(ROOT) else json_path}")
    print(
        f"Context pack Markdown: {markdown_path.relative_to(ROOT) if markdown_path.is_relative_to(ROOT) else markdown_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

````
