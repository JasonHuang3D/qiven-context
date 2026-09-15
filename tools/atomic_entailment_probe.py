from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evidence_span_probe import record_evidence_chunks  # noqa: E402
from nli_answerability_probe import NliBackend, OnnxNliBackend  # noqa: E402
from rerank_retriever import RerankedRetriever  # noqa: E402
from retrieval_acceptance import load_acceptance  # noqa: E402


TOP_BUNDLE_DOCUMENTS = 3

# Development-only atomic claims authored after blind-v3 was observed. This
# probe tests coverage behavior only; it is not acceptance evidence and must not
# be used to tune a production threshold against blind-v3.
DEVELOPMENT_ATOMS: dict[str, tuple[str, ...]] = {
    "foundation-ownership-must-stay-explicit": (
        "Qiven Foundation requires ownership, lifetime, allocation strategy, and allocator provenance to remain explicit.",
        "Ordinary Foundation allocation failure must not require exceptions.",
    ),
    "devkit-must-not-overwrite-consumer-edits": (
        "Devkit must not silently overwrite consumer edits during template synchronization.",
        "A divergent managed file requires explicit conflict or ownership handling.",
    ),
    "math-must-not-hide-global-epsilon": (
        "qiven-math vector equality is exact by default rather than approximate through one global epsilon.",
        "qiven-math core vector types do not bake in one product or world handedness or up-axis.",
    ),
    "recurring-ambiguity-should-be-codified": (
        "A repeated collaboration ambiguity should be codified into durable repository protocol or automation.",
        "Qiven should not rely on whichever chat session happens to remember a recurring workflow rule.",
    ),
    "foundation-support-is-ci-evidence": (
        "Portability intent alone does not establish that a Foundation platform is supported.",
        "A Foundation platform support claim requires continuous CI evidence for that platform combination.",
    ),
    "toolchain-name-does-not-imply-every-host-tool": (
        "qiven-toolchain-win owns the executable build tools explicitly declared in its manifest.",
        "The qiven-toolchain-win repository name does not prove that Python, CUDA, MSVC, the Windows SDK, or every Windows dependency is pinned.",
    ),
    "automated-record-writer-needs-id-issuance": (
        "Current Qiven seed identifiers were manually patterned.",
        "Automated MEM and OBL creation at scale requires a safer identifier-issuance rule than humans inventing suffixes.",
    ),
    "old-python-fixture-must-test-version-path": (
        "The Windows Python resolver implementation already checks interpreter version correctly.",
        "The old-Python test fixture must prove rejection of a runnable Python 3.10 specifically because of its reported version.",
    ),
    "negative-generic-cpp-vector-growth": (
        "Qiven has a canonical project rule defining how std::vector size and capacity must behave.",
        "Qiven has a canonical project rule defining what std::vector must do when growth requires reallocation.",
    ),
    "negative-generic-database-normalization": (
        "Qiven has an accepted architecture decision requiring third normal form for relational databases.",
    ),
    "negative-unknown-workstation-temperature": (
        "Canonical Qiven cognition records that the development workstation reached exactly 83 degrees Celsius during yesterday's build.",
    ),
    "negative-unknown-gas-cloud-region": (
        "Canonical Qiven cognition requires the industrial-gas product to deploy production in AWS ap-southeast-1 Singapore.",
    ),
}


@dataclass(frozen=True)
class AtomicSupport:
    atom: str
    entailment: float
    record_id: str
    evidence: str


def score_atom_bundle(
    backend: NliBackend,
    atoms: Sequence[str],
    evidence: Sequence[tuple[str, str]],
) -> list[AtomicSupport]:
    normalized_atoms = [atom.strip() for atom in atoms if atom.strip()]
    if not normalized_atoms:
        raise ValueError("at least one atomic claim is required")
    if not evidence:
        return []

    premises: list[str] = []
    hypotheses: list[str] = []
    owners: list[tuple[str, str, str]] = []
    for atom in normalized_atoms:
        for record_id, chunk in evidence:
            premises.append(chunk)
            hypotheses.append(atom)
            owners.append((atom, record_id, chunk))

    scores = backend.entailment_probabilities(premises, hypotheses)
    if len(scores) != len(owners):
        raise RuntimeError("NLI backend returned the wrong number of entailment scores")

    best: dict[str, AtomicSupport] = {}
    for (atom, record_id, chunk), raw_score in zip(owners, scores):
        candidate = AtomicSupport(atom=atom, entailment=float(raw_score), record_id=record_id, evidence=chunk)
        current = best.get(atom)
        if current is None or candidate.entailment > current.entailment:
            best[atom] = candidate
    return [best[atom] for atom in normalized_atoms]


def probe_case(
    case: Mapping[str, Any],
    retriever: RerankedRetriever,
    nli: NliBackend,
) -> dict[str, Any]:
    case_id = str(case["id"])
    atoms = DEVELOPMENT_ATOMS.get(case_id)
    if atoms is None:
        raise ValueError(f"no atomic development claims for case {case_id}")

    ranked = retriever.rank(case["query"])
    bundle_hits = ranked[:TOP_BUNDLE_DOCUMENTS]
    evidence: list[tuple[str, str]] = []
    for hit in bundle_hits:
        for chunk in record_evidence_chunks(retriever.records[hit.id]):
            evidence.append((hit.id, chunk))

    support = score_atom_bundle(nli, atoms, evidence)
    scores = [row.entailment for row in support]
    return {
        "id": case_id,
        "kind": str(case["kind"]),
        "bundle_ids": [hit.id for hit in bundle_hits],
        "support": support,
        "coverage_floor": min(scores) if scores else None,
        "coverage_mean": (sum(scores) / len(scores)) if scores else None,
    }


def _shorten(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe atomic candidate-answer coverage over a small retrieved evidence bundle."
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=Path("benchmarks/retrieval/blind-v3.yaml"),
        help="Observed blind-v3 benchmark used only as a development probe corpus.",
    )
    parser.add_argument("--model", default=None, help="Optional Hugging Face NLI model repo override.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.acceptance if args.acceptance.is_absolute() else ROOT / args.acceptance
    try:
        acceptance = load_acceptance(path, ROOT)
        case_ids = {str(case["id"]) for case in acceptance["cases"]}
        atom_ids = set(DEVELOPMENT_ATOMS)
        if case_ids != atom_ids:
            missing = sorted(case_ids - atom_ids)
            extra = sorted(atom_ids - case_ids)
            raise ValueError(f"atomic claim coverage mismatch: missing={missing} extra={extra}")
        retriever = RerankedRetriever(ROOT)
        nli = OnnxNliBackend() if args.model is None else OnnxNliBackend(args.model)
        cases = [probe_case(case, retriever, nli) for case in acceptance["cases"]]
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Atomic-entailment development probe: {acceptance['name']}")
    print(f"Frozen selector candidate: {acceptance['frozen_candidate']}")
    print(f"bundle_top_documents={TOP_BUNDLE_DOCUMENTS}")
    print("NOTE: observed blind-v3 cases; this output is diagnostic, not acceptance evidence.")
    for case in cases:
        floor = case["coverage_floor"]
        mean = case["coverage_mean"]
        floor_text = "None" if floor is None else f"{float(floor):.4f}"
        mean_text = "None" if mean is None else f"{float(mean):.4f}"
        print(f"[{case['kind'].upper():8}] {case['id']} floor={floor_text} mean={mean_text}")
        print(f"       bundle: {', '.join(case['bundle_ids'])}")
        for row in case["support"]:
            print(f"       atom={row.entailment:.4f} source={row.record_id}: {row.atom}")
            print(f"           evidence: {_shorten(row.evidence)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
