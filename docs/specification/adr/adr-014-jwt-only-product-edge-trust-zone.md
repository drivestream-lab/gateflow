# ADR-014 — JWT-only product edge trust zone

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-014 |
| Feasibility finding | FF-01 (`Initiative-Feasibility-Report-INIT-GATEFLOW-014.md`) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Source spec digest | `sha256:ba84792a5372ace145280aaa09730de368e5500f87c9cab4b6c6d7284e3258df` |
| product_constraints | `[REQ-04, REQ-06, REQ-28, REQ-29, REQ-32, REQ-33]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | `ADR-002, ADR-005, ADR-011` |
| superseded_by | none |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-10 via Cursor chat, Draft spec PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) |
| Approved head | Recorded at publish — see `/commit-workspace` result for the exact spec PR head containing this Accepted metadata |
| Lint evidence | adr_boundary_lint.py 2/2, PASS, sha256:d515f3792ed6a83e532469c0a69193914f6fa2aa15449a8d67aa2c8046cc5f67 |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-04, REQ-06, REQ-28, REQ-29, REQ-32, REQ-33.

## Context

ADR-002/005/011 authorize the programme-token and tenant-bearer zones that
REQ-32/REQ-33 require refused. Changing what an Accepted ADR authorizes
requires a superseding record (immutable-until-superseded rule) — that
obligation exists regardless of whether new verification machinery is
needed. The only substantive engineering question left open is whether
satisfying REQ-04/REQ-06/REQ-29 requires new verification machinery, given
that `AuthMiddleware`/`JWTSettings`/`AuthContext` already exist and are
merely unused on product routes today.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Extend the existing dormant `AuthMiddleware`/`AuthContext` (role + tenant claim handling) to cover product routes | No second verification stack; reuses code already exercising the JWT decode path | Existing claim shape (`sub`/`tenant_id`/`role`) must absorb `platform_admin` without a breaking shape change |
| B — Build a second, INIT-scoped verification component parallel to `AuthMiddleware` | Isolated blast radius for this INIT | Two JWT-verification code paths in one process; no technical reason distinguishes them |
| C — Delegate verification to a synchronous external identity-provider call per request | No local claim-shape change needed | New network dependency on every request; no such provider exists in this codebase |

## Recommendation

**Option A.** No new verification mechanism is introduced. `AuthMiddleware`'s
existing decode/claim-shaping path is extended to require presence on
product routes (allowlist shrink) rather than replaced. This record's
purpose is the formal supersession of ADR-002/005/011's now-superseded zone
table, not the design of a new mechanism.

## Consequences

- The edge allowlist no longer lists any product route prefix; only health,
  internal, and webhook paths remain allowlisted.
- The programme-token and tenant-bearer verification dependencies stop being
  imported by any product route module (structural removal tracked separately
  under the spec's delete-wave scope, not this record).
- At acceptance, ADR-002, ADR-005, and ADR-011 each move to `Superseded` with
  `superseded_by: ADR-014` per their own Lifecycle clauses — done at
  acceptance time, not while this record is Draft.

## Revisit triggers

- Product introduces a role beyond `platform_admin` / `tenant_admin` requiring
  a distinct verification path.
- Per-user RBAC finer-grained than role + programme binding is required.
- Webhook ingress moves off signature verification.

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
product_constraints: [REQ-04, REQ-06, REQ-28, REQ-29, REQ-32, REQ-33]
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
