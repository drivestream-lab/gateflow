# Wave execution — INIT-GATEFLOW-017 W3

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Wave | W3 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-017-w3-enter-programme` |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W3-01 | REQ-16, REQ-18, REQ-26 | `login_routes.py`, `auth_identity_service.py`, `auth_models.py`, `test_auth_identity_service.py` | `pytest tests/unit/test_auth_identity_service.py -q` exit 0 | `make check` exit 0; `make test` 626 passed; enter granted 200 snapshot; 403 `not granted`; no remint; me has grants and no roster | green |
| TASK-W3-02 | REQ-16, REQ-17, REQ-19, REQ-23 | `verify_cross_programme_isolation.py`, `verify_jwt_login.py` | human live command | FILE extended: enter→grant→login→enter-programme; two-programme delivery; platform_admin 403 — **did not** run smoke as success | green |
| TASK-W3-03 | REQ-19, REQ-27 | as-built detail + index | one index row; detail lists W0–W3 | Index collapsed to one 017 pointer; W3 capability detail added; not `human_approved` | green |

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` under `tests/verify`
- Agent created planned FILE: yes (rewrote isolation; extended jwt_login) — **did not** run smoke/sandbox as success

## Compile-safe extras (not in §9 file list)

- `src/app.py` — `public_paths` narrowed from `/api/auth` to `/api/auth/login` so `/me` and `/session/programme` receive JWT context
- `tests/README.md` — W3 feature map

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-017 W3] Enter programme + isolation + as-built`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W3.md`
  - head_ref: `feature/INIT-GATEFLOW-017-w3-enter-programme`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W3.md
  blockers: []
  signals:
    wave: W3
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/248"
    current_task: TASK-W3-03
    implements:
      - REQ-16
      - REQ-17
      - REQ-18
      - REQ-19
      - REQ-23
      - REQ-26
      - REQ-27
    completed_tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_cross_programme_isolation"
    check_result: "exit 0"
    test_result: "626 passed"
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-017 W3] Enter programme + isolation + as-built"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W3.md
    head_ref: feature/INIT-GATEFLOW-017-w3-enter-programme
    base_ref: develop
```
