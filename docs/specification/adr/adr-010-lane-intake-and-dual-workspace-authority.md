# ADR-010 — Lane intake and dual-workspace authority

| Field | Value |
|-------|-------|
| Status | Accepted — **amendment Draft** for INIT-GATEFLOW-007 closeout intake (pending PE re-accept on Draft spec PR; no ADR-011) |
| Initiative | INIT-GATEFLOW-006; amended by INIT-GATEFLOW-007 |
| Relates to | Extends ADR-005 (programme-token wave mutations); ADR-007 (bound prompt inputs); ADR-008 (stored baton ingest); ADR-009 (forge mutate remains separate); ADR-001 (Postgres SSOT for learning ingest is orthogonal — product INIT-007) |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance directed on 2026-07-29 via Cursor chat (INIT-GATEFLOW-006 interactive implement session — “Go ahead let us implement this now”) |
| Approved head | Record on merge of the ADR+W3 accept commit |
| Amendment | Closeout (Pass-2) intake folded here — see Recommendation §6; PE re-accept on INIT-GATEFLOW-007 TDD/spec PR |

## Context

Gateflow starts waves through a programme-token control plane (ADR-005). Product
requires **distinct intake shapes** (not one optional mega-body):

1. **Implement lane** — board/wave identity (`ticket_id`, initiative, wave) and
   Enter-at an orchestrated implement skill. App workspace only.
2. **Spec lane** — meta programme intake via a **prayog-meta PR URL**, with a
   **dual workspace bind**: app coding root (`workspace`) plus a checked-out
   meta tree (`meta_workspace`) for read intake.
3. **Wave closeout (Pass-2)** — finish an existing wave after human live-verify:
   **new run**, bind the **existing wave PR**, fixed Enter-at pin
   `learning-extract` (orchestrated). Same route for both lanes; meta intake
   fields are not required unless a later INIT adds them.

A single optional mega-body across these shapes hides required fields and
produces dishonest OpenAPI. This ADR decides **authority** for intake and bind —
not HTTP path strings, pin skill ids, or forge publish/mutate (ADR-009).

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
6. **Closeout intake authority (INIT-GATEFLOW-007).** A **third** distinct
   programme-token start contract finishes a wave (Pass-2). Authority =
   wave identity + absolute app `workspace` + **required** existing PR bind
   (`org`/`repo`/`pr_number` or equivalent) + dispatch defaults, with Enter-at
   **fixed** to orchestrated `learning-extract` (client must not choose
   arbitrary `start_node`). Creates a **new** `run_id` — does **not** resume a
   stopped Pass-1 run (no authorize→resume). Concurrent **ACTIVE** run for the
   same scope still fails closed (ADR-005 catalogue / existing RunStore policy).
   Optional `prior_run_id` is audit-only. Learning rows and artifact ingest are
   **not** intake authority — they follow ADR-001 + product/TDD data contract.
   Exact path (e.g. `/waves/closeout/start`) remains TDD.

Exact route paths, column names, and Gate 1 APPROVED evidence depth remain
TDD / INIT — this ADR does not catalogue them.

## Consequences

- OpenAPI and validators are lane-honest; wrong-lane bodies fail at the edge.
- Spec runs carry auditable meta PR identity without making meta the write root.
- Pin packages that need meta must declare `meta_workspace` (and optionally
  `meta_pr_url`) — Gateflow consumes; it does not invent schema.
- Callers of the former undifferentiated start must move in the same cutover.
- Closeout callers use a dedicated body (PR required; fixed Enter-at); Pass-1
  lane starts remain unchanged; pin `learning-extract` / `ground-spec` stay
  dispatch SSOT for Pass-2 walk.

## Revisit triggers

- Product reverts to a single start body.
- Meta intake becomes fetch-only (no local checkout) via a superseding ADR.
- Spec writes are allowed directly into the meta tree as a product rule.
- A superseding ADR changes lane intake authority.
- Product mandates authorize→resume from `live-verify` into closeout skills
  (same-run continuation) instead of new-run closeout Enter-at.
