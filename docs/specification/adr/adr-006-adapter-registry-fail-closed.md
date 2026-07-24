# ADR-006 — Adapter registry and fail-closed selection

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-002 |
| Feasibility finding | S-6, F13-2 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |
| Relates to | Extends ADR-003 (slot ownership unchanged); does not move adapters into business |

## Context

**ADR-003** places outbound adapters (forge client, agent runners, harness sync,
and any ToolProvider that performs external I/O) in **infra**, and orchestration
in **business**. It does not specify:

1. How multiple adapters for the same slot kind are **registered and selected**
2. When the runtime decides a selected adapter is **safe to use** (implemented
   vs honest stub / unavailable)
3. Whether an unimplemented selection fails **before work is accepted** or only
   when the adapter is first invoked

Product which adapters exist, which ids are live vs stub, and which programme
config keys select them remain in the INIT / programme config / TDD — adapters
must honor those contracts, but this ADR does **not** catalogue them
(same stance as ADR-003 on product invariants).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Hardcode selection inside the orchestrator | Fast to ship | Couples policy to concrete adapter types; blocks swaps |
| B — **Business-owned registry + validator**; infra adapters register by opaque id with an `implemented` capability; resolve required ids from config; **fail closed before accepting work** if any required id is unimplemented; unused registered stubs OK | Pluggable; auditable; no silent mid-run substitute | Registry must stay in sync with DI bindings |
| C — Validate only at first adapter invocation | Less work at the accept boundary | Mid-run surprise; silent fallback risk if callers catch and retry elsewhere |

## Recommendation

**Option B.**

1. **Registry** — opaque string id → capability descriptor at minimum
   `{ implemented: bool }` plus the injected infra instance / factory.
2. **Selection** — business resolves the **set of adapter ids required for the
   accepted unit of work** from programme configuration (defaults + overrides).
   Concrete key names and override shapes are TDD/config schema, not this ADR.
3. **Validation timing** — run validation **before** the unit of work is accepted
   for durable enqueue/dispatch (API accept path and again in the worker before
   first adapter call — defense in depth, same rule).
4. **Failure** — structured error identifying adapter id and config key; **zero**
   calls to unimplemented adapters; no silent substitution with another id.
5. **Ownership** — registry + validator are **business** (selection policy);
   live and stub adapters remain **infra** (ADR-003). Routers never import
   adapter implementations.

## Consequences

- Adding or swapping an adapter is register + config, not a PolicyEngine rewrite.
- Prefer rejecting at the accept boundary over creating durable work that cannot
  run; exact HTTP mapping is a TDD concern.
- DI may assemble a registry singleton from known adapter bindings.

## Revisit triggers

- Selection must incorporate live health probes beyond a static `implemented` flag.
- Per-stage notifier (or other slot) overrides change the “required set” algorithm
  enough to need a new decision.
- ToolProvider (or other) slots gain non-no-op implementations that must share
  the same validator.

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
