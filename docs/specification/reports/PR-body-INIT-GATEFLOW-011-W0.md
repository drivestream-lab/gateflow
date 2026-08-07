## Summary

- Extend ForgeClient with read-only `list_reviews`, `list_check_runs`, and merge fields on `GithubPullRequestDocument` (REQ-02).
- Resolve six pin checkpoint ids from `delivery-contract.yaml` via `WorkflowEngine.get_github_checkpoint_vocab` (REQ-02).
- Ship live CAP-01 `CheckpointEvidenceService.evaluate` + `GET /api/v1/checkpoints/status` (programme-token; GET-only; no persistence) (REQ-01/04/05/28).
- Co-ship `tests/verify/verify_checkpoint_status.py` + feature map + as-built W0 row.

## Initiative / board

- **Initiative:** INIT-GATEFLOW-011
- **Wave:** W0 — board [#161](https://github.com/drivestream-lab/gateflow/issues/161)
- **EPIC:** [#160](https://github.com/drivestream-lab/gateflow/issues/160)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- **Plan / WorkManifest:** `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` §9
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W0.md`
- **Verify (human):** `.venv/bin/python -m tests.verify.verify_checkpoint_status`

## Test plan

- [x] `make check`
- [x] `make test` (283 unit)
- [ ] Live verify: `.venv/bin/python -m tests.verify.verify_checkpoint_status` (API + programme token; optional `GATEFLOW_CHECKPOINT_PR`)
- [ ] Persistence / history / composed readout still **W1**

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative, Spec path, Verify command
- [x] As-built / feature map updated for W0 CAP-01
