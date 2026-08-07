## Initiative

INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile (gateflow only)

## Wave

W4 — Wave map readout (CAP-05)

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Summary

- New `GET /api/v1/initiatives/{initiative_id}/waves` returns per-wave status ∈ {`done`, `ready-to-start`, `blocked`, `active`} composed from board Feature tickets + run state only (REQ-14 / REQ-15) — no new wave-state store.
- When status is `blocked`, `block_reason` names why (e.g. predecessor not Done).
- Priority: board column `Done` → `done`; active run for the wave → `active`; predecessor not Done → `blocked`; else `ready-to-start`.
- Unknown initiative (no run / EPIC / Feature) → 404; programme-token required; non-GET → 405 (REQ-28).
- Zero mutate: CAP-05 path never writes Forge/board.

## Tasks

| TASK | Implements | Depends on | Exit | Proof |
|------|------------|------------|------|-------|
| TASK-W4-01 | REQ-14, REQ-15 | — | Per-wave status + block reason; no new wave-state store | make test |
| TASK-W4-02 | REQ-14, REQ-15, REQ-28 | TASK-W4-01 | GET .../waves route wired GET-only | make test |
| TASK-W4-03 | REQ-14, REQ-28 | TASK-W4-02 | Live wave-map smoke; as-built W4 row | make check && make test |

## Verify command (human — wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_wave_map
# API + PROGRAMME_SERVICE_TOKEN; tests/config.yaml (gateflow.org/repo = board Feature/EPIC repo);
# optional GATEFLOW_INITIATIVE_ID for live waves[] shape assert
```

## Local proof

- `make check` — exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` — 335 passed
- Live smoke **not** claimed by agent — human runs at wave-acceptance

## Issue

https://github.com/drivestream-lab/gateflow/issues/165
