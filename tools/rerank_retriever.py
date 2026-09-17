from __future__ import annotations

from context_snapshot import bind_snapshot

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from record_lifecycle import record_is_eligible

from context_compiler import CanonicalRecord, prepare_query
from hybrid_retriever import HybridHit, HybridRetriever
from semantic_retriever import DEFAULT_MODEL, eligible_records
from structural_retriever import (
    bidirectional_relation_graph,
    infer_active_project_scopes,
    is_scope_compatible,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RERANK_MODEL = "BAAI/bge-reranker-base"
DEFAULT_SEMANTIC_POOL_TOP_K = 16
DEFAULT_GRAPH_SEED_TOP_K = 1


class RerankerBackend(Protocol):
    model_name: str

    def score(self, query: str, documents: Sequence[str]) -> list[float]:
        ...


class FastEmbedRerankerBackend:
    def __init__(self, model_name: str = DEFAULT_RERANK_MODEL) -> None:
        try:
            from fastembed.rerank.cross_encoder import TextCrossEncoder
        except ImportError as exc:
            raise RuntimeError(
                "reranked retrieval requires the optional FastEmbed runtime; "
                "run tools\\bootstrap-semantic.cmd first"
            ) from exc

        self.model_name = model_name
        self._encoder = TextCrossEncoder(model_name=model_name)

    def score(self, query: str, documents: Sequence[str]) -> list[float]:
        scores = [float(value) for value in self._encoder.rerank(query, list(documents))]
        if len(scores) != len(documents):
            raise RuntimeError("reranker returned an unexpected score count")
        return scores


@dataclass(frozen=True)
class CandidateEvidence:
    id: str
    hybrid_rank: int
    deterministic_rank: int | None
    semantic_rank: int | None
    graph_candidate: bool
    explicit: bool


@dataclass(frozen=True)
class RerankHit:
    id: str
    rerank_score: float
    rerank_rank: int
    hybrid_rank: int
    deterministic_rank: int | None
    semantic_rank: int | None
    graph_candidate: bool
    explicit: bool


def canonical_record_map(root: Path = ROOT, query: Mapping[str, Any] | None = None) -> dict[str, CanonicalRecord]:
    return {record.id: record for record in eligible_records(root, query)}


def query_text(query: Mapping[str, Any], root: Path = ROOT) -> str:
    prepared = prepare_query(query, root)
    lines = [f"task: {prepared['task']}"]
    for key in ("topics", "scopes", "touches", "signals", "conditions", "changed"):
        values = prepared.get(key, []) or []
        if values:
            lines.append(f"{key}: {', '.join(str(value) for value in values)}")
    return "\n".join(lines)


def record_text(record: CanonicalRecord) -> str:
    metadata = record.metadata
    lines = [
        f"category: {record.category}",
        f"id: {record.id}",
        f"title: {record.title}",
        f"status: {record.status}",
    ]
    scopes = metadata.get("scope", []) or []
    tags = metadata.get("tags", []) or []
    if scopes:
        lines.append("scope: " + ", ".join(str(item) for item in scopes))
    if tags:
        lines.append("tags: " + ", ".join(str(item) for item in tags))
    for key in ("statement", "why_it_exists", "why_not_now", "completion"):
        value = metadata.get(key)
        if value:
            lines.append(f"{key}: {value}")
    body = record.body.strip()
    if body:
        lines.append(body)
    return "\n".join(lines)


class RerankedRetriever:
    """High-recall candidate generation followed by cross-encoder reranking.

    Relation edges are candidate evidence only. They do not add a ranking score.
    Reranking answers only which canonical evidence cognition should inspect
    first. It deliberately does not decide answerability or promote candidates
    into selected truth.
    """

    def __init__(
        self,
        root: Path = ROOT,
        *,
        hybrid_retriever: HybridRetriever | None = None,
        reranker_backend: RerankerBackend | None = None,
        semantic_model: str = DEFAULT_MODEL,
        rerank_model: str = DEFAULT_RERANK_MODEL,
    ) -> None:
        self.snapshot = bind_snapshot(root, hybrid_retriever)
        self.root = self.snapshot
        self.hybrid = (
            hybrid_retriever
            if hybrid_retriever is not None
            else HybridRetriever(self.root, semantic_model=semantic_model)
        )
        self.reranker = (
            reranker_backend
            if reranker_backend is not None
            else FastEmbedRerankerBackend(rerank_model)
        )
        self.semantic_model = str(self.hybrid.semantic_model)
        self.rerank_model = str(self.reranker.model_name)
        self.records = canonical_record_map(self.root, {"record_mode": "history"})
        self.graph = bidirectional_relation_graph(self.records)

    def candidate_evidence(self, query: Mapping[str, Any]) -> list[CandidateEvidence]:
        explicit_ids = {str(item) for item in query.get("include_ids", []) or []}
        active_scopes = infer_active_project_scopes(query, self.root)
        base_hits = list(self.hybrid.rank(query))
        compatible = [
            hit
            for hit in base_hits
            if hit.id in self.records
            and record_is_eligible(self.records[hit.id], query)
            and is_scope_compatible(
                self.records[hit.id], active_scopes, explicit_ids=explicit_ids
            )
        ]
        if not compatible:
            return []

        base_positions = {hit.id: index for index, hit in enumerate(base_hits, 1)}
        by_id = {hit.id: hit for hit in compatible}
        candidate_ids: set[str] = set(explicit_ids) & set(by_id)

        candidate_ids.update(
            hit.id for hit in compatible if hit.deterministic_rank is not None
        )
        candidate_ids.update(
            hit.id
            for hit in compatible
            if hit.semantic_rank is not None
            and hit.semantic_rank <= DEFAULT_SEMANTIC_POOL_TOP_K
        )

        seed_ids = [hit.id for hit in compatible[:DEFAULT_GRAPH_SEED_TOP_K]]
        graph_ids: set[str] = set()
        compatible_ids = set(by_id)
        for seed_id in seed_ids:
            graph_ids.update(
                neighbor
                for neighbor in self.graph.get(seed_id, set())
                if neighbor in compatible_ids
            )
        candidate_ids.update(graph_ids)

        rows: list[CandidateEvidence] = []
        for canonical_id in candidate_ids:
            hit: HybridHit = by_id[canonical_id]
            rows.append(
                CandidateEvidence(
                    id=canonical_id,
                    hybrid_rank=base_positions[canonical_id],
                    deterministic_rank=hit.deterministic_rank,
                    semantic_rank=hit.semantic_rank,
                    graph_candidate=canonical_id in graph_ids,
                    explicit=canonical_id in explicit_ids,
                )
            )
        return sorted(rows, key=lambda row: (row.hybrid_rank, row.id))

    def rank(self, query: Mapping[str, Any]) -> list[RerankHit]:
        evidence = self.candidate_evidence(query)
        if not evidence:
            return []
        documents = [record_text(self.records[item.id]) for item in evidence]
        scores = self.reranker.score(query_text(query, self.root), documents)
        scored = sorted(
            zip(evidence, scores),
            key=lambda pair: (-pair[1], pair[0].hybrid_rank, pair[0].id),
        )
        return [
            RerankHit(
                id=item.id,
                rerank_score=float(score),
                rerank_rank=index,
                hybrid_rank=item.hybrid_rank,
                deterministic_rank=item.deterministic_rank,
                semantic_rank=item.semantic_rank,
                graph_candidate=item.graph_candidate,
                explicit=item.explicit,
            )
            for index, (item, score) in enumerate(scored, 1)
        ]
