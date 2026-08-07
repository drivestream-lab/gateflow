## Initiative

INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile (gateflow only)

## Wave

W5 — Spec lane readout (CAP-04)

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Summary

- New `GET /api/v1/initiatives/{initiative_id}/spec` returns Draft Spec PR link when the walk has reached `spec-pr-action` (`pr_number` or `forge_executed`), plus pin next step, stage artifacts, and findings/open questions from Gateflow-owned handoff/stop context (REQ-12).
- Before `spec-pr-action`: `readiness=not_ready` with plain `readiness_reason` and **null** `draft_spec_pr_url` — never a broken URL (REQ-13).
- Initiative known but no spec-lane run (`meta_pr_url`) → `unavailable` with reason; unknown initiative → 404.
- GET-only; programme token; zero Forge writes (REQ-28).

## Tasks

| TASK | Implements | Depends on | Exit | Proof |
|------|------------|------------|------|-------|
| TASK-W5-01 | REQ-12, REQ-13 | — | Fields from pin+run; not-ready when no Draft Spec PR | make test |
| TASK-W5-02 | REQ-12, REQ-13, REQ-28 | TASK-W5-01 | GET .../spec GET-only route | make test |
| TASK-W5-03 | REQ-12, REQ-28 | TASK-W5-02 | Live spec readout smoke; as-built W5 row | make check && make test |

## Verify command (human — wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_spec_readout
# API + PROGRAMME_SERVICE_TOKEN; tests/config.yaml;
# optional GATEFLOW_INITIATIVE_ID for live readiness shape assert
```

## Local proof

- `make check` — exit 0
- `make test` — 345 passed
- Live smoke **not** claimed by agent — human runs at wave-acceptance

## Issue

https://github.com/drivestream-lab/gateflow/issues/166
