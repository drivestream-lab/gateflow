## Summary

INIT-GATEFLOW-015 W0 — persist full `RunOutcomeType` vocabulary on `stage_completed` / `stages.outcome_type`, and persist job `lane` into JSONB payloads on `stage_completed` / `run_stopped` (ADR-017). No new routes; `GET /metrics/runs` unchanged.

## Spec path

`docs/specification/product/INIT-GATEFLOW-015-gateflow.md` (REQ-01, REQ-02, REQ-03 no-backfill half, REQ-16 write half)

## Board

- EPIC: https://github.com/drivestream-lab/gateflow/issues/229
- Wave: https://github.com/drivestream-lab/gateflow/issues/230

## Smoke command

N/A — P15 not applicable (internal write-path only). Human wave-acceptance: unit evidence + TASK-W0-04 diff inspection (no backfill).

## Test plan

- [x] `make check`
- [x] `make test` (558 passed)
- [ ] Human accept with label `wave-accepted` on tip
