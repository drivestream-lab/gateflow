# Wave execution — INIT-GATEFLOW-017 W2

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Wave | W2 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W2-01 | REQ-21 | `programme_service.py`, `programme_admin_routes.py`, `test_programme_service.py` | `make test` exit 0; attach tests negated | `make check` exit 0; `make test` 622 passed; `attach_tenant_admin` removed; grant routes kept | green |
| TASK-W2-02 | REQ-20 | `tenant_routes.py` | `make test` exit 0 | `POST /tenants/{id}/users` removed; `test_historic_users_route_gone_with_jwt` 404/405 | green |
| TASK-W2-03 | REQ-10, REQ-15, REQ-21 | `programme_wipe_service.py`, `test_programme_wipe_service.py` | `pytest tests/unit/test_programme_wipe_service.py -q` | wipe deletes memberships; identity not a wipe collaborator; ACTIVE 409 unchanged | green |
| TASK-W2-04 | REQ-21, REQ-27 | helper + onboard/wipe/dead-doors/old-doors verify scripts | human live command | FILE extended: helper is enter→grant→login; dead-doors asserts 014/012 gone — **did not** run smoke as success | green |

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` under `tests/verify`
- Agent created planned FILE: yes (extended) — **did not** run smoke/sandbox as success

## Compile-safe extras (not in §9 file list)

- `tests/unit/test_tenant_routes.py` — historic users route gone (404/405)
- As-built pointer + `Implementation-Status-INIT-GATEFLOW-017.md` W2 detail (not `human_approved`)
- `tests/README.md` — W2 feature map; 014 attach row points at dead-doors

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-017 W2] Delete 014 doors + wipe collaborator`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W2.md`
  - head_ref: `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W2.md
  blockers: []
  signals:
    wave: W2
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/247"
    current_task: TASK-W2-04
    implements:
      - REQ-10
      - REQ-15
      - REQ-20
      - REQ-21
      - REQ-27
    completed_tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_dead_doors_deleted"
    check_result: "exit 0"
    test_result: "622 passed"
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-017 W2] Delete 014 doors + wipe collaborator"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W2.md
    head_ref: feature/INIT-GATEFLOW-017-w2-delete-doors-wipe
    base_ref: develop
```
