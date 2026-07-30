## Summary

- PolicyEngine: STOP external-action only when `authorization=explicit`; automated → `APPLY_FORGE`.
- Shared `ForgeActionService.apply_external_action` (pin ⋉ handoff + run-context head/base); authorize path reuses apply.
- Orchestrator: after coding hops, automated `wave-pr-action` applies without `/forge/authorize`, then STOPs at `live-verify`.
- Job start: `ensure_branch` only — no Draft PR create; `pr_number` null until open_draft_pr.
- Live script + feature map updated for Pass-1 PR timing (human runs verify).

## Initiative / board

- **Initiative:** INIT-GATEFLOW-008 (006A)
- **Wave:** W1 — board [#94](https://github.com/drivestream-lab/gateflow/issues/94)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-008-W1.md`

## Test plan

- [x] `make check`
- [x] `make test` (191 unit)
- [ ] Live: `.venv/bin/python -m tests.verify.verify_implement_lane` (human at live-verify)

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] As-built / feature map updated for W1 Pass-1 edges
