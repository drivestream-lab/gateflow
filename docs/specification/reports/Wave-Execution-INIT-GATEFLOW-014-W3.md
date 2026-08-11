# Wave execution — INIT-GATEFLOW-014 W3

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Wave | W3 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-014-w3-dead-door-wipe` @ Pre-Implement publish `5c249cf` (code unpublished until follow-on `/commit-workspace`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/218 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W3-01 | REQ-34 | delete `programme_token.py` / `tenant_token.py`; modify `tenant_routes.py`; create `verify_dead_doors_deleted.py` | `make check && pytest … -k register` — open-register gone | deleted modules; `POST /api/v1/tenants` → 404/405 with JWT; register unit green; verify FILE co-shipped | green |
| TASK-W3-02 | REQ-35, REQ-46 | create `programme_wipe_service.py` + unit; modify `programme_admin_routes.py`; create `verify_wipe_cutover.py` | wipe ACTIVE → 409; idle clears | `ProgrammeWipeService` + `POST /programmes/{id}/wipe`; unit ACTIVE/idle/not-found; verify FILE co-shipped | green |

## Observed toolchain

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — **540 passed**

## Live verify (human — not claimed here)

- Planned scripts:
  - `.venv/bin/python -m tests.verify.verify_dead_doors_deleted`
  - `.venv/bin/python -m tests.verify.verify_wipe_cutover`
- Agent created planned FILEs: **yes** — **did not** run smoke/sandbox as success
- Prerequisites: API up; `GATEFLOW_PROGRAMME_PAT` for wipe onboard; Postgres for synthetic ACTIVE run insert

## Supporting changes (wiring)

- Repository delete helpers: `ProgrammeRepository.delete_programme`, `TenantRepository.delete_tenant`, `RunRepository.find_active_run_for_tenant` / `delete_runs_for_tenant`, `UserIdentityRepository.delete_for_tenant`
- DI: `ProgrammeWipeService` in `BusinessServicesModule` + `_BUSINESS_SERVICE_TYPES`
- Models: `ProgrammeWipeResult`
- Docs: as-built W3 rows; `tests/README.md` feature map W2+W3
- Removed `tests/unit/test_tenant_token.py` (imported deleted module)

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-014 W3] Dead-door deletion + wipe cutover`
  - body_path: `docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W3.md`
  - head_ref: `feature/INIT-GATEFLOW-014-w3-dead-door-wipe`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W3.md
  blockers: []
  signals:
    wave: W3
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/218"
    completed_tasks:
      - TASK-W3-01
      - TASK-W3-02
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_wipe_cutover
    unit_passed: 540
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-014 W3] Dead-door deletion + wipe cutover"
    body_path: docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W3.md
    head_ref: feature/INIT-GATEFLOW-014-w3-dead-door-wipe
    base_ref: develop
```
