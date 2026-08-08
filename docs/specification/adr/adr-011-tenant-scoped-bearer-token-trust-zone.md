# ADR-011 — Tenant-scoped bearer-token trust zone

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-012 |
| Feasibility finding | FF-02 (`Initiative-Feasibility-Report-INIT-GATEFLOW-012.md`) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-012.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Source spec digest | `sha256:b8a490e7e7c7ceb02f18097d9164611086d2c7aecd1d9c2e0a6b0a7495a13190` |
| product_constraints | `[REQ-03, REQ-04]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Relates to | Extends [`adr-002`](adr-002-edge-trust-model.md) (three-zone model) and [`adr-005`](adr-005-programme-token-control-plane-mutations.md) (widened programme-token zone) — adds a fourth zone; the existing three are unchanged |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-08 via Cursor chat, Draft spec PR [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Approved head | `ff1320e5254510a448d1dedd5ec21dfd5b5a05e2` |
| Lint evidence | adr_boundary_lint.py 3/3, PASS, sha256:6d4578b99287b664a3a0e324196ed3f0fbcdb6f2a7b3a5d555c5be11d793b56e |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-03, REQ-04.

## Context

ADR-005 widened the programme-control-plane zone to one shared secret,
process-wide, for both reads and writes. REQ-03 requires a set of secrets,
one per registered tenant row, selected by an identifier the caller supplies
rather than compared as a fixed value. That is a different identity model
from the existing zone, not a larger value space for it, so the open question
is whether this is recorded as a fourth zone or folded into the third row of
ADR-005's zone table.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Generalize the shared-secret dependency to a per-row lookup keyed by a caller-supplied identifier; same Bearer/dependency mechanics; auth context left unpopulated | Reuses the zone's existing verification shape; no new middleware class | Identity model is genuinely new (a keyed set, not one value); needs its own row |
| B — Populate a typed auth context for tenant-scoped routes, reusing the shape of the dormant JWT path | Reuses an existing typed object | Repurposes machinery this initiative's own decision explicitly parks for an unrelated reason |
| C — Reactivate JWT issuance with a tenant claim through the dormant middleware | No new verification code path | Contradicts the parked-scaffolding decision; activates a path for one domain while it stays inert elsewhere |

## Recommendation

Option A. The new zone keeps the existing mechanics — Bearer header,
dependency-level check, no populated auth context — while its identity model
is recorded as a fourth, independent zone because it resolves against stored
values keyed by identity, not one process-global value. Nothing here touches
`AuthMiddleware` or reactivates the parked JWT path.

## Consequences

- No new middleware class; the change stays at the dependency layer.
- The parked JWT scaffolding's status is unaffected.
- Two independent Bearer-secret dependencies exist side by side; rotation and
  blast-radius must be documented per zone, not once overall.
- Future per-user RBAC work must reconcile three identity models, not two.

## Revisit triggers

- Per-user or role-scoped programme JWTs replace the shared static token
  (ADR-005's own revisit trigger) — would likely resolve this zone at the
  same time.
- A route must be reachable under both the global programme token and a
  tenant token, requiring an explicit precedence rule this record does not
  set.
- Tenant-token rotation or expiry policy becomes required — this record
  addresses only the zone's existence and mechanics, not token lifecycle.

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
product_constraints: [REQ-03, REQ-04]
changes_user_visible_behavior: false
spec_amendment_required: false
Lint evidence: adr_boundary_lint.py {sources_checked}/{N expected}, PASS,
  sha256:{hex}
```

`Lint evidence` must match this exact shape — `adr_boundary_lint.py N/M,
PASS|FAIL, sha256:<hex>` — presence alone (`yes`, `TBD`, `-`) fails the
shape check and is rejected. Generate the line with:

```bash
python scripts/adr_boundary_lint.py {this file} --strict \
  --source-text <req_text_file> --source-text <feasibility_evidence_file> \
  --approved-req-id <every approved REQ-* in the spec> \
  --finding-text-file <feasibility_finding_file> \
  --print-evidence
```

and paste the printed line verbatim — do not hand-write the hash.

The formal PE GitHub Approve must be on the final commit containing this
Accepted metadata. No file changes occur after that approval (publish via
Forge `/commit-workspace` — not inside content skills).
