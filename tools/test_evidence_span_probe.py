from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]

from evidence_span_probe import (  # noqa: E402
    MAX_CHUNK_CHARS,
    _split_long_text,
    record_evidence_chunks,
    score_record_evidence,
)


class FakeReranker:
    model_name = "fake-reranker"

    def score(self, query: str, documents: list[str]) -> list[float]:
        return [5.0 if "direct evidence" in document else -2.0 for document in documents]


class EvidenceSpanProbeTests(unittest.TestCase):
    def test_long_text_is_bounded(self) -> None:
        chunks = _split_long_text("x" * (MAX_CHUNK_CHARS * 2 + 17))
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= MAX_CHUNK_CHARS for chunk in chunks))

    def test_record_chunks_keep_metadata_and_body_evidence(self) -> None:
        record = SimpleNamespace(
            title="Example title",
            metadata={"statement": "direct evidence statement"},
            body="# Heading\n\nBody paragraph with more evidence.\n",
        )
        chunks = record_evidence_chunks(record)
        self.assertIn("title: Example title", chunks)
        self.assertIn("statement: direct evidence statement", chunks)
        self.assertIn("Body paragraph with more evidence.", chunks)
        self.assertFalse(any(chunk.startswith("#") for chunk in chunks))

    def test_best_chunk_is_scored_independently_from_whole_record(self) -> None:
        record = SimpleNamespace(
            title="Adjacent topic",
            metadata={"statement": "direct evidence lives here"},
            body="Unrelated broad prose.",
        )
        retriever = SimpleNamespace(
            records={"MEM-TEST": record},
            reranker=FakeReranker(),
            root=ROOT,
        )
        query = {"task": "Which record contains direct evidence?"}
        rows = score_record_evidence(retriever, query, "MEM-TEST")
        self.assertGreater(len(rows), 0)
        self.assertEqual(rows[0].score, 5.0)
        self.assertIn("direct evidence", rows[0].text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
