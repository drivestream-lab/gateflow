# ADR-007 — Invocation brief ownership and AgentRunner message contract

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-005-BOUNDINPUT |
| Feasibility finding | FF-06 (brief / runner half) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-27 via Cursor chat on Draft spec PR https://github.com/drivestream-lab/gateflow/pull/52 |
| Approved head | `d3c2177be2956dadeab8223ed5e3f2643d37957c` |
| Relates to | Extends ADR-003 (slot ownership unchanged); does not move AgentRunner into business |

## Context

**ADR-003** places outbound AgentRunner adapters in **infra** and orchestration
in **business**. It does not specify:

1. Which layer **constructs** the invocation brief for automated packaged-skill
   runs (pin package resolve / validate / render vs adapter-authored prose)
2. Whether the AgentRunner public contract is **message-executing** or
   **brief-authoring**

Product which packages exist, bind field names, template syntax, pin directory
layout, prove-it skill ids, and RunStore column names remain in the INIT / TDD /
upstream pin contract — this ADR does **not** catalogue them (same stance as
ADR-003 / ADR-006 on product invariants).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Infra AgentRunner owns brief construction (resolve/render or invent prose inside the adapter) | Fewer business types | Couples pin/filesystem/schema to SDK adapter; violates ADR-003 intent; hard to unit-test without the runner |
| B — **Business owns brief construction**; **infra AgentRunner executes a caller-supplied message only** (no brief authorship in the adapter) | Aligns ADR-003; swappable runners; testable without SDK | Extra business module + explicit orchestrator→runner message contract |
| C — Shared “prompt gateway” as a new slot kind beside AgentRunner | Clear third party | New slot taxonomy; premature for single Cursor runner |

## Recommendation

**Option B.**

1. **Business** owns resolve / validate / render of invocation briefs for
   automated packaged-skill runs (exact module name and pin search roots are TDD).
2. **Infra AgentRunner** accepts a caller-supplied message and must not author
   the invocation brief for that path.
3. Business depends on the AgentRunner abstraction, not SDK types (ADR-003).

Failure timing, HTTP mapping, bind dictionaries, and anti-hardcode test names
are TDD / INIT concerns — not this ADR.

## Consequences

- Swapping or adding an AgentRunner does not rewrite brief-construction policy.
- Brief construction can be unit-tested without Cursor (or other) SDK.
- Import-linter layers remain: api → business → repository; infra injected into
  business.

## Revisit triggers

- A second live AgentRunner needs a different message-construction ownership.
- Brief construction requires long-lived external I/O that belongs in infra
  (blur with ADR-003 ToolProvider-style resources).
- Upstream packages stop being filesystem artifacts and require a remote registry
  client (new infra slot).

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
