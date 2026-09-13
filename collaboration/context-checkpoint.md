# Context Checkpoint Protocol

A **Memory Delta** contains every category below; a category may be empty, but may not be omitted:

- New facts
- New decisions
- New rejected alternatives
- New obligations
- Changed obligations
- Closed obligations
- New risks
- New assumptions/hypotheses
- New lessons/incidents
- Superseded records
- Evidence references

Future checkpoint sequence: (1) capture evidence; (2) produce memory delta; (3) update canonical records; (4) update obligations; (5) update state; (6) refresh live repository observations; (7) validate; (8) compile working context; (9) cold-boot smoke test; (10) commit context checkpoint.

Context compiler and cold-boot execution are future work. Batch 001 defines only the protocol.
