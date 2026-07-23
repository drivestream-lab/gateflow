# ADR-002 — Edge trust model (JWT, programme token, forge signature)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-02, F-04 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-23 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/4); architecture package tip `ca74d77949046b8d91357c37bb2ea864dad60c26` |
| Approved head | `ca74d77949046b8d91357c37bb2ea864dad60c26` |

## Context

The scaffold authenticates users with JWT `AuthMiddleware` and a `public_paths`
allowlist. Gateflow adds two non-user trust zones: (1) forge webhook ingress
authenticated by App signature, and (2) programme-shared service token for
read-only control-plane APIs. Exact route paths and HTTP status matrices are
product/TDD contracts — this ADR decides how trust zones coexist.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Replace JWT with a single programme token everywhere | Simple | Breaks scaffold JWT path; conflates user and programme identity |
| B — One middleware accepting JWT *or* programme token as Bearer | Single choke point | Ambiguous `request.state.auth`; hard to audit |
| C — Path allowlist + route-level verification per trust zone | Clear zones; matches `architecture.mdc` public_paths pattern | Allowlist must track mounts |

## Recommendation

**Option C — three trust zones:**

| Zone | AuthN | AuthZ / identity model |
|------|-------|------------------------|
| Default `/api/v1` (future user routes) | JWT via `AuthMiddleware` | Populates `AuthContext` |
| Forge webhook ingress | GitHub App signature on raw body; path on `public_paths` | No JWT; no programme token; no `AuthContext` |
| Programme control-plane reads (status/metrics) | Path on `public_paths`; FastAPI dependency verifies shared programme service token | Does **not** populate user `AuthContext` |

Concrete mounts, signature header names, and status codes are specified in the
TDD interface contracts and INIT spec — not here.

Empty programme token or webhook secret fails fast at startup when those
surfaces are enabled.

## Consequences

- Operators must keep `public_paths` aligned with mounted webhook and programme
  read prefixes.
- Programme-token routes must not assume `request.state.auth`.
- Network boundary (mesh/VPN) is complementary, not a substitute for the token.

## Revisit triggers

- Per-user RBAC on audit APIs.
- Identity service issues programme-scoped JWTs replacing static tokens.
- Forge changes signature scheme.

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
