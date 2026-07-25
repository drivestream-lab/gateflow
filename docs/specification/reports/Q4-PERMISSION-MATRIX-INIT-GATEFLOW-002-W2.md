# Q-4 — App / Projects permission matrix (INIT-GATEFLOW-002 W2 exit)

| Item | Value |
|------|-------|
| Question | App/Projects permission matrix for board create/list/status/link (spec A-4 / IM-04) |
| Plan gate | TASK-W2-06 — block **W2 exit** until confirmed **or** board MVP narrowed |
| Date | 2026-07-24 |

## Decision for W2 exit

**Narrow board MVP (Issues API)** — do **not** require GitHub Projects (classic or
v2) permissions for W2 exit.

| Operation | Implementation | Required App permissions |
|-----------|----------------|--------------------------|
| Create / list tickets | GitHub Issues REST + labels (`gateflow/type:*`, `gateflow/initiative:*`) | `issues: write` (and read) on target repos |
| Status / column | Issue `state` + `gateflow/column:*` label | `issues: write` |
| Link PR → ticket | Structured issue comment (`gateflow-board-link`) | `issues: write` |
| PR create/comment (inherited W1) | Pulls + issue comments | `pull_requests: write`, `issues: write` |
| GitHub Projects column moves | **Not in W2 MVP** | N/A — deferred until Projects matrix confirmed |

## Rationale

TDD deferred Q-4 with default: proceed W0/W1; **block W2 exit** until matrix
confirmed **or** narrow board MVP if Projects unavailable. Issues-label MVP
satisfies FR-24 dumb primitives without Projects GraphQL.

## Follow-on

If PE later requires true Projects board columns, extend ForgeClient with
Projects APIs and re-open Q-4 with the App permission matrix before enabling
that transport.
