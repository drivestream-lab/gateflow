# Wave execution — INIT-GATEFLOW-013 W1

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Wave | W1 |
| Wave issue | https://github.com/drivestream-lab/gateflow/issues/201 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-013-w1-repo-selection` (cut from `develop` @ `c3a2b79` after Pre-Implement publish) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Outcome | pass |
| Date | 2026-08-09 |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W1-01 | REQ-12, REQ-13 | `tenant_models.py`, `tenant_service.py`, `test_tenant_service.py`, `verify_tenant_registry.py` | registration rejects `repos[]`; without repos succeeds | `repos` optional; non-empty → 422 `repos_not_allowed`; create with `[]`; registry verify updated; `make check` / `make test` | green |
| TASK-W1-02 | REQ-08–11, 26–27 | onboarding service, `programme_selection_models.py`, programme routes, `tenant_repository.py` | catalogue-gated select; PAT probe; deselect membership; ACTIVE-run blocks | `POST …/repos/select` + `…/deselect`; probe on new admits; `find_active_run` guard; `pending_setup` until W2; `make check` | green |
| TASK-W1-03 | REQ-08–13, 26–27 | `tests/unit/test_programme_selection.py` | unit covers select/deselect/probe/active-run/registration reject | suite covers admit, out-of-catalogue, probe fail, already-selected, deselect, active-run; `make test` | green |
| TASK-W1-04 | REQ-08,09,11,12,26,27 | `verify_repo_selection.py`, `tests/README.md`, as-built | live FILE present | FILE created; feature-map + as-built W1 row; PM-1 dependents (`verify_programme_connect`, workspace/branch lifecycle) updated to register without `repos[]` | green |

**Wave toolchain:** `make check` exit 0; `make test` exit 0 — **478 passed** (2026-08-09).

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_repo_selection`
- Agent created planned FILE: **yes** — **did not** run smoke/sandbox as success
- Prerequisites: human Alembic for tenants + `tenant_programme_connections`; PAT read on programme meta + selectable catalogue repo

## Contracts produced (for later Ground Report)

| Contract | Entry | Notes |
|----------|-------|-------|
| Registration without repos | `POST /api/v1/tenants` | non-empty `repos` → 422 `repos_not_allowed` |
| Select | `POST /api/v1/tenants/{tenant_id}/programme/repos/select` | body `{repos:[{org,repo}]}`; ⊂ current catalogue; probe new admits |
| Deselect | `POST /api/v1/tenants/{tenant_id}/programme/repos/deselect` | body `{org,repo}`; ACTIVE run → 422 `active_run` |
| Per-repo admit result | select response `results[]` | `pending_setup` / `already_selected` (setup W2) |

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-013 W1] Select/deselect repos; retire repos[]`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W1.md`
  - head_ref: `feature/INIT-GATEFLOW-013-w1-repo-selection`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W1.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W1
    wave_issue: https://github.com/drivestream-lab/gateflow/issues/201
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    completed_tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_repo_selection
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    title: "[INIT-GATEFLOW-013 W1] Select/deselect repos; retire repos[]"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W1.md
    head_ref: feature/INIT-GATEFLOW-013-w1-repo-selection
    base_ref: develop
    commit_workspace:
      required: true
      head_ref: feature/INIT-GATEFLOW-013-w1-repo-selection
```
