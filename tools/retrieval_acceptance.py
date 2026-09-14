from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from rerank_retriever import RerankedRetriever  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_acceptance(path: Path, root: Path = ROOT) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("acceptance YAML must be a mapping")

    schema = deepcopy(_read_json(Path(root) / "schema/retrieval-acceptance.schema.json"))
    query_schema = _read_json(Path(root) / "schema/context-query.schema.json")
    schema["properties"]["cases"]["items"]["properties"]["query"] = query_schema
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid retrieval acceptance: {details}")

    seen_ids: set[str] = set()
    for case in data["cases"]:
        case_id = str(case["id"])
        if case_id in seen_ids:
            raise ValueError(f"duplicate acceptance case id: {case_id}")
        seen_ids.add(case_id)
        required = list(case["required_ids"])
        allowed = list(case["allowed_extra_ids"])
        if case["kind"] == "positive" and not required:
            raise ValueError(f"positive acceptance case {case_id} must require at least one canonical ID")
        if case["kind"] == "negative":
            if required:
                raise ValueError(f"negative acceptance case {case_id} must not require canonical IDs")
            if allowed:
                raise ValueError(f"negative acceptance case {case_id} must not allow extra canonical IDs")
    return data


def evaluate_case(
    case: Mapping[str, Any], retriever: RerankedRetriever
) -> dict[str, Any]:
    # Diagnostics intentionally use a separate rank call from the production
    # selection call. Blind acceptance must exercise RerankedRetriever.select_ids
    # exactly as shipped rather than maintaining a benchmark-only copy of the
    # selection algorithm.
    ranked = retriever.rank(case["query"])
    selected = retriever.select_ids(case["query"])
    by_id = {hit.id: hit for hit in ranked}

    required = set(str(item) for item in case["required_ids"])
    forbidden = set(str(item) for item in case["forbidden_ids"])
    allowed_extra = set(str(item) for item in case["allowed_extra_ids"])
    hits = sorted(required & selected)
    misses = sorted(required - selected)
    forbidden_hits = sorted(forbidden & selected)
    extras = sorted(selected - required - allowed_extra)
    kind = str(case["kind"])
    abstained = len(selected) == 0

    if kind == "positive":
        case_pass = not misses and not forbidden_hits
    else:
        case_pass = abstained

    watched = set(required) | set(forbidden)
    if kind == "negative" and ranked:
        watched.add(ranked[0].id)
    diagnostics: dict[str, dict[str, Any]] = {}
    for canonical_id in sorted(watched):
        hit = by_id.get(canonical_id)
        diagnostics[canonical_id] = {
            "candidate": hit is not None,
            "selected": canonical_id in selected,
            "rerank_rank": hit.rerank_rank if hit is not None else None,
            "rerank_score": hit.rerank_score if hit is not None else None,
            "hybrid_rank": hit.hybrid_rank if hit is not None else None,
            "deterministic_rank": hit.deterministic_rank if hit is not None else None,
            "semantic_rank": hit.semantic_rank if hit is not None else None,
            "graph_candidate": hit.graph_candidate if hit is not None else False,
        }

    return {
        "id": str(case["id"]),
        "kind": kind,
        "critical": bool(case["critical"]),
        "selected_ids": sorted(selected),
        "required_hits": hits,
        "required_misses": misses,
        "forbidden_hits": forbidden_hits,
        "extra_ids": extras,
        "abstained": abstained,
        "pass": case_pass,
        "candidate_count": len(ranked),
        "rank_diagnostics": diagnostics,
    }


def evaluate_acceptance(
    acceptance: Mapping[str, Any], retriever: RerankedRetriever
) -> dict[str, Any]:
    cases = [evaluate_case(case, retriever) for case in acceptance["cases"]]
    positives = [case for case in cases if case["kind"] == "positive"]
    negatives = [case for case in cases if case["kind"] == "negative"]
    critical = [case for case in cases if case["critical"]]

    source_cases = {str(case["id"]): case for case in acceptance["cases"]}
    required_total = sum(
        len(source_cases[case["id"]]["required_ids"])
        for case in positives
    )
    required_hits = sum(len(case["required_hits"]) for case in positives)
    forbidden_hits = sum(len(case["forbidden_hits"]) for case in cases)
    positive_extra_mean = (
        sum(len(case["extra_ids"]) for case in positives) / len(positives)
        if positives
        else 0.0
    )
    negative_abstentions = sum(1 for case in negatives if case["abstained"])

    metrics = {
        "critical_case_success": (
            sum(1 for case in critical if case["pass"]) / len(critical)
            if critical
            else 1.0
        ),
        "positive_required_id_recall": (
            required_hits / required_total if required_total else 1.0
        ),
        "forbidden_hits": forbidden_hits,
        "mean_positive_extra_ids": positive_extra_mean,
        "negative_abstention_rate": (
            negative_abstentions / len(negatives) if negatives else 1.0
        ),
        "mean_positive_selected_ids": (
            sum(len(case["selected_ids"]) for case in positives) / len(positives)
            if positives
            else 0.0
        ),
        "mean_negative_selected_ids": (
            sum(len(case["selected_ids"]) for case in negatives) / len(negatives)
            if negatives
            else 0.0
        ),
    }
    thresholds = dict(acceptance["thresholds"])
    checks = {
        "critical_case_success": metrics["critical_case_success"] >= thresholds["critical_case_success_min"],
        "positive_required_id_recall": metrics["positive_required_id_recall"] >= thresholds["positive_required_id_recall_min"],
        "forbidden_hits": metrics["forbidden_hits"] <= thresholds["forbidden_hits_max"],
        "mean_positive_extra_ids": metrics["mean_positive_extra_ids"] <= thresholds["mean_positive_extra_ids_max"],
        "negative_abstention_rate": metrics["negative_abstention_rate"] >= thresholds["negative_abstention_rate_min"],
    }
    return {
        "acceptance": str(acceptance["name"]),
        "frozen_candidate": str(acceptance["frozen_candidate"]),
        "mode": "cross-encoder-adaptive-blind",
        "semantic_model": retriever.semantic_model,
        "rerank_model": retriever.rerank_model,
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "pass": all(checks.values()),
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run abstention-aware blind acceptance for Qiven retrieval."
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=Path("benchmarks/retrieval/blind-v3.yaml"),
        help="Blind acceptance YAML path.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return nonzero if blind acceptance thresholds are not met.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.acceptance if args.acceptance.is_absolute() else ROOT / args.acceptance
    try:
        acceptance = load_acceptance(path, ROOT)
        retriever = RerankedRetriever(ROOT)
        result = evaluate_acceptance(acceptance, retriever)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Acceptance: {result['acceptance']}")
        print(f"Frozen candidate: {result['frozen_candidate']}")
        print("Mode: cross-encoder-adaptive-blind")
        print(f"Semantic model: {result['semantic_model']}")
        print(f"Rerank model: {result['rerank_model']}")
        for case in result["cases"]:
            status = "PASS" if case["pass"] else "MISS"
            misses = ",".join(case["required_misses"]) or "-"
            forbidden = ",".join(case["forbidden_hits"]) or "-"
            print(
                f"[{status:4}] {case['id']} ({case['kind']}): "
                f"misses={misses} forbidden={forbidden} extras={len(case['extra_ids'])} "
                f"selected={len(case['selected_ids'])} candidates={case['candidate_count']} "
                f"abstained={'yes' if case['abstained'] else 'no'}"
            )
            for canonical_id, diagnostic in case["rank_diagnostics"].items():
                score = diagnostic["rerank_score"]
                score_text = "None" if score is None else f"{score:.4f}"
                print(
                    f"       {canonical_id}: "
                    f"{'selected' if diagnostic['selected'] else 'not-selected'} "
                    f"R={diagnostic['rerank_rank']} score={score_text} "
                    f"H={diagnostic['hybrid_rank']} D={diagnostic['deterministic_rank']} "
                    f"S={diagnostic['semantic_rank']} "
                    f"G={'yes' if diagnostic['graph_candidate'] else 'no'}"
                )
        metrics = result["metrics"]
        print("\nMetrics:")
        print(f"  critical_case_success={metrics['critical_case_success']:.3f}")
        print(f"  positive_required_id_recall={metrics['positive_required_id_recall']:.3f}")
        print(f"  forbidden_hits={metrics['forbidden_hits']}")
        print(f"  mean_positive_extra_ids={metrics['mean_positive_extra_ids']:.3f}")
        print(f"  negative_abstention_rate={metrics['negative_abstention_rate']:.3f}")
        print(f"  mean_positive_selected_ids={metrics['mean_positive_selected_ids']:.3f}")
        print(f"  mean_negative_selected_ids={metrics['mean_negative_selected_ids']:.3f}")
        print(f"Acceptance result: {'PASS' if result['pass'] else 'FAIL'}")

    return 1 if args.enforce and not result["pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
