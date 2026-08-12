# Technical Design Document — INIT-GATEFLOW-015

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-015 |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Spec digest | `sha256:17579cbe26dcba3eeaf6fa6512480c9e485141deb663ed805387055fe2e97d36` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-015.md` |
| PRD digest | `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-015.md` / `1` |
| Repo scope digest | `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` |
| Approved meta PR head | `63ebf8009a8d01721c432de0a92cb21649eb7613` |
| Source freshness | CURRENT — re-verified: meta PR [#40](https://github.com/drivestream-lab/prayog-meta/pull/40) head unchanged, label `impact-map-lgtm`; spec PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) head unchanged at `dfc0acd0…` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-12 |
| Branch | `chore/INIT-GATEFLOW-015-spec-gateflow` (spec PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-015` |
| Status | Draft |
| Review deadline | 2026-08-19 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

---

## 1. Problem statement

Two engineering decisions block planning, both raised at feasibility (FF-01,
FF-02) and both correctly left undecided by the product spec. FF-01: no
module persists a durable grouping dimension equivalent to `LaneType`
anywhere `stages`/`run_events` can be aggregated against (REQ-16). FF-02: the
existing tenant-attribution mechanism (ADR-016 Option C, a `run_id` join)
has no coverage path for a read projection that carries no `run_id` at all —
a board/EPIC ticket record — which the aggregate composition underlying
REQ-20/REQ-21/REQ-23 must still classify by tenant.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/business_services/metrics_emitter.py` | exists | extend (`record_stage_duration` outcome mapping — REQ-01/02/03) | business_services |
| `src/business_services/run_orchestrator.py` | exists | extend (`_run_orchestrated_stage`/`_finalize_run` stage-outcome + lane payload write — REQ-01, ADR-017) | business_services |
| New sibling metrics module(s) (name deferred — Q-1) | new | create (CAP-02/03/04 read aggregation — REQ-04–23) | business_services |
| `src/database/postgres/repository/run_store_repository.py` | exists | extend (new dwell-time / tenant-scoped stage-and-event queries — REQ-10, REQ-14, REQ-17) | database (repository) |
| `src/database/postgres/repository/learning_repository.py` | exists | extend (new org-wide `codify_hint`-joined query — REQ-08/09) | database (repository) |
| `src/database/postgres/repository/tenant_repository.py` | exists (`find_workspace_credential_by_org_repo`) | reuse as-is or add a narrower sibling read (ADR-018) | database (repository) |
| `src/business_services/initiative_readout_service.py` / `closure_preview_service.py` / `completion_readout_service.py` | exist | reuse (closure/completion evidence — REQ-20) | business_services |
| `src/api/v1/metrics_routes.py` | exists | extend (three new `GET` routes — REQ-04, REQ-11, REQ-18) | api |
| `src/models/` (new response models) | new | create (per `pydantic-schemas.mdc` — models live in `src/models/`, never in `api/`) | models |

**Boundary diagram (text):**

```
GET /api/v1/metrics/{skill-efficacy,factory-effectiveness,delivery-scorecard}
  → [new metrics module(s)] → [RunEventRepository / StageRepository / RunRepository]
                             → [LearningRepository]                (CAP-02 join)
                             → [TenantRepository org+repo lookup]  (CAP-04, ADR-018)
                             → [ClosurePreviewService / CompletionReadoutService] (CAP-04, REQ-20)
  ↑ tenant_id from AuthContext (require_role(TENANT_ADMIN))
```

---

## 3. Public interface contracts

### 3.1 New metrics module → `RunEventRepository`/`StageRepository`

**Method / entry point:** new tenant-scoped, node-grouped aggregation query
(name deferred to implementation)
**Arguments:**
- `tenant_id`: UUID — required, never optional (REQ-10/17/23)
- `retention_days` window — same convention as `aggregate_run_metrics`

**Return:**
- Per-`workflow_node` counts/rates (REQ-04–07); never raises on empty result
  set — returns a well-formed zero/empty response (spec Negative paths table)

**Invariants:**
- Pre-CAP-01 events are excluded from outcome-aware rates, not miscounted
  (REQ-03)
- Response never leaks another tenant's rows (REQ-10)

### 3.2 New metrics module → `LearningRepository` (new method)

**Method / entry point:** new org-wide `codify_hint`-joined query (name
deferred)
**Arguments:** none beyond retention scope — join key is `codify_hint.ref`
against `workflow_node`, filtered by `codify_hint.target == "skill"`

**Return:**
- Per-node rate for `target == "skill"`; flat org-wide rate for
  `{SPEC, HARNESS, ENV}`; explicit "unjoined" bucket for unmatched `ref`
  (REQ-08/09)

**Invariants:**
- Never drops or errors an unmatched `ref` (REQ-09)

### 3.3 New metrics module → `TenantRepository` (ADR-018)

**Method / entry point:** reuse `find_workspace_credential_by_org_repo`
(extract `tenant_id` only) or a narrower sibling read
**Arguments:** `org: str`, `repo: str`
**Return:** `tenant_id: UUID` or `None`
**Invariants:** fails closed (raises) on ambiguous multi-tenant registration
— existing behavior, not new for this initiative

### 3.4 `_run_orchestrated_stage` / `_finalize_run` → `record_stage_duration` / `append_event` (ADR-017)

**Method / entry point:** existing `record_stage_duration`, `append_event`
**Arguments:** unchanged signature; the `lane` value already present in the
in-scope job `payload` dict is added into the JSONB `payload` argument, not a
new parameter
**Return:** unchanged
**Invariants:** REQ-02 regression — `success`/`failed` persistence unchanged
byte-for-byte

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-01 | ADR_REQUIRED | `docs/specification/adr/adr-017-wave-lane-attribution-for-metrics.md` | `[REQ-16]` | none | Persist `lane` into existing JSONB `payload` on `stage_completed`/`run_stopped` events (Option C) | Draft | `sha256:9c731eef225adc08ec1ab3be30f93931a196aadcb4a81067ce95ed9943c9507b` |
| FF-02 | ADR_REQUIRED | `docs/specification/adr/adr-018-cap04-board-ticket-tenant-scoping.md` | `[REQ-20, REQ-21, REQ-23]` | none | Reuse existing org+repo → `tenant_id` lookup (`TenantRepository.find_workspace_credential_by_org_repo`) as a read-time classification (Option A) | Draft | `sha256:29a1356e296d69abd1f4055399c030332ad5834480bfa9e2b68f308b08c4abd3` |

**Derived counts:**

- ADR_REQUIRED: 2
- TDD_ONLY: 0
- DEFERRED_WITH_DEFAULT: 0
- Draft ADR files created: 2
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-------------------|-------------------|-------------|----------------------|
| CAP-01 outcome mapping | `record_stage_duration`/`_run_orchestrated_stage` with fixture `handoff.outcome` values covering `success`/`failed`/`findings`/`stopped`/`blocked`/`pending` — no I/O, mocked repositories | none named this wave | none — internal fix, no route | exact — persisted `outcome_type` must equal the fixture's declared outcome, byte-for-byte |
| CAP-02 skill efficacy | Fixture `stage_completed`/`run_events`/learning-item rows, hand-computed expected rates — no I/O | one named boundary: real Postgres session against `RunEventRepository`/`LearningRepository` for the new join query | new opt-in `verify_skill_efficacy` (not in `verify_all`, matching `verify_checkpoint_status` precedent) | exact — rate must match hand-computed fixture value |
| CAP-03 factory effectiveness | Fixture wave trace including one automated `external-action` hop (REQ-12), fixture `STOPPED` runs with/without continuation (REQ-14/15) | one named boundary: real Postgres session for the dwell-time inference query | new opt-in `verify_factory_effectiveness` | exact per rate/rule |
| CAP-04 delivery scorecard | Fixture wave with pre- and post-checkpoint findings loops (REQ-19); fixture EPIC ticket with zero runs (ADR-018 case) | one named boundary: real Postgres session + `TenantRepository` lookup | new opt-in `verify_delivery_scorecard` | exact per rate/rule |
| Tenant scoping (REQ-10/17/23) | Cross-tenant fixture asserting scoped-empty/refused response | same boundary as above, parameterized by tenant | covered by each capability's verify script | exact — 0 cross-tenant rows |

**AI-output determinism policy:** not applicable — no LLM-generated content
in any of the three response payloads; all values are deterministic
aggregations over fixture data.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Malformed/unknown `model_id`/`prompt_revision` filter (CAP-02) | new metrics module | caught at query layer, returns empty result | recoverable — named-clean empty response, not an error (REQ-07) |
| `codify_hint.ref` matches no known `workflow_node` | new metrics module | not an error path — routed to "unjoined" bucket | recoverable by design (REQ-09) |
| `STOPPED` wave with no continuation run yet | new metrics module | not an error path — routed to open/waiting state | recoverable by design (REQ-15) |
| Cross-tenant read attempt | new metrics module | scoped query returns zero rows; never raises a leak-revealing error | recoverable — scoped-empty response (REQ-10/17/23) |
| Ambiguous org+repo → tenant lookup (ADR-018) | `TenantRepository` | raises `ValueError` (existing behavior, unchanged) | terminal for that lookup — surfaces as a 5xx at the API boundary; same existing behavior as today's git-credential callers, not new for this initiative |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| CAP-01 fix (`metrics_emitter.py`) | INFO | `run_id`, `workflow_node`, `outcome` (existing `self.logger.info` call already logs these — REQ-01 changes only the persisted value, not the log call) | no new logging needed |
| New metrics module(s) | INFO | `tenant_id`, `retention_days` or `as_of`, endpoint name | new — one structured log line per aggregation call, per `logging-loguru.mdc` (kwargs, not `{}` placeholders) |
| ADR-018 tenant lookup | WARNING | `org`, `repo` | only on the ambiguous-registration exception path (existing pattern, unchanged) |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| New CAP-02/03/04 response models | new metrics module's owning business service | `src/models/` (per `pydantic-schemas.mdc`) | additive-only; amend-by-PE |
| `stage_completed`/`run_stopped` JSONB `payload.lane` (ADR-017) | `RunOrchestrator` (write) / new metrics module (read) | write-time: orchestrator; read-time: repository layer validates via `RunEventPayloadDocument` (`extra="allow"`) | additive JSONB field; no schema versioning needed |
| `RunOutcomeType` (existing enum) | `src/models/run_store_types.py` | unchanged — REQ-01 only changes which values get persisted, not the enum itself | unchanged |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-01 | PE | resolved (Draft ADR pending Accept) | Persist vs. infer `lane` for REQ-16 | Persist into existing JSONB `payload` at existing write call sites (Option C) | plan | N/A — resolved, not deferred | ADR-017 |
| FF-02 | PE | resolved (Draft ADR pending Accept) | Tenant-scope CAP-04 board/EPIC composition given ADR-016's revisit trigger #2 | Reuse existing org+repo → `tenant_id` lookup as a read-time classification (Option A) | plan | N/A — resolved, not deferred | ADR-018 |
| Q-1 (spec, carried) | PE | deferred | Exact JSON/OpenAPI field names for the three new endpoints | Deferred to implementation/OpenAPI pass; route paths + scoping stay normative | plan | Field names chosen at implementation; no re-review needed unless scoping/shape changes | spec §Target API surface |
| Q-4 (spec, carried) | PE | deferred | `prayog-skills` formal node-id-stability acknowledgment | No action required this INIT | not required this INIT | No action | impact map IM-02 |
| Q-5 (spec, carried) | PE | deferred | Reciprocal INIT-GATEFLOW-004 PRD update | One-way reference from this INIT is sufficient | before/at `gateflow-ops` consumption | No action this INIT | impact map IM-03 |
| F5 confirmation (feasibility) | PE | resolved | Does REQ-11–13 (unattended streak, `stop_reason`) need any additional persistence beyond CAP-01? | No — `WorkflowEngine`/`PolicyEngine` node-type/authorization metadata and `run_stopped.payload.stop_reason` are already correctly persisted; CAP-03 is read-only composition over existing signals | plan | N/A — confirmed, not deferred | feasibility Traceability matrix, REQ-11–13 row |

---

## 10. Routed out — product questions (PM)

None. No PM-lane item remains open (feasibility confirmed zero PM-blocking
items).

---

## 11. Routed out — domain clarifications (SME)

None. No business source-of-truth ambiguity in this initiative.

---

## 12. Fix disposition

None — no auto-fixable items were identified at feasibility.

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | PASS — see Check summary below |
| Engineering decisions resolved | 2 resolved (FF-01, FF-02 → Draft ADRs); 0 deferred |
| Draft ADR files written | 2 files / 2 required (`adr-017-…`, `adr-018-…`) |
| Product-boundary integrity (T12) | PASS — mechanical `adr_boundary_lint.py` PASS on both ADRs (2/2 sources checked each). A second, more adversarial critical re-read (post-independent-subagent-pass) found 2 real leakage issues the first pass missed: ADR-017 Context paraphrased REQ-16's acceptance shape ("percentile grouping" ≈ p50/p95 grouped by lane) with zero literal overlap (so the lexical lint could not catch it); ADR-018's Options table narrated a foreclosed option's product-scope impact in prose instead of citing it structurally, violating `adr-template.md`'s "product consequences do not get narrated here" rule. Both fixed in-place (Context reworded to a pure data-model gap statement; Option B's Costs/risks cell reworded to a boundary-only annotation); both files re-linted PASS after the fix (evidence below) |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` — T1–T12 all PASS; both ADRs classified, drafted, mechanically linted, and independently re-read clean; zero unresolved PE-lane item without a disposition; ready for PE architecture review |
| Ready for PE review | YES |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE approval required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 names every affected/new module; existing modules confirmed via direct `source_roots` read (not just feasibility's prose) |
| T2 Interface contracts | PASS | §3.1–3.4 specify argument/return shapes and invariants for every boundary crossing named in §2 |
| T3 NEW-ADR dispositions | PASS | FF-01 and FF-02 both `ADR_REQUIRED`, both Draft files exist, both grounded in re-verified code evidence (exact method names/line numbers confirmed independently during T2 Analyze, not trusted from feasibility prose alone) |
| T4 Test policy | PASS | Unit/integration/live-verify boundaries named per module; "integration" defined as one named boundary (real Postgres session), not "the whole stack" |
| T5 Error handling | PASS | Every failure mode from the spec's Negative paths table mapped to a module and a recovery classification |
| T6 Observability | PASS | Structured log fields named per module; no new logging needed for the CAP-01 fix itself (existing call already logs the relevant fields) |
| T7 Data contract ownership | PASS | New response models routed to `src/models/`; JSONB `payload.lane` ownership and validation layer named |
| T8 Dependency graph | PASS | No circular dependency introduced; new metrics module depends downward on repositories only (`repository-pattern.mdc`); no ORM type crosses into `api`/`business_services` signatures |
| T9 Engineering questions zero | PASS | Zero unresolved PE-lane items without a disposition — see §9 |
| T10 PE review readiness | PASS | This document + both Draft ADRs are the exact review package; `ready_for_pe_review: true`, `ready_for_plan: false` |
| T11 ADR artifact integrity | PASS | Both `ADR_REQUIRED` files exist under `{adr_dir}`, Status `Draft`, link `Feasibility finding`/`Technical review`/`Source spec digest`, contain Context/Options/Recommendation/Consequences/Revisit triggers, and are indexed in §4 with digest |
| T12 Product-boundary integrity | PASS (after fix) | Mechanical lint PASS (2/2 sources) on both ADRs both before and after fix. Independent re-read ([Independent T12 re-read](80ccfc6c-ab56-4315-8fbb-207df44fa7b4)) verdict CLEAN on both — but a subsequent adversarial critical re-read found 2 real issues that pass missed: ADR-017 Context paraphrased REQ-16's p50/p95-grouped-by-lane shape as "percentile grouping" (zero literal overlap, so undetected by lexical lint); ADR-018 Options table narrated Option B's product-scope impact in prose rather than citing it structurally. Both corrected; both files re-linted PASS post-fix (`sha256:9c731eef…` / `sha256:29a1356e…`) |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet. CODEOWNERS may request PE review on `Technical-Review-*`.

```
Branch:   chore/INIT-GATEFLOW-015-spec-gateflow
PR title: "[INIT-GATEFLOW-015] Spec — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics (gateflow)"
PR body:  link meta PRD PR #40; paste §13 Implementation readiness verdict when TDD is ready

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @drivestream-lab/prayog-pe-team  ← must give explicit Approve, not just silence

Review deadline: 2026-08-19
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — required Draft files exist; TDD-only/deferred rationales are valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — every required file/link/digest is valid
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*
  [ ] T12 mechanical: scripts/adr_boundary_lint.py run on every ADR (with
      --require-sources and --approved-req-id) AND on the TDD (--tdd) —
      confirm Lint evidence on each Accepted ADR, don't just take PASS on faith
  [ ] T12 manual (lint cannot see these — see checks.md "three gaps"):
      loose paraphrase in unfamiliar vocabulary; invented behavior under a
      real REQ with flags left false; multiple decisions narrated in one
      un-duplicated Recommendation section

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates ADR metadata Draft → Accepted and TDD Status → Accepted
    (only when changes_user_visible_behavior and spec_amendment_required are false,
    Approval evidence / Approved head are populated, and Lint evidence is recorded —
    not a placeholder)
  Publish acceptance package via Forge to spec branch (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → /create-board-tickets from merged plan §9
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md
    # digest omitted — TDD digests are walk-time only (PURGE at initiative closure)
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-015
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/228"
    spec_pr_head: "dfc0acd078b4523281f66d2595c6c3388c7e0899"
    new_adr_count: 2
    adr_files:
      - path: docs/specification/adr/adr-017-wave-lane-attribution-for-metrics.md
        digest: "sha256:9c731eef225adc08ec1ab3be30f93931a196aadcb4a81067ce95ed9943c9507b"
        status: Draft
      - path: docs/specification/adr/adr-018-cap04-board-ticket-tenant-scoping.md
        digest: "sha256:29a1356e296d69abd1f4055399c030332ad5834480bfa9e2b68f308b08c4abd3"
        status: Draft
    t12_mechanical_lint: "pass (2/2 sources, both ADRs, post-fix)"
    t12_independent_reread: "clean (both ADRs) — subagent 80ccfc6c-ab56-4315-8fbb-207df44fa7b4"
    t12_adversarial_recheck: "found and fixed 2 leakage issues missed by lint + subagent — ADR-017 Context REQ-16 paraphrase, ADR-018 Options table product-scope narration"
    ready_for_pe_review: true
    ready_for_plan: false
    source_freshness: CURRENT
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
```
