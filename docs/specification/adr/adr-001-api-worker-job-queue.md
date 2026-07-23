# ADR-001 — Dual-process API and async worker with Postgres job queue

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-01 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Context

PRD Decision #6 and spec FR-17 require webhook HTTP ack to be fast while
PolicyEngine, AgentRunner, and ForgeClient side effects run asynchronously.
The scaffold today has only `src/main.py` (HTTP). `dependency-injection.mdc`
documents a `worker_main.py` pattern sharing the same injector container.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Single process: background tasks in FastAPI | Simpler deploy | Agent runs block event loop / process; poor isolation; hard to scale workers |
| B — API + async worker; Postgres job table (SKIP LOCKED claim) | Matches Decision #6; durable queue; horizontal workers | Two entrypoints; migration for jobs table |
| C — External broker (Redis/SQS) in W1 | Familiar queue semantics | Extra infra; out of W1 product constraints (Postgres SSOT) |

## Recommendation

**Option B.** Ship `src/main.py` (API) and `src/worker_main.py` (worker). Both call
`configure_container()` → `initialize_all_services()`. API validates webhooks and
enqueues jobs; worker claims jobs from PostgreSQL (`FOR UPDATE SKIP LOCKED`),
runs orchestration, and writes RunStore. No Redis/SQS job broker in W1.

## Consequences

- Docker Compose / runtime must run both processes.
- Job schema is part of RunStore migrations (see ADR-003).
- Worker owns AgentRunner lifecycle and launchpad harness sync before dispatch.

## Revisit triggers

- Job claim contention or poison-message rate requires a dedicated broker.
- Need multi-region workers with different queue semantics.

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
