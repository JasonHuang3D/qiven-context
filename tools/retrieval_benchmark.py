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

from context_compiler import compile_context_pack  # noqa: E402
from semantic_retriever import DEFAULT_MODEL, DEFAULT_TOP_K, SemanticRetriever  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_benchmark(path: Path, root: Path = ROOT) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("benchmark YAML must be a mapping")

    schema = deepcopy(_read_json(Path(root) / "schema/retrieval-benchmark.schema.json"))
    query_schema = _read_json(Path(root) / "schema/context-query.schema.json")
    schema["properties"]["cases"]["items"]["properties"]["query"] = query_schema
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid retrieval benchmark: {details}")
    return data


def selected_canonical_ids(pack: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for category in ("decisions", "memory", "obligations"):
        for item in pack.get(category, []) or []:
            canonical_id = item.get("id")
            if canonical_id:
                result.add(str(canonical_id))
    return result


def evaluate_case(
    case: Mapping[str, Any],
    root: Path = ROOT,
    *,
    mode: str = "deterministic",
    semantic_retriever: SemanticRetriever | None = None,
    semantic_top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    if mode == "deterministic":
        pack = compile_context_pack(case["query"], root)
        selected = selected_canonical_ids(pack)
    elif mode == "semantic":
        if semantic_retriever is None:
            raise ValueError("semantic mode requires a semantic retriever")
        selected = semantic_retriever.select_ids(case["query"], top_k=semantic_top_k)
    else:
        raise ValueError(f"unsupported retrieval mode: {mode}")

    required = set(str(item) for item in case["required_ids"])
    forbidden = set(str(item) for item in case["forbidden_ids"])
    allowed_extra = set(str(item) for item in case["allowed_extra_ids"])
    hits = sorted(required & selected)
    misses = sorted(required - selected)
    forbidden_hits = sorted(forbidden & selected)
    extras = sorted(selected - required - allowed_extra)
    recall = len(hits) / len(required)
    return {
        "id": str(case["id"]),
        "critical": bool(case["critical"]),
        "selected_ids": sorted(selected),
        "required_hits": hits,
        "required_misses": misses,
        "forbidden_hits": forbidden_hits,
        "extra_ids": extras,
        "required_recall": recall,
        "critical_pass": not misses and not forbidden_hits,
    }


def evaluate_benchmark(
    benchmark: Mapping[str, Any],
    root: Path = ROOT,
    *,
    mode: str = "deterministic",
    semantic_retriever: SemanticRetriever | None = None,
    semantic_top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    if mode == "semantic" and semantic_retriever is None:
        semantic_retriever = SemanticRetriever(root)

    cases = [
        evaluate_case(
            case,
            root,
            mode=mode,
            semantic_retriever=semantic_retriever,
            semantic_top_k=semantic_top_k,
        )
        for case in benchmark["cases"]
    ]
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
    result: dict[str, Any] = {
        "benchmark": str(benchmark["name"]),
        "mode": mode,
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "pass": all(checks.values()),
        "cases": cases,
    }
    if mode == "semantic" and semantic_retriever is not None:
        result["semantic"] = {
            "model": semantic_retriever.model_name,
            "top_k": semantic_top_k,
        }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure Qiven retrieval against a frozen benchmark.")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("benchmarks/retrieval/open-set-v1.yaml"),
        help="Benchmark YAML path.",
    )
    parser.add_argument(
        "--mode",
        choices=("deterministic", "semantic"),
        default="deterministic",
        help="Retrieval candidate to measure.",
    )
    parser.add_argument(
        "--semantic-model",
        default=DEFAULT_MODEL,
        help="FastEmbed model name for semantic mode.",
    )
    parser.add_argument(
        "--semantic-top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help="Maximum canonical IDs selected by semantic mode.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Return nonzero if frozen benchmark thresholds are not met.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.semantic_top_k < 1:
        print("ERROR: --semantic-top-k must be >= 1", file=sys.stderr)
        return 2
    benchmark_path = args.benchmark if args.benchmark.is_absolute() else ROOT / args.benchmark
    try:
        benchmark = load_benchmark(benchmark_path, ROOT)
        retriever = (
            SemanticRetriever(ROOT, model_name=args.semantic_model)
            if args.mode == "semantic"
            else None
        )
        result = evaluate_benchmark(
            benchmark,
            ROOT,
            mode=args.mode,
            semantic_retriever=retriever,
            semantic_top_k=args.semantic_top_k,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Benchmark: {result['benchmark']}")
        print(f"Mode: {result['mode']}")
        if "semantic" in result:
            print(
                f"Semantic model: {result['semantic']['model']} "
                f"top_k={result['semantic']['top_k']}"
            )
        for case in result["cases"]:
            status = "PASS" if case["critical_pass"] else "MISS"
            misses = ",".join(case["required_misses"]) or "-"
            forbidden = ",".join(case["forbidden_hits"]) or "-"
            print(
                f"[{status:4}] {case['id']}: recall={case['required_recall']:.2f} "
                f"misses={misses} forbidden={forbidden} extras={len(case['extra_ids'])}"
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
