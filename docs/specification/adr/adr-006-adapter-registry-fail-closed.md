# ADR-006 — Adapter registry and fail-closed start selection

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

**ADR-003** places AgentRunner, Notifier outbound I/O, and ForgeClient in
**infra**, with business owning orchestration. INIT-GATEFLOW-002 requires:
- Multiple AgentRunner ids registered (`cursor` implemented; `opencode` /
  `claude_code` stubs)
- Multiple Notifier ids registered (`github_comment` implemented; `slack` /
  `teams` stubs)
- **Fail-closed at run start**: if any runner or notifier the run will need is
  a stub (or otherwise unimplemented), **block the entire run** before enqueue
  / dispatch — never silent fallback to Cursor/GitHub mid-run

ADR-003 does not specify selection, registry shape, or when validation runs.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Hardcode if/else in RunOrchestrator | Fast | Violates pluggability; PolicyEngine grows adapter knowledge |
| B — **Business-owned registry + SlotValidator**; infra adapters register by id; validate required slots at wave-start (API) and again before first dispatch | Clear fail-closed; unused stubs OK; ADR-003 ownership preserved | Extra types; must keep registry in sync with DI |
| C — Validate only at first AgentRunner call | Less API work | Mid-run surprise; contradicts FR-18 “block at start” |

## Recommendation

**Option B.**

1. **Registry** — string id → adapter capability descriptor:
   - `implemented: bool` (false for honest stubs)
   - factory / injected infra instance
2. **Resolution** — programme config selects defaults and per-`workflow_node`
   overrides (`runner.default`, `model.overrides`, `notifier.default`). Business
   resolves the **set of runner ids and the notifier id required for this run**
   before accept.
3. **Validation timing** — `SlotValidator.validate_for_run(...)` runs:
   - on wave-start API after identity + other preconditions that do not need
     dispatch, **before** job enqueue (FR-18 / precondition #10–11)
   - again in worker before AgentRunner (defense in depth; same result)
4. **Failure** — structured API/worker error naming stub id + config key;
   **zero** AgentRunner calls; unused registered stubs do not block.
5. **Ownership** — registry + validator are **business** (selection policy);
   stub/live adapters remain **infra** (ADR-003). Routers never import adapters.

## Consequences

- Adding OpenCode/Claude/Slack/Teams is register-stub + config — not PolicyEngine
  rewrites.
- Wave-start can 422 before RunStore run creation when stubs are selected
  (preferred) or create a terminal blocked run — TDD chooses **reject before
  enqueue** for cleaner concurrency/idempotency.
- DI may bind a registry singleton assembled from known adapter types.

## Revisit triggers

- Live second runner ships and needs health-probed readiness beyond `implemented`.
- Per-stage notifier overrides become product requirements.
- ToolProvider slots gain non-`none` implementations requiring the same validator.

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
