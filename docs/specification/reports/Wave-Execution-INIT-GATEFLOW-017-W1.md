# Wave execution — INIT-GATEFLOW-017 W1

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Wave | W1 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-017-w1-identity-directory` |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W1-01 | REQ-01, REQ-30 | `identity_models.py` create; `identity_status_types.py` reuse | `make check` exit 0 | `make check` exit 0; read models `extra=forbid`, no password fields | green |
| TASK-W1-02 | REQ-01…05, 12–14, 25, 29, 30 | directory service + DI + unit test | `pytest tests/unit/test_identity_directory_service.py -q` | that file + `make test` 622 passed; named refusals; epoch increment on suspend/password-set | green |
| TASK-W1-03 | REQ-05…11, 24, 28 | directory service + unit test modify | same pytest | grant idempotent; unknown 422; platform_admin not grantable; no mint | green |
| TASK-W1-04 | REQ-22 | identity routes + programme grants + `test_identity_routes.py` | `pytest tests/unit/test_identity_routes.py -q` | tenant_admin 403 `wrong actor`; platform_admin 200 | green |
| TASK-W1-05 | REQ-01, 02, 04–06, 09–12, 14, 22, 30 | `verify_identity_directory.py` create | human live command | FILE created with `prayog:covers:` those REQs — **did not** run smoke as success | green |

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_identity_directory` under `tests/verify`
- Agent created planned FILE: yes — **did not** run smoke/sandbox as success

## Compile-safe extras (not in §9 file list)

- `user_identity_repository.py` — list/search, status update, password update
- `programme_membership_repository.py` — list-by-identity/programme, delete
- `dependencies.py` — `require_directory_admin` (403 `wrong actor` without renaming `role_forbidden`)

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-017 W1] Identity directory + grant/detach`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W1.md`
  - head_ref: `feature/INIT-GATEFLOW-017-w1-identity-directory`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W1.md
  blockers: []
  signals:
    wave: W1
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/246"
    current_task: TASK-W1-05
    implements:
      - REQ-01
      - REQ-02
      - REQ-03
      - REQ-04
      - REQ-05
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-09
      - REQ-10
      - REQ-11
      - REQ-12
      - REQ-13
      - REQ-14
      - REQ-22
      - REQ-24
      - REQ-25
      - REQ-28
      - REQ-29
      - REQ-30
    completed_tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_identity_directory"
    check_result: "exit 0"
    test_result: "622 passed"
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-017 W1] Identity directory + grant/detach"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W1.md
    head_ref: feature/INIT-GATEFLOW-017-w1-identity-directory
    base_ref: develop
```
