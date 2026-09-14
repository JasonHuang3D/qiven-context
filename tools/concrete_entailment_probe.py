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


TOP_NEGATIVE_DOCUMENTS = 3

# Development-only claims written after blind-v3 was observed. They are used to
# test one narrow hypothesis: concrete proposition verification may separate
# supported answers from topical-but-insufficient evidence better than the
# generic "evidence is sufficient" meta-hypothesis. This is not blind
# acceptance evidence and no production threshold may be tuned from it.
DEVELOPMENT_CLAIMS: dict[str, str] = {
    "foundation-ownership-must-stay-explicit": (
        "Qiven Foundation requires allocator provenance and ownership to remain explicit, "
        "and ordinary allocation failure must not be represented with exceptions."
    ),
    "devkit-must-not-overwrite-consumer-edits": (
        "Devkit must not silently overwrite consumer edits during template synchronization; "
        "conflicts require explicit handling."
    ),
    "math-must-not-hide-global-epsilon": (
        "qiven-math must not use one global approximate-equality epsilon by default and must not "
        "bake a single world handedness or up-axis into core vector types."
    ),
    "recurring-ambiguity-should-be-codified": (
        "Repeated collaboration ambiguity should be codified into durable repository protocol "
        "instead of relying on whichever chat session remembers it."
    ),
    "foundation-support-is-ci-evidence": (
        "A Foundation platform is supported only when it is continuously exercised by CI; "
        "portability intent alone is not support evidence."
    ),
    "toolchain-name-does-not-imply-every-host-tool": (
        "qiven-toolchain-win owns only tools explicitly declared in its manifest; its repository "
        "name does not imply that Python, CUDA, MSVC, the Windows SDK, or every Windows dependency is pinned."
    ),
    "automated-record-writer-needs-id-issuance": (
        "Before automated writers mint MEM and OBL identifiers at scale, Qiven must implement an "
        "identifier-issuance mechanism instead of relying on humans to invent suffixes."
    ),
    "old-python-fixture-must-test-version-path": (
        "The Windows resolver has a validation gap: the old-Python fixture must prove rejection of a "
        "runnable Python 3.10 specifically because of its reported version."
    ),
    "negative-generic-cpp-vector-growth": (
        "Qiven has a canonical project rule defining how std::vector size, capacity, and reallocation must behave."
    ),
    "negative-generic-database-normalization": (
        "Qiven has a canonical architecture decision requiring third normal form for relational databases."
    ),
    "negative-unknown-workstation-temperature": (
        "The Qiven development workstation reached exactly 83 degrees Celsius during yesterday's build."
    ),
    "negative-unknown-gas-cloud-region": (
        "The industrial-gas product is required to deploy production in AWS ap-southeast-1 Singapore."
    ),
}


@dataclass(frozen=True)
class ClaimEvidenceScore:
    text: str
    entailment: float


def score_claim_entailment(
    backend: NliBackend,
    claim: str,
    chunks: Sequence[str],
) -> list[ClaimEvidenceScore]:
    claim = claim.strip()
    if not claim:
        raise ValueError("claim must not be empty")
    if not chunks:
        return []

    premises = [str(chunk) for chunk in chunks]
    hypotheses = [claim] * len(premises)
    entailments = backend.entailment_probabilities(premises, hypotheses)
    if len(entailments) != len(premises):
        raise RuntimeError("NLI backend returned the wrong number of entailment scores")

    rows = [
        ClaimEvidenceScore(text=chunk, entailment=float(score))
        for chunk, score in zip(premises, entailments)
    ]
    return sorted(rows, key=lambda row: (-row.entailment, row.text))


def probe_case(
    case: Mapping[str, Any],
    retriever: RerankedRetriever,
    nli: NliBackend,
) -> dict[str, Any]:
    case_id = str(case["id"])
    claim = DEVELOPMENT_CLAIMS.get(case_id)
    if claim is None:
        raise ValueError(f"no development claim for case {case_id}")

    ranked = retriever.rank(case["query"])
    by_id = {hit.id: hit for hit in ranked}
    watched = {
        *(str(item) for item in case.get("required_ids", []) or []),
        *(str(item) for item in case.get("forbidden_ids", []) or []),
    }
    if str(case["kind"]) == "negative":
        watched.update(hit.id for hit in ranked[:TOP_NEGATIVE_DOCUMENTS])
    elif ranked:
        watched.add(ranked[0].id)

    rows: list[dict[str, Any]] = []
    for canonical_id in sorted(watched):
        hit = by_id.get(canonical_id)
        if hit is None:
            rows.append({"id": canonical_id, "candidate": False})
            continue
        chunks = record_evidence_chunks(retriever.records[canonical_id])
        evidence = score_claim_entailment(nli, claim, chunks)
        best = evidence[0] if evidence else None
        rows.append(
            {
                "id": canonical_id,
                "candidate": True,
                "document_rank": hit.rerank_rank,
                "document_score": hit.rerank_score,
                "chunk_count": len(chunks),
                "best_entailment": best.entailment if best else None,
                "best_chunk": best.text if best else None,
            }
        )

    return {
        "id": case_id,
        "kind": str(case["kind"]),
        "claim": claim,
        "rows": rows,
    }


def _shorten(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe concrete candidate-answer entailment without changing retrieval selection."
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
        claim_ids = set(DEVELOPMENT_CLAIMS)
        if case_ids != claim_ids:
            missing = sorted(case_ids - claim_ids)
            extra = sorted(claim_ids - case_ids)
            raise ValueError(f"development claim coverage mismatch: missing={missing} extra={extra}")
        retriever = RerankedRetriever(ROOT)
        nli = OnnxNliBackend() if args.model is None else OnnxNliBackend(args.model)
        cases = [probe_case(case, retriever, nli) for case in acceptance["cases"]]
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Concrete-entailment development probe: {acceptance['name']}")
    print(f"Frozen selector candidate: {acceptance['frozen_candidate']}")
    print("NOTE: observed blind-v3 cases; this output is diagnostic, not acceptance evidence.")
    for case in cases:
        print(f"[{case['kind'].upper():8}] {case['id']}")
        print(f"       claim: {case['claim']}")
        for row in case["rows"]:
            if not row["candidate"]:
                print(f"       {row['id']}: candidate=no")
                continue
            entailment = row["best_entailment"]
            entailment_text = "None" if entailment is None else f"{float(entailment):.4f}"
            print(
                f"       {row['id']}: R={row['document_rank']} doc={float(row['document_score']):.4f} "
                f"entail={entailment_text} chunks={row['chunk_count']}"
            )
            if row["best_chunk"]:
                print(f"           evidence: {_shorten(str(row['best_chunk']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
