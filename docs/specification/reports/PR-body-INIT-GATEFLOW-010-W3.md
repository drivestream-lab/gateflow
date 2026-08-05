## Summary

- Closeout walk: after `ground-spec.pass`, orchestrator applies automated `wave-done-action` (`update_board_status` Done) then stops at `wave-signoff` with terminal purpose (REQ-05).
- Forge guards: no merge action in `ForgeActionType`; apply path rejects merge-like actions and `*-lgtm` labels (REQ-09, REQ-16).
- Policy guards: `wave-signoff` / `wave-complete` pass do not auto-chain to next wave or closure on the same run (REQ-19).
- Co-ship live verify: `verify_wave_closeout` dogfood asserts Done hop, terminal purpose, and no auto-chain stages (REQ-17 partial).

## Initiative / board

- **Initiative:** INIT-GATEFLOW-010
- **Wave:** W3 — board [#141](https://github.com/drivestream-lab/gateflow/issues/141)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- **Plan / WorkManifest:** `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` §9
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-010-W3.md`
- **Pre-implement:** `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W3.md`

## Test plan

- [x] `make check`
- [x] `make test` (256 unit)
- [ ] Human live verify: `.venv/bin/python -m tests.verify.verify_wave_closeout` (+ `verify_spec_lane` as needed)
- [ ] Ground / learning-extract — Pass-2 closeout after live-verify + merge

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative, Spec path, Verify command
- [x] As-built updated for W3 closeout Done + guards + no auto-chain
- [ ] Live-Verify W3 — human at `live-verify` checkpoint
