# Genesis Import Audit — Devkit

## Scope

This slice reconstructs qiven-devkit's responsibility boundary, snapshot materialization model, managed/bootstrap-only ownership split, safe sync/adoption lifecycle, brownfield adoption lessons, accepted transactionality limitation, and deferred Foundation adoption residue.

## Sources reviewed

Primary committed evidence:

- `JasonHuang3D/qiven-devkit@214dc5c933ef4f7db3fce9795a39d49ca382dfbf:README.md`
- `JasonHuang3D/qiven-devkit@214dc5c933ef4f7db3fce9795a39d49ca382dfbf:templates/cpp-library/managed-files.cmake`
- `JasonHuang3D/qiven-devkit@214dc5c933ef4f7db3fce9795a39d49ca382dfbf:cmake/QivenRepoAdopt.cmake`
- `JasonHuang3D/qiven-devkit@214dc5c933ef4f7db3fce9795a39d49ca382dfbf:cmake/QivenRepoSync.cmake`
- `JasonHuang3D/qiven-devkit@53e4f9673bcbabcc5b597fb1185162f285437390` (`fix(devkit): canonicalize adoption git root`)
- qiven-context current-state evidence that Foundation is not yet formally Devkit-managed.

Retrospective evidence:

- prior-session reconstruction of Devkit Acceptance002 against Foundation: 16 managed paths, 3 exact, 13 content drift, 0 missing;
- prior-session reconstruction that the successful MISSING adoption path lacks its own dedicated immediate post-adoption sync no-op assertion;
- prior-session reconstruction that lack of crash-consistent filesystem transactionality was accepted as a v0.1-scale limitation.

Retrospective details were kept explicitly retrospective. Exact per-path Foundation drift content was not reconstructed because the available evidence does not support it.

## Promoted canonical records

- `ADR-0010` — materialize Devkit conventions as independent repository snapshots;
- `ADR-0011` — separate managed shared conventions from bootstrap-only repository-owned files;
- `ADR-0012` — preserve consumer edits with hash-tracked all-conflicts-first lifecycle operations;
- `MEM-20260913T182338Z-6BC4F1` — template 0.1.1 currently has 16 managed and 4 bootstrap-only paths;
- `MEM-20260913T182338Z-92AD37` — physical path canonicalization lesson;
- `MEM-20260913T182338Z-D5E8A2` — conflict-atomic preflight is not crash-consistent transactionality;
- `OBL-20260913T182338Z-4F7C19` — semantically reconcile Foundation managed drift before adoption;
- `OBL-20260913T182338Z-8A21D6` — add MISSING-path immediate post-adoption sync no-op coverage;
- `OBL-20260913T182338Z-B37E54` — revisit stronger transactional recovery when scale/criticality changes.

## Rejected or non-promoted candidates

- Devkit was not promoted into ecosystem version composition; the committed README assigns that possible future responsibility to `qiven-workspace`.
- The current template path count was recorded as a versioned fact, not an invariant.
- The statement that adoption is "all-or-nothing" was not promoted as crash-atomic. The scripts justify no-mutation-on-known-conflict semantics, but not rollback after an unexpected failure during filesystem writes.
- The thirteen Foundation drift paths were not guessed or reconstructed from memory.

## Incident lesson

Brownfield adoption originally relied on lexical absolute-path normalization for Git-root identity. Cross-platform CI exposed equivalent physical roots with different textual paths. Commit `53e4f967...` replaced that comparison with `file(REAL_PATH)` and added alias coverage. The recovered lesson is broader than the one bug: safety checks that depend on path identity must compare physical canonical identity, not merely normalized spelling.

## Residue pass

Recovered non-terminal cognition:

1. Foundation must undergo semantic drift reconciliation before real Devkit adoption;
2. MISSING-path adoption should gain its own immediate sync no-op assertion when adoption tests are next touched;
3. transactionality should be revisited only if Devkit's managed surface or failure cost grows enough to justify the complexity.

## Gaps

The historical Acceptance002 drift report is available only through retrospective session reconstruction in this pass. It establishes the counts and recommendation context but not the individual thirteen path diffs. Those details must be recovered from stronger evidence before Foundation adoption work begins; Genesis intentionally records the gap instead of filling it with inference.
