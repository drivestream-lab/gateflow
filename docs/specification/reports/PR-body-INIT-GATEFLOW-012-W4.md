## Summary

- Implement INIT-GATEFLOW-012 **W4** repo-scoped `NO_CONCURRENT_RUN` (REQ-23–25): `find_active_run` matches any ACTIVE run for `org`+`repo` (query-only broaden); keeps `PC-06-no-concurrent-active-run` / HTTP 409; no new worktree/lock isolation.
- FF-06 fixture first (`test_run_store_concurrency`), then broaden; wave-start + trigger_router + closure callers updated.
- Extend `verify_wave_start` same-repo 409 probe (+ optional cross-repo env) + README + as-built W4 matrix.

## Spec path

- `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` (REQ-23–25)
- Plan §9 / Pre-Implement / Wave-Execution W4 under `docs/specification/reports/`

## Smoke command (human at wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_wave_start
```

Optional REQ-24: `GATEFLOW_VERIFY_CROSS_ORG` + `GATEFLOW_VERIFY_CROSS_REPO`.

## Test plan

- [x] `make check`
- [x] `make test` (456 passed at loop-spec)
- [ ] Human: live verify above (API + programme token; ACTIVE cleanup as needed)
- [ ] Label tip `wave-accepted` when smoke passes
