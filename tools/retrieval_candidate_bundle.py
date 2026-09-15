from __future__ import annotations

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
    ranked = list(active.rank(prepared))[:max_candidates]

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
        "schema_version": 1,
        "role": CANDIDATE_ROLE,
        "answerability": "unresolved",
        "instruction": CANDIDATE_INSTRUCTION,
        "query": prepared,
        "max_candidates": max_candidates,
        "candidates": candidates,
    }
