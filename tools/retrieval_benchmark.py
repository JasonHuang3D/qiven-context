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


def evaluate_case(case: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    pack = compile_context_pack(case["query"], root)
    selected = selected_canonical_ids(pack)
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


def evaluate_benchmark(benchmark: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    cases = [evaluate_case(case, root) for case in benchmark["cases"]]
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
        "mode": "deterministic",
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "pass": all(checks.values()),
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure Qiven retrieval against a frozen benchmark.")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("benchmarks/retrieval/open-set-v1.yaml"),
        help="Benchmark YAML path.",
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
    benchmark_path = args.benchmark if args.benchmark.is_absolute() else ROOT / args.benchmark
    try:
        benchmark = load_benchmark(benchmark_path, ROOT)
        result = evaluate_benchmark(benchmark, ROOT)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Benchmark: {result['benchmark']}")
        print("Mode: deterministic")
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
