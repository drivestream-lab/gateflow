# ADR-005 — Programme-token control-plane mutations

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-002 |
| Feasibility finding | C-1, F13-1, Q-6 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |
| Relates to | Supersedes ADR-002 programme-token zone wording (JWT + webhook zones unchanged) |

## Context

Accepted **ADR-002** defines three trust zones and scopes the programme service
token to **read-only** status/metrics APIs. INIT-GATEFLOW-002 requires the same
shared programme token to authenticate **mutations**: wave-start (FR-15) and
board operation APIs (FR-24), still without per-user RBAC. Leaving ADR-002
unchanged blocks a lawful implementation of the approved product scope.

Constraints that remain in force from ADR-002:
- JWT `AuthMiddleware` for future user routes stays separate from programme token.
- Forge webhook ingress stays signature-only (no programme token).
- Programme-token routes do **not** populate user `AuthContext`.
- Empty programme token fails fast at startup when those surfaces are enabled.
- Network boundary complements the token; it does not replace it.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Keep ADR-002 read-only; invent a second mutation token | Clearer privilege split | Extra secret; product/PRD assume one programme token (A4); ops burden |
| B — Route wave-start/board under JWT user auth | Reuses middleware | No per-user RBAC product; breaks programme-shared audit model |
| C — **Amend programme-token zone** to cover documented read **and** write control-plane routes under the same shared token; keep JWT and webhook zones unchanged | Matches PRD; minimal secrets; ADR-002 Option C path shape preserved | Shared token can mutate forge/board — mitigate with audit logs + narrow route allowlist |

## Recommendation

**Option C.**

Update the programme trust zone definition to:

| Zone | AuthN | AuthZ / identity model |
|------|-------|------------------------|
| Default `/api/v1` (future user routes) | JWT via `AuthMiddleware` | Populates `AuthContext` |
| Forge webhook ingress | GitHub App signature; `public_paths` | No JWT; no programme token |
| **Programme control-plane (reads + documented writes)** | Path on `public_paths`; FastAPI dependency verifies shared programme service token | Does **not** populate user `AuthContext`; authorize only the route catalog in the INIT-002 TDD |

Documented write surfaces for INIT-002 (exact paths in TDD §3):
- Wave-start mutation(s)
- Board operation mutations (status, link PR, create, list)

Documented read surfaces remain (extended):
- Run list/detail
- Metrics aggregates

**ADR-002** stays Accepted for JWT + webhook decisions; this ADR **supersedes only**
the programme-token “reads” row and consequences that forbid mutations.

## Consequences

- `public_paths` must include all programme-token prefixes (reads and writes).
- Board and wave-start mutations share the same blast radius as status reads —
  acceptable for programme-engineer shared token until RBAC revisit.
- Wave worker must still **never** call board APIs on run lifecycle (product
  invariant — enforced in business layer, not by a second token).
- Audit: board mutations logged separately from wave run events (spec NFR).

## Revisit triggers

- Per-user or role-scoped programme JWTs replace the shared static token.
- Board APIs require stronger auth than wave-start (split tokens).
- External untrusted clients need programme APIs (then RBAC or mTLS mandatory).

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
