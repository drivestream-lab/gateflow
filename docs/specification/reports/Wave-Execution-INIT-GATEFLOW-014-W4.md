# Wave execution — INIT-GATEFLOW-014 W4

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Wave | W4 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-014-w4-teaching-surfaces` @ Pre-Implement publish `03c2d6d` (code unpublished until follow-on `/commit-workspace`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/219 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W4-01 | REQ-36, REQ-38 | modify listed verify scripts + remaining token consumers | `verify_all` exit 0 (human); grep `PROGRAMME_SERVICE_TOKEN` in `tests/verify/` = 0 | Shared `tests/_helpers/verify_jwt_auth.py`; rewrote Appendix-C + remaining consumers to JWT; open-register scripts → programme provision + JWT; `rg PROGRAMME_SERVICE_TOKEN tests/verify` → CLEAN | green |
| TASK-W4-02 | REQ-37 | create `verify_old_doors_refused.py` | script exit 0 (human) | FILE co-shipped: opaque token→401, opaque bearer→401, `POST /tenants`→401/404/405 | green |
| TASK-W4-03 | REQ-38 | `tests/README.md`; as-built detail + index | review — no old-door examples | README JWT-only invocation; `Implementation-Status-INIT-GATEFLOW-014.md` W4 matrix; index W4 section | green |

## Observed toolchain

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — **540 passed**

## Live verify (human — not claimed here)

- Planned scripts:
  - `.venv/bin/python -m tests.verify.verify_all`
  - `.venv/bin/python -m tests.verify.verify_old_doors_refused`
- Agent created planned FILEs: **yes** — **did not** run smoke/sandbox as success
- Prerequisites: API (+ worker for wave-start steps); `SMOKE_TENANT_ADMIN_TOKEN` or prior programme attach; optional `GATEFLOW_PROGRAMME_PAT` for scripts that provision

## Supporting changes

- Helper: `tests/_helpers/verify_jwt_auth.py` — seed/login platform_admin, require tenant_admin JWT, `provision_programme_tenant_admin`
- Rewrote open-register consumers (`verify_tenant_registry`, `verify_repo_selection`, `verify_programme_connect`, `verify_catalogue_refresh`, `verify_harness_status`, workspace/branch lifecycle)
- `verify_jwt_cutover` uses `SMOKE_LEGACY_OPAQUE_TOKEN` (no `PROGRAMME_SERVICE_TOKEN` string)

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref` `feature/INIT-GATEFLOW-014-w4-teaching-surfaces`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-014 W4] Prove absence + rewrite teaching surfaces`
  - body_path: `docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W4.md`
  - head_ref: `feature/INIT-GATEFLOW-014-w4-teaching-surfaces`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W4.md
  blockers: []
  signals:
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/219"
    current_task: null
    implements: [REQ-36, REQ-37, REQ-38]
    completed_tasks: [TASK-W4-01, TASK-W4-02, TASK-W4-03]
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_all && .venv/bin/python -m tests.verify.verify_old_doors_refused"
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    commit_workspace: required
    open_draft_pr:
      title: "[INIT-GATEFLOW-014 W4] Prove absence + rewrite teaching surfaces"
      body_path: docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W4.md
      head_ref: feature/INIT-GATEFLOW-014-w4-teaching-surfaces
      base_ref: develop
      draft: true
```
