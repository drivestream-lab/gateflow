# ADR-010 — Lane intake and dual-workspace authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-006; amended by INIT-GATEFLOW-007 (closeout); hygiene + closure §7 INIT-GATEFLOW-010 |
| Relates to | Extends ADR-005 (programme-token mutations); ADR-007 (bound prompt inputs); ADR-008 (stored baton ingest); ADR-009 (forge mutate remains separate); ADR-001 (Postgres SSOT — orthogonal to intake) |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance directed on 2026-07-29 via Cursor chat (INIT-GATEFLOW-006); **closeout amendment** accepted 2026-07-29 (INIT-GATEFLOW-007 — fold into ADR-010, no separate closeout ADR). **Hygiene + §7 closure:** INIT-GATEFLOW-010 ADR cleanup — product catalogues deferred; initiative-closure intake folded as §7 (no ADR-011) |
| Approved head | Record on INIT-GATEFLOW-007 acceptance + plan commit tip; hygiene tip on INIT-GATEFLOW-010 spec branch |
| Amendment | Closeout (Pass-2) intake — Recommendation §6; initiative closure — Recommendation §7 |

## Product decisions excluded

- Exact HTTP path strings and OpenAPI field names — INIT / TDD
- Pin skill / node ids for Enter-at and Pass-2 / closure walks — pin SSOT
- Board Done-gate rules, EPIC hygiene timing, purge walk steps — INIT REQs
- Learning-row / artifact ingest schemas — INIT / TDD (not intake authority)

## Context

Gateflow starts programme work through a programme-token control plane (ADR-005).
Product requires **distinct intake shapes** (not one optional mega-body) so
OpenAPI and validators stay fail-closed per lane.

This ADR decides **authority** for intake and workspace bind across start
contracts — not route paths, pin skill ids, or forge publish/mutate (ADR-009).

Intake family (architecture kinds, not a product catalogue):

1. **Implement lane** — board/wave identity + Enter-at an orchestrated implement
   skill; app workspace only.
2. **Spec lane** — meta programme intake via a meta PR URL, with a **dual
   workspace bind**: app coding root plus a checked-out meta tree for read intake.
3. **Wave closeout (Pass-2)** — finish an existing wave after human live-verify:
   **new run**, bind the **existing wave PR**, fixed Enter-at (pin-orchestrated).
4. **Initiative closure** — finish an engineering initiative after waves are
   Done: **new run**, distinct binds from wave closeout, fixed Enter-at
   (pin-orchestrated). Not wave closeout and not Pass-1 resume.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — One start route with optional mega-body fields | Less routing surface | Fail-open on wrong lane; OpenAPI lies; hard to evolve |
| B — Separate start contracts; shared enqueue/run core; dual bind keys for spec | Fail-closed per lane; honest OpenAPI; bind is explicit | More routes; callers must use the right contract |
| C — Spec lane fetches meta over HTTP only (no local meta checkout) | One workspace | Non-deterministic package bind; pin packages expect filesystem roots |

## Recommendation

**Option B.**

1. **Separate start contracts.** Each intake kind above is a distinct
   authenticated mutation surface. Shared run persistence and job enqueue may
   be factored internally; request bodies must **not** share a single optional
   mega-model. Undifferentiated legacy start is **removed** at cutover (no
   long-lived alias).
2. **Implement intake authority** = caller board/wave identity + Enter-at
   orchestrated implement skill. Must **not** require meta PR / meta workspace
   fields.
3. **Spec intake authority** = caller-supplied meta PR URL + absolute meta
   workspace checkout + app org/repo/workspace, with initiative required on the
   request. Gateflow resolves the meta PR via ForgeClient and **fail-closes** on
   unreadable PR, wrong shape, or initiative mismatch (derive-when-possible and
   compare). Persist meta URL / head for audit. Exact field names are TDD.
4. **Dual bind authority.** Packaged spec hops bind an app write root and a meta
   read root, plus existing BOUNDINPUT keys when applicable. Pin package schema
   declares required vars; missing required bind fails closed before AgentRunner
   (ADR-007). Meta tree is **read** intake; durable coding writes target the app
   workspace / app forge head.
5. **Pin remains dispatch SSOT.** Enter-at must be an orchestrated skill on the
   active pin; Gateflow does not invent orchestrated edges. Client must **not**
   choose an arbitrary start node when the product contract fixes Enter-at.
6. **Closeout intake authority.** A distinct programme-token start contract
   finishes a wave (Pass-2). Authority = wave identity + absolute app workspace
   + **required** existing PR bind + dispatch defaults, with Enter-at **fixed**
   to the pin-orchestrated closeout entry. Creates a **new** `run_id` — does
   **not** resume a stopped Pass-1 run. Concurrent **ACTIVE** run for the same
   scope still fails closed (ADR-005 / RunStore policy). Optional prior-run id is
   audit-only. Learning rows and artifact ingest are **not** intake authority —
   they follow ADR-001 + product/TDD data contract.
7. **Initiative-closure intake authority (INIT-GATEFLOW-010).** A further
   distinct programme-token start contract finishes an engineering initiative.
   Authority = initiative identity + epic/wave ticket binds + absolute app
   workspace (exact fields and validators are INIT / TDD). Enter-at **fixed** to
   the pin-orchestrated closure entry. Creates a **new** `run_id` — does **not**
   resume implement, spec, or wave-closeout runs, and must **not** overload the
   closeout body. Post-enqueue walk and board hygiene rules remain product /
   pin / TDD — not this ADR.

Exact route paths, column names, and Gate evidence depth remain TDD / INIT —
this ADR does not catalogue them.

## Consequences

- OpenAPI and validators are lane-honest; wrong-lane bodies fail at the edge.
- Spec runs carry auditable meta PR identity without making meta the write root.
- Pin packages that need meta must declare the meta workspace bind — Gateflow
  consumes; it does not invent schema.
- Callers of the former undifferentiated start must move in the same cutover.
- Closeout and closure callers each use a dedicated body (fixed Enter-at;
  new run); Pass-1 lane starts remain unchanged.
- Adding another Enter-at kind extends this ADR (amend) — do **not** invent a
  parallel intake ADR that restates product REQs.

## Revisit triggers

- Product reverts to a single start body.
- Meta intake becomes fetch-only (no local checkout) via a superseding ADR.
- Spec writes are allowed directly into the meta tree as a product rule.
- Product mandates authorize→resume from live-verify into closeout skills
  (same-run continuation) instead of new-run closeout Enter-at.
- Product merges initiative closure into wave closeout as one body (would
  revisit §7).
