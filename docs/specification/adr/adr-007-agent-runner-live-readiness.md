# ADR-007 — AgentRunner live readiness (extends ADR-006)

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-003 |
| Feasibility finding | FF-02, FF-09, PE-1 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |
| Relates to | Extends ADR-006 (`implemented` unchanged); AgentRunner remains infra (ADR-003); secrets stay out of programme.yaml (ADR-004) |

## Context

**ADR-006** registers adapters by opaque id with a boolean `implemented` capability
and fail-closes at wave-start when a required id is unimplemented. INIT-002 marked
`cursor` as `implemented=True` while `CursorAgentRunner` was still a **stub**
(`mock-*` / `GATEFLOW_AGENT_STUB`). INIT-GATEFLOW-003 requires a **live** Cursor
path (REQ-27) and fail-fast when credentials/SDK are missing (REQ-29).

Collapsing “registered stub” and “live-ready production runner” into the same
boolean reintroduces honesty bugs: wave-start accepts Cursor, then the worker
cannot perform live coding work (or silently succeeds via stub env).

Constraints:

- Do not move AgentRunner into business (ADR-003).
- Do not put Cursor secrets in committed `programme.yaml` (ADR-004).
- Do not rewrite PolicyEngine allowlists — pin `dispatch` remains SSOT.
- OpenCode / Claude Code remain `implemented=False` until a later INIT.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Flip `cursor` to `implemented=False` until SDK ships | Reuses ADR-006 only | Breaks stub-based local/dev wave-start; conflates “code exists” with “live-ready” |
| B — **Separate live-readiness preflight** from ADR-006 `implemented`; Cursor requires credentials + live SDK path; stub env quarantined from REQ-27 exit | Honest start gate; preserves stub runners semantics; reversible | Extra check in SlotValidator / wave-start |
| C — Trust worker-only fail; leave wave-start as today | Smallest change | Mid-run surprise; violates REQ-28/29 “block at start” / fail-fast |

## Recommendation

**Option B.**

1. **ADR-006 `implemented` unchanged in meaning** — opaque id has a callable
   backend that is not an always-refuse stub. `opencode` / `claude_code` stay
   `implemented=False`. After the live Cursor SDK adapter lands, `cursor`
   remains `implemented=True` because a real backend is wired.

2. **Live readiness (this ADR)** — for runner ids that require external auth/SDK
   (today: `cursor`), wave-start (and worker defense-in-depth) MUST pass a
   **live-readiness** check before accepting durable work:
   - Required Cursor auth material is present via settings/env (not programme.yaml).
   - Live SDK path is configured (stub-only success path is not active for this run).
   - Failure names adapter id + config/settings key; **zero** AgentRunner dispatch.

3. **Stub quarantine** — `GATEFLOW_AGENT_STUB` and `mock-*` skill prefixes remain
   **test doubles** only. They MUST NOT count as REQ-27 live prove-it evidence.
   Production / live-verify with `runner=cursor` runs with stub env unset; if stub
   env is set in a production-like environment, fail fast rather than pretend live.

4. **Ownership** — live-readiness policy lives in **business** (extend
   `SlotValidator` or a dedicated preflight called from `WaveStartService` /
   orchestrator). Credential presence and SDK client construction stay in
   **infra** (`CursorAgentRunner` + settings). Routers do not import the SDK.

## Consequences

- Wave-start can reject Cursor runs before enqueue when secrets/SDK are missing.
- ADR-006 stub catalogue for OpenCode/Claude unchanged.
- Multi-runner DI routing remains optional; hardwired `CursorAgentRunner` for
  003 is allowed if live-readiness + `implemented` checks run at start (see TDD).
- Unit tests may still use stub env / `mock-*`; live verify must not.

## Revisit triggers

- A second live AgentRunner brand ships (OpenCode/Claude) — generalize readiness
  per runner id.
- Cursor SDK auth model changes (file vs env vs device login) — update settings
  contract without changing ADR-006.
- Registry grows a structured capability beyond boolean — may fold readiness into
  ADR-006 supersession.

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
