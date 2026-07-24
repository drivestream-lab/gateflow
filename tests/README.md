# Tests for gateflow

## Structure

```
tests/
  unit/        Pure unit tests — no real infra, no network calls.
               Run: make test
  verify/      Live verify scripts (not collected by make test).
  _helpers/    Shared fixtures and helpers (e.g. verify preflight).
```

## Running

```bash
# Unit only (CI gate)
make check && make test

# Live verify (integration) — requires running API + Postgres with RunStore migration:
# docker compose -f docker/docker-compose.yml up -d
# ./scripts/run_postgres_migration.sh head
# .venv/bin/python -m src.main
# optional worker: .venv/bin/python -m src.worker_main
# set -a && source .env && set +a
#   needs GITHUB_WEBHOOK_SECRET + PROGRAMME_SERVICE_TOKEN
# .venv/bin/python -m tests.verify.verify_all
#
# Individual scripts:
# .venv/bin/python -m tests.verify.verify_health
# .venv/bin/python -m tests.verify.verify_webhook
# .venv/bin/python -m tests.verify.verify_status_metrics
# .venv/bin/python -m tests.verify.verify_wave_smoke
```

See also: `docs/runbooks/w1-runtime-api-worker.md`.

## Feature map (INIT-GATEFLOW-001 — delivered)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Health | `python -m tests.verify.verify_health` (in `verify_all`) | `tests/unit/test_health.py` |
| Programme config | — | `tests/unit/test_programme_config.py` |
| RunStore DTOs | — | `tests/unit/test_run_store_models.py` |
| Webhook signature / idempotency | `python -m tests.verify.verify_webhook` (in `verify_all`) | `tests/unit/test_webhook_ingress.py` |
| Trigger / policy | — | `tests/unit/test_trigger_policy.py` |
| Orchestrator paths | — | `tests/unit/test_run_orchestrator.py` |
| Tools none | — | `tests/unit/test_stage_tools.py` |
| Programme-token status/metrics | `python -m tests.verify.verify_status_metrics` (in `verify_all`) | `tests/unit/test_programme_token_api.py` |
| Labelled wave enqueue smoke | `python -m tests.verify.verify_wave_smoke` (in `verify_all`) | — |
| Full W0/W1 live smoke | `python -m tests.verify.verify_all` | — |
| Worker claim | `src.worker_main` (manual / compose) | `tests/unit/test_job_worker.py` |
| Handoff / workflow resolve | — | `tests/unit/test_handoff_workflow.py` |
| ForgeClient forbid gates | — | `tests/unit/test_forge_client.py` |

## Feature map (INIT-GATEFLOW-002 — planned)

| Capability | Verify script (planned) | Pytest (planned) |
|------------|-------------------------|------------------|
| API wave-start (FR-15) | replace label primary path in `verify_wave_smoke` / new `verify_wave_start` | wave-start auth, dual identity, preconditions |
| Stub fail-closed (FR-18) | — | registry + start validation |
| PR at run start (FR-19) | live PR-thread assert | ForgeClient PR open/update |
| Run list/detail (FR-20) | extend `verify_status_metrics` | list/filter + timeline |
| Metrics dims (FR-21) | extend `verify_status_metrics` | by runner / model_id |
| Board APIs (FR-24) | new board verify (W2) | dumb primitives + idempotency |
| Production no `gh` (FR-25/26a) | inspection / path guard | ForgeClient transport tests |

See spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` and feasibility:
`docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-002.md`.
