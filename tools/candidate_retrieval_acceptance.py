from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from context_compiler import validate_query  # noqa: E402
from retrieval_candidate_bundle import build_candidate_bundle  # noqa: E402
from rerank_retriever import RerankedRetriever  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidate_acceptance(path: Path, root: Path = ROOT) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("candidate acceptance YAML must be a mapping")
    schema = _read_json(Path(root) / "schema/retrieval-candidate-acceptance.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    )
    if errors:
        raise ValueError("invalid candidate acceptance: " + "; ".join(error.message for error in errors))

    seen: set[str] = set()
    for case in data["cases"]:
        case_id = str(case["id"])
        if case_id in seen:
            raise ValueError(f"duplicate candidate acceptance case id: {case_id}")
        seen.add(case_id)
        validate_query(case["query"], root)
        required = list(case["required_ids"])
        if case["kind"] == "positive" and not required:
            raise ValueError(f"positive case {case_id} must require at least one canonical ID")
        if case["kind"] == "negative" and required:
            raise ValueError(f"negative case {case_id} must not require canonical IDs")
        expected = "answer" if case["kind"] == "positive" else "abstain"
        if case["cognition_expectation"] != expected:
            raise ValueError(f"case {case_id} must use cognition_expectation={expected}")
    return data


def evaluate_case(
    case: Mapping[str, Any],
    retriever: Any,
    *,
    root: Path = ROOT,
    max_candidates: int,
) -> dict[str, Any]:
    bundle = build_candidate_bundle(
        case["query"], retriever, root=root, max_candidates=max_candidates
    )
    candidate_ids = [str(item["id"]) for item in bundle["candidates"]]
    required = {str(item) for item in case["required_ids"]}
    forbidden = {str(item) for item in case["forbidden_ids"]}
    top1 = candidate_ids[0] if candidate_ids else None
    required_hits = sorted(required & set(candidate_ids))
    required_misses = sorted(required - set(candidate_ids))
    top1_required = bool(required) and top1 in required
    forbidden_top1 = top1 if top1 in forbidden else None
    return {
        "id": str(case["id"]),
        "kind": str(case["kind"]),
        "critical": bool(case["critical"]),
        "cognition_expectation": str(case["cognition_expectation"]),
        "candidate_ids": candidate_ids,
        "required_hits": required_hits,
        "required_misses": required_misses,
        "top1": top1,
        "top1_required": top1_required,
        "forbidden_top1": forbidden_top1,
    }


def evaluate_acceptance(
    acceptance: Mapping[str, Any], retriever: Any, *, root: Path = ROOT
) -> dict[str, Any]:
    max_candidates = int(acceptance["max_candidates"])
    cases = [
        evaluate_case(case, retriever, root=root, max_candidates=max_candidates)
        for case in acceptance["cases"]
    ]
    positives = [case for case in cases if case["kind"] == "positive"]
    required_total = sum(
        len(next(source for source in acceptance["cases"] if source["id"] == case["id"])["required_ids"])
        for case in positives
    )
    required_hits = sum(len(case["required_hits"]) for case in positives)
    top1_required = sum(1 for case in positives if case["top1_required"])
    forbidden_top1_hits = sum(1 for case in cases if case["forbidden_top1"] is not None)

    metrics = {
        "positive_required_id_recall": required_hits / required_total if required_total else 1.0,
        "positive_top1_required_rate": top1_required / len(positives) if positives else 1.0,
        "forbidden_top1_hits": forbidden_top1_hits,
        "mean_candidate_count": (
            sum(len(case["candidate_ids"]) for case in cases) / len(cases) if cases else 0.0
        ),
    }
    thresholds = dict(acceptance["thresholds"])
    checks = {
        "positive_required_id_recall": metrics["positive_required_id_recall"] >= thresholds["positive_required_id_recall_min"],
        "positive_top1_required_rate": metrics["positive_top1_required_rate"] >= thresholds["positive_top1_required_rate_min"],
        "forbidden_top1_hits": metrics["forbidden_top1_hits"] <= thresholds["forbidden_top1_hits_max"],
    }
    return {
        "acceptance": str(acceptance["name"]),
        "frozen_candidate": str(acceptance["frozen_candidate"]),
        "max_candidates": max_candidates,
        "metrics": metrics,
        "thresholds": thresholds,
        "checks": checks,
        "retrieval_pass": all(checks.values()),
        "cognition_status": "manual-pending",
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run candidate-boundary blind retrieval acceptance.")
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=Path("benchmarks/retrieval/blind-v4.yaml"),
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.acceptance if args.acceptance.is_absolute() else ROOT / args.acceptance
    try:
        acceptance = load_candidate_acceptance(path, ROOT)
        retriever = RerankedRetriever(ROOT)
        result = evaluate_acceptance(acceptance, retriever, root=ROOT)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Candidate acceptance: {result['acceptance']}")
        print(f"Frozen candidate: {result['frozen_candidate']}")
        print(f"max_candidates={result['max_candidates']}")
        print("NOTE: retrieval is automated here; cognition answer/abstain review remains manual and source-grounded.")
        for case in result["cases"]:
            expectation = case["cognition_expectation"]
            required = ",".join(case["required_hits"]) or "-"
            misses = ",".join(case["required_misses"]) or "-"
            forbidden = case["forbidden_top1"] or "-"
            print(
                f"[{case['kind'].upper():8}] {case['id']} expect={expectation} "
                f"top1={case['top1'] or '-'} required_hits={required} misses={misses} "
                f"forbidden_top1={forbidden}"
            )
            print("       candidates: " + (", ".join(case["candidate_ids"]) or "<none>"))
        metrics = result["metrics"]
        print("\nRetrieval metrics:")
        print(f"  positive_required_id_recall={metrics['positive_required_id_recall']:.3f}")
        print(f"  positive_top1_required_rate={metrics['positive_top1_required_rate']:.3f}")
        print(f"  forbidden_top1_hits={metrics['forbidden_top1_hits']}")
        print(f"  mean_candidate_count={metrics['mean_candidate_count']:.3f}")
        print(f"Retrieval acceptance: {'PASS' if result['retrieval_pass'] else 'FAIL'}")
        print("Cognition acceptance: MANUAL-PENDING")

    return 1 if args.enforce and not result["retrieval_pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
