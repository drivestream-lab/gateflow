# Wave execution — INIT-GATEFLOW-017 W0

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Wave | W0 |
| Wave head context | Bound by Forge/human: `feature/INIT-GATEFLOW-017-w0-session-membership` |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/245 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W0-01 | REQ-21 | `user_identity_schema.py` modify; `programme_membership_schema.py` create; `postgres_migrations/env.py` modify | Alembic create script adds memberships and drops `user_identities.tenant_id` | `./scripts/create_postgres_migration.sh "identity membership and session epoch"` exit 0; revision `postgres_migrations/versions/9713e795e01c_identity_membership_and_session_epoch.py` | green |
| TASK-W0-02 | REQ-21 | `user_identity_repository.py` modify; `programme_membership_repository.py` create; `test_programme_membership_repository.py` create | Unique `(identity_id, programme_id)` pair persists | `make test` exit 0; `test_create_and_load_unique_identity_programme_pair` green; `delete_for_tenant` removed | green |
| TASK-W0-03 | REQ-12, REQ-14, REQ-16 | `middleware.py` modify; `dependencies.py` modify; `test_auth_middleware.py` modify | TENANT_ADMIN without `tenant_id` not 401; epoch/status 401 | `make check && make test` exit 0; `test_tenant_admin_missing_tenant_id_not_401`; `test_require_role_suspended_401`; `test_require_role_epoch_mismatch_401` | green |
| TASK-W0-04 | REQ-03, REQ-16, REQ-18 | `auth_identity_service.py` modify; `auth_models.py` modify; `login_routes.py` modify; `test_auth_identity_service.py` modify | Login 200 includes `access_token` and `grants`; JWT has no `tenant_id` | `pytest tests/unit/test_auth_identity_service.py -q` covered by `make test` exit 0 | green |
| TASK-W0-05 | REQ-03, REQ-18 | `tests/verify/verify_jwt_login.py` modify | Live login 200 with `grants`; marker includes REQ-03 and REQ-18 | FILE extended (`prayog:covers:` includes REQ-03, REQ-18); **not** executed as success | green |

## Observed toolchain

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — **602 passed**

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_jwt_login`
- Agent created planned FILE: **yes** (extended) — **did not** run smoke/sandbox as success
- Prerequisite: human `./scripts/run_postgres_migration.sh head` (revision `9713e795e01c`); `make run`; `auth.platform_admin` in `tests/config.yaml`

## Supporting changes (compile-safe / wiring)

- `src/models/identity_status_types.py` — `IdentityStatusType` (`active` / `suspended`) for W0 session checks
- `src/models/programme_membership_models.py` — membership read DTO
- `src/di/modules/repository_module.py` — bind `ProgrammeMembershipRepository`
- `src/business_services/programme_service.py` — attach no longer writes `tenant_id` or mints a programme claim
- `src/business_services/programme_wipe_service.py` — no longer deletes identity rows
- `tests/unit/conftest.py` — default bypass of row session/membership gates; `real_session_gate` opts in
- as-built + `tests/README.md` feature map rows

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-017 W0] Membership schema + identity JWT session`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W0.md`
  - head_ref: `feature/INIT-GATEFLOW-017-w0-session-membership`
  - base_ref: `develop`

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    wave: W0
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/245"
    current_task: null
    completed_tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_jwt_login"
    unit_result: "602 passed"
    wave_head: feature/INIT-GATEFLOW-017-w0-session-membership
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    title: "[INIT-GATEFLOW-017 W0] Membership schema + identity JWT session"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W0.md
    head_ref: feature/INIT-GATEFLOW-017-w0-session-membership
    base_ref: develop
```
