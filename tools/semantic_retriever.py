from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence

from context_compiler import CanonicalRecord, load_canonical_store, prepare_query


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_TOP_K = 8


class EmbeddingBackend(Protocol):
    model_name: str

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


def default_cache_dir() -> Path:
    override = os.environ.get("QIVEN_FASTEMBED_CACHE", "").strip()
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", "").strip()
        if base:
            return Path(base) / "Qiven" / "fastembed"
    xdg = os.environ.get("XDG_CACHE_HOME", "").strip()
    if xdg:
        return Path(xdg) / "qiven" / "fastembed"
    return Path.home() / ".cache" / "qiven" / "fastembed"


class FastEmbedBackend:
    def __init__(self, model_name: str = DEFAULT_MODEL, cache_dir: Path | None = None) -> None:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise RuntimeError(
                "semantic retrieval requires the optional FastEmbed dependency; "
                "run tools\\bootstrap-semantic.cmd first"
            ) from exc
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(self.cache_dir))

    @staticmethod
    def _materialize(vectors: Iterable[Any]) -> list[list[float]]:
        result: list[list[float]] = []
        for vector in vectors:
            values = vector.tolist() if hasattr(vector, "tolist") else list(vector)
            result.append([float(value) for value in values])
        return result

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._materialize(self._model.embed(list(texts)))

    def embed_query(self, text: str) -> list[float]:
        vectors = self._materialize(self._model.embed([text]))
        if len(vectors) != 1:
            raise RuntimeError("semantic backend returned an unexpected query embedding count")
        return vectors[0]


def _query_text(query: Mapping[str, Any], root: Path = ROOT) -> str:
    prepared = prepare_query(query, root)
    lines = [f"task: {prepared['task']}"]
    for key in ("topics", "scopes", "touches", "signals", "conditions", "changed"):
        values = prepared.get(key, []) or []
        if values:
            lines.append(f"{key}: {', '.join(str(value) for value in values)}")
    return "\n".join(lines)


def _record_text(record: CanonicalRecord) -> str:
    metadata = record.metadata
    lines = [f"category: {record.category}", f"id: {record.id}", f"title: {record.title}", f"status: {record.status}"]
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


def eligible_records(root: Path = ROOT) -> tuple[CanonicalRecord, ...]:
    """Return only records eligible for default current-state retrieval.

    Superseded/rejected/history remains addressable from canonical files and Git,
    but it must not compete with current truth in the normal retrieval corpus.
    """
    store = load_canonical_store(root)
    rows: list[CanonicalRecord] = [
        record for record in store["decisions"] if record.status == "accepted"
    ]
    rows.extend(record for record in store["memory"] if record.status == "active")
    rows.extend(
        record
        for record in store["obligations"]
        if record.status in {"open", "deferred", "blocked"}
    )
    return tuple(sorted(rows, key=lambda record: record.id))


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions do not match")
    dot = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) * float(value) for value in left))
    right_norm = math.sqrt(sum(float(value) * float(value) for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


@dataclass(frozen=True)
class SemanticHit:
    id: str
    category: str
    path: str
    title: str
    score: float


class SemanticRetriever:
    def __init__(self, root: Path = ROOT, *, backend: EmbeddingBackend | None = None, model_name: str = DEFAULT_MODEL) -> None:
        self.root = Path(root)
        self.backend = backend if backend is not None else FastEmbedBackend(model_name=model_name)
        self.model_name = str(self.backend.model_name)
        self.records = eligible_records(self.root)
        documents = [_record_text(record) for record in self.records]
        self.document_vectors = self.backend.embed_documents(documents)
        if len(self.document_vectors) != len(self.records):
            raise RuntimeError("semantic backend returned an unexpected document embedding count")

    def rank(self, query: Mapping[str, Any]) -> list[SemanticHit]:
        query_vector = self.backend.embed_query(_query_text(query, self.root))
        hits = [
            SemanticHit(id=record.id, category=record.category, path=record.path, title=record.title, score=cosine_similarity(query_vector, vector))
            for record, vector in zip(self.records, self.document_vectors)
        ]
        return sorted(hits, key=lambda hit: (-hit.score, hit.id))

    def select_ids(self, query: Mapping[str, Any], *, top_k: int = DEFAULT_TOP_K) -> set[str]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        explicit = [str(item) for item in query.get("include_ids", []) or []]
        selected: list[str] = []
        seen: set[str] = set()
        eligible_ids = {record.id for record in self.records}
        for canonical_id in explicit:
            if canonical_id in eligible_ids and canonical_id not in seen:
                selected.append(canonical_id); seen.add(canonical_id)
        for hit in self.rank(query):
            if len(selected) >= top_k:
                break
            if hit.id not in seen:
                selected.append(hit.id); seen.add(hit.id)
        return set(selected)
