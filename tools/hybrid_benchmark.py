from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hybrid_retriever import DEFAULT_RRF_K, DEFAULT_TOP_K, HybridRetriever  # noqa: E402
from retrieval_benchmark import load_benchmark  # noqa: E402
from semantic_retriever import DEFAULT_MODEL  # noqa: E402


def _select_from_ranked(
    query: Mapping[str, Any], ranked: list[Any], *, top_k: int = DEFAULT_TOP_K
) -> set[str]:
    selected: list[str] = []
    seen: set[str] = set()
    available = {hit.id for hit in ranked}
    for canonical_id in (str(item) for item in query.get("include_ids", []) or []):
        if canonical_id in available and canonical_id not in seen:
            selected.append(canonical_id)
            seen.add(canonical_id)
    for hit in ranked:
        if len(selected) >= top_k:
            break
        if hit.id not in seen:
            selected.append(hit.id)
            seen.add(hit.id)
    return set(selected)


def evaluate_case(
    case: Mapping[str, Any], hybrid: HybridRetriever, *, top_k: int = DEFAULT_TOP_K
) -> dict[str, Any]:
    ranked = hybrid.rank(case["query"])
    selected = _select_from_ranked(case["query"], ranked, top_k=top_k)
    positions = {hit.id: index for index, hit in enumerate(ranked, 1)}
    by_id = {hit.id: hit for hit in ranked}

    required = set(str(item) for item in case["required_ids"])
    forbidden = set(str(item) for item in case["forbidden_ids"])
    allowed_extra = set(str(item) for item in case["allowed_extra_ids"])
    hits = sorted(required & selected)
    misses = sorted(required - selected)
    forbidden_hits = sorted(forbidden & selected)
    extras = sorted(selected - required - allowed_extra)
    watched = sorted(required | forbidden)
    rank_diagnostics: dict[str, dict[str, Any]] = {}
    for canonical_id in watched:
        hit = by_id.get(canonical_id)
        rank_diagnostics[canonical_id] = {
            "selected": canonical_id in selected,
            "hybrid_rank": positions.get(canonical_id),
            "deterministic_rank": hit.deterministic_rank if hit is not None else None,
            "semantic_rank": hit.semantic_rank if hit is not None else None,
            "fused_score": hit.score if hit is not None else None,
        }

    return {
        "id": str(case["id"]),
        "critical": bool(case["critical"]),
        "selected_ids": sorted(selected),
        "required_hits": hits,
        "required_misses": misses,
        "forbidden_hits": forbidden_hits,
        "extra_ids": extras,
        "required_recall": len(hits) / len(required),
        "critical_pass": not misses and not forbidden_hits,
        "rank_diagnostics": rank_diagnostics,
    }


def evaluate_benchmark(
    benchmark: Mapping[str, Any], hybrid: HybridRetriever, *, top_k: int = DEFAULT_TOP_K
) -> dict[str, Any]:
    cases = [evaluate_case(case, hybrid, top_k=top_k) for case in benchmark["cases"]]
    required_total = sum(len(case["required_ids"]) for case in benchmark["cases"])
    required_hits = sum(len(case["required_hits"]) for case in cases)
    critical_cases = [case for case in cases if case["critical"]]
    critical_passes = sum(1 for case in critical_cases if case["critical_pass"])
    forbidden_hits = sum(len(case["forbidden_hits"]) for case in cases)
    mean_extra = sum(len(case["extra_ids"]) for case in cases) / len(cases)
    metrics = {
        "critical_case_recall": critical_passes / len(critical_cases) if critical_cases else 1.0,
        "required_id_recall": required_hits / required_total if required_total else 1.0,
        "forbidden_hits": forbidden_hits,
        "mean_extra_ids": mean_extra,
    }
    thresholds = dict(benchmark["thresholds"])
    checks = {
        "critical_case_recall": metrics["critical_case_recall"] >= thresholds["critical_case_recall_min"],
        "required_id_recall": metrics["required_id_recall"] >= thresholds["required_id_recall_min"],
        "forbidden_hits": metrics["forbidden_hits"] <= thresholds["forbidden_hits_max"],
        "mean_extra_ids": metrics["mean_extra_ids"] <= thresholds["mean_extra_ids_max"],
    }
    return {
        "benchmark": str(benchmark["name"]),
        "mode": "hybrid-rrf",
        "semantic_model": hybrid.semantic_model,
        "top_k": top_k,
        "rrf_k": DEFAULT_RRF_K,
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "pass": all(checks.values()),
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure the frozen equal-weight RRF hybrid retrieval candidate."
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("benchmarks/retrieval/open-set-v1.yaml"),
        help="Frozen benchmark YAML path.",
    )
    parser.add_argument(
        "--semantic-model",
        default=DEFAULT_MODEL,
        help="FastEmbed model used for the semantic rank channel.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return nonzero if frozen thresholds are not met.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    benchmark_path = args.benchmark if args.benchmark.is_absolute() else ROOT / args.benchmark
    try:
        benchmark = load_benchmark(benchmark_path, ROOT)
        hybrid = HybridRetriever(ROOT, semantic_model=args.semantic_model)
        result = evaluate_benchmark(benchmark, hybrid)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Benchmark: {result['benchmark']}")
        print("Mode: hybrid-rrf")
        print(
            f"Semantic model: {result['semantic_model']} top_k={result['top_k']} rrf_k={result['rrf_k']}"
        )
        for case in result["cases"]:
            status = "PASS" if case["critical_pass"] else "MISS"
            misses = ",".join(case["required_misses"]) or "-"
            forbidden = ",".join(case["forbidden_hits"]) or "-"
            print(
                f"[{status:4}] {case['id']}: recall={case['required_recall']:.2f} "
                f"misses={misses} forbidden={forbidden} extras={len(case['extra_ids'])}"
            )
            for canonical_id, diagnostic in case["rank_diagnostics"].items():
                marker = "selected" if diagnostic["selected"] else "not-selected"
                print(
                    f"       {canonical_id}: {marker} "
                    f"H={diagnostic['hybrid_rank']} "
                    f"D={diagnostic['deterministic_rank']} "
                    f"S={diagnostic['semantic_rank']}"
                )
        metrics = result["metrics"]
        print("\nMetrics:")
        print(f"  critical_case_recall={metrics['critical_case_recall']:.3f}")
        print(f"  required_id_recall={metrics['required_id_recall']:.3f}")
        print(f"  forbidden_hits={metrics['forbidden_hits']}")
        print(f"  mean_extra_ids={metrics['mean_extra_ids']:.3f}")
        print(f"Threshold result: {'PASS' if result['pass'] else 'FAIL'}")

    return 1 if args.enforce and not result["pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
