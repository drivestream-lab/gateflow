# ADR-008 — Packaged-skill handoff ingest authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-005-BOUNDINPUT |
| Feasibility finding | FF-06 (handoff authority half) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-27 via Cursor chat on Draft spec PR https://github.com/drivestream-lab/gateflow/pull/52 |
| Approved head | `ffa718142db4cbbaec605b17abf74028ff5cb49c` |
| Relates to | Extends ADR-001 (RunStore SSOT) and ADR-003 (handoff orchestration in business); does not redefine dual API+worker topology |

## Context

**ADR-003** places handoff read orchestration in **business**. **ADR-001** makes
PostgreSQL the durable run store. Neither decides the **authority** for where
automated packaged-skill runs obtain the next handoff envelope:

1. **Ambient discovery** in the workspace (globs / mtime / document trees), or
2. A **Gateflow-defined, run-scoped locator** persisted on the run record

Product path strings, file formats, wave timing (when define vs when ingest),
and column names remain in the INIT / TDD — this ADR does **not** catalogue them.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Ambient workspace discovery remains automate SSOT | No new run field | Cross-run collision risk; couples ingest to repo layout; hard to isolate concurrent runs |
| B — **Automate SSOT = Gateflow-defined run-scoped locator stored on the run**; business defines/persists/reads that locator; ambient discovery is not automate SSOT | Isolation; RunStore authority; aligns ADR-001 | Requires durable run field + define-before-dispatch discipline |
| C — External object store / blob URI as baton authority | Strong multi-host isolation | Extra infra; premature for single-workspace worker |

## Recommendation

**Option B.**

1. For **packaged-skill automated** runs, handoff ingest SSOT is a locator
   **defined by Gateflow**, **stored on the run** (RunStore), and **read back
   from that stored value only**.
2. Ambient repo/glob/mtime discovery is **not** automate SSOT under this decision
   (legacy/debug use outside that path is an INIT/TDD concern).
3. Concrete locator representation (filesystem path vs URI), exact column name,
   and when the empty baton is created are **TDD** — not this ADR.
4. Multi-host / object-store batons (Option C) are deferred until revisit triggers.

## Consequences

- Concurrent runs cannot rely on shared document trees to select each other’s
  handoffs for automate ingest.
- RunStore remains the durability authority for the baton locator (ADR-001).
- Handoff **parse** stays business; storage of the locator is via repository
  boundary (no ORM in business).

## Revisit triggers

- Workers span hosts without a shared workspace filesystem for batons.
- Product requires batons outside RunStore (e.g. forge-only artifacts).
- Ambient discovery must remain SSOT for a documented non-packaged automate class
  (would need an explicit superseding decision).

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
