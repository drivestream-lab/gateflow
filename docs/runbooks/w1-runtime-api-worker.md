# W1 runtime — API + worker

## Topology (ADR-001)

| Process | Entry | Role |
|---------|-------|------|
| API | `.venv/bin/python -m src.main` | Webhooks, health, programme-token status/metrics |
| Worker | `.venv/bin/python -m src.worker_main` | Claim jobs (`SKIP LOCKED`) → `RunOrchestrator` |

Postgres job rows couple the processes. Webhook handlers must not run PolicyEngine
or AgentRunner inline.

## Local stack

```bash
# Preferred — API + worker (ADR-001). Needed for wave-start / engineering-lane verify.
make run

# Or separate terminals:
make run-api      # HTTP only
make run-worker   # job claim loop only
```

`make run` alone used to start **only** the API; jobs stayed `pending` and Cursor
never ran. Worker claims Postgres jobs and runs `RunOrchestrator`.

```bash
./scripts/run_postgres_migration.sh head
# .env already points at shared Postgres/Redis (no docker-compose required)

# Terminal A
make run

# Terminal B — verify
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_all
```

Health while worker runs:

```bash
curl -s "http://127.0.0.1:8080/health?detailed=true"
```

Expect aggregate `up` with postgres/redis `up`. Webhook ack stays fast; work happens
in the worker after claim.

## Live verify

```bash
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_all
```

`verify_all` includes health, webhook signature/idempotency, programme-token
metrics/status, and labelled wave enqueue smoke.
