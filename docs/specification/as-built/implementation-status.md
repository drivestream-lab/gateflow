# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-07-23 |
| Source | INIT-GATEFLOW-001 W0 on `feature/INIT-GATEFLOW-001-w0-control-plane` |

## Testing harness

| Layer | Command / path | Status |
|-------|----------------|--------|
| Toolchain | `make check` | Wired (black, ruff, pyright, import-linter) |
| Unit | `make test` → `tests/unit/` | Health, programme config, RunStore DTOs, webhook, worker, handoff/workflow, ForgeClient |
| Live verify | `tests/verify/verify_webhook.py` | Implemented; needs API + migrated Postgres |
| CI | `.github/workflows/ci.yml` | Placeholder (does not run `make check`/`test`) |

## Capability matrix

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Health liveness | scaffold | `GET /health` | `tests/unit/test_health.py` | `tests/verify/01-health-detailed.md` (manual) | Exists |
| JWT AuthMiddleware | scaffold | `src/common/auth/` | via TestClient fixture | — | `public_paths`: `/health`, `/internal`, `/webhooks` |
| Postgres / Redis infra | scaffold | `PostgresService`, `RedisService` | mocked in unit | docker-compose | Lifecycle only |
| GitHub App webhooks | INIT FR-1 | `POST /webhooks/github` + `WebhookIngressService` | `tests/unit/test_webhook_ingress.py` | `tests.verify.verify_webhook` | Needs human RunStore migration for live |
| RunStore + job queue | INIT FR-5, FR-17 | ORM + repos | `tests/unit/test_run_store_models.py` | blocked on migration | See `DDL-NOTE-INIT-GATEFLOW-001-W0-runstore.md` |
| HandoffReader / WorkflowEngine | INIT FR-6–7 (resolve) | `handoff_reader.py`, `workflow_engine.py` | `tests/unit/test_handoff_workflow.py` | — | Resolve only; no PolicyEngine dispatch |
| PolicyEngine / AgentRunner | INIT FR-7–9 | — | — | — | W1 |
| ForgeClient | INIT FR-12 | `forge_client.py` | `tests/unit/test_forge_client.py` | — | Comments + forbid gate labels/auto-merge |
| Notifier / metrics / status API | INIT FR-11,13,15 | — | — | — | W1 |
| Programme config | INIT FR-18 | `config/programme.yaml` + loader | `tests/unit/test_programme_config.py` | — | Fail-fast at API/worker startup |
| W1 runbook | INIT FR-19 | — | — | — | W1 |
| Async worker process | INIT FR-17 (partial) | `src/worker_main.py` stub | `tests/unit/test_job_worker.py` | manual | Stub handler only |

## Wave status

| Wave | Plan | Ground report | as-built status |
|------|------|---------------|-----------------|
| W0 | Code complete; migration + live verify outstanding | `docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W0.md` (findings) | **not** human_approved |
| W1 | Not started | — | — |

## Verdict

**W0 code skeleton is in place** (programme config, RunStore ORM/repos, webhook, worker stub, handoff/workflow resolve, ForgeClient, unit tests, verify script). Ground-spec **findings**: human Alembic revision and live `verify_webhook` still required before wave sign-off. Do not mark `human_approved` yet.
