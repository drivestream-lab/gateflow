## Initiative

INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile (gateflow only)

## Wave

W2 — Initiative list/detail (Gateflow-owned) (CAP-03)

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Summary

- `GET /api/v1/initiatives` and `GET /api/v1/initiatives/{initiative_id}` return initiative list/detail composed from Gateflow-owned data only: runs (`RunRepository.list_runs`) + board EPIC tickets (`BoardService.list_tickets`) (REQ-09, REQ-10).
- Every response carries id, name, `prd_approval`, `affected_repos`, `current_stage`, `in_flight_run`, and EPIC link — fields present or explicitly `unavailable` (REQ-09).
- `prd_approval` is `unavailable` in W2 (no meta PR read wired); W3 populates it via composed CAP-01 against `prd-impact-acceptance` on the meta PR (REQ-10).
- `current_stage` derived from active run / EPIC board column / latest run state (plain language).
- GET-only on the new surface (non-GET 405); 401 without programme token; 404 unknown initiative distinct from malformed; existing `POST /initiatives/closure/start` (INIT-010 W4) unchanged (REQ-28).
- Zero mutate: no `apply_labels`/review create-update/merge/`update_board_status` from any new path (REQ-05 / REQ-28).

## Tasks

| TASK | Implements | Depends on | Exit | Proof |
|------|------------|------------|------|-------|
| TASK-W2-01 | REQ-09, REQ-10 | — | List/detail returns Gateflow-owned fields; prd_approval=unavailable | make test |
| TASK-W2-02 | REQ-09, REQ-10, REQ-28 | TASK-W2-01 | GET list/detail routes programme-token; GET-only guard | make test |
| TASK-W2-03 | REQ-09, REQ-10, REQ-28 | TASK-W2-02 | Live smoke exit 0; as-built W2 row | make check && make test |

## Verify command (human — wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_initiatives_readout
# API + PROGRAMME_SERVICE_TOKEN; tests/config.yaml (gateflow.org/repo = board EPIC repo);
# optional GATEFLOW_INITIATIVE_ID for a live detail assert
```

## Local proof

- `make check` — exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` — 319 passed

## Notes

- No new ORM table / no Alembic revision (reads existing `runs` + board via ForgeClient reads).
- No Forge write APIs on the CAP-03 path; board reads go through `BoardService` (read-only `list_tickets`).
- This PR does not self-approve; `wave-accepted` is applied by the human at `wave-acceptance`.
