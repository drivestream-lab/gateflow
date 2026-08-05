## Summary

- Parse optional pin `purpose` / `owner` on `ResolvedWorkflowNode` via `WorkflowEngine._to_resolved`.
- Emit pin `purpose` / `owner` on `run_stopped` timeline payload when the stop node declares them (REQ-10).
- Extend board-status parse unit matrix; harness pin `v0.5.0-rc.2` ≡ submodule `6561c7c`.

## Initiative / board

- **Initiative:** INIT-GATEFLOW-010
- **Wave:** W0 — board [#138](https://github.com/drivestream-lab/gateflow/issues/138)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- **Plan / WorkManifest:** `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` §9
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-010-W0.md`

## Test plan

- [x] `make check`
- [x] `make test` (237 unit)
- [ ] Live verify: **N/A — P15 N/A** (parse + stop payload only; no new callable product surface)
- [ ] W1 still required for APPLY_FORGE `update_board_status` apply (REQ-03)

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative, Spec path, Verify command (N/A for W0)
- [x] As-built updated for W0 parse + REQ-10 stop payload
