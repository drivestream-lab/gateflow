## Summary

- Parse pin `authorization` (`explicit` \| `automated`) on every `external-action` node into `ResolvedWorkflowNode` (`AuthorizationModeType`); omit/unknown fail closed.
- Align Pass-1 unit suite with remounted pin: `loop-spec` pass → `wave-pr-action`; pre-implement `commit_workspace: required`; day-one authorization matrix.
- As-built: INIT-008 W0 unit-complete; INIT-006 REQ-7 superseded for `automated` nodes; harness pin `v0.5.0-rc.2` ≡ submodule `355f403`.

## Initiative / board

- **Initiative:** INIT-GATEFLOW-008 (006A)
- **Wave:** W0 — board [#93](https://github.com/drivestream-lab/gateflow/issues/93)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- **Plan / WorkManifest:** `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` §9
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-008-W0.md`

## Test plan

- [x] `make check`
- [x] `make test` (189 unit)
- [ ] Live verify: **N/A — P15 N/A** (no new product surface this wave)
- [ ] W1 still required for automated ForgeClient.apply + retire PR-at-start (not in this PR)

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative, Spec path, Verify command (N/A for W0)
- [x] As-built updated for W0 parse/consume
