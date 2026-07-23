# Ground report — INIT-GATEFLOW-001 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Control plane skeleton |
| Spec | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` |
| Date | 2026-07-23 |
| Branch | `feature/INIT-GATEFLOW-001-w0-control-plane` |
| Status | Draft — **wave incomplete** |
| Review deadline | 2026-07-27 |
| Deciders | Tech lead / reviewer: @nikd10x — explicit LGTM required (only after W0 tasks complete) |

## Automated check output

`ground_command`: N/A (no Makefile ground target; manual FR validation + `make check` / `make test`).

### `make check` (exit 0)

```
.venv/bin/black --line-length 100 src/ tests/
All done! 70 files left unchanged.
.venv/bin/ruff check --fix src/ tests/
All checks passed!
.venv/bin/pyright
0 errors, 0 warnings, 0 informations
.venv/bin/lint-imports
Layered architecture — no cross-layer imports KEPT
Contracts: 1 kept, 0 broken.
```

### `make test` (exit 0)

```
collected 5 items
tests/unit/test_health.py::test_health_returns_ok PASSED
tests/unit/test_programme_config.py::test_load_default_programme_config PASSED
tests/unit/test_programme_config.py::test_missing_programme_config_fails_fast PASSED
tests/unit/test_programme_config.py::test_invalid_programme_config_fails_fast PASSED
tests/unit/test_programme_config.py::test_get_instance_before_load_raises PASSED
5 passed
```

### Live verify

`verify_command` `.venv/bin/python -m tests.verify.verify_webhook` — **not applicable / missing** (TASK-W0-07 not implemented; no `tests/verify/verify_webhook.py`).

## FR checklist

W0 scope from Implementation Plan §1–§2: FR-1, FR-5, FR-6, FR-7 (resolve only), FR-12 (comments + forbid), FR-17 (partial worker), FR-18.

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-1 | Webhook signature + idempotency + enqueue; 401/503 | No `POST /webhooks/github`; `public_paths` still `/health`, `/internal` only | **fail** |
| FR-5 | Postgres RunStore (runs/stages/events/jobs) | No domain ORM schemas beyond base; `postgres_migrations/versions/` empty | **fail** |
| FR-6 | HandoffReader (ref + globs) | No `handoff_reader` business service | **fail** |
| FR-7 | WorkflowEngine resolve next node (no dispatch) | No `workflow_engine`; pin not loaded for resolve | **fail** |
| FR-12 | ForgeClient comments; forbid gate labels/auto-merge | No `forge_client` infra service | **fail** |
| FR-17 | API + async worker; job claim | No `worker_main.py`; no job claim loop | **fail** |
| FR-18 | Programme config load fail-fast | `config/programme.yaml` + `ProgrammeConfig` + `load_programme_config()` in API lifespan; unit tests | **pass** (API startup); worker startup N/A until W0-04 |

Out-of-wave FRs (W1 — not required for W0 exit; recorded for completeness):

| FR | Status |
|----|--------|
| FR-2, FR-3, FR-4, FR-8–11, FR-13–16, FR-19 | **fail** / not started (expected for W0) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Programme config is settings-style singleton, not injector-bound | ADR-004 | **pass** — `ProgrammeConfig.get_instance()` / `load_programme_config` |
| Secrets not in committed programme YAML | ADR-004 | **pass** — file has non-secret knobs only |
| Fail-fast on missing/invalid config | fail-fast.mdc; ADR-004 | **pass** — unit coverage |
| Models under `src/models/` only | pydantic-schemas.mdc | **pass** — `programme_config_models.py` |
| API does not import ORM schema | import-linter / repository-pattern | **pass** — layers KEPT |
| Webhook on `public_paths` (forge signature zone) | ADR-002 | **fail** — webhook not mounted |
| Dual process API + worker; jobs in Postgres | ADR-001 | **fail** — worker/jobs absent |
| ForgeClient is infra; handoff/workflow are business | ADR-003 | **fail** — modules absent |
| No agent-authored Alembic `versions/` yet | database-migrations.mdc | **pass** (nothing to violate); human migration still required when schemas land |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Scaffold DI + Postgres/Redis lifecycle | prior scaffold (no Ground-Report-W-1) | yes — unchanged |
| JWT `AuthMiddleware` + `public_paths` | scaffold / ADR-002 baseline | yes — still `/health`, `/internal` |
| Prior-wave Ground Report | N/A (W0 first wave) | N/A |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|---------|
| D-W0-01 | FR-1 | Webhook ingress, signature verify, idempotency, enqueue missing | Critical |
| D-W0-02 | FR-5 | RunStore schemas/repos + human Alembic revision missing | Critical |
| D-W0-03 | FR-17 | `worker_main` + SKIP LOCKED claim + stub handler missing | Critical |
| D-W0-04 | FR-6 / FR-7 | HandoffReader + WorkflowEngine resolve missing | Critical |
| D-W0-05 | FR-12 | ForgeClient + forbid-gate audit missing | Critical |
| D-W0-06 | FR-1 | Live `verify_webhook` missing | Critical |
| D-W0-07 | — | As-built still said programme config not started (corrected in this report's companion as-built edit) | Low |
| D-W0-08 | — | `/loop-spec` interrupted after TASK-W0-01; W0-02…W0-08 not done | Critical |

## Contracts produced by this wave

> **Incomplete wave.** Only the ProgrammeConfig contract is produced. Do **not** treat this table as a full W0 baseline for W1 `/pre-implement` until discrepancies D-W0-01…06 are closed and this report is revised to Status Draft→Ready with all W0 FRs pass/partial as planned.

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| ProgrammeConfig load | `src/configs/programme_config_loader.py` + `src/models/programme_config_models.py` | `load_programme_config` / `ProgrammeConfig.get_instance` | YAML path (default `config/programme.yaml` or `PROGRAMME_CONFIG_PATH`) | Validated programme knobs: trigger, handoff, retry, metrics, runner, model, tools | Missing/invalid file fails process start; not injector-bound; secrets excluded | W0 remaining tasks + W1 |

**Not yet produced (blocked for W1):** webhook enqueue, RunStore/job claim, HandoffReader, WorkflowEngine resolve, ForgeClient.

## PR instructions

> Do **not** open a merge-ready W0 PR until `/loop-spec` completes remaining tasks and this ground report is re-run to pass.
>
> When ready: commit this report + as-built on the same wave branch as code.

Branch:   `feature/INIT-GATEFLOW-001-w0-control-plane`
PR title: `[INIT-GATEFLOW-001 W0] control-plane — implementation + ground report` (when green)
Required reviewer: per CODEOWNERS / prayog-pe-team
Review deadline: 2026-07-27 (revisit after loop completes)

After reviewer approves (only when Ready for human checkpoint = yes):
  Update as-built: W0 → human_approved
  Merge PR
  → `/pre-implement` for W1

## Ready for human checkpoint?

**no** — W0 plan tasks W0-02…W0-08 incomplete; FR-1,5,6,7,12,17 fail; only FR-18 passed. Resume `/loop-spec` before re-running `/ground-spec`.

Human must (when re-grounded green):
- [ ] Review FR checklist — all W0 FRs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for W1
- [ ] Mark as-built: INIT-GATEFLOW-001 W0 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: findings
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W0.md
    digest: sha256:8da16975bd4f444c433908ed70704bc44e2ea8040a3e53dc49ec647f8dc76f0b
  blockers:
    - D-W0-01
    - D-W0-02
    - D-W0-03
    - D-W0-04
    - D-W0-05
    - D-W0-06
    - D-W0-08
  signals:
    wave: W0
    contracts_produced: 1
    wave_complete: false
    tasks_done: [TASK-W0-01]
    tasks_remaining: [TASK-W0-02, TASK-W0-03, TASK-W0-04, TASK-W0-05, TASK-W0-06, TASK-W0-07, TASK-W0-08]
    board_issue: https://github.com/drivestream-lab/gateflow/issues/6
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```
