# ADR-003 — RunStore and job persistence (PostgreSQL, repository boundary)

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-03 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Context

Spec FR-5 / FR-3 require durable runs, stages, and events in PostgreSQL with no
SQLite fallback. FR-17 / ADR-001 add a Postgres job queue. Platform rules require
ORM only in repositories, Pydantic at business boundaries, and
**human-owned** Alembic revisions (`database-migrations.mdc`).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — SQLite for local, Postgres for prod | Easy laptop | Violates FR-5; dual schemas |
| B — Postgres everywhere; concrete ORM schemas + repos; human Alembic | Aligns product + MDC | Requires local docker Postgres |
| C — Business services call SQLAlchemy sessions directly | Faster short term | Violates repository-pattern / import-linter |

## Recommendation

**Option B.**

Logical tables (names illustrative; exact DDL in human migration):

| Table | Purpose |
|-------|---------|
| `webhook_deliveries` | Delivery/event id idempotency |
| `runs` | Run header: repo, PR/issue, status, retry_count, notify_pending, timestamps |
| `run_stages` | Per workflow_node attempt: outcome, runner, model_*, timestamps |
| `run_events` | Append-only metrics/audit events (FR-13 schema fields) |
| `jobs` | Async job queue: type, payload JSONB (Pydantic), status, claimed_at, run_id |

- ORM under `src/database/postgres/schema/`; repositories under
  `.../repository/`; DTOs under `src/models/`.
- JSONB payloads validated with Pydantic in the repository.
- Agents update schema modules + `postgres_migrations/env.py` imports; **humans**
  create/edit `versions/` revisions.

## Consequences

- W0 must land migrations before live verify of webhooks/runs.
- Metrics retention (90 days) enforced by documented SQL / purge job (W1 may be
  manual/ops SQL initially — note in plan).

## Revisit triggers

- Event volume requires partitioning or OLAP offload.
- Job queue moves to external broker (ADR-001 revisit).

## Acceptance finalization

After PE review comments are resolved and PE explicitly states the decision is
ready for acceptance, update the file before final GitHub approval:

```text
Status: Accepted
Decision owner: @{pe-name}
Approval evidence: {review/comment URL}
Approved head: {full SHA to be approved}
```

The formal PE GitHub Approve must be on the final commit containing this
Accepted metadata. No file changes occur after that approval.
