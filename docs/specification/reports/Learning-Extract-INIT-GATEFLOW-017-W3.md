# Learning extract — INIT-GATEFLOW-017 W3

| Field | Value |
|-------|-------|
| Wave | W3 — Enter programme + isolation + as-built |
| Initiative | INIT-GATEFLOW-017 |
| Branch / head | `feature/INIT-GATEFLOW-017-w3-enter-programme` @ `e0d7a24490ebe17426108fe1095ef785675d889c` |
| Pass-1 tip (approx) | `e0d7a24490ebe17426108fe1095ef785675d889c` (code commit after Pre-Implement `a96ed99`) |
| human_fix_detected | no |
| Date | 2026-08-14 |

## Learnings

| ID | Class | Summary | Evidence | Codify hint | Status |
|----|-------|---------|----------|-------------|--------|
| — | — | *(none)* | — | — | — |

Empty `items: []`: PR [#253](https://github.com/drivestream-lab/gateflow/pull/253) tip equals Pass-1 publish (`e0d7a24`); label `wave-accepted` is present; no commits or force-pushes after that tip. No human-fix signal to classify. Tip matches WorkManifest W3 intent (enter-programme without remint, isolation + jwt_login extend, one 017 as-built index row).

## Signals

- verify_evidence: human accept via `wave-accepted` on tip; live command `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` (not re-run by this skill)
- notes: Pass-1 `make test` recorded 626 passed; `make check` exit 0

## Ready for ground-spec?

yes — no open learning items; tip matches Pass-1 intent

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-017
  wave: W3
  human_fix_detected: false
  items: []
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: learning-extract
  outcome: pass
  artifact:
    path: docs/specification/reports/Learning-Extract-INIT-GATEFLOW-017-W3.md
  blockers: []
  signals:
    wave: W3
    human_fix_detected: false
    item_count: 0
    pr_url: https://github.com/drivestream-lab/gateflow/pull/253
  next_candidates:
    - ground-spec
  human_checkpoint: false
  external_action: false
```
