## Initiative

INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile (gateflow only)

## Wave

W3 — Meta bridge + partial success (CAP-03 PRD approval)

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Summary

- Initiative list/detail now populate `prd_approval` via CAP-01 against checkpoint `prd-impact-acceptance` on the initiative's meta PR (run `meta_pr_url` → `MetaPrIntakeService.parse_url` → `CheckpointEvidenceService.evaluate`) (REQ-09 complete).
- Uses `evaluate` with a meta `CheckpointPrRef` — **not** `evaluate_composed` (which resolves the app wave PR).
- When meta is unreachable, meta PR is missing, or no `meta_pr_url` is on runs: HTTP **200** with `prd_approval=unavailable` and Gateflow-owned fields still present (REQ-11).
- CAP-01 `could_not_verify` (transport) maps to initiative `unavailable` for the meta bridge; `satisfied` / `not_satisfied` map 1:1.
- No new routes; existing GET `/initiatives` + `/initiatives/{id}` behaviour extended. GET-only / programme-token / 404 unknown unchanged (REQ-28).
- Zero mutate: no `apply_labels` / review create-update / merge / `update_board_status` from the CAP-03 path.

## Tasks

| TASK | Implements | Depends on | Exit | Proof |
|------|------------|------------|------|-------|
| TASK-W3-01 | REQ-09 | — | PRD approval populated via CAP-01 against prd-impact-acceptance on meta PR | make test |
| TASK-W3-02 | REQ-11 | TASK-W3-01 | Meta unreachable → HTTP 200; meta fields unavailable; owned fields present | make test |
| TASK-W3-03 | REQ-09, REQ-11, REQ-28 | TASK-W3-02 | Live meta-up + meta-down paths; as-built W3 row | make check && make test |

## Verify command (human — wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_initiative_meta_bridge
# API + PROGRAMME_SERVICE_TOKEN; tests/config.yaml (gateflow.org/repo = board EPIC repo);
# optional GATEFLOW_INITIATIVE_ID (+ GATEFLOW_EXPECT_PRD_APPROVAL=…) for meta-up;
# optional GATEFLOW_META_DOWN_INITIATIVE_ID for explicit meta-down assert
```

## Local proof

- `make check` — exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` — 325 passed
- Live smoke **not** claimed by agent — human runs at wave-acceptance

## Issue

https://github.com/drivestream-lab/gateflow/issues/164
