# ADR-005 — Programme-token control-plane mutations

| Field | Value |
|-------|-------|
| Status | Superseded |
| Initiative | INIT-GATEFLOW-002 |
| Feasibility finding | C-1, F13-1, Q-6 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-24 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/10); architecture package tip after ADR hygiene `13a734dfa7a5fa8352e5d9f3ef939d49912ab07f` |
| Approved head | `ff73cddf93f5d81f7b3585f59ea9b57e9410991b` |
| Relates to | Supersedes ADR-002 programme-token zone wording (JWT + webhook zones unchanged) |
| superseded_by | [`adr-014`](adr-014-jwt-only-product-edge-trust-zone.md) — JWT-only product edge; programme-token zone retired (INIT-GATEFLOW-014, Accepted 2026-08-10) |

## Context

Accepted **ADR-002** defines three trust zones and scopes the programme service
token to **read-only** control-plane APIs. Later initiatives require the same
shared programme token to authenticate **mutations** on programme control-plane
routes, still without per-user RBAC. Leaving ADR-002 unchanged forces either a
second secret or conflating programme mutations with JWT user identity.

This ADR decides **how trust zones coexist when the programme token may mutate**.
Which routes are reads vs writes, path strings, status codes, and which business
operations are allowed remain **INIT / TDD contracts** — not this ADR
(same boundary as ADR-002: “exact mounts … are product/TDD contracts”).

Constraints that remain in force from ADR-002:
- JWT `AuthMiddleware` for future user routes stays separate from programme token.
- Forge webhook ingress stays signature-only (no programme token).
- Programme-token routes do **not** populate user `AuthContext`.
- Empty programme token fails fast at startup when those surfaces are enabled.
- Network boundary complements the token; it does not replace it.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Keep programme token read-only; introduce a second mutation token | Clearer privilege split | Extra secret lifecycle; two Bearer schemes to operate |
| B — Authenticate programme mutations with JWT user auth | Reuses existing middleware | Conflates user and programme identity; implies RBAC the platform does not yet provide |
| C — **Widen the programme-token zone** to cover **documented** control-plane reads **and** writes under one shared token; keep JWT and webhook zones unchanged | One programme secret; zone model stays path-allowlist + route dependency | Shared token blast radius includes mutations — mitigate with allowlisted mounts + audit |

## Recommendation

**Option C.**

Update the programme trust zone definition to:

| Zone | AuthN | AuthZ / identity model |
|------|-------|------------------------|
| Default `/api/v1` (future user routes) | JWT via `AuthMiddleware` | Populates `AuthContext` |
| Forge webhook ingress | GitHub App signature; path on `public_paths` | No JWT; no programme token; no `AuthContext` |
| **Programme control-plane (reads + documented writes)** | Path on `public_paths`; FastAPI dependency verifies shared programme service token | Does **not** populate user `AuthContext`; only routes listed in the active INIT/TDD catalogue |

**ADR-002** stays Accepted for JWT + webhook decisions; this ADR **supersedes only**
the programme-token “reads” row and any consequence that forbids mutations under
that token.

## Consequences

- Operators must keep `public_paths` aligned with **all** programme-token mounts
  (reads and writes) declared in the active TDD.
- Programme-token routes must not assume `request.state.auth`.
- Mutation and read routes that share the token share blast radius until a
  revisit introduces split tokens or RBAC.
- Cross-cutting audit of programme-token mutations vs unrelated run telemetry is
  an observability concern for implementers; concrete event schemas stay in TDD.

## Revisit triggers

- Per-user or role-scoped programme JWTs replace the shared static token.
- Mutation surfaces need a stronger authZ model than reads (split tokens).
- External untrusted clients consume programme APIs (RBAC or mTLS mandatory).

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
