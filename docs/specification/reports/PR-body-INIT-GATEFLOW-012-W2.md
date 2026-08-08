## Summary

- Implement INIT-GATEFLOW-012 **W2** branch create-or-reuse (REQ-16–19): `RunOrchestrator.resolve_branch` composes existing `ForgeClient.ensure_branch_from_base` + naming helpers (TDD §3.5) — new-wave fork from live base tip; continuation reuses remote head with zero create; explicit `head_ref` missing → named fail-closed reason.
- Co-ship `tests/verify/verify_branch_lifecycle.py` (P15) + README feature map + as-built W2 matrix.
- PE-1 W2 coding-start waiver: current pin `v0.5.0-rc.2` 0 BROKEN for existing nodes; CTR-01 pin-shape consume remains DEP-02.

## Spec path

- `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` (REQ-16–19)
- Plan §9 / Pre-Implement / PE-Waiver W2 / Wave-Execution W2 under `docs/specification/reports/`

## Smoke command (human at wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_branch_lifecycle
```

## Test plan

- [x] `make check`
- [x] `make test` (440 passed at loop-spec)
- [ ] Human: live verify above (API + worker, `require_worker: true`, PAT)
- [ ] Label tip `wave-accepted` when smoke passes
