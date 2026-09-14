from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from rerank_retriever import RerankedRetriever, query_text  # noqa: E402
from retrieval_acceptance import load_acceptance  # noqa: E402


MAX_CHUNK_CHARS = 900
TOP_DOCUMENTS_TO_PROBE = 3
SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?。！？])\s+")


@dataclass(frozen=True)
class EvidenceChunkScore:
    text: str
    score: float


def _split_long_text(text: str, *, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    sentences = [part.strip() for part in SENTENCE_BOUNDARY_RE.split(text) if part.strip()]
    if len(sentences) <= 1:
        return [text[index : index + max_chars] for index in range(0, len(text), max_chars)]

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if not current:
            current = sentence
            continue
        candidate = f"{current} {sentence}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.extend(_split_long_text(current, max_chars=max_chars))
            current = sentence
    if current:
        chunks.extend(_split_long_text(current, max_chars=max_chars))
    return chunks


def record_evidence_chunks(record: Any) -> list[str]:
    metadata = record.metadata
    chunks: list[str] = []

    title = str(record.title).strip()
    if title:
        chunks.append(f"title: {title}")

    for key in ("statement", "why_it_exists", "why_not_now", "completion"):
        value = metadata.get(key)
        if value:
            chunks.extend(_split_long_text(f"{key}: {value}"))

    body = str(record.body).strip()
    if body:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
        for paragraph in paragraphs:
            normalized = " ".join(
                line.strip()
                for line in paragraph.splitlines()
                if line.strip() and not line.strip().startswith("#")
            )
            if normalized:
                chunks.extend(_split_long_text(normalized))

    unique: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        normalized = chunk.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return unique


def score_record_evidence(
    retriever: RerankedRetriever,
    query: Mapping[str, Any],
    canonical_id: str,
) -> list[EvidenceChunkScore]:
    record = retriever.records[canonical_id]
    chunks = record_evidence_chunks(record)
    if not chunks:
        return []
    scores = retriever.reranker.score(query_text(query, retriever.root), chunks)
    rows = [
        EvidenceChunkScore(text=chunk, score=float(score))
        for chunk, score in zip(chunks, scores)
    ]
    return sorted(rows, key=lambda row: (-row.score, row.text))


def _shorten(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def probe_case(case: Mapping[str, Any], retriever: RerankedRetriever) -> dict[str, Any]:
    ranked = retriever.rank(case["query"])
    by_id = {hit.id: hit for hit in ranked}
    watched: set[str] = {
        *(str(item) for item in case.get("required_ids", []) or []),
        *(str(item) for item in case.get("forbidden_ids", []) or []),
    }
    watched.update(hit.id for hit in ranked[:TOP_DOCUMENTS_TO_PROBE])

    rows: list[dict[str, Any]] = []
    for canonical_id in sorted(watched):
        hit = by_id.get(canonical_id)
        if hit is None:
            rows.append(
                {
                    "id": canonical_id,
                    "candidate": False,
                    "document_rank": None,
                    "document_score": None,
                    "best_chunk_score": None,
                    "best_chunk": None,
                    "chunk_count": 0,
                }
            )
            continue
        evidence = score_record_evidence(retriever, case["query"], canonical_id)
        best = evidence[0] if evidence else None
        rows.append(
            {
                "id": canonical_id,
                "candidate": True,
                "document_rank": hit.rerank_rank,
                "document_score": hit.rerank_score,
                "best_chunk_score": best.score if best else None,
                "best_chunk": best.text if best else None,
                "chunk_count": len(evidence),
            }
        )

    return {
        "id": str(case["id"]),
        "kind": str(case["kind"]),
        "rows": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure passage-level evidence separability without changing retrieval selection."
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=Path("benchmarks/retrieval/blind-v3.yaml"),
        help="Acceptance YAML to probe.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.acceptance if args.acceptance.is_absolute() else ROOT / args.acceptance
    try:
        acceptance = load_acceptance(path, ROOT)
        retriever = RerankedRetriever(ROOT)
        cases = [probe_case(case, retriever) for case in acceptance["cases"]]
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Evidence-span probe: {acceptance['name']}")
    print(f"Frozen selector candidate: {acceptance['frozen_candidate']}")
    print(f"max_chunk_chars={MAX_CHUNK_CHARS} top_documents={TOP_DOCUMENTS_TO_PROBE}")
    for case in cases:
        print(f"[{case['kind'].upper():8}] {case['id']}")
        for row in case["rows"]:
            if not row["candidate"]:
                print(f"       {row['id']}: candidate=no")
                continue
            document_score = float(row["document_score"])
            chunk_score = row["best_chunk_score"]
            chunk_score_text = "None" if chunk_score is None else f"{float(chunk_score):.4f}"
            print(
                f"       {row['id']}: R={row['document_rank']} doc={document_score:.4f} "
                f"best_chunk={chunk_score_text} chunks={row['chunk_count']}"
            )
            if row["best_chunk"]:
                print(f"           evidence: {_shorten(str(row['best_chunk']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
