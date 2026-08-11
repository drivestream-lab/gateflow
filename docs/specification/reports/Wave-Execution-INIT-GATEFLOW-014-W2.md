# Wave execution — INIT-GATEFLOW-014 W2

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Wave | W2 |
| Wave head context | Bound by Forge/human: `develop` @ `5524952` (local tree; publish via `/commit-workspace` onto `feature/INIT-GATEFLOW-014-w2-*` cut from develop) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/217 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W2-01 | REQ-23,24,29,30,31 | `src/common/auth/dependencies.py` | `pytest tests/unit/test_auth_dependencies.py -v` | exit 0; `require_programme_scope` / path-tenant matrix | green |
| TASK-W2-02 | REQ-04,32,33 | Appendix-C routes + `src/app.py` + `catalogue_connection_routes.py` | flipped programme/tenant token tests | old doors refused; `public_paths` = health/internal/webhooks/auth; `verify_jwt_cutover.py` co-shipped | green |
| TASK-W2-03 | REQ-25 | `forge_client.py`, `github_token_provider.py`, `infra_module.py` | `pytest tests/unit/test_forge_client_factory.py -v` | exit 0; `ForgeClientFactory` + `ProgrammePatTokenProvider` | green |
| TASK-W2-04 | REQ-23,24,31 | `run_store_schema.py`, `run_store_repository.py`, verify isolation | tenant_scope unit + verify script | `RunSchema.tenant_id` non-null; get/list scoped; DDL note; `verify_cross_programme_isolation.py` | green |
| TASK-W2-05 | REQ-26,41 | `slot_validator.py`, `cursor_agent_runner.py` | slot + cursor unit; zero `has_api_key()` in slot_validator | catalogue-only; orchestrator passes catalogue `credential=` (supporting wiring) | green |
| TASK-W2-06 | REQ-28 | `src/api/webhooks/github_routes.py` inspect | review: no JWT/`require_role` imports; `/webhooks` still public | confirmed — webhook file not mutated for JWT cutover | green |

## Observed toolchain

- `make check` — exit 0 (black, ruff, pyright, import-linter)
- `make test` — **544 passed**

## Live verify (human — not claimed here)

- Planned scripts:
  - `.venv/bin/python -m tests.verify.verify_jwt_cutover`
  - `.venv/bin/python -m tests.verify.verify_cross_programme_isolation`
- Agent created planned FILEs: **yes** — **did not** run smoke/sandbox as success
- Prerequisite: human Alembic — squashed baseline
  `postgres_migrations/versions/5e85268f844f_first_version.py` (DB reset;
  includes non-nullable `runs.tenant_id`)

## Supporting changes (wiring)

- Auth deps + JWT cutover on control-plane / tenant / catalogue routes
- Create-run paths (`wave_start` / `run_orchestrator` / `closure_start`) resolve `tenant_id` via workspace credential
- `RunOrchestrator` injects `PlatformAgentCatalogueRepository` and passes catalogue credential into `CursorAgentRunner.run_skill`
- Unit fixtures updated for required `tenant_id` and SlotValidator catalogue mocks

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-014 W2] JWT cutover + per-programme ForgeClient + tenant-scoped runs + catalogue agents`
  - body_path: `docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W2.md`
  - head_ref: `feature/INIT-GATEFLOW-014-w2-jwt-cutover` (cut from develop — Forge/human)
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W2.md
  blockers: []
  signals:
    wave: W2
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/217"
    completed_tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
      - TASK-W2-05
      - TASK-W2-06
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_jwt_cutover
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_cross_programme_isolation
    unit_passed: 544
    migration: postgres_migrations/versions/5e85268f844f_first_version.py
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-014 W2] JWT cutover + per-programme ForgeClient + tenant-scoped runs + catalogue agents"
    body_path: docs/specification/reports/PR-Body-INIT-GATEFLOW-014-W2.md
    head_ref: feature/INIT-GATEFLOW-014-w2-jwt-cutover
    base_ref: develop
```
