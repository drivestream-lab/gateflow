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
docker compose -f docker/docker-compose.yml up -d
./scripts/run_postgres_migration.sh head
cp -n .env.example .env   # set GITHUB_* and PROGRAMME_SERVICE_TOKEN
make setup

# Terminal A
.venv/bin/python -m src.main

# Terminal B
.venv/bin/python -m src.worker_main
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
