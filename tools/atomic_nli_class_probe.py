from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from atomic_entailment_probe import DEVELOPMENT_ATOMS, TOP_BUNDLE_DOCUMENTS  # noqa: E402
from evidence_span_probe import record_evidence_chunks  # noqa: E402
from nli_answerability_probe import (  # noqa: E402
    NliClassProbabilities,
    OnnxNliBackend,
)
from rerank_retriever import RerankedRetriever  # noqa: E402
from retrieval_acceptance import load_acceptance  # noqa: E402


@dataclass(frozen=True)
class AtomicClassSupport:
    atom: str
    supported: bool
    record_id: str
    evidence: str
    probabilities: NliClassProbabilities


def _class_margin(probabilities: NliClassProbabilities) -> float:
    return probabilities.entailment - max(
        probabilities.neutral,
        probabilities.contradiction,
    )


def score_atom_bundle_classes(
    backend: OnnxNliBackend,
    atoms: Sequence[str],
    evidence: Sequence[tuple[str, str]],
) -> list[AtomicClassSupport]:
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

    scores = backend.class_probabilities(premises, hypotheses)
    if len(scores) != len(owners):
        raise RuntimeError("NLI backend returned the wrong number of class-probability rows")

    candidates: dict[str, list[AtomicClassSupport]] = {atom: [] for atom in normalized_atoms}
    for (atom, record_id, chunk), probabilities in zip(owners, scores):
        candidates[atom].append(
            AtomicClassSupport(
                atom=atom,
                supported=probabilities.winner == "entailment",
                record_id=record_id,
                evidence=chunk,
                probabilities=probabilities,
            )
        )

    result: list[AtomicClassSupport] = []
    for atom in normalized_atoms:
        rows = candidates[atom]
        supported = [row for row in rows if row.supported]
        pool = supported if supported else rows
        best = max(
            pool,
            key=lambda row: (
                _class_margin(row.probabilities),
                row.probabilities.entailment,
            ),
        )
        result.append(best)
    return result


def probe_case(case, retriever: RerankedRetriever, nli: OnnxNliBackend):
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

    support = score_atom_bundle_classes(nli, atoms, evidence)
    return {
        "id": case_id,
        "kind": str(case["kind"]),
        "bundle_ids": [hit.id for hit in bundle_hits],
        "support": support,
        "all_atoms_supported": bool(support) and all(row.supported for row in support),
    }


def _shorten(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe native three-way NLI class semantics for atomic evidence-bundle support."
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

    print(f"Atomic NLI-class development probe: {acceptance['name']}")
    print(f"Frozen selector candidate: {acceptance['frozen_candidate']}")
    print(f"bundle_top_documents={TOP_BUNDLE_DOCUMENTS}")
    print("decision=each atomic claim needs at least one evidence span whose NLI winner is entailment")
    print("NOTE: observed blind-v3 cases; this output is diagnostic, not acceptance evidence.")
    for case in cases:
        status = "SUPPORTED" if case["all_atoms_supported"] else "ABSTAIN"
        print(f"[{case['kind'].upper():8}] {case['id']} decision={status}")
        print(f"       bundle: {', '.join(case['bundle_ids'])}")
        for row in case["support"]:
            p = row.probabilities
            print(
                f"       atom={'YES' if row.supported else 'NO '} "
                f"winner={p.winner:<13} E={p.entailment:.4f} N={p.neutral:.4f} C={p.contradiction:.4f} "
                f"source={row.record_id}: {row.atom}"
            )
            print(f"           evidence: {_shorten(row.evidence)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
