from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from retrieval_benchmark import load_benchmark  # noqa: E402
from rerank_retriever import (  # noqa: E402
    DEFAULT_GRAPH_SEED_TOP_K,
    DEFAULT_MAX_SELECTED,
    DEFAULT_MIN_LOGIT,
    DEFAULT_RERANK_MODEL,
    DEFAULT_SEMANTIC_POOL_TOP_K,
    RerankedRetriever,
)
from semantic_retriever import DEFAULT_MODEL  # noqa: E402


def evaluate_case(case: Mapping[str, Any], retriever: RerankedRetriever) -> dict[str, Any]:
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

    diagnostics: dict[str, dict[str, Any]] = {}
    for canonical_id in sorted(required | forbidden):
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
        "critical": bool(case["critical"]),
        "selected_ids": sorted(selected),
        "required_hits": hits,
        "required_misses": misses,
        "forbidden_hits": forbidden_hits,
        "extra_ids": extras,
        "required_recall": len(hits) / len(required),
        "critical_pass": not misses and not forbidden_hits,
        "candidate_count": len(ranked),
        "rank_diagnostics": diagnostics,
    }


def evaluate_benchmark(
    benchmark: Mapping[str, Any], retriever: RerankedRetriever
) -> dict[str, Any]:
    cases = [evaluate_case(case, retriever) for case in benchmark["cases"]]
    required_total = sum(len(case["required_ids"]) for case in benchmark["cases"])
    required_hits = sum(len(case["required_hits"]) for case in cases)
    critical_cases = [case for case in cases if case["critical"]]
    critical_passes = sum(1 for case in critical_cases if case["critical_pass"])
    forbidden_hits = sum(len(case["forbidden_hits"]) for case in cases)
    mean_extra = sum(len(case["extra_ids"]) for case in cases) / len(cases)
    mean_selected = sum(len(case["selected_ids"]) for case in cases) / len(cases)
    mean_candidates = sum(case["candidate_count"] for case in cases) / len(cases)

    metrics = {
        "critical_case_recall": critical_passes / len(critical_cases) if critical_cases else 1.0,
        "required_id_recall": required_hits / required_total if required_total else 1.0,
        "forbidden_hits": forbidden_hits,
        "mean_extra_ids": mean_extra,
        "mean_selected_ids": mean_selected,
        "mean_candidate_ids": mean_candidates,
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
        "mode": "cross-encoder-adaptive",
        "semantic_model": retriever.semantic_model,
        "rerank_model": retriever.rerank_model,
        "semantic_pool_top_k": DEFAULT_SEMANTIC_POOL_TOP_K,
        "graph_seed_top_k": DEFAULT_GRAPH_SEED_TOP_K,
        "max_selected": DEFAULT_MAX_SELECTED,
        "min_logit": DEFAULT_MIN_LOGIT,
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "pass": all(checks.values()),
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure high-recall candidates with cross-encoder reranking and adaptive selection."
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("benchmarks/retrieval/held-out-v2.yaml"),
        help="Benchmark YAML path.",
    )
    parser.add_argument(
        "--semantic-model",
        default=DEFAULT_MODEL,
        help="FastEmbed bi-encoder used by the first-stage semantic channel.",
    )
    parser.add_argument(
        "--rerank-model",
        default=DEFAULT_RERANK_MODEL,
        help="FastEmbed TextCrossEncoder model.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return nonzero if benchmark thresholds are not met.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    benchmark_path = args.benchmark if args.benchmark.is_absolute() else ROOT / args.benchmark
    try:
        benchmark = load_benchmark(benchmark_path, ROOT)
        retriever = RerankedRetriever(
            ROOT,
            semantic_model=args.semantic_model,
            rerank_model=args.rerank_model,
        )
        result = evaluate_benchmark(benchmark, retriever)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Benchmark: {result['benchmark']}")
        print("Mode: cross-encoder-adaptive")
        print(f"Semantic model: {result['semantic_model']}")
        print(
            f"Rerank model: {result['rerank_model']} "
            f"semantic_pool_top_k={result['semantic_pool_top_k']} "
            f"graph_seed_top_k={result['graph_seed_top_k']} "
            f"max_selected={result['max_selected']} min_logit={result['min_logit']:.3f}"
        )
        for case in result["cases"]:
            status = "PASS" if case["critical_pass"] else "MISS"
            misses = ",".join(case["required_misses"]) or "-"
            forbidden = ",".join(case["forbidden_hits"]) or "-"
            print(
                f"[{status:4}] {case['id']}: recall={case['required_recall']:.2f} "
                f"misses={misses} forbidden={forbidden} extras={len(case['extra_ids'])} "
                f"selected={len(case['selected_ids'])} candidates={case['candidate_count']}"
            )
            for canonical_id, diagnostic in case["rank_diagnostics"].items():
                marker = "selected" if diagnostic["selected"] else "not-selected"
                score = diagnostic["rerank_score"]
                score_text = "None" if score is None else f"{score:.4f}"
                print(
                    f"       {canonical_id}: {marker} candidate={'yes' if diagnostic['candidate'] else 'no'} "
                    f"R={diagnostic['rerank_rank']} score={score_text} "
                    f"H={diagnostic['hybrid_rank']} D={diagnostic['deterministic_rank']} "
                    f"S={diagnostic['semantic_rank']} G={'yes' if diagnostic['graph_candidate'] else 'no'}"
                )
        metrics = result["metrics"]
        print("\nMetrics:")
        print(f"  critical_case_recall={metrics['critical_case_recall']:.3f}")
        print(f"  required_id_recall={metrics['required_id_recall']:.3f}")
        print(f"  forbidden_hits={metrics['forbidden_hits']}")
        print(f"  mean_extra_ids={metrics['mean_extra_ids']:.3f}")
        print(f"  mean_selected_ids={metrics['mean_selected_ids']:.3f}")
        print(f"  mean_candidate_ids={metrics['mean_candidate_ids']:.3f}")
        print(f"Threshold result: {'PASS' if result['pass'] else 'FAIL'}")

    return 1 if args.enforce and not result["pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
