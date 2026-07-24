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
#   (INIT-GATEFLOW-002 W0: apply human Alembic for runs.wave_id — see
#    docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-002-W0-wave-id.md)
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
# .venv/bin/python -m tests.verify.verify_wave_start   # primary wave-start (002)
# .venv/bin/python -m tests.verify.verify_wave_smoke   # label ingress ack only
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
| Labelled wave enqueue smoke | `python -m tests.verify.verify_wave_smoke` (superseded as primary) | — |
| Full live smoke | `python -m tests.verify.verify_all` | — |
| Worker claim | `src.worker_main` (manual / compose) | `tests/unit/test_job_worker.py` |
| Handoff / workflow resolve | — | `tests/unit/test_handoff_workflow.py` |
| ForgeClient forbid gates | — | `tests/unit/test_forge_client.py` |

## Feature map (INIT-GATEFLOW-002 — W0)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Programme config notifier + override coerce | — | `test_programme_config` |
| Adapter registry / SlotValidator fail-closed | — | `test_slot_validator` |
| API wave-start (FR-15) | `python -m tests.verify.verify_wave_start` (in `verify_all`) | `test_wave_start` |
| Label start disabled (FR-15) | unit + note in `verify_wave_start` | `test_trigger_policy` |
| Run list/detail timeline (FR-20) | `verify_wave_start` + `verify_status_metrics` | programme token / wave start tests |
| Stub fail-closed (FR-18) | — | `test_slot_validator`, `test_wave_start` |

See spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`.
