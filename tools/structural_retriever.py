from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from record_lifecycle import record_is_eligible

from context_compiler import CanonicalRecord, compile_context_pack
from hybrid_retriever import DEFAULT_RRF_K, DEFAULT_TOP_K, HybridRetriever, reciprocal_rank
from semantic_retriever import DEFAULT_MODEL, eligible_records


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH_SEED_TOP_K = 4
DEFAULT_GRAPH_DEPTH = 1


@dataclass(frozen=True)
class StructuralHit:
    id: str
    score: float
    structural_rank: int | None
    hybrid_rank: int
    deterministic_rank: int | None
    semantic_rank: int | None
    graph_rank: int | None
    scope_compatible: bool


def canonical_record_map(root: Path = ROOT, query: Mapping[str, Any] | None = None) -> dict[str, CanonicalRecord]:
    return {record.id: record for record in eligible_records(root, query)}


def project_scopes(record: CanonicalRecord) -> set[str]:
    return {
        str(scope).casefold()
        for scope in record.metadata.get("scope", []) or []
        if str(scope).casefold().startswith("qiven-")
    }


def infer_active_project_scopes(query: Mapping[str, Any], root: Path = ROOT) -> set[str]:
    """Use the existing Context Compiler's project selection as the scope resolver."""
    pack = compile_context_pack(query, root)
    active: set[str] = set()
    for item in pack.get("projects", []) or []:
        path = Path(str(item["path"]))
        if len(path.parts) >= 2 and path.parts[0] == "projects":
            active.add(f"qiven-{path.parts[1]}".casefold())
    return active


def is_scope_compatible(
    record: CanonicalRecord,
    active_project_scopes: set[str],
    *,
    explicit_ids: set[str] | None = None,
) -> bool:
    if explicit_ids and record.id in explicit_ids:
        return True
    if not active_project_scopes:
        return True
    record_scopes = project_scopes(record)
    if not record_scopes:
        return True
    return bool(record_scopes & active_project_scopes)


def bidirectional_relation_graph(
    records: Mapping[str, CanonicalRecord],
) -> dict[str, set[str]]:
    graph = {canonical_id: set() for canonical_id in records}
    for record in records.values():
        for related in record.metadata.get("related", []) or []:
            related_id = str(related)
            if related_id not in records or related_id == record.id:
                continue
            graph[record.id].add(related_id)
            graph[related_id].add(record.id)
    return graph


def graph_channel_rank(
    graph: Mapping[str, set[str]],
    seed_ids: Sequence[str],
    *,
    allowed_ids: set[str],
    depth: int = DEFAULT_GRAPH_DEPTH,
) -> dict[str, int]:
    if depth != 1:
        raise ValueError("Phase 1 structural retrieval freezes graph depth at 1")
    ranked: list[str] = []
    seen: set[str] = set()
    for seed_id in seed_ids:
        for neighbor in sorted(graph.get(seed_id, set())):
            if neighbor not in allowed_ids or neighbor in seen:
                continue
            seen.add(neighbor)
            ranked.append(neighbor)
    return {canonical_id: index for index, canonical_id in enumerate(ranked, 1)}


class StructuralRetriever:
    """Hybrid RRF plus project-scope compatibility and one-hop relation evidence.

    Phase 1 freezes these structural parameters before benchmark observation:
    final top_k=8, hybrid RRF k=60, graph seed top_k=4, graph depth=1,
    and an equal-weight graph RRF channel.
    """

    def __init__(
        self,
        root: Path = ROOT,
        *,
        hybrid_retriever: HybridRetriever | None = None,
        semantic_model: str = DEFAULT_MODEL,
        graph_seed_top_k: int = DEFAULT_GRAPH_SEED_TOP_K,
    ) -> None:
        if graph_seed_top_k < 1:
            raise ValueError("graph_seed_top_k must be >= 1")
        self.root = Path(root)
        self.hybrid = (
            hybrid_retriever
            if hybrid_retriever is not None
            else HybridRetriever(self.root, semantic_model=semantic_model)
        )
        self.semantic_model = str(self.hybrid.semantic_model)
        self.graph_seed_top_k = graph_seed_top_k
        self.records = canonical_record_map(self.root, {"record_mode": "history"})
        self.graph = bidirectional_relation_graph(self.records)

    def rank(self, query: Mapping[str, Any]) -> list[StructuralHit]:
        explicit_ids = {str(item) for item in query.get("include_ids", []) or []}
        active_scopes = infer_active_project_scopes(query, self.root)
        base_hits = list(self.hybrid.rank(query))
        base_positions = {hit.id: index for index, hit in enumerate(base_hits, 1)}

        compatible_ids = {
            canonical_id
            for canonical_id, record in self.records.items()
            if record_is_eligible(record, query)
            and is_scope_compatible(record, active_scopes, explicit_ids=explicit_ids)
        }
        compatible_base = [hit for hit in base_hits if hit.id in compatible_ids]
        seed_ids = [hit.id for hit in compatible_base[: self.graph_seed_top_k]]
        graph_positions = graph_channel_rank(
            self.graph,
            seed_ids,
            allowed_ids=compatible_ids,
            depth=DEFAULT_GRAPH_DEPTH,
        )

        rows: list[StructuralHit] = []
        for base_hit in compatible_base:
            graph_rank = graph_positions.get(base_hit.id)
            score = base_hit.score + reciprocal_rank(graph_rank, k=DEFAULT_RRF_K)
            rows.append(
                StructuralHit(
                    id=base_hit.id,
                    score=score,
                    structural_rank=None,
                    hybrid_rank=base_positions[base_hit.id],
                    deterministic_rank=base_hit.deterministic_rank,
                    semantic_rank=base_hit.semantic_rank,
                    graph_rank=graph_rank,
                    scope_compatible=True,
                )
            )

        ranked = sorted(rows, key=lambda hit: (-hit.score, hit.id))
        return [
            StructuralHit(
                id=hit.id,
                score=hit.score,
                structural_rank=index,
                hybrid_rank=hit.hybrid_rank,
                deterministic_rank=hit.deterministic_rank,
                semantic_rank=hit.semantic_rank,
                graph_rank=hit.graph_rank,
                scope_compatible=hit.scope_compatible,
            )
            for index, hit in enumerate(ranked, 1)
        ]

    def select_ids(self, query: Mapping[str, Any], *, top_k: int = DEFAULT_TOP_K) -> set[str]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        ranked = self.rank(query)
        available = {hit.id for hit in ranked}
        selected: list[str] = []
        seen: set[str] = set()
        for canonical_id in (str(item) for item in query.get("include_ids", []) or []):
            if canonical_id in available and canonical_id not in seen:
                selected.append(canonical_id)
                seen.add(canonical_id)
        for hit in ranked:
            if len(selected) >= top_k:
                break
            if hit.id not in seen:
                selected.append(hit.id)
                seen.add(hit.id)
        return set(selected)
