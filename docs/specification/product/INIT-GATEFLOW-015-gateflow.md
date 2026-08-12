# INIT-GATEFLOW-015 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-015 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-015.md` |
| PRD digest (H1) | `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/40 |
| Meta PR approved head (G1) | `63ebf8009a8d01721c432de0a92cb21649eb7613` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-015.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/40#pullrequestreview-4912330943) 2026-08-12T02:03:08Z on `63ebf8009a8d01721c432de0a92cb21649eb7613` — attestation: `initiative: INIT-GATEFLOW-015`, `map_revision: 1`, `prd_digest` match, `artifact: prd/reports/Impact-Map-INIT-GATEFLOW-015.md`; label `impact-map-lgtm` |
| Architecture constraints (existing) | Pin SSOT [`prayog-skills/workflow.yaml`](../../../prayog-skills/workflow.yaml) @ `v0.5.0` (consume-only; `workflow_node` ids + `codify_hint.ref` are read-only join keys, no pin contract change); [`adr-016`](../adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md) (**Accepted** — tenant scoping precedent for run/board/checkpoint reads that this INIT extends to metrics) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-12 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure — see
> [`artifact-write-contract.md`](../../../prayog-skills/references/artifact-write-contract.md).

## Overview

Gateflow persists almost everything needed to answer "is this working" but
computes almost none of it. Today's only derived signal —
`GET /api/v1/metrics/runs` (INIT-GATEFLOW-001/FR-10) — reports stage duration
p50/p95 by `workflow_node`, additionally broken down by `runner`/`model_id` in
the current implementation; it answers **how long**, never **how well** or
**whether it's improving**. This INIT delivers, **gateflow only**: a
prerequisite fix (CAP-01) so `stage_completed` events and `stages` rows persist
the full `RunOutcomeType` vocabulary (`success/failed/stopped/blocked/findings/
pending`) instead of collapsing `findings`/`stopped`/`blocked` to `None`; then
three additive, tenant-scoped, live-aggregated **GET** APIs composing existing
`RunRepository`/`RunEventRepository`/`StageRepository`/`LearningRepository`/
`InitiativeReadoutService` data: **Skill/Spec Efficacy**
(`GET /api/v1/metrics/skill-efficacy`, CAP-02), **Factory Effectiveness**
(`GET /api/v1/metrics/factory-effectiveness`, CAP-03 — fulfills
INIT-GATEFLOW-004's `REQ-37`/`A2` aggregate dependency, marked `[TBD in spec]`
there; terminology map: this INIT's "gate dwell time" = 004's
"human-wait time"), and a **Delivery Scorecard**
(`GET /api/v1/metrics/delivery-scorecard`, CAP-04) covering only Gateflow's own
evidence half. `GET /api/v1/metrics/runs` is **unchanged** — byte-for-byte
regression guard.

**Scope boundary (this repo only):** no new tables; live aggregation on read
only (no worker/rollup job); no new `continues_run_id` schema column (dwell
time is inferred via `initiative_id`+`wave_id`+chronology); no per-developer
attribution; no cost/token metrics; no intent→merge lead time (stays
`unavailable`, cross-repo/meta-bridge deferred); no `gateflow-ops` screens
(deferred consumer of the three new JSON APIs). `prayog-skills` is
consume-only — `workflow_node` ids and `codify_hint.ref` values become a
read-only join key for a third consumption pattern (metrics), no pin contract
change requested (CTR-01).

**Ownership:** this spec defines observable behavior, acceptance, field
meaning, invariants, errors, and compatibility. Exact JSON field/OpenAPI
shapes, whether a new module or new methods on `MetricsEmitter` host the three
capabilities, the `lane` derivation mechanism for wave-cycle-time grouping
(REQ-16), and how CAP-04 composes a tenant-scoped variant of
`InitiativeReadoutService`'s data are **deferred to feasibility / technical
review** — not decided here (see Spec questions).

**As-built baseline (2026-08-12, verified by direct source inspection):**

- `MetricsEmitter.record_stage_duration` (`src/business_services/metrics_emitter.py:120-153`)
  maps its `outcome` string parameter to `RunOutcomeType.SUCCESS` /
  `RunOutcomeType.FAILED` / `None` only — `findings`/`stopped`/`blocked`/
  `pending` are never produced today, confirming the PRD's CAP-01 problem
  statement in this codebase.
- `RunOrchestrator._run_orchestrated_stage` (`src/business_services/run_orchestrator.py:868-873`)
  derives `stage_outcome` (persisted on **both** the `stages` row via
  `StageCreate.outcome_type` **and** passed into `record_stage_duration`) purely
  from `agent_result.outcome` (`AgentRunOutcomeType` — `success`/`failed` only,
  the low-level Cursor agent-run result). The skill's own declared verdict
  (`handoff.outcome`, a free string that already includes `"findings"` — see
  line 494's existing `handoff.outcome == "findings"` retry-counter check) is
  **not** threaded into `stage_outcome` today. CAP-01's fix scope is both the
  `stage_completed` run event and the `stages.outcome_type` column.
- `RunOrchestrator._finalize_run` (`src/business_services/run_orchestrator.py:1491-1585`)
  **already** persists the full vocabulary correctly for `run_stopped` events
  (`outcome_type` ∈ `{FAILED, BLOCKED, STOPPED}` as appropriate) — CAP-01's gap
  is scoped to stage-level events/rows, not run-level finalize.
- `RunSchema.tenant_id` exists on `runs`; `StageSchema` and `RunEventSchema`
  have **no** `tenant_id` column — tenant scoping for CAP-02/CAP-03 (which
  aggregate `stages`/`run_events`) requires joining through `runs.tenant_id`,
  the same pattern `RunRepository.list_runs(tenant_id=...)` already uses
  (ADR-016).
- `LaneType` (`spec`/`implement`/`closeout`, `src/models/lane_types.py`) is
  set at wave-start (`src/business_services/wave_start_service.py:149,354,393`)
  but flows only through the **ephemeral** job queue payload
  (`JobSchema.payload`) — it is **not** persisted on `RunSchema`/`StageSchema`
  for later query. REQ-16 (wave cycle time grouped by lane) needs a durable
  lane signal that does not exist yet (Spec question Q-2).
- `InitiativeReadoutService.list_initiatives()` / `_all_runs()`
  (`src/business_services/initiative_readout_service.py:66-138`) composes
  **all** runs with **no `tenant_id` filter** today (same gap the PRD names
  for `/metrics/runs` at D5, extended here to the initiative/board
  composition CAP-04 REQ-20/REQ-21 reuse). REQ-23 requires CAP-04 to be
  tenant-scoped; the underlying composition will need the same
  `tenant_id`-scoped pattern `RunRepository.list_runs` already supports
  (Spec question Q-3).
- `codify_hint.target` (a free string on `LearningCodifyHintDocument`, e.g.
  `"skill"` — confirmed lowercase against `prayog-skills`
  `skills/development/learning-extract/references/output-template.md`) is a
  **different field** from `LearningItemDocument.class_type`
  (`LearningClassType` enum: `SPEC`/`SKILL`/`HARNESS`/`ENV`, uppercase). REQ-08's
  join key is `codify_hint.target == "skill"` + `codify_hint.ref ==
  workflow_node id` — not `class_type`. Naming collision risk flagged for
  whoever implements CAP-02 (Assumption A-9).
- `LearningRepository` today exposes `get_by_run_id` and
  `list_items(initiative_id, wave_id)` only — no org-wide "all items" query;
  CAP-02's per-`workflow_node` / org-wide codify-rate aggregation (REQ-08/09)
  needs a new repository method, not a new store (schema already supports it
  via the existing `codify_hint` JSONB column).

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | Stage-outcome recording maps the **full** `RunOutcomeType` vocabulary (`success/failed/stopped/blocked/findings/pending`) onto `stage_completed` run events **and** the `stages.outcome_type` column, not just `success`/`failed` | PRD REQ-01; CAP-01; US-1 | Stage completes with any outcome | Persisted `outcome_type` matches the actual value on both `run_events` and `stages`; never silently `None` for `findings`/`stopped`/`blocked` | unit | W0 |
| REQ-02 | Existing `success`/`failed` recording behavior is unchanged | PRD REQ-02; CAP-01; regression guard | Stage completes with `success`/`failed` | Identical to pre-fix persisted values | unit (existing suite green) | W0 |
| REQ-03 | Metrics queries can group by the full outcome vocabulary; events recorded before this fix ships are excluded from outcome-aware rates rather than miscounted as a default value | PRD REQ-03; CAP-01; Risk | Query spans pre-fix and post-fix events | Response reports an effective data-available-from boundary; pre-fix events never silently treated as `success` | unit + inspection | W0 |
| REQ-04 | `GET /api/v1/metrics/skill-efficacy` returns run count, first-pass rate, findings rate, retry avg per `workflow_node`, tenant-scoped, within the retention window | PRD REQ-04; CAP-02; D5, D7, A5 | Authorized call with `TENANT_ADMIN` role | Response computed live from `stage_completed`/`stages` scoped to caller's `tenant_id` | unit + verify | W1 |
| REQ-05 | First-pass rate for a node = stages reaching `success` with zero prior `findings` re-entry on that node within the run, over total stages for that node | PRD REQ-05; CAP-02; D1 | Query | Rate matches a hand-computed fixture | unit | W1 |
| REQ-06 | Findings rate for a node counts every `findings` occurrence at that node regardless of position relative to any `human-checkpoint` on the wave | PRD REQ-06; CAP-02; D3 (CAP-02 scope) | Query | Rate includes all findings occurrences, pre- and post-checkpoint alike | unit | W1 |
| REQ-07 | Response supports filtering/grouping the same `workflow_node` by `model_id` and/or `prompt_revision` | PRD REQ-07; CAP-02; skill-efficacy use case | Query with filter | Filtered response only includes matching stage rows; two revisions of the same skill are directly comparable | unit + verify | W1 |
| REQ-08 | Learning codify rate is reported per `workflow_node` only for `codify_hint.target == "skill"` (join key `codify_hint.ref == workflow_node id`); items with `codify_hint.target` in `{SPEC, HARNESS, ENV}` report as flat, unjoined org-wide rates | PRD REQ-08; CAP-02; D4, A1 | Query learning items | Per-node rate only for `target == "skill"`; others flat, org-wide | unit | W1 |
| REQ-09 | A `codify_hint.ref` that matches no known `workflow_node` reports under an explicit "unjoined" bucket — never dropped silently or treated as an error | PRD REQ-09; CAP-02; D4, Risk | `ref` matches no known `workflow_node` | Item appears in unjoined bucket; 200 response, not dropped or errored | unit | W1 |
| REQ-10 | CAP-02 response is scoped to the caller's tenant; a caller cannot see another tenant's skill-efficacy data | PRD REQ-10; CAP-02; D5 | Cross-tenant query attempt | Refused / scoped empty — 0 cross-tenant data exposure | unit + verify | W1 |
| REQ-11 | `GET /api/v1/metrics/factory-effectiveness` returns unattended Pass-1 rate, tenant-scoped, within the retention window | PRD REQ-11; CAP-03; D5, D7, A5 | Authorized call | Response computed live | unit + verify | W2 |
| REQ-12 | A wave counts as **unattended** when, between its entrypoint and the first STOP whose node `type` is `human-checkpoint` or whose `authorization` is `explicit`, no run event records a mid-chain PE-initiated skill dispatch; automated `external-action` hops (`authorization: automated`, e.g. `wave-pr-action`, `wave-done-action`) do **not** break the streak | PRD REQ-12; CAP-03; D2 | Wave trace | Streak preserved across automated hops; broken only by PE dispatch or a real gate | unit | W2 |
| REQ-13 | Response includes a `stop_reason` breakdown — counts of `STOPPED` runs grouped by the pin's own `stop_reason` string, passed through as-is (no gateflow-side hardcoded taxonomy) | PRD REQ-13; CAP-03; D2, A4, OQ-2 | Query `RUN_STOPPED`/`run_stopped` events | Breakdown matches raw `stop_reason` values grouped correctly | unit + verify | W2 |
| REQ-14 | For a `STOPPED` run, response includes gate dwell time as the elapsed time between that run's `ended_at` and the `created_at` of the next run for the same `initiative_id` + `wave_id` (inferred continuation — no new schema column this INIT) | PRD REQ-14; CAP-03; D8, A3 | Stopped run followed by a later run for the same initiative+wave | Dwell time computed correctly from the two timestamps | unit | W2 |
| REQ-15 | A `STOPPED` wave with no continuation run **yet** reports as currently open/waiting — never a zero, negative, or silently omitted dwell value | PRD REQ-15; CAP-03; D8, Risk | Stopped wave, no continuation yet | Reported as open/waiting, no dwell value | unit | W2 |
| REQ-16 | Response includes wave cycle time (existing `wave_duration_ms`) as p50/p95, grouped by lane (spec / implement / closeout) — reusing existing persisted data where possible | PRD REQ-16; CAP-03; existing data reuse | Query runs by lane | Correct percentile grouping per lane | unit + verify | W2 |
| REQ-17 | CAP-03 response is scoped to the caller's tenant, consistent with CAP-02/CAP-04 | PRD REQ-17; CAP-03; D5 | Cross-tenant query attempt | Refused / scoped empty | unit + verify | W2 |
| REQ-18 | `GET /api/v1/metrics/delivery-scorecard` is tenant-scoped and returns an explicit `as_of` snapshot timestamp plus a trailing-90-day delta alongside the all-time cumulative value for each metric | PRD REQ-18; CAP-04; D5, D6, OQ-3 | Authorized call | Response includes all three framings (`as_of`, cumulative, 90-day delta) for each metric | unit + verify | W3 |
| REQ-19 | Rework count/rate counts a wave only when a `findings`/`blocked` re-entry into an earlier node occurs **strictly after** a `human-checkpoint` on that wave already recorded `outcome_type = pass`; pre-checkpoint self-loops are excluded (already counted in CAP-02's findings rate) | PRD REQ-19; CAP-04; D3 | Wave with checkpoint pass then later findings/blocked re-entry | Counted only in the post-checkpoint case | unit | W3 |
| REQ-20 | Initiatives-closed-with-evidence counts initiatives whose closure/completion readout exists (via existing `InitiativeReadoutService`/closure composition) — not a manual or chat claim of completion | PRD REQ-20; CAP-04; CAP-04 pillar | Query initiatives | Count matches initiatives with a persisted closure/completion readout | unit + verify | W3 |
| REQ-21 | Factory coverage % = EPIC-ticketed initiatives visible on the connected board (via the existing "runs + board EPIC tickets" composition) that have ≥1 Gateflow-tracked run, over total EPIC-ticketed initiatives visible on that board — not a claim about total company delivery activity | PRD REQ-21; CAP-04; D6, A2 | Query initiatives + board | Percentage matches this precise, scoped definition | unit + verify | W3 |
| REQ-22 | Intent→merge lead time is absent/`unavailable` in this response, not fabricated from partial data | PRD REQ-22; CAP-04; D6 | Query | Field absent or explicitly `unavailable` | inspection | W3 |
| REQ-23 | CAP-04 response is scoped to the caller's tenant | PRD REQ-23; CAP-04; D5 | Cross-tenant query attempt | Refused / scoped empty | unit + verify | W3 |

### Response shape conventions (product-normative on scoping, illustrative on exact keys)

| Convention | Applies to | Notes |
|---|---|---|
| `tenant_id` scoping | CAP-02, CAP-03, CAP-04 | Shared across all three (D5); `/metrics/runs` remains global/unscoped, unchanged (REQ-02) |
| `retention_days` window field | CAP-02, CAP-03 | Matches existing `/metrics/runs` convention (`OrchestrationSettings.metrics_retention_days`) |
| `as_of` snapshot + cumulative + 90-day delta | CAP-04 only | Resolves OQ-3; CAP-04 is a state snapshot, not a percentile-over-window stat |
| Unjoined/open bucket instead of drop/error | CAP-02 (unjoined learning refs), CAP-03 (dwell with no continuation yet) | Never silently omit or fabricate a value |

### Target API surface (already named in PRD Appendix B; exact JSON fields → Q-1)

| Route | Capability | Wave |
|-------|------------|------|
| (internal fix — no new route) | CAP-01 | W0 |
| `GET /api/v1/metrics/skill-efficacy` | CAP-02 | W1 |
| `GET /api/v1/metrics/factory-effectiveness` | CAP-03 | W2 |
| `GET /api/v1/metrics/delivery-scorecard` | CAP-04 | W3 |
| `GET /api/v1/metrics/runs` (existing, INIT-GATEFLOW-001) | unchanged | — |

**Implementation notes (non-normative):** PRD-suggested seam is a new
sibling module to `src/business_services/metrics_emitter.py` (or new methods
on it) reusing `RunRepository`/`RunEventRepository`/`StageRepository`/
`LearningRepository`/a tenant-scoped composition equivalent to
`InitiativeReadoutService`, mounted as new routes alongside
`src/api/v1/metrics_routes.py`'s existing `get_run_metrics`. Module/class
names, whether `lane` needs new persistence, and how CAP-04 reuses or extends
`InitiativeReadoutService`'s tenant-unscoped composition are design detail for
feasibility / technical review — not decided here.

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|-----------------|----------|
| REQ-03 | Query spans events recorded before CAP-01 ships | Pre-fix events excluded from outcome-aware rates; response/docs state the effective data-available-from point | Prevents silently treating historical `None` outcomes as `success`, which would inflate first-pass/findings rates with data that was never actually observed | unit + inspection |
| REQ-09 | `codify_hint.ref` matches no known `workflow_node` | Reported in an explicit "unjoined" bucket, 200 response | A skills-repo rename or drift must not silently disappear learning signal or hard-error the whole endpoint | unit |
| REQ-15 | `STOPPED` wave has no continuation run yet | Reported as open/waiting, no dwell value | A zero/negative/omitted dwell value would misrepresent an in-progress human-wait as instantaneous or invisible | unit |
| REQ-10, REQ-17, REQ-23 | Cross-tenant read attempt on any of the three new endpoints | Refused / scoped empty | Prevents cross-tenant data exposure — CAP-02/03/04 are the first metrics surface to add tenant scoping that `/metrics/runs` today lacks (D5) | unit + verify |
| REQ-22 | Caller queries CAP-04 expecting intent→merge lead time | Field absent / `unavailable`, not fabricated | Fabricating a cross-repo value Gateflow cannot observe would misrepresent programme evidence to leadership | inspection |
| REQ-07 | Malformed/unknown filter value on CAP-02 (`model_id`/`prompt_revision` matching no known value at all) | Named-clean empty response, not an error | A 500/400 on a benign filter mismatch would block routine dashboard queries; empty is the correct signal | unit |
| REQ-04, REQ-11, REQ-18 | Valid tenant with no data recorded yet on any of the three new endpoints | Well-formed empty/zero response, not a 404 or fabricated value | New tenants and freshly-migrated data must see honest zeros, not an error that looks like a broken integration | unit + verify |
| REQ-08 | `codify_hint.target` in `{SPEC, HARNESS, ENV}` queried per-`workflow_node` (CAP-02 join scope) | Reported as flat, org-wide rate — never forced into a per-node bucket it does not semantically belong to | Misjoining non-skill learning items to a `workflow_node` would misattribute spec/harness/env learnings to the wrong owner (prayog-skills owners vs PE) | unit |

## Out of scope for this repo

- `gateflow-ops` screens/charts rendering these APIs — later, deferred consumer (INIT-GATEFLOW-004 track)
- Intent→merge lead time — needs a meta-side PRD/impact-acceptance timestamp; cross-repo, deferred to a future meta-bridge initiative
- Token/cost metrics — `CursorAgentRunner` exposes no usage data today
- A precomputed rollup/worker job — live aggregation only, same pattern as `/metrics/runs`
- A new `continues_run_id` schema column — inferred join (`initiative_id`+`wave_id`+chronology) is sufficient this INIT
- Per-developer attribution — explicit anti-goal; Gateflow attributes to runner/model/skill node, never a human identity
- Any change to `/metrics/runs`' existing shape or values — additive only
- `prayog-skills` pin/workflow redesign — consume-only; `workflow_node` ids and `codify_hint.ref` remain read-only join keys (CTR-01)
- Backfilling historical `stage_completed` events for CAP-01 — old events keep their existing (lossy) values

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow | Resolve `workflow_node` ids from pinned `workflow.yaml` as a read-only join key for CAP-02's learning-codify-rate join (REQ-08/REQ-09) and CAP-01/CAP-03's `workflow_node`/`stop_reason` grouping (REQ-01, REQ-13) | `codify_hint.ref` string / `workflow_node` string from persisted `run_events`/`stages`/learning items | Match/no-match against current pin tip's node ids | `workflow_node` ids never hardcoded per capability; read-only, no pin contract change requested | Unmatched `ref` → explicit "unjoined" bucket, never dropped/errored (REQ-09) | Consume pin tip only; a skills-repo node-id rename is a named, accepted risk (A3/A-9 below), not a breaking contract change | unit (fixture pin ids) + inspection |

No outbound write contract exists for this INIT — all three new routes are
`GET`-only (live aggregation on read); no `apply_labels`, board-status writes,
or forge mutations are introduced.

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | All three new endpoints reuse `require_role(RoleType.TENANT_ADMIN)` (existing pattern, same as `/metrics/runs`/`/initiatives`) **and** additionally scope by `tenant_id`, which `/metrics/runs` today does not (D5). No new PII or credential surface — aggregates over data Gateflow already persists. | Route auth tests + tenant-scoping unit/verify per REQ-10/17/23 |
| Reliability | Live aggregation fails closed on malformed filters (named-clean empty, not 500); pre-CAP-01 events excluded rather than miscounted (REQ-03); open/waiting dwell never fabricated as zero (REQ-15) | unit + verify |
| Performance / capacity | N/A as a product SLO this INIT — live aggregation on read must complete under normal DB query latency, same pattern as existing `/metrics/runs`; no new capacity claim | inspection / verify smoke |
| Observability | Structured logs for each new aggregation call (endpoint, tenant_id, retention window / as_of) using existing `get_logger()`/`self.logger` conventions; no secrets logged | unit + inspection |
| Privacy / data handling | No per-developer identity is ever attributed by these endpoints (explicit non-goal, matches system brief's anti-JTBD); factory coverage (CAP-04) must not be presented as total-company coverage — response/docs state its precise, narrower scope (REQ-21) | inspection |
| Migration / compatibility | Additive GET routes only; `GET /api/v1/metrics/runs` response shape and values are byte-for-byte unchanged against its existing test suite (REQ-02) | unit regression on `/metrics/runs` existing suite |
| Rollback / recovery | Feature is read-only and additive — rollback = disable the three new routes; no board/GitHub write to reverse; CAP-01's outcome-persistence fix is additive to the vocabulary (no destructive migration, no column removed) | inspection |
| Operations / support | Document verify commands per wave in `tests/README.md`; PE/prayog-skills owners/programme leadership can each answer their own question from a live GET without asking a colleague | live verify + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | `workflow_node` ids in `run_events`/`stages` and `codify_hint.ref` values in learning items share the same namespace when `codify_hint.target == "skill"` | PRD A1; confirmed by inspection — `learning-extract` output template (`prayog-skills/skills/development/learning-extract/references/output-template.md`) shows `ref: "loop-spec"`, a real pin node id | PE | confirmed | prayog-skills renames node ids without updating the join convention |
| A-2 | `InitiativeReadoutService`'s existing "runs + board EPIC tickets" composition is the only honest denominator for factory coverage | PRD A2; confirmed by inspection (`src/business_services/initiative_readout_service.py`) | PE | confirmed | A different, more complete initiative-visibility source becomes available |
| A-3 | A `STOPPED` run's continuation is reliably the next-created run sharing the same `initiative_id` + `wave_id`; concurrent overlapping waves for one initiative are rare enough at current scale to accept as a named risk rather than requiring a new schema column | PRD A3 `(Source: User-confirmed)` | PE | assumed — named risk | Concurrent overlapping waves for one initiative become common in practice |
| A-4 | `stop_reason` free-text grouping (no gateflow-side hardcoded taxonomy) is modeled specifically on `WorkflowEngine.resolve_next`'s no-allowlist approach to node resolution — not a documented system-wide "no allowlists" policy | PRD A4 (post-CHG-02 wording); `src/business_services/workflow_engine.py` | PE | confirmed | Product later standardizes a fixed `stop_reason` enum |
| A-5 | Existing role gate `require_role(RoleType.TENANT_ADMIN)` (used by `GET /api/v1/metrics/runs`, `GET /initiatives`) is the correct role for all three new endpoints | PRD A5; confirmed by inspection — `src/api/v1/metrics_routes.py`, `src/api/v1/initiatives_routes.py` | PE | confirmed | Product requires a narrower/different role for metrics visibility |
| A-6 | `RunOrchestrator._finalize_run` already persists the full `RunOutcomeType` vocabulary correctly for `run_stopped` events; CAP-01's gap is scoped to `stage_completed` events and the `stages.outcome_type` column, not run-level finalize | Confirmed by inspection — `src/business_services/run_orchestrator.py:1491-1585` vs `:868-873`/`metrics_emitter.py:120-153` | PE | confirmed | A future refactor changes `_finalize_run`'s persisted vocabulary |
| A-7 | Tenant scoping for CAP-02/CAP-03 aggregation is achievable by joining `stages`/`run_events` through `runs.tenant_id` — no new `tenant_id` column needed on `stages`/`run_events` | Confirmed by inspection — `src/database/postgres/schema/run_store_schema.py` (`RunSchema.tenant_id` present; `StageSchema`/`RunEventSchema` absent) | PE | confirmed | Query performance at scale requires denormalizing `tenant_id` onto `stages`/`run_events` |
| A-8 | `lane` (spec/implement/closeout) for a completed run must be derived at query time (from existing signals such as `meta_pr_url` presence, or a new field) because `LaneType` today flows only through the ephemeral job payload, never persisted on `RunSchema` | Confirmed by inspection — `src/business_services/wave_start_service.py:149,354,393`; `src/models/run_store_models.py` (no `lane` field) | PE | open — see Q-2 | Feasibility/technical review adds a persisted `lane` column instead of inferring it |
| A-9 | `codify_hint.target` (free string, e.g. `"skill"`) and `LearningItemDocument.class_type` (`LearningClassType` enum: `SPEC`/`SKILL`/`HARNESS`/`ENV`) are two distinct fields on the same learning item; REQ-08's join condition is `codify_hint.target == "skill"` (lowercase string), not `class_type == LearningClassType.SKILL` | Confirmed by inspection — `src/models/learning_models.py` | PE | confirmed | `prayog-skills` collapses the two vocabularies into one field |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact JSON field names / OpenAPI response shapes for the three new endpoints (PRD Appendix B/C are explicitly illustrative; impact map IM-01) | PE | no | Spec PR / OpenAPI pass | Route paths, tenant-scoping, and `as_of`/`retention_days` semantics stay normative; field names deferred | open | pending |
| Q-2 | PE / architecture | REQ-16 needs wave cycle time grouped by lane (spec/implement/closeout), but `LaneType` is never persisted on `RunSchema` today (A-8) — should feasibility add a persisted `lane` column, or infer lane at query time from existing signals (e.g. `meta_pr_url` presence ⇒ spec)? | PE | no | feasibility / technical review | Infer lane at query time from best-effort existing signals; REQ-16 acceptance ("correct percentile grouping by lane") stays implementation-neutral regardless of the chosen mechanism | open | pending |
| Q-3 | PE / architecture | REQ-23 requires CAP-04 to be tenant-scoped, but `InitiativeReadoutService.list_initiatives()`/`_all_runs()` (which REQ-20/REQ-21 reuse) has no `tenant_id` filter today — should CAP-04 extend `InitiativeReadoutService` with a tenant-scoped variant, or build an independent tenant-scoped composition reusing `RunRepository.list_runs(tenant_id=...)`? | PE | no | feasibility / technical review | Extend with a tenant-scoped composition reusing the existing `RunRepository.list_runs(tenant_id=...)` pattern (ADR-016); no product decision required here | open | pending |
| Q-4 | PE | Should `prayog-skills` formally acknowledge that `workflow_node` id stability is now load-bearing for a third consumer (metrics joins), beyond navigation and checkpoint evidence already noted in earlier maps? (impact map IM-02) | PE | no | not required this INIT | No action required this INIT; unmatched refs report as "unjoined," never erroring (REQ-09) | open | pending |
| Q-5 | PE | Does the new cross-reference from INIT-GATEFLOW-015 to INIT-GATEFLOW-004's `REQ-37`/`A2` require a reciprocal update to INIT-GATEFLOW-004's own PRD? (impact map IM-03) | PE | no | before/at `gateflow-ops` consumption (follow-on INIT) | One-way reference from this INIT is sufficient for this INIT's exit; revisit only when a `gateflow-ops`-consuming INIT is scoped | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR [#40](https://github.com/drivestream-lab/prayog-meta/pull/40) head `63ebf8009a8d01721c432de0a92cb21649eb7613` = tech-lead APPROVED review `commit_id` ([review](https://github.com/drivestream-lab/prayog-meta/pull/40#pullrequestreview-4912330943)); label `impact-map-lgtm`; H1 PRD digest matches (`sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666`, verified via `shasum -a 256`); H3 revision 1; H2 gateflow affected `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | CAP-01…04 map to REQ-01…23 1:1 with the PRD; every REQ row cites PRD REQ/CAP/US/D/A/OQ ids |
| D3 Repo-bounded scope | PASS | Matches H2 payload exactly; `gateflow-ops` deferred (future consumer); `prayog-skills` consume-only monitor; `prayog-meta` not an eng delivery repo this INIT |
| D4 Observable acceptance | PASS | Each REQ states condition/event, observable result, evidence layer; architecture (module names, lane persistence, InitiativeReadoutService extension) deferred to Q-2/Q-3, not decided in REQ rows |
| D5 Negative/failure paths | PASS | 8 rows covering PRD's resolved error table (incl. CHG-05's malformed-filter and empty-tenant additions) plus explicit "why it matters" rationale per row |
| D6 Assumptions/questions | PASS | A-1…A-9 (A-1…A-5 from PRD, A-6…A-9 from direct source inspection); Q-1…Q-5 all non-blocking with explicit defaults |
| D7 Cross-repository contracts | PASS | CTR-01 semantic (workflow_node/codify_hint.ref read-only join key); no outbound write contract; "no cross-repo boundary" otherwise |
| D8 NFR applicability | PASS | All 8 areas specified or N/A with reason |
| D9 As-built alignment | PASS | Overview's "As-built baseline" section cites exact file:line evidence distinguishing existing (run-level finalize already correct), changed (stage-level outcome mapping), and new (three GET endpoints, tenant-scoped composition) behavior |
| D10 Dependency order | PASS | Matches impact map §7: `prayog-skills` (consume-only) → W0 (CAP-01) → W1 (CAP-02) → W2 (CAP-03) → W3 (CAP-04) → `gateflow-ops` (deferred) |
| D11 Zero unresolved blockers | PASS | No blocking PM/PE/domain question; Q-1…Q-5 all non-blocking with recorded defaults |
| D12 Output completeness | PASS | Header H4, all required tables, check summary, selected workflow outcome, PR readiness handoff, and dev-review checklist present with no placeholders presented as fact |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on current meta PR head; PRD digest verified byte-for-byte against the actual PRD file; zero material unresolved questions after the clarification loop (Q-1…Q-5 all non-blocking with recorded defaults, including two new technical gaps — REQ-16 lane persistence and REQ-23/CAP-04 tenant-scoping composition — discovered by direct source inspection and routed to feasibility rather than blocking this draft).

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full traceability; no material blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-015] Spec — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` / `/open-draft-pr` — do not commit/push/open PR inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** Persist the draft locally, present
this section in chat, and ask whether to authorize Forge publish
(`/commit-workspace` / `/open-draft-pr` or Gateflow ForgeClient). Continue only
after explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-015 — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/40
- Approved meta head: `63ebf8009a8d01721c432de0a92cb21649eb7613`
- Impact-map revision: 1
- PRD digest: `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666`
- Repo scope digest: `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72`

## Spec path

`docs/specification/product/INIT-GATEFLOW-015-gateflow.md`

## Summary

- CAP-01 (W0) outcome-persistence prerequisite fix (REQ-01–03); CAP-02 (W1) Skill/Spec Efficacy API (REQ-04–10); CAP-03 (W2) Factory Effectiveness API (REQ-11–17); CAP-04 (W3) Delivery Scorecard API, gateflow-owned half (REQ-18–23)
- All three new routes are additive `GET`s; `GET /api/v1/metrics/runs` unchanged
- Open engineering questions: Q-1…Q-5 (non-blocking; defaults documented, including two technical gaps found by source inspection — lane persistence for REQ-16, tenant-scoping composition for REQ-23/CAP-04)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `/open-draft-pr`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADRs (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [ ] Scope matches the approved impact-map repo scope digest
- [ ] REQs have condition/event, observable result, and evidence layer
- [ ] Contracts are semantic (logical operation); no architecture decisions in REQs
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Never infer approval from labels
alone — `spec-lgtm` requires matching artifacts on the exact PR head.

Provision labels before PR creation when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-015.md` @ meta PR [#40](https://github.com/drivestream-lab/prayog-meta/pull/40)
- Outline: `prayog-meta/prd/INIT-GATEFLOW-015-outline.md`
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-015.md` revision 1
- Predecessor: [`INIT-GATEFLOW-001-gateflow.md`](INIT-GATEFLOW-001-gateflow.md) (`GET /metrics/runs` v0); [`INIT-GATEFLOW-011-gateflow.md`](INIT-GATEFLOW-011-gateflow.md) (`InitiativeReadoutService`, `CheckpointEvidenceService`, closure/completion readouts this INIT reuses)
- Related, not blocking: [`INIT-GATEFLOW-004-gateflow.md`](INIT-GATEFLOW-004-gateflow.md) — CAP-03 fulfills its `REQ-37`/`A2` aggregate dependency
- As-built: `docs/specification/as-built/implementation-status.md`
- Pin: `prayog-skills` (`workflow.yaml` — consume-only, `workflow_node` ids + `codify_hint.ref` join keys)
- Source grounding: `src/business_services/metrics_emitter.py`, `src/business_services/run_orchestrator.py`, `src/models/run_store_types.py`, `src/models/learning_models.py`, `src/business_services/initiative_readout_service.py`, `src/api/v1/metrics_routes.py`, `src/database/postgres/schema/run_store_schema.py`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    # digest omitted — spec-draft does not mint/cite a durable identity per
    # references/handoff-envelope.md; artifact.path existing at the canonical
    # location is the walk-time proof-of-write
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-015
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/40"
    meta_pr_head: "63ebf8009a8d01721c432de0a92cb21649eb7613"
    map_revision: 1
    prd_digest: "sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666"
    scope_digest: "sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72"
    d_checks: pass
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4,Q-5"
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-015] Spec — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
```
