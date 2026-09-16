from __future__ import annotations

from record_lifecycle import lifecycle_fields, record_is_eligible
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_CANDIDATES = 3
CANDIDATE_ROLE = "untrusted_candidate_evidence"
CANDIDATE_INSTRUCTION = (
    "Retrieved candidates are leads, not selected truth. Their presence or ranking score does not "
    "establish that the task is answerable. The cognition layer must read the candidate content, "
    "use only propositions directly supported by canonical evidence, preserve source provenance, "
    "and abstain when the bundle does not answer the task."
)


def build_candidate_bundle(
    query: Mapping[str, Any],
    retriever: Any | None = None,
    *,
    root: Path = ROOT,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> dict[str, Any]:
    """Build a small provenance-preserving retrieval bundle for the reasoning layer.

    This deliberately does not perform answerability selection. Reranking answers
    "what evidence should cognition read first?" rather than "what is true?".
    """

    if max_candidates < 1:
        raise ValueError("max_candidates must be >= 1")

    # Imports remain lazy so normal context-compiler use does not acquire the
    # optional semantic/reranker runtime merely by importing this module.
    from context_compiler import prepare_query
    from rerank_retriever import RerankedRetriever, record_text

    root = Path(root)
    prepared = prepare_query(query, root)
    active = retriever if retriever is not None else RerankedRetriever(root)
    ranked = [hit for hit in active.rank(prepared)
              if record_is_eligible(active.records[hit.id], prepared)]
    explicit = set(prepared["include_ids"])
    pinned = [hit for hit in ranked if hit.id in explicit]
    if len(pinned) > max_candidates:
        raise ValueError("explicit IDs exceed max_candidates; increase the candidate ceiling")
    selected = {hit.id for hit in pinned}
    for hit in ranked:
        if len(selected) >= max_candidates:
            break
        selected.add(hit.id)
    ranked = [hit for hit in ranked if hit.id in selected]

    candidates: list[dict[str, Any]] = []
    for hit in ranked:
        record = active.records[hit.id]
        candidates.append(
            {
                "id": record.id,
                "path": record.path,
                "category": record.category,
                "title": record.title,
                "status": record.status,
                **lifecycle_fields(record),
                "candidate_rank": hit.rerank_rank,
                "ranking": {
                    "rerank_score": hit.rerank_score,
                    "hybrid_rank": hit.hybrid_rank,
                    "deterministic_rank": hit.deterministic_rank,
                    "semantic_rank": hit.semantic_rank,
                    "graph_candidate": hit.graph_candidate,
                    "explicit": hit.explicit,
                },
                "content": record_text(record),
            }
        )

    return {
        "schema_version": 2,
        "role": CANDIDATE_ROLE,
        "answerability": "unresolved",
        "instruction": CANDIDATE_INSTRUCTION,
        "query": prepared,
        "max_candidates": max_candidates,
        "candidates": candidates,
        "diagnostics": [
            {"code": "unknown-explicit-id", "id": canonical_id}
            for canonical_id in sorted(explicit - set(active.records))
        ],
    }
