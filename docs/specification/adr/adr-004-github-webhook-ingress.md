# ADR-004 — GitHub App webhook ingress (public path + signature verification)

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-04 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Context

Spec FR-1 requires GitHub App webhooks (PR, issue, label) with signature
validation, delivery idempotency, and fast HTTP ack. User JWT auth must not
gate webhook delivery. Invalid signatures must fail closed (401).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — JWT-authenticated webhook | Reuses middleware | GitHub cannot send user JWTs; broken |
| B — Public `/webhooks/github` + HMAC App signature; persist delivery id; enqueue job | Matches GitHub App model + FR-1 | Must keep secret; clock/replay handled via delivery id |
| C — Internal mesh-only webhook without signature | Simpler local | Unsafe if exposed; fails product security table |

## Recommendation

**Option B.**

- Route: `POST /webhooks/github` (router under `src/api/` — e.g. `webhooks` package
  or `api/v1` sibling mounted at `/webhooks`).
- `public_paths` includes `/webhooks` (ADR-002).
- Verify `X-Hub-Signature-256` (or App-configured scheme) against webhook secret
  from settings; mismatch → 401, no persist/enqueue.
- Persist `X-GitHub-Delivery` (or equivalent) in `webhook_deliveries` for
  idempotency; duplicates return 2xx without creating a second run.
- On success: enqueue job, return **202** quickly; Postgres unavailable → **503**.
- Trigger routing (label → run authorization) happens in the **worker** after
  claim, not inline in the HTTP handler beyond enqueue.

## Consequences

- Webhook secret is required in all environments that accept GitHub traffic.
- Live verify needs a signature fixture or recorded payload harness.

## Revisit triggers

- GitHub changes signature headers/schemes.
- Need synchronous precondition evaluation in the request path for latency reasons
  (unlikely; prefer worker).

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
