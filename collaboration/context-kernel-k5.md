# ContextKernel K5 lossless LLM transport compression contract

K5 begins only after K4 Canonical Artifact Handoff is accepted. Its purpose is to
reduce LLM input cost for complete-context transfer without weakening the semantics,
integrity, provenance, negative knowledge or isolation proven by K4.

## Semantic boundary

K5 is **lossless transport optimization**. It is not:

- task-specific retrieval or ContextBundle selection;
- summarization;
- semantic pruning;
- a replacement authority;
- permission to drop history, provenance, constraints, unknowns or abstentions;
- an excuse to rely on model-native memory to expand omitted content.

The K4 handoff semantic closure is the reference meaning. A K5 transport may change
representation but must deterministically recover that reference meaning.

## Codec requirements

A candidate codec/profile must be versioned, deterministic and self-delimiting. It
may use compact field vocabularies, symbol tables, dictionaries, structural factoring,
canonical binary forms, textual encodings or another reversible mechanism.

Any dictionary, schema, decoder instruction or project-specific vocabulary needed by
the consumer is part of the measured delivery unless it is an independently admitted,
version-pinned generic platform primitive. Mutable remote dictionaries and hidden
system prompts are forbidden dependencies.

Decode must be bounded. Invalid version, malformed input, unknown symbol, duplicate
or ambiguous mapping, truncation, trailing unexplained data, digest mismatch,
resource-limit violation and decompression-bomb behavior fail closed.

## Exact equivalence

K5 records both:

1. the compact artifact digest; and
2. the recovered K4 semantic/handoff identity.

The strongest reference path is reversible decoding to the exact canonical K4
handoff bytes. If a codec canonicalizes transport metadata that is intentionally
outside semantic identity, it must instead prove byte-identical reconstruction of
all semantic inputs plus an explicit, versioned equivalence rule for those excluded
transport fields. No fuzzy comparison is accepted for the machine gate.

## LLM token metric

Token efficiency is model/tokenizer dependent. Every result must name the tokenizer
or tokenizer suite and version/configuration used. Report:

- K4 reference bytes and tokens;
- K5 artifact bytes and tokens;
- any decoder/dictionary/instruction tokens that must accompany K5;
- total effective LLM-input tokens;
- absolute savings and compression ratio.

A byte-smaller representation is not a token win unless measured token input also
falls. A codec that requires a large explanatory prompt counts that prompt.

## Engineering acceptance

The fixed automated suite must include at least:

- deterministic encode/decode golden vectors;
- exact K4 round trip;
- randomized/fuzzed structural round trips over admitted object forms;
- corruption at every framing region;
- truncation and trailing-data rejection;
- version/dictionary mismatch rejection;
- duplicate/ambiguous symbol rejection;
- bounded memory/output expansion and decompression-bomb fixtures;
- Unicode and absent/null distinction preservation;
- provenance, lifecycle, negative-knowledge and unknown-value preservation;
- stable tokenizer measurement on a pinned evaluation corpus.

Property tests must compare decoded canonical structures/digests, not only rendered
text.

## Cognitive equivalence acceptance

Run paired isolated fresh-LLM trials using the same Project Continuity challenge:

- control receives the accepted K4 uncompressed handoff artifact;
- treatment receives only the K5 compact artifact plus admitted decoder material;
- neither may read canonical GitHub cognition before sealing reconstruction;
- both must recover the same required facts, protected constraints, lifecycle status,
  negative knowledge, unsupported-history abstentions and next legitimate action;
- discrepancies are classified against canonical K4 semantics; material semantic
  divergence fails K5 even if automated round-trip tests pass.

The trial corpus must include adversarial cases where compression could accidentally
collapse distinctions such as `unknown` vs absent, current vs superseded, evidence vs
interpretation, authorization vs retrieval, and live vs snapshot facts.

## Acceptance target

K5 is accepted only when:

- all machine equivalence/security/resource gates pass;
- paired fresh-LLM semantic equivalence passes;
- the measured effective token count is strictly lower than the K4 reference on the
  declared evaluation suite;
- no new authority or hidden external cognition dependency is introduced.

No minimum compression ratio is assumed before measurement. Correctness dominates
ratio; an optimization with attractive size but semantic drift is rejected.
