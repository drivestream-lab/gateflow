# ADR-002 — Auth model: webhook public path, programme service token, JWT coexistence

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-02 (includes Q-3) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Context

Scaffold `AuthMiddleware` verifies user JWTs and uses `public_paths` of
`/health` and `/internal`. Spec FR-15 requires a **programme service token** for
status/metrics (Decision #4). FR-1 webhooks must not use user JWT; they use
GitHub App signature verification (ADR-004). Spec Q-3 asks for exact mounts.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Replace JWT entirely with programme token | Simple | Breaks scaffold JWT path; blocks future user-facing routes |
| B — Extend AuthMiddleware to accept either JWT or programme token as Bearer | One middleware | Ambiguous identity model; harder to reason about `request.state.auth` |
| C — Path allowlist + route-level deps: webhook signature; status/metrics programme token; other `/api/v1` keep JWT | Clear trust zones; aligns with `architecture.mdc` public_paths | Must keep allowlist in sync with mounts |

## Recommendation

**Option C.**

1. **Webhook** — mount at `/webhooks/github`; add `/webhooks` to `public_paths`;
   verify GitHub App signature in the handler (ADR-004). No JWT, no programme token.
2. **Status / metrics** — mount:
   - `GET /api/v1/runs/{run_id}`
   - `GET /api/v1/metrics/runs`
   Add `/api/v1/runs` and `/api/v1/metrics` to `public_paths` (skip user JWT).
   Protect with FastAPI `Depends(verify_programme_service_token)` comparing
   `Authorization: Bearer <token>` to settings (`PROGRAMME_SERVICE_TOKEN` or
   equivalent). Do **not** populate user `AuthContext` from this token.
3. **Future product routes** under `/api/v1` remain JWT-protected via existing
   middleware unless explicitly allowlisted.

Network boundary (VPN/mesh) remains an ops control; token is still required.

## Consequences

- `request.state.auth` stays JWT-only; programme-token routes must not assume it.
- OpenAPI documents programme-token security scheme for status/metrics.
- Misconfigured empty programme token fails fast at startup when those routes
  are enabled (fail-fast.mdc).

## Revisit triggers

- Per-user RBAC required on audit APIs (Decision #4 revisited).
- Identity service issues programme-scoped JWTs that replace static tokens.

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
