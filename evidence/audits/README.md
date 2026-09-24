# Audit evidence

Durable incident, acceptance and migration evidence lives here so
canonical memory can be reconstructed or corrected later.

Registration conventions:

- One dated file per execution, incident or trial:
  `<topic>-<YYYY-MM-DD>.md` (or `.txt` for verbatim captured output).
- The file records: exact ref/artifact identities (commit, tree, digests
  where applicable), environment, what was executed/observed, the
  property claimed, abstentions, and the PASS/FAIL or diagnostic
  disposition.
- Evidence is bound to the exact tested identity; a carry-forward claim
  names its rationale per the acceptance contracts.
- Audits are immutable history: corrections land as new dated files that
  reference the original, never as rewrites.
- Legacy/deprecated evidence buckets are museum material under
  `legacy/evidence/` (ADR-0042); nothing may be written there.
