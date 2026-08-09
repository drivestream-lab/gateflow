# ADR-012 — Programme catalogue discovery authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-013 |
| Feasibility finding | FF-01 (`Initiative-Feasibility-Report-INIT-GATEFLOW-013.md`) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Source spec digest | `sha256:44e10fa850753325b8acf1a892723fe5d3293da94f10ed9a129d8651dca595b4` |
| product_constraints | `[REQ-05, REQ-06, REQ-07]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Relates to | Boundary clarification vs [`adr-004`](adr-004-programme-config-authority.md) (**Accepted**); does not supersede ADR-004 |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-09 via Cursor chat (INIT-GATEFLOW-013 technical-review package) |
| Approved head | `3d9fa93b4b3f4519585898928a78b744d455c5f0` (Forge publish tip of Accepted package on chore/INIT-GATEFLOW-013-spec-gateflow) |
| Lint evidence | adr_boundary_lint.py 4/4, PASS, sha256:85b68eb85910aeea07252fa7dc9731c0e34ee4da66bb5f2cbf8a4f1975bcd05e |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-05, REQ-06, REQ-07.

## Context

ADR-004 assigns **Gateflow process runtime knobs** (non-secret orchestration /
adapter settings, typically `GATEFLOW_*` / settings singletons) to this
repository’s process and rejected loading that class of config from meta
harness YAML (Option C). INIT-GATEFLOW-013 also needs to deserialize
meta-published YAML from a synced checkout (CTR-01), under product_constraints
REQ-05, REQ-06, and REQ-07. Those two input classes can be conflated:
implementers may treat the checkout parse as a forbidden revisit of ADR-004
Option C, or as a separate authority lane. The decision is **which authority
model applies to checkout-sourced YAML**.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Split authority: checkout-sourced catalogue YAML is a distinct read-only discovery input; ADR-004 continues to own in-process runtime knobs only | Preserves Accepted ADR-004; clear ownership at the parse boundary | Meta schema drift becomes a live consumer concern |
| B — Revisit ADR-004 Option C: fold checkout YAML into meta-owned programme/runtime config | One shared carrier story | Overturns Accepted ADR-004; couples deploy knobs to meta change control |
| C — Mirror catalogue bytes into Gateflow-owned settings at deploy time | No runtime meta parse | Second write path; diverges from checkout SSOT |

## Recommendation

**Option A.** Checkout-sourced catalogue YAML is a **discovery-input** class:
parsed and validated in Gateflow, never used as the carrier for ADR-004
runtime knobs. ADR-004 Option B remains the authority for process settings.
Call-site timing and response shape stay with REQ-05, REQ-06, REQ-07 and the
TDD — not restated here.

## Consequences

- `GATEFLOW_*` / adapter settings must not be loaded from meta YAML under this
  ADR.
- Catalogue deserialization sits behind a typed model boundary
  (`src/models/` + parser outside the repository/ORM layer).
- Provider-side meta file evolution is monitor-only for this INIT’s eng scope.

## Revisit triggers

- ADR-004 is superseded to restore meta-owned runtime knobs.
- Discovery input moves off checkout-sourced YAML (API or event bus).
- One process must host multiple concurrent catalogue authorities.

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
product_constraints: [REQ-05, REQ-06, REQ-07]
changes_user_visible_behavior: false
spec_amendment_required: false
Lint evidence: adr_boundary_lint.py {sources_checked}/{N expected}, PASS,
  sha256:{hex}
```
