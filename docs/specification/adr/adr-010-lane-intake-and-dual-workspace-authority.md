# ADR-010 — Lane intake and dual-workspace authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-006 |
| Relates to | Extends ADR-005 (programme-token wave mutations); ADR-007 (bound prompt inputs); ADR-008 (stored baton ingest); ADR-009 (forge mutate remains separate) |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance directed on 2026-07-29 via Cursor chat (INIT-GATEFLOW-006 interactive implement session — “Go ahead let us implement this now”) |
| Approved head | Record on merge of the ADR+W3 accept commit |

## Context

Gateflow starts waves through a programme-token control plane (ADR-005). Product
now requires **two intake shapes**:

1. **Implement lane** — board/wave identity (`ticket_id`, initiative, wave) and
   Enter-at an orchestrated implement skill. App workspace only.
2. **Spec lane** — meta programme intake via a **prayog-meta PR URL**, with a
   **dual workspace bind**: app coding root (`workspace`) plus a checked-out
   meta tree (`meta_workspace`) for read intake.

A single optional mega-body for both lanes hides required fields and produces
dishonest OpenAPI. This ADR decides **authority** for intake and bind — not
HTTP path strings, pin skill ids, or forge publish/mutate (ADR-009).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — One `POST /waves/start` with optional meta fields | Less routing surface | Fail-open on wrong lane; OpenAPI lies; hard to evolve |
| B — Separate lane start contracts; shared enqueue/run core; dual bind keys for spec | Fail-closed per lane; honest OpenAPI; bind is explicit | Two routes; callers must migrate; pin schemas must declare new vars |
| C — Spec lane fetches meta over HTTP only (no local meta checkout) | One workspace | Non-deterministic package bind; pin packages expect filesystem roots |

## Recommendation

**Option B.**

1. **Separate start contracts.** Implement and spec wave starts are distinct
   authenticated mutation surfaces. Shared run persistence and job enqueue may
   be factored internally; request bodies must not share a single optional
   mega-model. Undifferentiated legacy start is **removed** at cutover (no
   long-lived alias).
2. **Implement intake authority** = caller board/wave identity + Enter-at
   orchestrated implement skill. Must **not** require meta PR / meta workspace
   fields.
3. **Spec intake authority** = caller-supplied `meta_pr_url` + absolute
   `meta_workspace` checkout + app `org`/`repo`/`workspace`, with initiative
   required on the request. Gateflow resolves the meta PR via ForgeClient and
   **fail-closes** on unreadable PR, wrong shape, or initiative mismatch
   (derive-when-possible and compare). Persist meta URL / head for audit.
4. **Dual bind authority.** Packaged spec hops bind `workspace` (app write
   root) and `meta_workspace` (meta read root), plus existing BOUNDINPUT keys
   when applicable. Pin `schema.yaml` declares required vars; missing required
   bind fails closed before AgentRunner (ADR-007). Meta tree is **read**
   intake; durable coding writes target the app workspace / app forge head.
5. **Pin remains dispatch SSOT.** Spec Enter-at must be an orchestrated skill
   on the active pin; Gateflow does not invent orchestrated edges.

Exact route paths, column names, and Gate 1 APPROVED evidence depth remain
TDD / INIT — this ADR does not catalogue them.

## Consequences

- OpenAPI and validators are lane-honest; wrong-lane bodies fail at the edge.
- Spec runs carry auditable meta PR identity without making meta the write root.
- Pin packages that need meta must declare `meta_workspace` (and optionally
  `meta_pr_url`) — Gateflow consumes; it does not invent schema.
- Callers of the former undifferentiated start must move in the same cutover.

## Revisit triggers

- Product reverts to a single start body.
- Meta intake becomes fetch-only (no local checkout) via a superseding ADR.
- Spec writes are allowed directly into the meta tree as a product rule.
- A superseding ADR changes lane intake authority.
