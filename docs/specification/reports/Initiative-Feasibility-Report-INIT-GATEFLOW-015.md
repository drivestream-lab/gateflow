# Feasibility report — INIT-GATEFLOW-015

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-015 |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| PRD digest | `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-015.md` / `1` |
| Repo scope digest | `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` |
| Approved meta PR head | `63ebf8009a8d01721c432de0a92cb21649eb7613` |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/40#pullrequestreview-4912330943), 2026-08-12T02:03:08Z |
| Source freshness | CURRENT — re-verified: meta PR [#40](https://github.com/drivestream-lab/prayog-meta/pull/40) head still `63ebf80…`, label still `impact-map-lgtm`; spec PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) head still `dfc0acd0…`; no drift |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-12 |
| Branch | `chore/INIT-GATEFLOW-015-spec-gateflow` — spec PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) (single review surface) |
| Initiative segment | `INIT-GATEFLOW-015` |
| Status | Draft |
| Review deadline | 2026-08-15 |
| Deciders | PM: programme PM · Domain SME: n/a (no domain-specific business rule this INIT) |

## Summary

Buildable as scoped. CAP-01 (outcome-persistence fix) touches a small,
well-understood surface (`MetricsEmitter.record_stage_duration` +
`RunOrchestrator._run_orchestrated_stage`) with existing regression tests to
protect (REQ-02). CAP-02/03/04 are net-new read endpoints composing existing
repositories — no new tables, consistent with the spec's stated scope. Two
genuine, spec-correctly-deferred architecture questions surfaced by direct
ADR/code grounding must be resolved by `/spec-technical-review` before
planning: (1) `REQ-16` (wave cycle time by lane) has no durable `lane` signal
today — `LaneType` only flows through the ephemeral job payload; (2) `REQ-21`/
`REQ-23` (CAP-04 factory-coverage tenant scoping) hits a gap **explicitly
named as a revisit trigger in Accepted ADR-016** — board/EPIC tickets carry no
`run_id` link, so ADR-016's chosen tenant-attribution mechanism (Option C,
"derive tenant through the `run_id` link") cannot cover them. Both are
correctly *not* decided in the spec (product-boundary discipline held) and
both have safe, named defaults if deferred. No blocking PM or domain
questions. Recommend: proceed to `/spec-technical-review`.

**Findings:** 2 total (0 Critical, 2 Should fix, 0 Verify, 0 Gap as blocking; multiple informational Gap observations recorded as signals, not counted as findings)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 0 | 0 |
| PE / ADR | 2 | 3 (Q-1, Q-4, Q-5 carried from spec, non-blocking) | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 0 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 2 |
| Verify / Gap (informational) | 6 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `findings` |
| Rationale | Two unresolved Should-fix PE/ADR items (FF-01, FF-02) remain after feasibility — by design, feasibility flags architecture questions, it does not resolve them; zero blocking PM/domain items, zero authority drift |
| Next (from workflow) | `spec-technical-review` |

Informational observations alone do not select `findings`. FF-01 and FF-02
are the deciding items — both PE-lane, both `NEW-ADR` candidates per the
qualification rubric (real trade-off, storage/attribution authority, hard to
reverse, constrains later initiatives).

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/test_metrics_emitter.py`, `tests/unit/test_metrics_emitter_tenant_scope.py` cover existing `record_stage_duration`/`aggregate_run_metrics`/`list_runs`/`get_run_status`; no test yet asserts the full `RunOutcomeType` vocabulary on `stage_completed` (expected — CAP-01 not yet built) | `tests/unit/test_metrics_emitter.py:84-111` (`test_record_stage_duration_failed_outcome` only covers `failed`) |
| Live verify | `tests/verify/verify_status_metrics.py` exercises `/metrics/runs` and is wired into `verify_all.py`; no `verify_skill_efficacy`/`verify_factory_effectiveness`/`verify_delivery_scorecard` exist yet (expected — new capability) | `tests/verify/verify_all.py:32,41`; `tests/README.md` feature map has no CAP-02/03/04 rows yet |
| As-built | `implementation-status.md` INIT-GATEFLOW-002 W1 row confirms `/metrics/runs` already reports `by_runner`/`by_model_id` in addition to `by_workflow_node` — matches spec Overview's precise predecessor attribution | `docs/specification/as-built/implementation-status.md:239` |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01 / W0 | Full `RunOutcomeType` on `stage_completed` + `stages.outcome_type` | `src/business_services/metrics_emitter.py:120-153` (binary success/failed/None mapping); `src/business_services/run_orchestrator.py:868-873` (`stage_outcome` from `agent_result.outcome` only, ignores `handoff.outcome`) | `test_metrics_emitter.py::test_record_stage_duration_failed_outcome` (partial — only `failed`) | none | **drift** — code exists, behavior does not match REQ |
| REQ-02 / W0 | `success`/`failed` unchanged | same files | same test | existing suite | exists — regression guard already in place |
| REQ-03 / W0 | Pre-fix events excluded from outcome-aware rates | none yet — new query-time behavior | none | none | gap (planned) |
| REQ-04–07 / W1 | `GET /api/v1/metrics/skill-efficacy` core shape | none yet; reuses `RunEventRepository`/`StageRepository` (`src/database/postgres/repository/run_store_repository.py`) | none | none | gap (planned; no module conflict — sibling to `metrics_emitter.py` per spec's non-normative note) |
| REQ-08–09 / W1 | Learning codify-rate join on `codify_hint.target`/`ref` | `LearningRepository` (`src/database/postgres/repository/learning_repository.py`) has `get_by_run_id`/`list_items(initiative_id, wave_id)` only — no org-wide "all items" query | none | none | gap (planned; needs new repository method, not a new store — schema already supports via `codify_hint` JSONB) |
| REQ-10 / W1 | CAP-02 tenant-scoped | `RunSchema.tenant_id` present; `StageSchema`/`RunEventSchema` have none — join through `runs.tenant_id` per ADR-016 Option C | `test_metrics_emitter_tenant_scope.py` (covers `list_runs`/`get_run_status`, not stage/event aggregation yet) | none | gap (planned; ADR-016-conformant pattern, not a new decision) |
| REQ-11–13 / W2 | `GET /api/v1/metrics/factory-effectiveness`; unattended streak; `stop_reason` breakdown | `WorkflowEngine`/`PolicyEngine` node types (`human-checkpoint`, `external-action`) already resolvable (`src/business_services/workflow_engine.py`, `policy_engine.py`); `run_stopped` events already carry `stop_reason` in payload (`run_orchestrator.py:1515-1519`) | none | none | gap (planned; underlying signals already persisted correctly — confirms F5, no additional persistence fix needed beyond CAP-01) |
| REQ-14–15 / W2 | Gate dwell time (inferred join) | `RunRepository` has no "find next run for initiative+wave after a given timestamp" query yet — straightforward addition over existing `runs` columns (`initiative_id`, `wave_id`, `created_at`) | none | none | gap (planned; no schema change per REQ-14) |
| REQ-16 / W2 | Wave cycle time p50/p95 by lane | `LaneType` (`src/models/lane_types.py`) set at wave-start (`src/business_services/wave_start_service.py:149,354,393`) but **only** flows through ephemeral `JobSchema.payload` — never persisted on `RunSchema` | none | none | **gap + open architecture question — see FF-01** |
| REQ-17 / W2 | CAP-03 tenant-scoped | same ADR-016 pattern as REQ-10 | none | none | gap (planned) |
| REQ-18–19 / W3 | `GET /api/v1/metrics/delivery-scorecard`; rework post-checkpoint-only | `checkpoint_check` run events already persisted (`CheckpointEvidenceService`, INIT-GATEFLOW-011 W1) — usable evidence for "already passed a human-checkpoint" | none | none | gap (planned) |
| REQ-20 / W3 | Initiatives-closed-with-evidence via existing closure/completion readout | `ClosurePreviewService`, `CompletionReadoutService` exist (`src/business_services/closure_preview_service.py`, `completion_readout_service.py`) — both per-initiative, no aggregate-all-initiatives query yet | none | none | gap (planned; existing services confirmed reusable, no new store) |
| REQ-21 / W3 | Factory coverage % (EPIC board composition) | `InitiativeReadoutService.list_initiatives()`/`_all_runs()` (`src/business_services/initiative_readout_service.py:66-138`) has **no** `tenant_id` filter; `BoardTicketResource` (`src/models/board_models.py:86-100`) has no `run_id` or `tenant_id` field | none | none | **gap + open architecture question — see FF-02 (ADR-016 revisit trigger)** |
| REQ-22 / W3 | Intent→merge lead time absent/`unavailable` | precedent: `InitiativeReadoutService._resolve_prd_approval` already returns an explicit `unavailable` state for a different meta-bridge gap | none | none | gap (planned; existing precedent pattern to reuse) |
| REQ-23 / W3 | CAP-04 tenant-scoped | same as REQ-21 — blocked on FF-02 resolution for the board/EPIC half | none | none | **gap + open architecture question — see FF-02** |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Code evidence | Finding |
|-----------------|-----------------|--------|----------------|---------|
| REQ-04, REQ-11, REQ-18 (role gate) | ADR-014 (JWT-only product edge trust zone) | aligned | `src/api/v1/metrics_routes.py:26`, `src/api/v1/initiatives_routes.py` (`require_role(RoleType.TENANT_ADMIN)` reused verbatim) | N/A — direct conformance, no finding |
| REQ-10, REQ-17 (CAP-02/03 tenant scoping) | ADR-016 (Tenant-scoped run, board, and checkpoint authorization) | aligned | `src/database/postgres/schema/run_store_schema.py` (`RunSchema.tenant_id`; `StageSchema`/`RunEventSchema` have none) | N/A — `stages`/`run_events` both reference `run_id`, so ADR-016 Option C ("records that reference a `run_id` derive tenant... through that link") applies directly; no new decision needed |
| REQ-16 (wave cycle time by lane) | N/A — no existing ADR covers persisted lane state | missing ADR | `src/models/lane_types.py`; `src/business_services/wave_start_service.py:149,354,393`; `src/models/run_store_models.py` (no `lane` field on `RunCreate`/`RunModel`) | `ALTERNATIVE: persist a durable lane field on RunSchema at wave-start (new column, human Alembic per database-migrations.mdc) vs. infer lane at metrics-query time from existing signals (e.g. meta_pr_url presence for spec lane) for REQ-16's wave-cycle-time-by-lane grouping` |
| REQ-21, REQ-23 (CAP-04 board/EPIC tenant scoping) | ADR-016 (Accepted) — **revisit trigger #2 named in the ADR itself is now firing** | conflict/gap — ADR's own documented boundary case | `src/models/board_models.py:86-100` (`BoardTicketResource` — no `run_id`, no `tenant_id`); `src/business_services/initiative_readout_service.py:66-138` (`list_initiatives`/`_all_runs` — no tenant filter today); ADR-016 §Consequences: "A board ticket or checkpoint record is created with no `run_id` link, requiring its own scoping column after all" | `ALTERNATIVE: tenant-scope CAP-04's EPIC/board-ticket composition — which has no run_id link — by (a) reusing ADR-016's rejected Option B (runtime join through TenantRepoSchema org+repo → tenant_id) scoped narrowly to this read path, or (b) narrowing REQ-21's denominator to only EPIC tickets that already have ≥1 Gateflow run, making the existing run_id-derived Option C path sufficient without touching board-ticket scoping at all` |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F13 | "REQ-16 | Response includes wave cycle time (existing `wave_duration_ms`) as p50/p95, grouped by lane (spec / implement / closeout)" | none (missing ADR) | `ALTERNATIVE: persist a durable lane field on RunSchema at wave-start (new column, human Alembic) vs. infer lane at metrics-query time from existing signals (e.g. meta_pr_url presence) for REQ-16's wave-cycle-time-by-lane grouping` |
| FF-02 | F13 | "REQ-21 | Factory coverage % = EPIC-ticketed initiatives visible on the connected board ... that have ≥1 Gateflow-tracked run, over total EPIC-ticketed initiatives visible on that board" | ADR-016 (Accepted) — revisit trigger #2 | `ALTERNATIVE: tenant-scope CAP-04's EPIC/board-ticket composition (no run_id link) via a narrow reuse of ADR-016's rejected Option B (org+repo → tenant_id runtime join) vs. narrowing REQ-21's denominator to EPIC tickets with ≥1 Gateflow run so the existing run_id-derived Option C path suffices` |

No F14 (MDC conformance) findings — spec wording does not imply any pattern
contradicting `pydantic-schemas.mdc` (models deferred to `src/models/` per
spec's own non-normative note), `http-api-conventions.mdc` (all three new
routes are GET with query filters, no PUT/PATCH body ambiguity),
`repository-pattern.mdc` (spec explicitly reuses existing repositories, no
ORM leakage implied), or `dependency-injection.mdc`/`architecture.mdc`
(module/class naming deferred to technical review, consistent with rules —
not decided in the spec).

## Findings by severity

### Critical

None.

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F13 | `NEW-ADR`: no durable `lane` signal exists for REQ-16's wave-cycle-time-by-lane grouping | `src/models/lane_types.py`; `src/business_services/wave_start_service.py:149,354,393`; `src/models/run_store_models.py` |
| FF-02 | F13 | `NEW-ADR`: CAP-04's board/EPIC tenant scoping (REQ-21/REQ-23) hits ADR-016's own named revisit trigger — board tickets have no `run_id` link | `src/models/board_models.py:86-100`; `src/business_services/initiative_readout_service.py:66-138`; `docs/specification/adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md` §Consequences/§Revisit triggers |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 (CAP-01) | `src/business_services/metrics_emitter.py`, `src/business_services/run_orchestrator.py`, `src/models/run_store_models.py` (no schema change) | `tests/unit/test_metrics_emitter.py`, `tests/unit/test_run_orchestrator.py` — extend with `findings`/`stopped`/`blocked`/`pending` fixture cases; existing `success`/`failed` cases must stay green (REQ-02) |
| W1 (CAP-02) | New sibling module/methods near `metrics_emitter.py`; new route in `src/api/v1/metrics_routes.py`; new `LearningRepository` org-wide query method | New unit test file (naming per technical review); no live verify script yet |
| W2 (CAP-03) | Same route file; new dwell-time query on `RunRepository`; unattended-streak trace logic over `WorkflowEngine`/`PolicyEngine` node types | New unit test file; fixture wave including one automated `external-action` hop (per REQ-12's specific exclusion) |
| W3 (CAP-04) | Depends on FF-02 resolution; likely touches `InitiativeReadoutService` or a new tenant-scoped sibling composition, `ClosurePreviewService`/`CompletionReadoutService` reuse | New unit test file; fixture initiative with pre- and post-checkpoint findings loops (REQ-19) |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | REQ-16 ships with an inferred (not persisted) `lane` heuristic that later proves unreliable for closeout runs (no `meta_pr_url`, ambiguous vs. implement) | Named risk if FF-01 defers to inference; revisit trigger = heuristic misclassifies >1 real wave in dogfood usage |
| R-2 | CAP-04 factory-coverage denominator narrows to "EPIC tickets with ≥1 run" (FF-02 default) instead of "all EPIC tickets," understating true coverage gaps the metric is meant to surface | Named risk if FF-02 defers to the narrower default; revisit trigger = PE/programme leadership finds the narrower definition materially misleading in practice |
| A-10 | `WorkflowEngine`/`PolicyEngine` already expose enough node-type/authorization metadata (`human-checkpoint`, `external-action`, `authorization: explicit\|automated`) to trace the REQ-12 unattended streak without new pin surface | Confirmed by inspection — `src/business_services/policy_engine.py:15,113,124,191`; `src/business_services/run_orchestrator.py:664` |

## Recommended spec edits

- None required. The spec correctly deferred both FF-01 and FF-02 to
  feasibility/technical review (Q-2, Q-3) rather than inventing an
  architecture decision — this feasibility report sharpens Q-3 into the
  specific ADR-016-grounded board-ticket question (FF-02) and elevates Q-2
  into a formal `NEW-ADR` candidate (FF-01). No REQ wording change needed.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| FF-01 | PE / ADR | Persist a `lane` column on `RunSchema` vs. infer lane at query time for REQ-16 | yes | PE | open | technical review | Infer at query time from existing signals (e.g. `meta_pr_url` presence for spec lane); named risk R-1 | `src/models/lane_types.py`, `wave_start_service.py:149,354,393` | pending `/spec-technical-review` |
| FF-02 | PE / ADR | Tenant-scope CAP-04's board/EPIC composition given no `run_id` link (ADR-016 revisit trigger #2) | yes | PE | open | technical review | Narrow REQ-21 denominator to EPIC tickets with ≥1 Gateflow run (Option C sufficient, no board scoping needed); named risk R-2 | `board_models.py:86-100`, `initiative_readout_service.py:66-138`, ADR-016 | pending `/spec-technical-review` |
| Q-1 | PE | Exact JSON field names / OpenAPI shapes (carried from spec) | no | PE | open | Spec PR / OpenAPI pass | Route paths/scoping stay normative; field names deferred | spec §Target API surface | pending |
| Q-4 | PE | `prayog-skills` formal acknowledgment of node-id stability as a third consumer (carried from spec / impact map IM-02) | no | PE | open | not required this INIT | No action required this INIT | impact map §10 IM-02 | pending |
| Q-5 | PE | Reciprocal update to INIT-GATEFLOW-004 PRD (carried from spec / impact map IM-03) | no | PE | open | before/at `gateflow-ops` consumption | One-way reference sufficient | impact map §10 IM-03 | pending |

### PM questions (product scope, UX, priority)

None. All open items are PE/ADR-lane engineering decisions correctly deferred
by the spec.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

> These are **not** for PM. Run `/spec-technical-review` to produce a
> Technical Design Document that resolves these before
> `/spec-implementation-plan`.

#### Blocking for implementation plan

1. FF-01 — `RunSchema.lane` persistence vs. inference (REQ-16).
2. FF-02 — CAP-04 board/EPIC tenant scoping given ADR-016's named revisit trigger (REQ-21/REQ-23).

#### Defer with default

1. Q-1 — exact JSON/OpenAPI field names (defer to OpenAPI pass; route shapes stay normative).
2. Q-4 — `prayog-skills` node-id stability acknowledgment (no action required this INIT).
3. Q-5 — reciprocal INIT-GATEFLOW-004 PRD update (one-way reference sufficient this INIT).

### Domain clarifications (business source-of-truth)

None — no business source-of-truth ambiguity in this INIT (all rate/derivation
rules are already fully specified in the PRD/spec with concrete fixtures to
match).

### Auto-fixable (agent resolves later — not inside this skill)

None identified.

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | See Baseline snapshot table |
| F2 Spec → code map | PASS | CAP-01 maps to existing modules (drift confirmed); CAP-02/03/04 map to planned sibling modules (gap, expected pre-implementation) |
| F3 Spec → verify map | PASS (informational gap) | No verify scripts exist yet for CAP-02/03/04 — expected; not blocking |
| F4 Spec → unit map | PASS (informational gap) | No unit test files exist yet for CAP-02/03/04 — expected; not blocking |
| F5 As-built drift | PASS | `/metrics/runs` `by_runner`/`by_model_id` claim matches as-built exactly; `run_stopped` `stop_reason` already correctly persisted (confirms CAP-01 scope is stage-level only) |
| F6 Docs drift | PASS | No `AGENTS.md`/rules/ADR-index drift found |
| F7 Overlap risk | PASS | No duplicate unit+live coverage of the same journey |
| F8 CI vs live boundary | PASS | New unit tests → `make test`; new verify scripts (when written) → opt-in, same pattern as `verify_checkpoint_status`/`verify_wave_map`, not required in `verify_all` |
| F9 Cross-service touch | PASS | CTR-01 (`workflow_node`/`codify_hint.ref`) — `prayog-skills/workflow.yaml` exists and is read-only consumed |
| F10 Assumptions | PASS | All spec Assumptions (A-1…A-9) are evidenced by file:line citations in the spec itself; none asserted without repo evidence |
| F11 Effort drivers | PASS | See Impact surface table — W2 (CAP-03) is the highest-complexity wave (multi-signal streak trace + dwell inference); W3 (CAP-04) is dependency-ordered behind FF-02 |
| F12 PM questions | PASS | Zero blocking PM items; all open items are PE/ADR-lane with numbered ids (FF-01, FF-02) |
| F13 ADR conformance | **FINDINGS** | 2 `NEW-ADR` candidates (FF-01, FF-02); 2 rows confirmed ADR-016/ADR-014-aligned with no finding |
| F14 MDC conformance | PASS | No spec wording contradicts `rules_glob` patterns |

**Check PASS** = zero unresolved blocking findings (informational OK). F13
carries the two unresolved Should-fix findings that select workflow outcome
`findings`.

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge`
> for `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill. The
> spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → none this round.

**PE questions** → discuss FF-01/FF-02 on the [Draft spec PR](https://github.com/drivestream-lab/gateflow/pull/228); run `/spec-technical-review` next.
  PE accepts TDD/ADRs in **files** (`Draft` → `Accepted`); do **not** set
  `spec-lgtm` until the full package includes the implementation plan.

**Domain clarifications** → none this round.

**Auto-fixable items** → none this round.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-015.md` |
| Target branch | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-015-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered on meta PRD PR — N/A, none this round
  [x] All blocking Domain clarifications answered and published via Forge — N/A, none this round
  [ ] Spec updated to reflect answers (same branch, via Forge) — N/A, no spec edit needed
  [ ] Incremental re-run of /initiative-feasibility on updated spec is clean — N/A, no spec edit needed
  [x] Proceed: /spec-technical-review (always — pin routes pass and findings here)
  [ ] After spec + feasibility + TDD (if any) + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: `/create-board-tickets` from plan §9 — then /pre-implement → /loop-spec
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-015.md
    # digest omitted — feasibility digests are walk-time only (PURGE at initiative closure)
  blockers:
    - FF-01
    - FF-02
  signals:
    initiative: INIT-GATEFLOW-015
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/228"
    spec_pr_head: "dfc0acd078b4523281f66d2595c6c3388c7e0899"
    lane_counts:
      pm_blocking: 0
      pe_adr_blocking: 2
      domain_blocking: 0
      auto_fix: 0
    new_adr_count: 2
    critical_count: 0
    should_fix_count: 2
    source_freshness: CURRENT
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
```
