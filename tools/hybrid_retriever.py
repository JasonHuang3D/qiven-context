from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from context_compiler import compile_context_pack
from semantic_retriever import DEFAULT_MODEL, SemanticHit, SemanticRetriever


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOP_K = 8
DEFAULT_RRF_K = 60


@dataclass(frozen=True)
class DeterministicHit:
    id: str
    category: str
    score: int


@dataclass(frozen=True)
class HybridHit:
    id: str
    score: float
    deterministic_rank: int | None
    semantic_rank: int | None


class SemanticRanker(Protocol):
    model_name: str

    def rank(self, query: Mapping[str, Any]) -> Sequence[SemanticHit]:
        ...


DeterministicRanker = Callable[[Mapping[str, Any], Path], Sequence[DeterministicHit]]


def _count_reason_values(value: str) -> int:
    return max(1, len([part for part in value.split(",") if part.strip()]))


def deterministic_reason_score(category: str, reasons: Sequence[Mapping[str, str]]) -> int:
    """Reconstruct the compiler's direct selection score from emitted reasons.

    The Context Compiler deliberately emits only selected records. This adapter
    does not create a second lexical engine; it converts the compiler's own
    selection reasons back into a stable rank suitable for fusion experiments.
    """

    score = 0
    kinds = [str(reason.get("kind", "")) for reason in reasons]
    for reason in reasons:
        kind = str(reason.get("kind", ""))
        value = str(reason.get("value", ""))
        if kind == "explicit_id":
            score += 1000
        elif kind == "scope_match":
            score += 120
        elif kind == "tag_match":
            score += 80
        elif kind == "project_match":
            score += 60
        elif kind == "title_match":
            score += min(90, 30 * _count_reason_values(value))
        elif kind == "content_match":
            score += min(16, 4 * _count_reason_values(value))
        elif kind == "trigger_due":
            score += 240
        elif kind == "trigger_applicable":
            score += 180
        elif kind == "related_record":
            # Decisions/memory are relation-only when this reason is emitted;
            # obligations receive relation as a corroborating +40 booster.
            score += 40 if category == "obligations" and len(kinds) > 1 else 25
    return score


def deterministic_rank(query: Mapping[str, Any], root: Path = ROOT) -> list[DeterministicHit]:
    pack = compile_context_pack(query, root)
    rows: list[DeterministicHit] = []
    for category in ("decisions", "memory", "obligations"):
        for item in pack.get(category, []) or []:
            canonical_id = item.get("id")
            if not canonical_id:
                continue
            rows.append(
                DeterministicHit(
                    id=str(canonical_id),
                    category=category,
                    score=deterministic_reason_score(category, item.get("reasons", []) or []),
                )
            )
    return sorted(rows, key=lambda hit: (-hit.score, hit.id))


def reciprocal_rank(rank: int | None, *, k: int = DEFAULT_RRF_K) -> float:
    if rank is None:
        return 0.0
    if rank < 1:
        raise ValueError("rank must be >= 1")
    if k < 1:
        raise ValueError("RRF k must be >= 1")
    return 1.0 / (k + rank)


class HybridRetriever:
    """Equal-weight RRF over compiler ranking and semantic ranking.

    The constants are intentionally frozen before observing hybrid benchmark
    results: RRF k=60 and final top_k=8. Explicit IDs remain hard inclusions.
    """

    def __init__(
        self,
        root: Path = ROOT,
        *,
        semantic_retriever: SemanticRanker | None = None,
        semantic_model: str = DEFAULT_MODEL,
        deterministic_ranker: DeterministicRanker | None = None,
    ) -> None:
        self.root = Path(root)
        self.semantic_retriever = (
            semantic_retriever
            if semantic_retriever is not None
            else SemanticRetriever(self.root, model_name=semantic_model)
        )
        self.semantic_model = str(self.semantic_retriever.model_name)
        self.deterministic_ranker = deterministic_ranker or deterministic_rank

    def rank(self, query: Mapping[str, Any]) -> list[HybridHit]:
        deterministic = list(self.deterministic_ranker(query, self.root))
        semantic = list(self.semantic_retriever.rank(query))
        deterministic_positions = {hit.id: index for index, hit in enumerate(deterministic, 1)}
        semantic_positions = {hit.id: index for index, hit in enumerate(semantic, 1)}
        ids = set(deterministic_positions) | set(semantic_positions)

        hits = [
            HybridHit(
                id=canonical_id,
                score=(
                    reciprocal_rank(deterministic_positions.get(canonical_id))
                    + reciprocal_rank(semantic_positions.get(canonical_id))
                ),
                deterministic_rank=deterministic_positions.get(canonical_id),
                semantic_rank=semantic_positions.get(canonical_id),
            )
            for canonical_id in ids
        ]
        return sorted(hits, key=lambda hit: (-hit.score, hit.id))

    def select_ids(self, query: Mapping[str, Any], *, top_k: int = DEFAULT_TOP_K) -> set[str]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        selected: list[str] = []
        seen: set[str] = set()
        explicit = [str(item) for item in query.get("include_ids", []) or []]
        ranked = self.rank(query)
        ranked_ids = {hit.id for hit in ranked}

        for canonical_id in explicit:
            if canonical_id in ranked_ids and canonical_id not in seen:
                selected.append(canonical_id)
                seen.add(canonical_id)

        for hit in ranked:
            if len(selected) >= top_k:
                break
            if hit.id not in seen:
                selected.append(hit.id)
                seen.add(hit.id)
        return set(selected)
