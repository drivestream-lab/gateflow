# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-07-23 |
| Source | Scaffold + INIT-GATEFLOW-001 W0 in progress (`feature/INIT-GATEFLOW-001-w0-control-plane`) |

## Testing harness

| Layer | Command / path | Status |
|-------|----------------|--------|
| Toolchain | `make check` | Wired (black, ruff, pyright, import-linter) |
| Unit | `make test` → `tests/unit/` | Health + programme config |
| Live verify | `tests/verify/` | Placeholder docs; no `verify_webhook` yet |
| CI | `.github/workflows/ci.yml` | Placeholder (does not run `make check`/`test`) |

## Capability matrix

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Health liveness | scaffold | `GET /health` | `tests/unit/test_health.py` | `tests/verify/01-health-detailed.md` (manual) | Exists |
| JWT AuthMiddleware | scaffold | `src/common/auth/` | via TestClient fixture | — | `public_paths`: `/health`, `/internal` |
| Postgres / Redis infra | scaffold | `PostgresService`, `RedisService` | mocked in unit | docker-compose | Lifecycle only |
| GitHub App webhooks | INIT FR-1–4 | — | — | — | Not started (W0 remaining) |
| RunStore + job queue | INIT FR-5, FR-17 | — | — | — | No ORM tables; Alembic `versions/` empty |
| HandoffReader / WorkflowEngine / PolicyEngine | INIT FR-6–8, FR-10 | — | — | — | Consume pin `v0.5.0-rc.2` |
| AgentRunner (Cursor) | INIT FR-9 | — | — | — | No worker entrypoint |
| ForgeClient / Notifier | INIT FR-11–12 | — | — | — | — |
| Metrics + status API | INIT FR-13, FR-15 | — | — | — | Programme-token auth not present |
| Programme config | INIT FR-18 | `config/programme.yaml` + `load_programme_config` in API lifespan | `tests/unit/test_programme_config.py` | — | Partial W0 — worker load pending W0-04; **not** human_approved |
| W1 runbook | INIT FR-19 | — | — | — | — |
| Async worker process | INIT FR-17 | — | — | — | No `worker_main.py` |

## Wave status

| Wave | Plan | Ground report | as-built status |
|------|------|---------------|-----------------|
| W0 | In progress (TASK-W0-01 done) | `docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W0.md` (findings) | **not** human_approved |
| W1 | Not started | — | — |

## Verdict

**W0 incomplete.** Programme config (FR-18) landed on the feature branch; webhook, RunStore, worker, handoff/workflow resolve, ForgeClient, and live verify remain. Resume `/loop-spec` before wave sign-off.
