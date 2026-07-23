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
# docker-compose -f docker/docker-compose.yml up -d
# ./scripts/run_postgres_migration.sh head
# .venv/bin/python -m src.main
# set -a && source .env && set +a   # needs GITHUB_WEBHOOK_SECRET for webhook step
# .venv/bin/python -m tests.verify.verify_all
#
# Individual scripts:
# .venv/bin/python -m tests.verify.verify_health
# .venv/bin/python -m tests.verify.verify_webhook
```

## Feature map (INIT-GATEFLOW-001)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Health | `python -m tests.verify.verify_health` (also in `verify_all`) | `tests/unit/test_health.py` |
| Programme config | — | `tests/unit/test_programme_config.py` |
| RunStore DTOs | — (needs human migration for live) | `tests/unit/test_run_store_models.py` |
| Webhook signature / idempotency | `python -m tests.verify.verify_webhook` (also in `verify_all`) | `tests/unit/test_webhook_ingress.py` |
| Full W0 live smoke | `python -m tests.verify.verify_all` | — |
| Worker stub claim | docker-compose worker (manual) | `tests/unit/test_job_worker.py` |
| Handoff / workflow resolve | — | `tests/unit/test_handoff_workflow.py` |
| ForgeClient forbid gates | — | `tests/unit/test_forge_client.py` |
