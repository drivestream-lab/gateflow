# ADR-019 — Identity JWT programme scope and session epoch

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-017 |
| Feasibility finding | FF-01 (`Initiative-Feasibility-Report-INIT-GATEFLOW-017.md`) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Source spec digest | `sha256:6fcc4e9f18215774676618dd917fe07c4fd3ba67c2a1e82c193173000b7bf1cd` |
| product_constraints | `[REQ-09, REQ-12, REQ-14, REQ-16, REQ-18]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | `ADR-014 (TENANT_ADMIN-must-carry-tenant_id claim clause only — JWT-only product edge and RoleType vocabulary unaffected)` |
| superseded_by | none |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-09, REQ-12, REQ-14, REQ-16, REQ-18.

## Context

`AuthMiddleware` returns 401 when `role == TENANT_ADMIN` and `tenant_id` is
absent. `mint_user_jwt` writes `tenant_id` from `user_identities.tenant_id`.
`require_programme_scope` compares that claim to the path tenant (ADR-014
Option A). That 1:1 claim cannot represent zero or many memberships, and a
decoded JWT is not re-checked against identity status or credential
generation. ADR-016 attributes `RunSchema.tenant_id` from the tenant that
passed scope. Middleware has no repository; Redis is not durable session
authority (ADR-001). Binds REQ-09, REQ-12, REQ-14, REQ-16, REQ-18.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Remint `tenant_id` at programme-select; invalidate via Redis `jti` denylist or `session_epoch` | Claim-sourced tenant in ADR-016 stays; scope stays in-memory after decode | Second mint is a second credential; Redis denylist is not durable (ADR-001) |
| B — No `tenant_id` on the JWT; scope loads membership `(user_id, path tenant)`; refuse suspended status or `session_epoch` mismatch | One mint per login; N and zero memberships are rows; status/epoch take effect next request | Extra indexed reads; invert `test_tenant_admin_missing_tenant_id_401` |
| C — Embed all granted programme ids in the JWT | No membership read on scope | Unbounded claim; grant change still needs remint; no status invalidation |

Option C is a rejected peer (unbounded claim; still needs A or B to invalidate).
Redis denylist under A is annotated, not recommended.

## Recommendation

**Option B.** Drop the middleware 401 for missing `tenant_id` on
`TENANT_ADMIN`. Login mints `sub` / `role` / `session_epoch` (plus existing
`iss`/`aud`/`iat`/`exp`) without a programme claim. `require_programme_scope`
authorizes from a membership row. `require_role` loads the identity by `sub`
and refuses when status is suspended or JWT `session_epoch` ≠ row
`session_epoch`. Increment `session_epoch` on password-set and on suspend.
`AuthContext.tenant_id` remains optional and unused for scope. ADR-016 is
unchanged except the authorized tenant is the path tenant after membership
check. Binds REQ-09, REQ-12, REQ-14, REQ-16, REQ-18.

## Consequences

- `user_identities.tenant_id` is no longer membership SSOT; a membership
  table is required (TDD data contract).
- Wipe must delete memberships, not identity rows (TDD §9 FF-02).
- `mint_user_jwt` stops requiring `tenant_id` for `TENANT_ADMIN`.
- Per-request identity read is the invalidation mechanism; no Redis denylist.

## Revisit triggers

- Membership lookup latency forces a cached grant set in the JWT.
- A caller needs a bound programme when the path does not name a tenant.
- Session authority moves off PostgreSQL.

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
product_constraints: [REQ-09, REQ-12, REQ-14, REQ-16, REQ-18]
changes_user_visible_behavior: false
spec_amendment_required: false
Lint evidence: adr_boundary_lint.py {sources_checked}/{N expected}, PASS,
  sha256:{hex}
```
