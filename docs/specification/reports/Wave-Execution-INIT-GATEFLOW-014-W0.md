# Wave execution — INIT-GATEFLOW-014 W0

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Wave | W0 |
| Wave head context | Bound by Forge/human: `develop` (local tree; publish via `/commit-workspace`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/215 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W0-01 | REQ-06 | `src/models/role_types.py` create; `src/models/auth_models.py` modify | exit 0; invalid role raises ValidationError | `make check` exit 0; `make test` exit 0; `pytest tests/unit/test_auth_middleware.py -k role -q` exit 0 | green |
| TASK-W0-02 | REQ-05 | `tests/unit/test_auth_middleware.py` create | 6+ negative-path 401 cases | `make check` / `make test`; `pytest tests/unit/test_auth_middleware.py -v` — missing/malformed/expired/wrong-iss/wrong-aud/unrecognized-role/tenant_admin-missing-tenant_id | green |
| TASK-W0-03 | REQ-01 | user identity schema + repository create | create+read by credential id | `pytest tests/unit/test_user_identity_repository.py -q` exit 0; `env.py` registers schema | green |
| TASK-W0-04 | REQ-01, REQ-47 | `scripts/seed_platform_admin.py` create | double-run → one row, two JWTs | Script delivered; unit covers idempotent ensure via `test_auth_identity_service`; live seed path in `verify_jwt_login` | green |
| TASK-W0-05 | REQ-02, REQ-03, REQ-43 | `auth_identity_service.py` + `login_routes.py` create | happy 200+JWT / invalid 401 | `pytest tests/unit/test_auth_identity_service.py -v` exit 0; mounted `POST /api/auth/login` + `/api/auth` public allowlist | green |
| TASK-W0-06 | REQ-04, REQ-06, REQ-07 | `middleware.py` modify; `tests/verify/verify_jwt_login.py` create | claim_shape round-trip | `pytest tests/unit/test_auth_middleware.py -k claim_shape -q` exit 0; live FILE created (not executed as success) | green |

## Observed toolchain

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — **507 passed**

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_jwt_login`
- Agent created planned FILE: **yes** — **did not** run smoke/sandbox as success
- Prerequisite: human Alembic for `user_identities` — `DDL-NOTE-INIT-GATEFLOW-014-W0-user-identities.md`

## Supporting changes (wiring)

- DI: `RepositoryModule`, `BusinessServicesModule`, `dependency_container`
- `src/app.py` — mount auth router; add `/api/auth` to `public_paths` (product `/api/v1/*` allowlist unchanged)
- `postgres_migrations/env.py` — register `user_identity_schema`
- `src/utils/password_hashing.py` — PBKDF2 helpers
- as-built + `tests/README.md` feature map rows

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-014 W0] Seed platform_admin + JWT mint/login edge`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W0.md`
  - head_ref: bound wave head (recommend `feature/INIT-GATEFLOW-014-w0-jwt-login` cut from `develop`, or current bound ref)
  - base_ref: `develop`

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-014
    wave: W0
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/215"
    completed_tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
      - TASK-W0-06
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_jwt_login"
    unit_result: "507 passed"
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    title: "[INIT-GATEFLOW-014 W0] Seed platform_admin + JWT mint/login edge"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W0.md
    head_ref: feature/INIT-GATEFLOW-014-w0-jwt-login
    base_ref: develop
```
