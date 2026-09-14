from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evidence_span_probe import record_evidence_chunks  # noqa: E402
from rerank_retriever import RerankedRetriever  # noqa: E402
from retrieval_acceptance import load_acceptance  # noqa: E402


DEFAULT_NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
DEFAULT_NLI_ONNX_FILE = "onnx/model_quantized.onnx"
MAX_NLI_TOKENS = 512
TOP_NEGATIVE_DOCUMENTS = 3
SUFFICIENT_HYPOTHESIS = "The evidence contains enough information to answer the question."
INSUFFICIENT_HYPOTHESIS = "The evidence does not contain enough information to answer the question."


@dataclass(frozen=True)
class NliEvidenceScore:
    text: str
    sufficient_entailment: float
    insufficient_entailment: float
    margin: float


def _softmax(row: Sequence[float]) -> list[float]:
    values = [float(value) for value in row]
    if not values:
        raise ValueError("softmax requires at least one value")
    maximum = max(values)
    exps = [math.exp(value - maximum) for value in values]
    total = sum(exps)
    return [value / total for value in exps]


def default_cache_dir() -> Path:
    override = os.environ.get("QIVEN_NLI_CACHE", "").strip()
    if override:
        return Path(override)
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "Qiven" / "nli"
    return Path.home() / ".cache" / "qiven" / "nli"


def question_text(query: Mapping[str, Any]) -> str:
    parts = [str(query["task"]).strip()]
    for key in ("topics", "scopes", "touches", "signals", "conditions", "changed"):
        values = [str(value).strip() for value in query.get(key, []) or [] if str(value).strip()]
        if values:
            parts.append(f"{key}: {', '.join(values)}")
    return "\n".join(parts)


def nli_premise(question: str, evidence: str) -> str:
    return f"Question: {question}\nEvidence: {evidence}"


class OnnxNliBackend:
    """Small experimental multilingual NLI backend using existing semantic-runtime deps.

    This is deliberately a probe backend, not a production selector. It uses the
    quantized ONNX export so the experiment does not introduce PyTorch.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_NLI_MODEL,
        *,
        cache_dir: Path | None = None,
    ) -> None:
        try:
            from huggingface_hub import hf_hub_download
            import onnxruntime as ort
            from tokenizers import Tokenizer
        except ImportError as exc:
            raise RuntimeError(
                "NLI probe requires the optional semantic runtime; run tools\\bootstrap-semantic.cmd first"
            ) from exc

        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        tokenizer_path = hf_hub_download(
            repo_id=model_name,
            filename="tokenizer.json",
            cache_dir=str(self.cache_dir),
        )
        model_path = hf_hub_download(
            repo_id=model_name,
            filename=DEFAULT_NLI_ONNX_FILE,
            cache_dir=str(self.cache_dir),
        )

        self._tokenizer = Tokenizer.from_file(tokenizer_path)
        self._tokenizer.enable_truncation(max_length=MAX_NLI_TOKENS)
        self._tokenizer.enable_padding(pad_id=0)
        self._session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self._input_names = {item.name for item in self._session.get_inputs()}

    def entailment_probabilities(
        self,
        premises: Sequence[str],
        hypotheses: Sequence[str],
    ) -> list[float]:
        if len(premises) != len(hypotheses):
            raise ValueError("premises and hypotheses must have the same length")
        if not premises:
            return []

        encodings = self._tokenizer.encode_batch(list(zip(premises, hypotheses)))
        input_ids = np.asarray([encoding.ids for encoding in encodings], dtype=np.int64)
        attention_mask = np.asarray(
            [encoding.attention_mask for encoding in encodings], dtype=np.int64
        )
        type_ids = np.asarray([encoding.type_ids for encoding in encodings], dtype=np.int64)

        feeds: dict[str, np.ndarray] = {}
        if "input_ids" in self._input_names:
            feeds["input_ids"] = input_ids
        if "attention_mask" in self._input_names:
            feeds["attention_mask"] = attention_mask
        if "token_type_ids" in self._input_names:
            feeds["token_type_ids"] = type_ids
        missing = self._input_names - set(feeds)
        if missing:
            raise RuntimeError(f"unsupported NLI ONNX inputs: {sorted(missing)}")

        logits = self._session.run(None, feeds)[0]
        result: list[float] = []
        for row in logits:
            probabilities = _softmax(row)
            # Model config freezes id2label: 0=entailment, 1=neutral, 2=contradiction.
            result.append(float(probabilities[0]))
        return result


def score_answerability(
    backend: OnnxNliBackend,
    query: Mapping[str, Any],
    chunks: Sequence[str],
) -> list[NliEvidenceScore]:
    if not chunks:
        return []
    question = question_text(query)
    premises: list[str] = []
    hypotheses: list[str] = []
    for chunk in chunks:
        premise = nli_premise(question, chunk)
        premises.extend((premise, premise))
        hypotheses.extend((SUFFICIENT_HYPOTHESIS, INSUFFICIENT_HYPOTHESIS))
    entailments = backend.entailment_probabilities(premises, hypotheses)

    rows: list[NliEvidenceScore] = []
    for index, chunk in enumerate(chunks):
        sufficient = entailments[index * 2]
        insufficient = entailments[index * 2 + 1]
        rows.append(
            NliEvidenceScore(
                text=chunk,
                sufficient_entailment=sufficient,
                insufficient_entailment=insufficient,
                margin=sufficient - insufficient,
            )
        )
    return sorted(rows, key=lambda row: (-row.margin, -row.sufficient_entailment, row.text))


def _shorten(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def probe_case(
    case: Mapping[str, Any],
    retriever: RerankedRetriever,
    nli: OnnxNliBackend,
) -> dict[str, Any]:
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
        evidence = score_answerability(nli, case["query"], chunks)
        best = evidence[0] if evidence else None
        rows.append(
            {
                "id": canonical_id,
                "candidate": True,
                "document_rank": hit.rerank_rank,
                "document_score": hit.rerank_score,
                "chunk_count": len(chunks),
                "best_sufficient": best.sufficient_entailment if best else None,
                "best_insufficient": best.insufficient_entailment if best else None,
                "best_margin": best.margin if best else None,
                "best_chunk": best.text if best else None,
            }
        )
    return {"id": str(case["id"]), "kind": str(case["kind"]), "rows": rows}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe multilingual NLI as an answerability/evidence-sufficiency signal."
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=Path("benchmarks/retrieval/blind-v3.yaml"),
        help="Blind acceptance YAML to probe without changing selector behavior.",
    )
    parser.add_argument("--model", default=DEFAULT_NLI_MODEL, help="Hugging Face NLI model repo.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.acceptance if args.acceptance.is_absolute() else ROOT / args.acceptance
    try:
        acceptance = load_acceptance(path, ROOT)
        retriever = RerankedRetriever(ROOT)
        nli = OnnxNliBackend(args.model)
        cases = [probe_case(case, retriever, nli) for case in acceptance["cases"]]
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"NLI answerability probe: {acceptance['name']}")
    print(f"Frozen selector candidate: {acceptance['frozen_candidate']}")
    print(f"NLI model: {nli.model_name} file={DEFAULT_NLI_ONNX_FILE}")
    print(f"max_tokens={MAX_NLI_TOKENS}")
    for case in cases:
        print(f"[{case['kind'].upper():8}] {case['id']}")
        for row in case["rows"]:
            if not row["candidate"]:
                print(f"       {row['id']}: candidate=no")
                continue
            margin = row["best_margin"]
            sufficient = row["best_sufficient"]
            insufficient = row["best_insufficient"]
            print(
                f"       {row['id']}: R={row['document_rank']} doc={row['document_score']:.4f} "
                f"nli_margin={margin:.4f} sufficient={sufficient:.4f} insufficient={insufficient:.4f} "
                f"chunks={row['chunk_count']}"
            )
            if row["best_chunk"]:
                print(f"           evidence: {_shorten(str(row['best_chunk']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
