from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_gateway import prepare_context  # noqa: E402
from context_pack import write_context_pack  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare Qiven task context and emit a Context Lease proving retrieval was invoked."
    )
    parser.add_argument("--query", required=True, type=Path, help="Path to a context-query JSON file.")
    parser.add_argument(
        "--output-prefix",
        required=True,
        type=Path,
        help="Output path prefix; .json/.md context pack plus .lease.json are written.",
    )
    parser.add_argument(
        "--previous-lease",
        type=Path,
        help="Optional prior Context Lease used only to classify transition versus same-task refresh.",
    )
    parser.add_argument("--json", action="store_true", help="Print one machine-readable summary object.")
    return parser.parse_args()


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    args = parse_args()
    query_path = _resolve(args.query)
    output_prefix = _resolve(args.output_prefix)
    previous_path = _resolve(args.previous_lease) if args.previous_lease else None

    try:
        query = json.loads(query_path.read_text(encoding="utf-8"))
        if not isinstance(query, dict):
            raise ValueError("query JSON must be an object")
        previous = None
        if previous_path is not None:
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
            if not isinstance(previous, dict):
                raise ValueError("previous lease JSON must be an object")
        pack, lease = prepare_context(query, ROOT, previous_lease=previous)
        json_path, markdown_path = write_context_pack(pack, output_prefix, ROOT)
        lease_path = output_prefix.with_suffix(".lease.json")
        lease_path.parent.mkdir(parents=True, exist_ok=True)
        lease_path.write_text(json.dumps(lease, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    summary = {
        "retrieval_invoked": True,
        "lease_id": lease["lease_id"],
        "transition": lease["transition"],
        "canonical_ref": lease["canonical_ref"],
        "context_pack_json": str(json_path),
        "context_pack_markdown": str(markdown_path),
        "context_lease": str(lease_path),
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print("Context retrieval: INVOKED")
        print(f"Context lease: {lease['lease_id']}")
        print(f"Transition: {lease['transition']}")
        print(f"Canonical ref: {lease['canonical_ref']}")
        print(f"Context pack JSON: {json_path}")
        print(f"Context pack Markdown: {markdown_path}")
        print(f"Context lease JSON: {lease_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
