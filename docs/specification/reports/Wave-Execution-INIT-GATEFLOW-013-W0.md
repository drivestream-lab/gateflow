# Wave execution — INIT-GATEFLOW-013 W0

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Wave | W0 |
| Wave issue | https://github.com/drivestream-lab/gateflow/issues/200 |
| Wave head context | Bound by Forge/human: `develop` working tree (recommended publish head `feature/INIT-GATEFLOW-013-w0-programme-connect`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Outcome | pass |
| Date | 2026-08-09 |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W0-01 | REQ-01, REQ-28 | `tenant_schema.py`, `tenant_repository.py`, `env.py` (existing import), DDL note | DDL note + schema + repo upsert/get | DDL-NOTE created; `TenantProgrammeConnectionSchema` + repo methods; env.py already imports tenant_schema | green |
| TASK-W0-02 | REQ-01 | `tenant_git_workspace_client.py`, unit test | `make test` | optional `ref` + `_checkout_ref`; unit tests green | green |
| TASK-W0-03 | REQ-05–07 | `src/engine/catalogue_parser.py`, catalogue models, unit test | `make test` | parser fail-closed; unit suite green | green |
| TASK-W0-04 | REQ-01–07, REQ-28 | onboarding service, connection models, programme routes, DI | `make check` | PUT connect + GET catalogue/connection; DI bound | green |
| TASK-W0-05 | REQ-02–04, REQ-28 | `test_programme_onboarding.py` | `make test` | upsert / fail-closed / auth mismatch / catalogue errors | green |
| TASK-W0-06 | REQ-01,04–06,28 | `verify_programme_connect.py`, README, as-built | live script FILE present | FILE created; feature-map + as-built W0 in_progress | green |

**Wave toolchain:** `make check` exit 0; `make test` exit 0 (2026-08-09).

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_programme_connect`
- Agent created planned FILE: **yes** — **did not** run smoke/sandbox as success
- Prerequisites: human Alembic from `DDL-NOTE-INIT-GATEFLOW-013-programme-connection.md`; PAT read on programme meta

## Contracts produced (for later Ground Report)

| Contract | Entry | Notes |
|----------|-------|-------|
| Programme connect | `PUT /api/v1/tenants/{tenant_id}/programme/connect` | body org/repo/optional ref; upsert one connection |
| Programme connection read | `GET …/programme/connection` | |
| Catalogue read | `GET …/programme/catalogue` | ADR-012 discovery-input parse |
| Git resolve + ref | `TenantGitWorkspaceClient.resolve_workspace(..., ref=)` | |

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - title: `[INIT-GATEFLOW-013 W0] Connect programme + catalogue discovery`
  - body_path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W0.md`
  - head_ref: `feature/INIT-GATEFLOW-013-w0-programme-connect`
  - base_ref: `develop`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W0
    wave_issue: https://github.com/drivestream-lab/gateflow/issues/200
    completed_tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
      - TASK-W0-06
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_programme_connect
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    title: "[INIT-GATEFLOW-013 W0] Connect programme + catalogue discovery"
    body_path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W0.md
    head_ref: feature/INIT-GATEFLOW-013-w0-programme-connect
    base_ref: develop
    # Prior hop on same pin: commit_workspace required before open_draft_pr
    commit_workspace:
      action: commit_workspace
      head_ref: feature/INIT-GATEFLOW-013-w0-programme-connect
```
