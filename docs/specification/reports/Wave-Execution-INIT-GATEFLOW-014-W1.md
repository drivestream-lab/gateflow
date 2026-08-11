# Wave execution — INIT-GATEFLOW-014 W1

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Wave | W1 |
| Wave head context | Bound by Forge/human: `develop` @ `85f9984` (local tree; publish via `/commit-workspace` onto `feature/INIT-GATEFLOW-014-w1-*` cut from develop) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/216 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W1-01 | REQ-08,11,12,14 | `programme_schema.py`, `programme_repository.py` | `pytest tests/unit/test_programme_repository.py -q` exit 0 | exit 0; PAT/workspace/reserved App fields persisted in unit | green |
| TASK-W1-02 | REQ-08,09,10,13 | `programme_service.py` | `pytest tests/unit/test_programme_service.py -v` | bad PAT/meta → 0 rows; agent_key field → ValidationError; happy path creates | green |
| TASK-W1-03 | REQ-08,17,18 | `programme_admin_routes.py` | `pytest tests/unit/test_programme_admin_routes.py -v` | platform_admin create/list; tenant_admin → 403 FORBIDDEN | green |
| TASK-W1-04 | REQ-15,16,44,47 | programme_service + admin routes modify | `pytest … -k attach -v` | unknown programme 422; idempotent re-attach | green |
| TASK-W1-05 | REQ-19,20,40,45 | agent catalogue schema + repository | `pytest tests/unit/test_platform_agent_catalogue_repository.py -q` | exit 0 | green |
| TASK-W1-06 | REQ-21,22,41,42 | catalogue service + admin routes + `verify_agent_catalogue.py` | `pytest tests/unit/test_platform_agent_catalogue_service.py -v` | caller wins / lane default / unprovisioned reject; no CursorAgentSettings import | green |
| TASK-W1-07 | REQ-08 | rename to `catalogue_connection_*` + `verify_programme_onboarding.py` | `make check` exit 0; zero old symbol refs in `src/` / `tests/unit/` | rename complete; URLs under `/tenants/{id}/programme` unchanged | green |

## Observed toolchain

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — **525 passed**

## Live verify (human — not claimed here)

- Planned scripts:
  - `.venv/bin/python -m tests.verify.verify_programme_onboarding`
  - `.venv/bin/python -m tests.verify.verify_agent_catalogue`
- Agent created planned FILEs: **yes** — **did not** run smoke/sandbox as success
- Prerequisite: human Alembic — `DDL-NOTE-INIT-GATEFLOW-014-W1-programmes-agent-catalogue.md`

## Supporting changes (wiring)

- DI: `ProgrammeRepository`, `PlatformAgentCatalogueRepository`, `ProgrammeService`, `PlatformAgentCatalogueService`
- `src/common/auth/dependencies.py` — `require_role`
- `src/api/v1/__init__.py` — mount programme admin + agent-catalogue routers (`/api/v1/programmes`, `/api/v1/agent-catalogue` — not on `public_paths`, JWT required)
- `postgres_migrations/env.py` — register new schemas
- as-built + `tests/README.md` feature map

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-014 W1] Programme validate-then-create + tenant_admin attach + agent catalogue`
  - body_path: `docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W1.md`
  - head_ref: `feature/INIT-GATEFLOW-014-w1-programme-catalogue` (cut from develop — Forge/human)
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W1.md
  blockers: []
  signals:
    wave: W1
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/216"
    completed_tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
      - TASK-W1-06
      - TASK-W1-07
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_programme_onboarding
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_agent_catalogue
    unit_passed: 525
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-014 W1] Programme validate-then-create + tenant_admin attach + agent catalogue"
    body_path: docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W1.md
    head_ref: feature/INIT-GATEFLOW-014-w1-programme-catalogue
    base_ref: develop
```
