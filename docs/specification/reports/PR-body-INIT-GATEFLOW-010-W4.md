## Summary

- Initiative-closure Enter-at: `POST /api/v1/initiatives/closure/start` with programme token; Done-gate on `wave_ticket_ids[]`; EPIC → Done before purge-app dispatch (REQ-12–14).
- Closure walk: `purge-initiative-artifacts-app` → automated `initiative-closure-pr-action-app` → STOP `initiative-closure-signoff-app`; never meta purge (REQ-15).
- Partial failure hygiene after EPIC Done: `partial_closure_failure` recorded; no closure-complete claim (REQ-20).
- Co-ship live verify: `verify_closure` smoke (401/4xx/optional Done-gate/202); Feature-Readiness freeze doc (REQ-17, REQ-18).

## Initiative / board

- **Initiative:** INIT-GATEFLOW-010
- **Wave:** W4 — board [#142](https://github.com/drivestream-lab/gateflow/issues/142)
- **EPIC:** [#137](https://github.com/drivestream-lab/gateflow/issues/137)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- **Plan / WorkManifest:** `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` §9
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-010-W4.md`
- **Pre-implement:** `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W4.md`

## Test plan

- [x] `make check`
- [x] `make test` (266 unit)
- [ ] Human live verify: `.venv/bin/python -m tests.verify.verify_closure` (400/422/202 + Done-gate + purge walk)
- [ ] Ground / learning-extract — Pass-2 closeout after live-verify + merge

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative, Spec path, Verify command
- [x] As-built updated for W4 closure Enter-at + freeze row
- [x] Feature-Readiness freeze doc
- [ ] Live-Verify W4 — human at `live-verify` checkpoint
