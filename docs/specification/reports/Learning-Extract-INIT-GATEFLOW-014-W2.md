# Learning extract — INIT-GATEFLOW-014 W2

| Field | Value |
|-------|-------|
| Wave | W2 — JWT cutover; refuse old doors; per-programme ForgeClient; tenant-scoped runs; catalogue agents |
| Initiative | INIT-GATEFLOW-014 |
| Branch / head | `feature/INIT-GATEFLOW-014-w2-jwt-cutover` @ `0c8e8a5782f794802eddc2200e98e22010c8263e` |
| Pass-1 tip | `0c8e8a5782f794802eddc2200e98e22010c8263e` (sole PR commit at acceptance) |
| human_fix_detected | no |
| Date | 2026-08-11 |

## Learnings

| ID | Class | Summary | Evidence | Codify hint | Status |
|----|-------|---------|----------|-------------|--------|
| — | — | *(none)* | — | — | — |

Empty `items: []`: tip SHA equals Pass-1 publish commit; PR [#222](https://github.com/drivestream-lab/gateflow/pull/222) shows `wave-accepted` (2026-08-11 by @nikd10x) with **no** subsequent commits before Pass-2.

## Signals

- verify_evidence: human accept via `wave-accepted` on tip; live commands documented (`verify_jwt_cutover`, `verify_cross_programme_isolation`) — not re-run by this skill
- notes: Pass-1 recorded `make check` exit 0; `make test` **544** passed; Alembic baseline squashed to `5e85268f844f_first_version.py` (human DB reset)

## Ready for ground-spec?

yes — no open learning items; tip matches Pass-1 intent

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-014
  wave: W2
  human_fix_detected: false
  items: []
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: learning-extract
  outcome: pass
  artifact:
    path: docs/specification/reports/Learning-Extract-INIT-GATEFLOW-014-W2.md
  blockers: []
  signals:
    wave: W2
    human_fix_detected: false
    item_count: 0
  next_candidates:
    - ground-spec
  human_checkpoint: false
  external_action: false
```
