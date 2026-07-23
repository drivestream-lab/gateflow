# ADR-003 — Slot and layer ownership (infra vs business)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-05 (Q-1) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-23 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/4); architecture package tip `ca74d77949046b8d91357c37bb2ea864dad60c26` |
| Approved head | `ca74d77949046b8d91357c37bb2ea864dad60c26` |

## Context

Gateflow introduces pluggable outbound adapters (forge API, coding agent,
harness sync) and in-process orchestration (workflow/policy/handoff). Platform
MDC already separates infra clients from business services; this ADR records
how Gateflow applies that split so H2 runner swaps do not rewrite policy.

Product invariants (e.g. no gate-approval label writes, no auto-merge) remain
in the INIT/PRD — adapters must honor them, but this ADR does not redefine them.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Business services call SDKs directly | Fewer types | Untestable; violates infra boundary |
| B — Outbound I/O = infra (`BaseInfraService`); orchestration = business | Swappable adapters; DI-clear | More bindings |
| C — Single runtime “god” service | Fast to start | Blocks multi-runner; untestable |

## Recommendation

**Option B.**

- **Infra:** forge HTTP client, agent runner adapter, launchpad/harness client,
  and any ToolProvider that performs external I/O (H1 may be a no-op provider).
- **Business:** workflow resolution, dispatch policy, handoff read orchestration,
  run orchestration, notifier formatting, metrics emission, tool-slot resolution.
- Contracts (Protocol/ABC) live outside routers; business depends on abstractions,
  not SDK types.
- **Forge credentials (Q-1):** App installation token in production; scoped PAT
  only when explicitly configured for non-prod.

Named module list and DI wiring live in the TDD module boundary table.

## Consequences

- Swapping agent runners is an infra adapter + config change, not a PolicyEngine
  rewrite.
- Import-linter layers remain: api → business → repository → schema; infra is
  injected into business, not imported from api.

## Revisit triggers

- Multi-runner or model gateway changes ownership of “who picks models.”
- Tool providers gain long-lived resource lifecycles that blur infra vs business.

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
