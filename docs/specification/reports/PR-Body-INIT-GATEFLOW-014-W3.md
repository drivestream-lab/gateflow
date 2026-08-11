## Summary

- INIT-GATEFLOW-014 **W3**: structurally delete programme-token / tenant-bearer modules and remove open `POST /api/v1/tenants` (REQ-34).
- Add `ProgrammeWipeService` + `POST /api/v1/programmes/{id}/wipe` with ACTIVE-run 409 guard (REQ-35, REQ-46).
- Co-ship live verify: `verify_dead_doors_deleted`, `verify_wipe_cutover`.

## Spec path

`docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-34, REQ-35, REQ-46)

## Board

https://github.com/drivestream-lab/gateflow/issues/218

## Smoke command (human at wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_dead_doors_deleted
.venv/bin/python -m tests.verify.verify_wipe_cutover
```

(API up; wipe script needs `GATEFLOW_PROGRAMME_PAT` + Postgres.)

## Test plan

- [x] `make check`
- [x] `make test` (540 passed locally)
- [ ] Human live verify scripts above
- [ ] Label tip `wave-accepted` when smoke passes
