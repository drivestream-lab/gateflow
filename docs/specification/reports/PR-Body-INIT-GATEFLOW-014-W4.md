## Summary

- INIT-GATEFLOW-014 **W4**: rewrite teaching/verify surfaces to JWT-only (REQ-36, REQ-38).
- Co-ship consolidated old-door refusal script (REQ-37).
- Zero `PROGRAMME_SERVICE_TOKEN` references under `tests/verify/`.

## Spec path

`docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-36, REQ-37, REQ-38)

## Board

https://github.com/drivestream-lab/gateflow/issues/219

## Smoke command (human at wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_all
.venv/bin/python -m tests.verify.verify_old_doors_refused
```

(API up; `SMOKE_TENANT_ADMIN_TOKEN` or programme-attach JWT; webhook secret for `verify_all` webhook step.)

## Test plan

- [x] `make check`
- [x] `make test` (540 passed locally)
- [ ] Human live verify scripts above
- [ ] Label tip `wave-accepted` when smoke passes
