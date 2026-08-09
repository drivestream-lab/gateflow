# ADR-013 — Dual harness-readiness evaluators

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-013 |
| Feasibility finding | FF-02 (`Initiative-Feasibility-Report-INIT-GATEFLOW-013.md`) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Source spec digest | `sha256:44e10fa850753325b8acf1a892723fe5d3293da94f10ed9a129d8651dca595b4` |
| product_constraints | `[REQ-17, REQ-18, REQ-20, REQ-21, REQ-22]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Relates to | Infra boundary relative to existing `LaunchpadClient.sync_harness`; does not amend [`adr-003`](adr-003-slot-layer-ownership.md) |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-09 via Cursor chat (INIT-GATEFLOW-013 technical-review package) |
| Approved head | `3d9fa93b4b3f4519585898928a78b744d455c5f0` (Forge publish tip of Accepted package on chore/INIT-GATEFLOW-013-spec-gateflow) |
| Lint evidence | adr_boundary_lint.py 6/6, PASS, sha256:abcdfbb2b82045c2722df633bebf60036698339404488b38285989b5958d65dc |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-17, REQ-18, REQ-20, REQ-21, REQ-22.

## Context

Readiness evaluation today is one infra entry point:
`LaunchpadClient.sync_harness` (filesystem presence), called from wave-start
and the worker orchestrator. INIT-GATEFLOW-013 adds a second protocol —
inspect-only Launchpad `status` with a Gateflow-owned meta config directory
(CTR-02) — under product_constraints REQ-17, REQ-18, REQ-20, REQ-21, and
REQ-22. The engineering choice is **module/protocol shape**: mutate the
existing client in place, or keep two evaluators and switch at the business
gate by durable provenance.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Evolve `sync_harness` in place to invoke `status` for all callers | One public symbol | Two protocols behind one name; hard to isolate write paths; CLI on every force-recheck |
| B — Separate inspect-only status infra client; retain filesystem `sync_harness`; business layer selects by durable provenance | Clear infra boundary; legacy call graph unchanged | Two DI bindings; gate must stay provenance-aware |
| C — Delete filesystem evaluator; `status` only | Single protocol | Removes evaluator when meta sync/provenance is absent; breaks existing force-recheck sites |

## Recommendation

**Option B.** Add a dedicated inspect-only status client for the CTR-02
protocol. Keep filesystem `sync_harness` as a separate evaluator. Wave-start
and orchestrator select the evaluator from durable provenance on the
`tenant_repos` row (or an explicit `readiness_source` column — TDD §8), not
from a process-global flag. Provenance→evaluator mapping and cache-write
rules stay with REQ-17, REQ-18, REQ-20, REQ-21, REQ-22 — this ADR only fixes
the module split and selection mechanism.

## Consequences

- New infra type binds in `InfraModule` / `_INFRA_SERVICE_TYPES` with normal
  lifecycle hooks.
- Status client public API exposes only inspect/status operations (no apply /
  install methods on that type).
- Feasibility FF-04 (gate branching) is the business-layer consequence of this
  split — recorded in the TDD, not a second ADR.

## Revisit triggers

- Filesystem evaluator has zero remaining callers in durable provenance data.
- Launchpad ships a stable in-process library API replacing CLI `status`.
- Provenance cannot be inferred without adding `readiness_source` (TDD §8).

## Lifecycle — Accepted immutability and supersession

Once `Status: Accepted`, do **not** rewrite the accepted body in place.
To change the decision:

1. create a new ADR that `supersedes` this one,
2. set this ADR's `superseded_by` to the new id and status `Superseded`,
3. record owner, date, and review evidence on both files.

## Acceptance finalization

After PE review comments are resolved and PE explicitly states the decision is
ready for acceptance — **and** product-boundary fields remain `false` —
update the file before final GitHub approval:

```text
Status: Accepted
Decision owner: @{pe-name}
Approval evidence: {review/comment URL}
Approved head: {full SHA to be approved}
product_constraints: [REQ-17, REQ-18, REQ-20, REQ-21, REQ-22]
changes_user_visible_behavior: false
spec_amendment_required: false
Lint evidence: adr_boundary_lint.py {sources_checked}/{N expected}, PASS,
  sha256:{hex}
```
