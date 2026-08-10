# Wave execution — INIT-GATEFLOW-013 W2

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Wave | W2 |
| Wave issue | https://github.com/drivestream-lab/gateflow/issues/202 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-013-w2-repo-setup` (cut from `develop` @ `d6f623c` after Pre-Implement PASS) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Outcome | pass |
| Date | 2026-08-10 |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W2-01 | REQ-14, REQ-15, REQ-16 | `programme_onboarding_service.py`, `programme_selection_models.py` | newly admitted repos `resolve_workspace` independently; per-repo setup results; `make check` | `select_repos` calls `resolve_workspace` per new admit; isolates `TenantGitWorkspaceError`; outcomes `ok` / `setup_failed` (+ named reason); membership retained on setup fail; `make check` exit 0 | green |
| TASK-W2-02 | REQ-14, REQ-15, REQ-16 | `tests/unit/test_programme_selection.py` | unit proves setup isolation and result shape; `make test` | `test_select_setup_isolation_mixed_batch` + updated admit/outcome assertions; `make test` exit 0 — **479 passed** | green |
| TASK-W2-03 | REQ-14, REQ-15, REQ-16 | `verify_repo_selection.py`, `tests/README.md`, `as-built/implementation-status.md` | live FILE asserts workspace for newly selected repo | Verify asserts `ok` + `{workspace}/{org}/{repo}/.git`; W2 feature-map + as-built matrix; `make check` / `make test` still green | green |

**Wave toolchain:** `make check` exit 0; `make test` exit 0 — **479 passed** (2026-08-10).

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_repo_selection`
- Agent created/updated planned FILE: **yes** — **did not** run smoke/sandbox as success
- Prerequisites: W0+W1; workspace_root writable; PAT; programme DDL

## Contracts produced (for later Ground Report)

| Contract | Entry | Notes |
|----------|-------|-------|
| Setup-on-select batch | `select_repos` after admit | per-repo `ok` / `setup_failed`; peers independent (REQ-15/16) |
| Workspace layout | `resolve_workspace(credential)` | `{workspace_root}/{org}/{repo}` present on success (ADR-010) |
| Select response shape | `ProgrammeSelectResponse.results[]` | `ok`, `already_selected`, `setup_failed` (+ reason); admit kept on setup fail |

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-013 W2] Setup chosen repos (batch)`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W2.md`
  - head_ref: `feature/INIT-GATEFLOW-013-w2-repo-setup`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W2
    wave_issue: https://github.com/drivestream-lab/gateflow/issues/202
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    current_task: null
    implements:
      - REQ-14
      - REQ-15
      - REQ-16
    completed_tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
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
    title: "[INIT-GATEFLOW-013 W2] Setup chosen repos (batch)"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W2.md
    head_ref: feature/INIT-GATEFLOW-013-w2-repo-setup
    base_ref: develop
    commit_workspace:
      required: true
      head_ref: feature/INIT-GATEFLOW-013-w2-repo-setup
```
