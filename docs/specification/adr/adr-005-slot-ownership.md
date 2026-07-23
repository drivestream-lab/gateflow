# ADR-005 — Pluggable slot ownership (infra vs business)

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-05 (includes Q-1 ForgeClient auth) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Context

Spec FR-9/11/12/14 define AgentRunner, ToolProvider, ForgeClient, and Notifier
slots. Platform `infra-services.mdc` places outbound HTTP/SDK clients in infra;
business services orchestrate use cases without embedding forge/agent SDKs.
Feasibility Q-1 asks App token vs PAT for ForgeClient.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — All slots as business services calling raw SDKs | Fewer packages | Violates infra boundary; untestable without network |
| B — Outbound clients = infra (`BaseInfraService`); orchestration = business | Aligns MDC; swappable adapters | More types in DI |
| C — Single “GateflowRuntime” god service | Fast initial coding | Untestable; blocks H2 multi-runner |

## Recommendation

**Option B.**

| Slot / component | Layer | Notes |
|------------------|-------|-------|
| `ForgeClient` | infra | GitHub App installation token in production; **scoped PAT allowed only in non-prod** when explicitly configured (resolves Q-1). Forbids gate-approval label writes and auto-merge. |
| `CursorAgentRunner` (AgentRunner) | infra | Implements runner interface; returns `RunResult`. |
| `LaunchpadHarnessClient` | infra | Pre-dispatch `sync-harness` (CTR-04). |
| `ToolProvider` / `NoneToolProvider` | infra or thin business adapter | H1 returns empty context. |
| `WorkflowEngine`, `PolicyEngine`, `HandoffReader`, `TriggerRouter` | business | No hardcoded node allowlists; read pin + programme config. |
| `RunOrchestrator` (or equivalent) | business | Claims job → policy → dispatch → stop; owns retry budget. |
| `Notifier` | business | Formats run events; calls `ForgeClient` for comments. |
| `MetricsEmitter` | business | Writes run_events via repository. |
| `StageToolResolver` | business | Resolves tool slot from config/metadata. |

Interfaces are Protocol/ABC types in `src/models/` or a dedicated
`src/business_services/slots/` contracts module — **not** defined inside routers.

## Consequences

- DI registers infra and business types per existing modules.
- Swapping Cursor → other runner is an infra adapter change without PolicyEngine edits.
- ForgeClient audit log retained with run (spec security table).

## Revisit triggers

- H2 multi-runner or LiteLLM gateway changes ModelGateway ownership.
- ToolProvider becomes MCP/Graphify with its own lifecycle.

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
