## Initiative

INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile (gateflow only)

## Wave

W1 — Check persistence + composed readout (CAP-02)

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Summary

- Persist every CAP-01 evaluate attempt as a `checkpoint_check` run_event in the existing run/timeline store, correlated to initiative/wave when a run is resolvable from the PR (REQ-06).
- Stale evidence (approval predating a later commit) → `not_satisfied` with reason `stale — new commits since approval`; `checked_sha`/`checked_at` always present on live verdicts; never a silent pass (REQ-03).
- `GET /api/v1/checkpoints/history` returns prior persisted records marked `historical=true`; never claims a live verdict (REQ-07).
- Composed readout via `initiative_id`+`wave_id` on `GET /api/v1/checkpoints/status`; 404 `no run found for this wave` when unresolved (distinct from malformed id) (REQ-08).
- GET-only; zero mutate (no `apply_labels`/review/merge/`update_board_status`) from any new path (REQ-28).

## Tasks

| TASK | Implements | Depends on | Exit | Proof |
|------|------------|------------|------|-------|
| TASK-W1-01 | REQ-06 | — | Every evaluate attempt appends `checkpoint_check` run_event with required payload | make test |
| TASK-W1-02 | REQ-03 | TASK-W1-01 | Stale → not_satisfied + reason; checked_sha/checked_at always present | make test |
| TASK-W1-03 | REQ-07, REQ-28 | TASK-W1-01 | GET /checkpoints/history marks records historical | make test |
| TASK-W1-04 | REQ-08, REQ-28 | TASK-W1-02, TASK-W1-03 | Composed readout via initiative+wave; 404 no run found for this wave | make test |
| TASK-W1-05 | REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 | TASK-W1-04 | Live verify exit 0; as-built W1 row | make check && make test |

## Verify command (human — wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_checkpoint_history
# API + PROGRAMME_SERVICE_TOKEN; optional GATEFLOW_CHECKPOINT_PR for live persist/stale;
# optional GATEFLOW_COMPOSED_INITIATIVE + GATEFLOW_COMPOSED_WAVE for composed readout
```

## Local proof

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — 302 passed

## Notes

- No new ORM table / no Alembic revision (reuses `run_events` JSONB payload).
- No Forge write APIs on CAP-01/02 paths; persistence is DB-only.
- This PR does not self-approve; `wave-accepted` is applied by the human at `wave-acceptance`.
