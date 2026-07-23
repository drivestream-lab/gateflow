# ADR-001 — Runtime topology and durable store

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-01, F-03 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-23 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/4); architecture package tip `ca74d77949046b8d91357c37bb2ea864dad60c26` |
| Approved head | `ca74d77949046b8d91357c37bb2ea864dad60c26` |

## Context

Gateflow must acknowledge inbound forge events quickly while long-running
orchestration (policy evaluation, agent dispatch, outbound forge calls) cannot
safely share the HTTP request lifecycle. Platform rules require PostgreSQL
persistence via the repository boundary and human-owned Alembic revisions.
Product constraints (Postgres SSOT; no SQLite fallback; dual API+worker) are
accepted upstream — this ADR chooses the engineering topology that satisfies them.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Single process (in-process background tasks) | One deployable | Agent work blocks/isolates poorly; hard to scale workers independently |
| B — Dual process (API + worker) with durable jobs in PostgreSQL | Fast HTTP ack; crash-safe queue; shared DB with run history; aligns DI `worker_main` pattern | Two entrypoints; job schema in same DB |
| C — Dual process with external broker (Redis/SQS/etc.) | Familiar queue ops | Extra infra; splits durability from run store |

## Recommendation

**Option B.**

- HTTP process: validate ingress, persist idempotency + enqueue work, return quickly.
- Worker process: claim jobs from PostgreSQL (`FOR UPDATE SKIP LOCKED` or equivalent),
  run orchestration, write run history through repositories.
- Both processes share `configure_container()` → `initialize_all_services()`.
- PostgreSQL is the sole durable store for runs and jobs; ORM only in repositories;
  agents update schema modules, humans own migration revision files.
- Domain table/column shapes live in the TDD data-contract section and migrations —
  not in this ADR.

## Consequences

- Runtime must schedule both API and worker.
- Job and run persistence share one migration stream.
- Moving to an external broker later supersedes the queue half of this decision
  (revisit triggers).

## Revisit triggers

- Job claim contention or poison-message rate needs a dedicated broker.
- Multi-region workers require different queue semantics.
- Event volume forces OLAP offload or partitioning beyond OLTP Postgres.

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
