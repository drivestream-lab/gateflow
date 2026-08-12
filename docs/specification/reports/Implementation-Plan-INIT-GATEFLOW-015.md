---
goal: INIT-GATEFLOW-015 — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics
initiative: INIT-GATEFLOW-015
status: Planned
date_created: 2026-08-12
source_spec: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-015.md
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md
prd_digest: sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-015.md
impact_map_revision: 1
repo_scope_digest: sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72
approved_meta_pr_head: 63ebf8009a8d01721c432de0a92cb21649eb7613
branch: chore/INIT-GATEFLOW-015-spec-gateflow
review_deadline: 2026-08-15
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-015

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` | CURRENT |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-015.md` (outcome `findings`) | CURRENT |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md` (`Status: Accepted`) | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-015.md` / `1` | CURRENT |
| Repo scope digest | `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` | CURRENT |
| Approved meta PR head | `63ebf8009a8d01721c432de0a92cb21649eb7613` | CURRENT — re-verified via `gh pr view 40` this session (label `impact-map-lgtm` unchanged) |
| `check_command` | `make check` (`black`, `ruff`, `pyright`, `lint-imports`) | RESOLVED |
| `test_command` | `make test` (`.venv/bin/pytest tests/unit/ -v`) | RESOLVED |
| `verify_command` | `.venv/bin/python -m tests.verify.<script>` (per wave below; no single command covers all waves; W0 has none — no route surface) | RESOLVED |
| `ground_command` | N/A — this repo has no dedicated ground-truth script; `/ground-spec` verifies against as-built + spec citations directly, not a runnable command | N/A |

Spec PR: [#228](https://github.com/drivestream-lab/gateflow/pull/228), head `e0e1d53c201d1d387079fecf8914ae0252cfeadd` (local plan below not yet published to this head).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md` |
| Technical review status | **Accepted** |
| PE sign-off | [x] complete — 2026-08-12, @nikd10x, Cursor chat, Draft spec PR [#228](https://github.com/drivestream-lab/gateflow/pull/228), approved head `4505eabf5e09a1409065d8067c26bd0608e505b6` |
| Resolved ADRs | [`adr-017`](../adr/adr-017-wave-lane-attribution-for-metrics.md) (Accepted — persist `lane` into existing JSONB `payload` on `stage_completed`/`run_stopped`, no schema column), [`adr-018`](../adr/adr-018-cap04-board-ticket-tenant-scoping.md) (Accepted — reuse existing org+repo → `tenant_id` lookup as a read-time classification for run-less EPIC tickets) |
| ADR product-boundary re-check | Both: `changes_user_visible_behavior: false`, `spec_amendment_required: false` confirmed in file headers. Re-ran `adr_boundary_lint.py --verify-lint-evidence --require-sources` at plan time with sources reconstructed from the spec's REQ-16/REQ-21 sentences and the feasibility report's FF-01/FF-02 finding text (not a bare structure-only pass) — see command log below. Both PASS |
| Outstanding PM questions | none |
| Outstanding domain questions | none |

**P13 lint re-check command log (source parity, not a bare re-run):**

```text
adr-017-wave-lane-attribution-for-metrics.md --verify-lint-evidence --require-sources --source-text <REQ-16 sentence from spec> --source-text <FF-01 finding text from feasibility report> --approved-req-id <REQ-01..REQ-23> → PASS (2 sources checked)
adr-018-cap04-board-ticket-tenant-scoping.md --verify-lint-evidence --require-sources --source-text <REQ-21 sentence from spec> --source-text <FF-02 finding text from feasibility report> --approved-req-id <REQ-01..REQ-23> → PASS (2 sources checked)
```

> Do not start W0 implementation until PE sign-off is marked complete above (it is).

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Full `RunOutcomeType` vocabulary onto `stage_completed` + `stages.outcome_type` | spec §Functional requirements | W0 |
| REQ-02 | Existing `success`/`failed` recording unchanged (regression) | spec | W0 |
| REQ-03 | Pre-fix events excluded from outcome-aware rates; effective boundary reported | spec | W0, W1 |
| REQ-04 | `GET /metrics/skill-efficacy` — run count, first-pass rate, findings rate, retry avg per node, tenant-scoped, within retention | spec | W1 |
| REQ-05 | First-pass rate derivation rule | spec | W1 |
| REQ-06 | Findings rate counts pre- and post-checkpoint identically | spec | W1 |
| REQ-07 | Filter/group by `model_id`/`prompt_revision` | spec | W1 |
| REQ-08 | Learning codify rate per node only for `codify_hint.target == "skill"`; others flat org-wide | spec | W1 |
| REQ-09 | Unmatched `codify_hint.ref` → explicit "unjoined" bucket | spec | W1 |
| REQ-10 | CAP-02 tenant-scoped | spec | W1 |
| REQ-11 | `GET /metrics/factory-effectiveness` — unattended Pass-1 rate, tenant-scoped, within retention | spec | W2 |
| REQ-12 | Unattended streak definition — automated `external-action` hops don't break it | spec | W2 |
| REQ-13 | `stop_reason` breakdown, free-text passthrough | spec | W2 |
| REQ-14 | Gate dwell time — inferred `initiative_id`+`wave_id`+chronology join | spec | W2 |
| REQ-15 | No-continuation `STOPPED` wave reports open/waiting, never fabricated dwell | spec | W2 |
| REQ-16 | Wave cycle time p50/p95 grouped by lane | spec | W0 (ADR-017 write), W2 (read/report) |
| REQ-17 | CAP-03 tenant-scoped | spec | W2 |
| REQ-18 | `GET /metrics/delivery-scorecard` — tenant-scoped, `as_of` + cumulative + 90-day delta | spec | W3 |
| REQ-19 | Rework rate — post-checkpoint-only findings/blocked re-entry | spec | W3 |
| REQ-20 | Initiatives-closed-with-evidence via existing closure/completion readout | spec | W3 |
| REQ-21 | Factory coverage % — EPIC-ticketed board initiatives with ≥1 run, over total EPIC-ticketed | spec | W3 (ADR-018) |
| REQ-22 | Intent→merge lead time absent/`unavailable` | spec | W3 |
| REQ-23 | CAP-04 tenant-scoped | spec | W3 |

---

## 2. Implementation phases

### Phase W0 — Persist full `RunOutcomeType` vocabulary + lane payload (CAP-01 prerequisite)

**GOAL-W0:** `stage_completed` and `run_stopped` events, and the `stages` row, persist the skill's actual declared outcome (`success`/`failed`/`findings`/`stopped`/`blocked`/`pending`) instead of collapsing non-binary outcomes to `None`; the same write path also persists a `lane` value into the existing JSONB `payload` (ADR-017), laying the groundwork W2 reads for REQ-16. No new route, no schema migration, no behavior change to `GET /metrics/runs` (REQ-02 regression guard).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Extend `MetricsEmitter.record_stage_duration`'s `outcome` string mapping to the full `RunOutcomeType` vocabulary (`success/failed/findings/stopped/blocked/pending`) instead of binary success/failed/`None` | REQ-01, REQ-02 | — | `src/business_services/metrics_emitter.py` modify | Each of the 6 outcome strings maps 1:1 to its `RunOutcomeType` member; an unset `outcome` still maps to `None` (caller silence, not data loss) | command | `pytest tests/unit/test_metrics_emitter.py -v` | exit 0; 6 parametrized outcome cases + 2 existing success/failed cases pass | Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-01 | gateflow | spec REQ-01, REQ-02 | N/A (no route this wave — P15 N/A) | `pydantic-schemas.mdc` — reuse existing `RunOutcomeType` enum, no new vocabulary | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W0-02 | In `RunOrchestrator._run_orchestrated_stage`, derive `stage_outcome` (persisted on **both** `StageCreate.outcome_type` and passed into `record_stage_duration`) from `handoff.outcome` when `agent_result.outcome == AgentRunOutcomeType.SUCCESS`, mapping `findings`/`blocked`/`stopped`/`pending`/`pass` onto `RunOutcomeType`; when `agent_result.outcome == FAILED`, `stage_outcome` stays `FAILED` regardless of `handoff.outcome` | REQ-01, REQ-02 | TASK-W0-01 | `src/business_services/run_orchestrator.py` modify | Fixture with `handoff.outcome="findings"` after agent success → `stages.outcome_type == FINDINGS` and the `stage_completed` event's `outcome_type == FINDINGS`; fixture `handoff.outcome="pass"` → `SUCCESS` unchanged; agent failure fixture → `FAILED` regardless of `handoff.outcome`; existing pre-fix success/failed-only fixtures still pass unmodified (REQ-02) | command | `pytest tests/unit/test_run_orchestrator.py -k stage_outcome_vocabulary -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-02 | gateflow | spec REQ-01, REQ-02 | N/A (no route this wave) | `fail-fast.mdc` — no silent collapse to `None` for a real outcome | N/A — implements REQ-01 directly; TDD Overview grounding confirmed this is not an open trade-off (only `handoff.outcome` can supply this signal) | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W0-03 | Persist `lane` (read from the job payload already in scope at these call sites) into the JSONB `payload` of the `stage_completed` event (`record_stage_duration` call in `_run_orchestrated_stage`) and the `run_stopped` event (`_finalize_run`'s `append_event` call) | REQ-16 (write half; ADR-017 Option C) | TASK-W0-02 | `src/business_services/run_orchestrator.py` modify (same file, `_finalize_run` + `_run_orchestrated_stage`) | `run_events.payload["lane"]` present on both event types when the job payload carries a non-empty `lane` key; absent (not fabricated as e.g. `"unknown"`) when the job payload has no `lane` key | command | `pytest tests/unit/test_run_orchestrator.py -k lane_payload -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-03 | gateflow | spec REQ-16 | N/A (no route this wave) | N/A | **ADR-017** (Option C — JSONB payload field, no schema column, no human Alembic) | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W0-04 | Confirm (inspection) that TASK-W0-01…03 touch only the write path for events recorded **going forward** — zero `UPDATE`/backfill statement against existing `run_events`/`stages` rows | REQ-03 (no-backfill half) | TASK-W0-01, TASK-W0-02, TASK-W0-03 | none — `files: []`, docs-only / inspection-only | docs-only / inspection task — the W0 diff contains zero SQL/ORM mutation statement touching a pre-existing row; reviewer confirms by reading the diff | review | PE reviews the W0 diff for absence of any backfill/migration statement | Reviewer confirms zero backfill statements present | Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-04 | gateflow | spec REQ-03 | N/A | `database-migrations.mdc` — no Alembic revision needed this wave (no schema change) | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/business_services/metrics_emitter.py` | modify |
| FILE-W0-02 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W0-03 | `tests/unit/test_metrics_emitter.py` | modify |
| FILE-W0-04 | `tests/unit/test_run_orchestrator.py` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` (`pytest tests/unit/test_metrics_emitter.py tests/unit/test_run_orchestrator.py -v`) | REQ-01, REQ-02, REQ-03 (no-backfill half), REQ-16 (write half) |

**P15 applicability (W0):** `applicable: false` — no new/changed HTTP route, worker ingress, lane start, or public contract this wave. CAP-01 is an internal write-path fix (per spec Appendix B: "internal fix; no new route"); `GET /metrics/runs`'s response shape and values are unchanged (REQ-02 regression guard is the proof, not a new live surface). No `live_verify_dir` FILE required this wave.

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01 full vocabulary persisted | TEST-W0-U | N/A | N/A | N/A | P15 N/A — no route surface |
| REQ-02 regression (success/failed unchanged) | TEST-W0-U | N/A | N/A | N/A | Existing fixtures re-asserted, not just new ones added |
| REQ-03 no-backfill half | inspection (TASK-W0-04) | N/A | N/A | N/A | Boundary-reporting half completes in W1 (TASK-W1-05) |
| REQ-16 write half (lane payload) | TEST-W0-U | N/A | N/A | N/A | Read/report half completes in W2 (TASK-W2-05) |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | no — internal outcome-persistence fix; zero new/changed HTTP route or public contract this wave; `GET /metrics/runs` unchanged (REQ-02) |
| Environment class | N/A |
| Mode | N/A |
| Runtime head binding | N/A |
| Prerequisites | N/A |
| Safe test data | N/A |
| Steps / command | N/A |
| Expected observations | N/A |
| Expected evidence | N/A |
| Cleanup | N/A |
| Stop conditions | N/A |

---

### Phase W1 — Skill/Spec Efficacy API (CAP-02)

**GOAL-W1:** `GET /api/v1/metrics/skill-efficacy` returns, per `workflow_node` and tenant-scoped: run count, first-pass rate, findings rate, retry avg, and a learning codify rate joined against `codify_hint.target == "skill"` — composed live from `RunEventRepository`/`StageRepository`/a new `LearningRepository` org-wide query, reusing the ADR-016 `run_id`-join tenant-scoping pattern (no new decision). Also completes REQ-03's boundary-reporting half.

**Module design decision (plan-level, not ADR-worthy — see governance note below):** one new business service per capability, `SkillEfficacyService`, following this repo's existing per-concern service pattern (`ClosurePreviewService`, `CompletionReadoutService`, `InitiativeReadoutService` are separate services, not one monolithic "ReadoutService") rather than adding methods to `MetricsEmitter`. This is a local, easily reversible implementation choice bounded by `architecture.mdc`'s `*_service` naming convention — it does not meet the ADR qualification rubric (no cross-service/storage-authority/security trade-off; renaming or merging services later is a routine refactor), so it is decided here, not routed to `/spec-technical-review`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | `SkillEfficacyResponse` + per-node item models (run count, first-pass rate, findings rate, retry avg, codify rate, unjoined bucket, `model_id`/`prompt_revision` filter echo) | REQ-04, REQ-07, REQ-08, REQ-09 | — | `src/models/skill_efficacy_models.py` create | `SkillEfficacyResponse.model_validate(...)` accepts a hand-built fixture dict for a 2-node response including one unjoined-bucket entry and one filtered-by-`model_id` entry | command | `pytest tests/unit/test_skill_efficacy_service.py -k models -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-01 | gateflow | spec REQ-04, REQ-07, REQ-08, REQ-09 | N/A (unit-only task) | `pydantic-schemas.mdc` — models in `src/models/` only, `ConfigDict(extra="forbid")` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W1-02 | New tenant-scoped, node-grouped `stage_completed` aggregation query on `RunEventRepository` (joins `run_events`→`runs.tenant_id`, the same `run_id`-join pattern ADR-016 Option C already establishes for `stages`/`run_events`) | REQ-04, REQ-05, REQ-06, REQ-10 | TASK-W0-01, TASK-W0-02 (reads the outcome values CAP-01 now writes correctly) | `src/database/postgres/repository/run_store_repository.py` modify | Fixture with 2 tenants' stage rows on the same `workflow_node` returns only the requesting tenant's rows; a fixture wave with one `findings` re-entry then `success` yields a first-pass rate that excludes that node run from the numerator (REQ-05) | command | `pytest tests/unit/test_skill_efficacy_service.py -k tenant_scope -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-02 | gateflow | spec REQ-04, REQ-05, REQ-06, REQ-10 | N/A (unit-only task) | `repository-pattern.mdc` — query lives in repository, not business service | **ADR-016** (tenant `run_id`-join pattern reused, not a new decision — confirmed aligned in Technical-Review-INIT-GATEFLOW-015.md ADR traceability table) | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W1-03 | New org-wide `LearningRepository` query: per-`workflow_node` codify rate for items where `codify_hint.target == "skill"` joined on `codify_hint.ref == workflow_node`; items with `target` in `{SPEC, HARNESS, ENV}` returned as a flat, unjoined-from-node aggregate; a `ref` matching no known node returned in an explicit "unjoined" bucket | REQ-08, REQ-09 | — | `src/database/postgres/repository/learning_repository.py` modify | Fixture with 3 learning items (`target="skill"` matching a real node, `target="spec"`, `target="skill"` with an unmatched `ref`) returns exactly 1 per-node row, 1 flat org-wide row, and 1 unjoined-bucket row — zero items dropped or errored | command | `pytest tests/unit/test_skill_efficacy_service.py -k codify_rate -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-03 | gateflow | spec REQ-08, REQ-09 | N/A (unit-only task) | `repository-pattern.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W1-04 | `SkillEfficacyService` composing TASK-W1-02/03's repository queries; first-pass/findings-rate/retry-avg derivation rules; `model_id`/`prompt_revision` filter narrows rows; malformed/unknown filter value → named-clean empty response (not an error) | REQ-04, REQ-05, REQ-06, REQ-07 | TASK-W1-01, TASK-W1-02, TASK-W1-03 | `src/business_services/skill_efficacy_service.py` create | Hand-computed fixture wave (2 stages same node, one `findings` re-entry) yields first-pass rate and findings rate matching manual computation exactly; a filter value matching zero rows returns an empty per-node entry, not a 4xx/5xx | command | `pytest tests/unit/test_skill_efficacy_service.py -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-04 | gateflow | spec REQ-04, REQ-05, REQ-06, REQ-07 | N/A (unit-only task) | `dependency-injection.mdc` `@inject`; `repository-pattern.mdc` — business service calls repositories only | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W1-05 | Compute `outcome_vocabulary_available_since` as `MIN(created_at)` among `stage_completed` events with `outcome_type` present and not in `{success, failed}`; include in the response; report "not yet observed" (not a fabricated date) when zero such rows exist yet | REQ-03 (boundary-reporting half) | TASK-W1-04 | `src/business_services/skill_efficacy_service.py` modify (same file, additional method); `src/database/postgres/repository/run_store_repository.py` modify (supporting query) | Fixture with zero non-binary-outcome rows → field reports "not yet observed"; fixture with one `findings` row at `T` → field reports `T` exactly | command | `pytest tests/unit/test_skill_efficacy_service.py -k outcome_boundary -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-05 | gateflow | spec REQ-03 | N/A (unit-only task) | `fail-fast.mdc` — never silently treat old `None` as `success` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W1-06 | `GET /api/v1/metrics/skill-efficacy` route (`require_role(RoleType.TENANT_ADMIN)`, `auth.tenant_id` passed through, same pattern as `runs_routes.py`); DI wiring (`SkillEfficacyService` bound in `business_services_module.py`, added to `_BUSINESS_SERVICE_TYPES`, `get_skill_efficacy_service()` in `api/dependencies.py`) | REQ-04, REQ-10 | TASK-W1-04 | `src/api/v1/metrics_routes.py` modify; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify; `src/api/dependencies.py` modify | Authorized `tenant_admin` JWT → 200, response scoped to caller's `tenant_id`; missing/invalid JWT → 401 (existing `require_role` behavior, unchanged) | command | `pytest tests/unit/test_skill_efficacy_service.py -k route -v` (TestClient) | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-06 | gateflow | spec REQ-04, REQ-10 | `.venv/bin/python -m tests.verify.verify_skill_efficacy` | `http-api-conventions.mdc` — GET query filters, no body; `architecture.mdc` — service imported from its own module, not package `__init__.py` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W1-07 | `verify_skill_efficacy.py` live verify script; self-declares `prayog:covers:` marker | REQ-04, REQ-07, REQ-10 | TASK-W1-06 | `tests/verify/verify_skill_efficacy.py` create | Script asserts 401 without token, 200 with `tenant_admin` JWT, response shape includes `by_workflow_node`; file's first ~20 lines contain `prayog:covers: REQ-04, REQ-07, REQ-10` | command | `.venv/bin/python -m tests.verify.verify_skill_efficacy` (human-run) | exit 0; prints PASS for each assertion | `wave-accepted` on tip | gateflow | spec REQ-04, REQ-07, REQ-10 | `.venv/bin/python -m tests.verify.verify_skill_efficacy` | `testing-verify-flows.mdc` — opt-in script, not added to `verify_all.py` (matches `verify_checkpoint_status`/`verify_wave_map` precedent for new, non-core capabilities) | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/models/skill_efficacy_models.py` | create |
| FILE-W1-02 | `src/database/postgres/repository/run_store_repository.py` | modify |
| FILE-W1-03 | `src/database/postgres/repository/learning_repository.py` | modify |
| FILE-W1-04 | `src/business_services/skill_efficacy_service.py` | create |
| FILE-W1-05 | `src/api/v1/metrics_routes.py` | modify |
| FILE-W1-06 | `src/di/modules/business_services_module.py` | modify |
| FILE-W1-07 | `src/di/dependency_container.py` | modify |
| FILE-W1-08 | `src/api/dependencies.py` | modify |
| FILE-W1-09 | `tests/unit/test_skill_efficacy_service.py` | create |
| FILE-W1-10 | `tests/verify/verify_skill_efficacy.py` | create |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` (`pytest tests/unit/test_skill_efficacy_service.py -v`) | REQ-03 (boundary half), REQ-04–REQ-10 |
| TEST-W1-I | integration/contract | `pytest tests/unit/test_skill_efficacy_service.py -k tenant_scope -v` (one named boundary: real Postgres session against `RunEventRepository`'s new tenant-join query) | REQ-10 |
| TEST-W1-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_skill_efficacy` (human-run) | REQ-04, REQ-07, REQ-10 |

**Overlap check (P15, before declaring TEST-W1-L a new FILE):** `PYTHONPATH=prayog-skills python3 prayog-skills/scripts/verify_coverage_query.py tests/verify --capability skill-efficacy` and `--capability metrics` run against `tests/verify/` this session — zero existing artifacts carry a `prayog:covers:` marker at all for this capability; `verify_status_metrics.py` exists but covers the unrelated, unchanged `GET /metrics/runs` (no marker; legacy). No candidate to extend; `verify_skill_efficacy.py` is a new FILE, declared with the marker convention going forward.

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-03 boundary-reporting half | TEST-W1-U | N/A | N/A | N/A | |
| REQ-04 core response shape | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-05 first-pass rate rule | TEST-W1-U | N/A | N/A | N/A | Exact-match fixture |
| REQ-06 findings rate (pre+post checkpoint identical) | TEST-W1-U | N/A | N/A | N/A | |
| REQ-07 filter by model_id/prompt_revision | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-08 codify rate join | TEST-W1-U | N/A | N/A | N/A | |
| REQ-09 unjoined bucket | TEST-W1-U | N/A | N/A | N/A | |
| REQ-10 tenant scoping | TEST-W1-U | TEST-W1-I | TEST-W1-L | N/A | Integration = real Postgres session, one named boundary |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API up (`make run`); `SMOKE_TENANT_ADMIN_TOKEN` set; at least one prior wave-start run recorded for the smoke tenant |
| Safe test data | Reuses the existing `SMOKE_TENANT_ADMIN_TOKEN` tenant; no new synthetic identity needed (read-only endpoint) |
| Steps / command | `.venv/bin/python -m tests.verify.verify_skill_efficacy` |
| Expected observations | Script prints PASS for 401-no-token, 200-with-token, and response-shape assertions; exits 0 |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | None required — read-only endpoint, no durable state written |
| Stop conditions | Non-zero exit or unexpected 5xx → stop; do not proceed to W2 |

---

### Phase W2 — Factory Effectiveness API (CAP-03)

**GOAL-W2:** `GET /api/v1/metrics/factory-effectiveness` returns unattended Pass-1 rate, `stop_reason` breakdown, gate dwell time (inferred join, no new schema), and wave cycle time by lane (reading the `lane` payload field W0 wrote per ADR-017) — tenant-scoped, composed from `WorkflowEngine`/`PolicyEngine` node-type metadata and existing `run_events`/`runs` data.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | `FactoryEffectivenessResponse` + per-field models (unattended rate, `stop_reason` breakdown, dwell-time item incl. open/waiting state, lane cycle-time percentiles) | REQ-11, REQ-13, REQ-14, REQ-15, REQ-16 | — | `src/models/factory_effectiveness_models.py` create | Fixture dict with one open/waiting dwell entry (no fabricated zero/negative value) validates | command | `pytest tests/unit/test_factory_effectiveness_service.py -k models -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-01 | gateflow | spec REQ-11, REQ-13, REQ-14, REQ-15, REQ-16 | N/A (unit-only task) | `pydantic-schemas.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W2-02 | Unattended Pass-1 streak trace: between wave entrypoint and the first STOP whose resolved node `type == "human-checkpoint"` or `authorization == "explicit"`, no run event records a mid-chain PE-initiated dispatch; automated `external-action` hops (`authorization: automated`) do not break the streak — reads `WorkflowEngine`/`PolicyEngine` node-type/authorization metadata already exposed | REQ-11, REQ-12 | TASK-W2-01 | `src/business_services/factory_effectiveness_service.py` create | Fixture wave trace including one automated `external-action` hop (e.g. `wave-pr-action`) still reports unattended `true`; a fixture with a mid-chain manual dispatch reports unattended `false` | command | `pytest tests/unit/test_factory_effectiveness_service.py -k unattended -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-02 | gateflow | spec REQ-11, REQ-12 | N/A (unit-only task) | `dependency-injection.mdc` `@inject` | N/A — signals (`node_type`, `authorization`) already correctly persisted per feasibility Traceability matrix REQ-11–13 row; no additional persistence needed | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W2-03 | `stop_reason` breakdown: group `RUN_STOPPED`/`run_stopped` events by the raw `stop_reason` string, passed through as-is (no gateflow-side taxonomy) | REQ-13 | TASK-W2-01 | `src/database/postgres/repository/run_store_repository.py` modify | Fixture with 3 `run_stopped` events across 2 distinct `stop_reason` strings returns exactly 2 grouped counts, values byte-identical to the source strings | command | `pytest tests/unit/test_factory_effectiveness_service.py -k stop_reason -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-03 | gateflow | spec REQ-13 | N/A (unit-only task) | `repository-pattern.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W2-04 | New `RunRepository` method: for a `STOPPED` run, find the next-created run for the same `initiative_id`+`wave_id` after that run's `ended_at`; dwell time = elapsed time between the two; no continuation found → reported open/waiting, never a zero/negative/omitted value | REQ-14, REQ-15 | TASK-W2-01 | `src/database/postgres/repository/run_store_repository.py` modify | Fixture `STOPPED` run followed by a later run for the same initiative+wave → dwell time computed correctly; fixture `STOPPED` run with no later run → reported open/waiting, not `0`/negative/omitted | command | `pytest tests/unit/test_factory_effectiveness_service.py -k dwell_time -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-04 | gateflow | spec REQ-14, REQ-15 | N/A (unit-only task) | `repository-pattern.mdc`; `database-migrations.mdc` — no new column (A3 named risk accepted per spec) | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W2-05 | Wave cycle time (`wave_duration_ms`) as p50/p95, grouped by the `lane` value read from the `stage_completed`/`run_stopped` JSONB `payload` W0 wrote (ADR-017); a run with no `lane` in its payload is grouped under an explicit "unknown" bucket, never silently dropped | REQ-16 (read/report half) | TASK-W0-03, TASK-W2-01 | `src/business_services/factory_effectiveness_service.py` modify (same file, additional method); `src/database/postgres/repository/run_store_repository.py` modify | Fixture with 2 spec-lane and 1 implement-lane completed runs returns 2 percentile groups matching hand-computed p50/p95; a fixture run with no `lane` payload key appears in an explicit "unknown" bucket | command | `pytest tests/unit/test_factory_effectiveness_service.py -k lane_cycle_time -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-05 | gateflow | spec REQ-16 | N/A (unit-only task) | N/A | **ADR-017** (reads the JSONB payload field written in W0 — no new persistence this wave) | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W2-06 | `GET /api/v1/metrics/factory-effectiveness` route + DI wiring, same pattern as TASK-W1-06 | REQ-11, REQ-17 | TASK-W2-02, TASK-W2-03, TASK-W2-04, TASK-W2-05 | `src/api/v1/metrics_routes.py` modify; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify; `src/api/dependencies.py` modify | Authorized `tenant_admin` JWT → 200, tenant-scoped; missing/invalid JWT → 401 | command | `pytest tests/unit/test_factory_effectiveness_service.py -k route -v` (TestClient) | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-06 | gateflow | spec REQ-11, REQ-17 | `.venv/bin/python -m tests.verify.verify_factory_effectiveness` | `http-api-conventions.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W2-07 | `verify_factory_effectiveness.py` live verify script; self-declares `prayog:covers:` marker | REQ-11, REQ-13, REQ-17 | TASK-W2-06 | `tests/verify/verify_factory_effectiveness.py` create | Script asserts 401 without token, 200 with `tenant_admin` JWT, response shape includes `stop_reason_breakdown`; marker present in first ~20 lines | command | `.venv/bin/python -m tests.verify.verify_factory_effectiveness` (human-run) | exit 0 | `wave-accepted` on tip | gateflow | spec REQ-11, REQ-13, REQ-17 | `.venv/bin/python -m tests.verify.verify_factory_effectiveness` | `testing-verify-flows.mdc` — opt-in, not in `verify_all.py` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/models/factory_effectiveness_models.py` | create |
| FILE-W2-02 | `src/business_services/factory_effectiveness_service.py` | create |
| FILE-W2-03 | `src/database/postgres/repository/run_store_repository.py` | modify |
| FILE-W2-04 | `src/api/v1/metrics_routes.py` | modify |
| FILE-W2-05 | `src/di/modules/business_services_module.py` | modify |
| FILE-W2-06 | `src/di/dependency_container.py` | modify |
| FILE-W2-07 | `src/api/dependencies.py` | modify |
| FILE-W2-08 | `tests/unit/test_factory_effectiveness_service.py` | create |
| FILE-W2-09 | `tests/verify/verify_factory_effectiveness.py` | create |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` (`pytest tests/unit/test_factory_effectiveness_service.py -v`) | REQ-11–REQ-17 |
| TEST-W2-I | integration/contract | `pytest tests/unit/test_factory_effectiveness_service.py -k dwell_time -v` (one named boundary: real Postgres session against `RunRepository`'s new continuation-lookup query) | REQ-14 |
| TEST-W2-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_factory_effectiveness` (human-run) | REQ-11, REQ-13, REQ-17 |

**Overlap check (P15):** `PYTHONPATH=prayog-skills python3 prayog-skills/scripts/verify_coverage_query.py tests/verify --capability factory-effectiveness` — zero matches; no marked artifact exists for this capability. New FILE declared.

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-11 core response shape | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-12 unattended streak (automated hop excluded) | TEST-W2-U | N/A | N/A | N/A | Exact-match fixture |
| REQ-13 stop_reason breakdown | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-14 gate dwell time | TEST-W2-U | TEST-W2-I | N/A | N/A | |
| REQ-15 open/waiting no-continuation | TEST-W2-U | N/A | N/A | N/A | |
| REQ-16 lane cycle time (read half) | TEST-W2-U | N/A | N/A | N/A | Write half proven in W0 |
| REQ-17 tenant scoping | TEST-W2-U | N/A | TEST-W2-L | N/A | |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API up (`make run`); `SMOKE_TENANT_ADMIN_TOKEN` set; at least one prior run recorded for the smoke tenant |
| Safe test data | Reuses existing smoke tenant; no new synthetic identity needed |
| Steps / command | `.venv/bin/python -m tests.verify.verify_factory_effectiveness` |
| Expected observations | Script prints PASS for 401/200/shape assertions; exits 0 |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | None required — read-only endpoint |
| Stop conditions | Non-zero exit or unexpected 5xx → stop; do not proceed to W3 |

---

### Phase W3 — Delivery Scorecard API, gateflow-owned half (CAP-04)

**GOAL-W3:** `GET /api/v1/metrics/delivery-scorecard` returns rework rate (post-checkpoint-only), initiatives-closed-with-evidence, and factory coverage % — tenant-scoped, with the board/EPIC-ticket half of tenant scoping resolved via ADR-018 (reuse of `TenantRepository`'s existing org+repo→tenant lookup for tickets with no `run_id` link).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | `DeliveryScorecardResponse` model: `as_of` snapshot + all-time cumulative + trailing-90-day delta per metric; intent→merge lead time field absent (not fabricated) | REQ-18, REQ-22 | — | `src/models/delivery_scorecard_models.py` create | Fixture dict validates with all three framings present per metric and no `intent_to_merge_lead_time` key at all | command | `pytest tests/unit/test_delivery_scorecard_service.py -k models -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-01 | gateflow | spec REQ-18, REQ-22 | N/A (unit-only task) | `pydantic-schemas.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W3-02 | Rework rate query: a wave counts only when a `findings`/`blocked` re-entry into an earlier node occurs **strictly after** a `human-checkpoint` on that wave already recorded `outcome_type = pass`; pre-checkpoint self-loops excluded (already counted in CAP-02's findings rate) | REQ-19 | TASK-W3-01 | `src/database/postgres/repository/run_store_repository.py` modify | Fixture with a pre-checkpoint findings loop then a post-checkpoint-pass findings re-entry counts only the post-checkpoint occurrence | command | `pytest tests/unit/test_delivery_scorecard_service.py -k rework -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-02 | gateflow | spec REQ-19 | N/A (unit-only task) | `repository-pattern.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W3-03 | Initiatives-closed-with-evidence: count initiatives whose closure/completion readout exists via existing `ClosurePreviewService`/`CompletionReadoutService` composition, tenant-filtered by `RunRepository.list_runs(tenant_id=...)` | REQ-20 | TASK-W3-01 | `src/business_services/delivery_scorecard_service.py` create | Fixture with 2 initiatives (one with a persisted closure readout, one without) counts exactly 1 | command | `pytest tests/unit/test_delivery_scorecard_service.py -k closed_with_evidence -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-03 | gateflow | spec REQ-20 | N/A (unit-only task) | `repository-pattern.mdc`; `dependency-injection.mdc` `@inject` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W3-04 | Factory coverage %: EPIC-ticketed board initiatives with ≥1 Gateflow run, over total EPIC-ticketed initiatives visible on the board — tenant-scoped via a new `TenantRepository` read (reusing `find_workspace_credential_by_org_repo`'s org+repo→`tenant_id` lookup, extracting only `tenant_id`) for EPIC tickets that carry no `run_id` | REQ-21 | TASK-W3-01 | `src/database/postgres/repository/tenant_repository.py` modify; `src/business_services/delivery_scorecard_service.py` modify | Fixture with 3 EPIC tickets (2 with ≥1 run for the caller's tenant, 1 with zero runs but resolvable org+repo→tenant via `TenantRepository`) reports coverage matching the precise, scoped definition — never counting another tenant's tickets | command | `pytest tests/unit/test_delivery_scorecard_service.py -k factory_coverage -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-04 | gateflow | spec REQ-21 | N/A (unit-only task) | `repository-pattern.mdc` | **ADR-018** (Option A — reuse existing org+repo→`tenant_id` lookup as a read-time classification; no new schema, no new tenant-attribution write path) | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W3-05 | `GET /api/v1/metrics/delivery-scorecard` route + DI wiring, same pattern as TASK-W1-06/W2-06 | REQ-18, REQ-23 | TASK-W3-02, TASK-W3-03, TASK-W3-04 | `src/api/v1/metrics_routes.py` modify; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify; `src/api/dependencies.py` modify | Authorized `tenant_admin` JWT → 200, tenant-scoped; missing/invalid JWT → 401 | command | `pytest tests/unit/test_delivery_scorecard_service.py -k route -v` (TestClient) | exit 0 | Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-05 | gateflow | spec REQ-18, REQ-23 | `.venv/bin/python -m tests.verify.verify_delivery_scorecard` | `http-api-conventions.mdc` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |
| TASK-W3-06 | `verify_delivery_scorecard.py` live verify script; self-declares `prayog:covers:` marker | REQ-18, REQ-21, REQ-23 | TASK-W3-05 | `tests/verify/verify_delivery_scorecard.py` create | Script asserts 401 without token, 200 with `tenant_admin` JWT, response includes `as_of` + cumulative + 90-day-delta shape; marker present in first ~20 lines | command | `.venv/bin/python -m tests.verify.verify_delivery_scorecard` (human-run) | exit 0 | `wave-accepted` on tip | gateflow | spec REQ-18, REQ-21, REQ-23 | `.venv/bin/python -m tests.verify.verify_delivery_scorecard` | `testing-verify-flows.mdc` — opt-in, not in `verify_all.py` | N/A | `chore/INIT-GATEFLOW-015-spec-gateflow` |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/models/delivery_scorecard_models.py` | create |
| FILE-W3-02 | `src/business_services/delivery_scorecard_service.py` | create |
| FILE-W3-03 | `src/database/postgres/repository/run_store_repository.py` | modify |
| FILE-W3-04 | `src/database/postgres/repository/tenant_repository.py` | modify |
| FILE-W3-05 | `src/api/v1/metrics_routes.py` | modify |
| FILE-W3-06 | `src/di/modules/business_services_module.py` | modify |
| FILE-W3-07 | `src/di/dependency_container.py` | modify |
| FILE-W3-08 | `src/api/dependencies.py` | modify |
| FILE-W3-09 | `tests/unit/test_delivery_scorecard_service.py` | create |
| FILE-W3-10 | `tests/verify/verify_delivery_scorecard.py` | create |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` (`pytest tests/unit/test_delivery_scorecard_service.py -v`) | REQ-18–REQ-23 |
| TEST-W3-I | integration/contract | `pytest tests/unit/test_delivery_scorecard_service.py -k factory_coverage -v` (one named boundary: real Postgres session against `TenantRepository`'s org+repo lookup) | REQ-21 |
| TEST-W3-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_delivery_scorecard` (human-run) | REQ-18, REQ-21, REQ-23 |

**Overlap check (P15):** `PYTHONPATH=prayog-skills python3 prayog-skills/scripts/verify_coverage_query.py tests/verify --capability delivery-scorecard` — zero matches; no marked artifact exists for this capability. New FILE declared.

#### Verification Coverage (W3)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-18 core response shape (as_of + cumulative + delta) | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-19 rework post-checkpoint-only | TEST-W3-U | N/A | N/A | N/A | |
| REQ-20 closed-with-evidence | TEST-W3-U | N/A | N/A | N/A | |
| REQ-21 factory coverage % | TEST-W3-U | TEST-W3-I | TEST-W3-L | N/A | Integration = real Postgres session, one named boundary |
| REQ-22 intent→merge absent | TEST-W3-U | N/A | N/A | N/A | Inspection-provable — field never present |
| REQ-23 tenant scoping | TEST-W3-U | N/A | TEST-W3-L | N/A | |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API up (`make run`); `SMOKE_TENANT_ADMIN_TOKEN` set; at least one closed initiative and one EPIC ticket recorded for the smoke tenant/board |
| Safe test data | Reuses existing smoke tenant + board fixtures; no new synthetic identity needed |
| Steps / command | `.venv/bin/python -m tests.verify.verify_delivery_scorecard` |
| Expected observations | Script prints PASS for 401/200/shape assertions; exits 0 |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | None required — read-only endpoint |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | W0 (CAP-01 outcome vocabulary) must ship before W1 can compute correct first-pass/findings rates | W1 |
| DEP-02 | W0's `lane` payload write (TASK-W0-03, ADR-017) must ship before W2's lane cycle-time read (TASK-W2-05) | W2 |
| DEP-03 | W1's tenant-scoped stage aggregation pattern (TASK-W1-02) establishes the query shape W2 (TASK-W2-02/03/04) and W3 (TASK-W3-02) extend | W2, W3 |
| DEP-04 | ADR-017 and ADR-018 must be `Accepted` before their respective TASKs (W0-03, W2-05, W3-04) start — **satisfied**, both Accepted at `4505eabf5e09a1409065d8067c26bd0608e505b6` | W0, W2, W3 |
| DEP-05 | `prayog-skills` `workflow.yaml` node types (`human-checkpoint`, `external-action`, `authorization`) are read-only consumed by W2 (TASK-W2-02); no pin change requested (CTR-01) | W2 |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Inferred dwell-time join (`initiative_id`+`wave_id`+chronology, TASK-W2-04) misattributes a continuation run if two waves for the same initiative genuinely overlap | Named accepted risk (spec A3, `Source: User-confirmed`); revisit with an explicit link column if it proves unreliable in practice |
| RISK-02 | `lane` persisted only in JSONB `payload` (ADR-017 Option C) is not indexed — query cost grows with `run_events` table size at larger scale | Named in ADR-017 Revisit triggers; schema promotion (Option A) is the accepted follow-up if this fires |
| RISK-03 | ADR-018's org+repo→`tenant_id` read-time lookup inherits ADR-016's own named risk: a repo shared across >1 tenant breaks org+repo as a stable key | Named in both ADR-016 and ADR-018 Revisit triggers; both mechanisms would need reconciling together if this fires — not this INIT's problem to solve preemptively |
| RISK-04 | `codify_hint.ref` values drift from `workflow_node` ids over time (a `prayog-skills` rename) | Best-effort join; unmatched refs report as unjoined rather than erroring (REQ-09, TASK-W1-03) |
| RISK-05 | Historical `stage_completed` events recorded before W0 ships have no `findings`/`stopped`/`blocked` outcome | REQ-03's boundary-reporting (TASK-W1-05) makes this explicit in every response rather than silently backfilled |
| RISK-06 (operational, feasibility-carried) | Q-1 (exact JSON/OpenAPI field names) remains open at plan time | Non-blocking per feasibility/TDD; field names are an implementation-time choice within each TASK's file scope — do not block coding start |

---

## 5. Out of scope

- `gateflow-ops` screens/charts rendering these APIs (deferred consumer)
- Intent→merge lead time (REQ-22 explicitly reports it absent/`unavailable`)
- Token/cost metrics
- A precomputed rollup/worker job — live aggregation only, per spec D7
- A new `continues_run_id` schema column — inferred join accepted (A3)
- Per-developer attribution
- Any change to `GET /metrics/runs`'s existing shape or values
- `prayog-skills` pin/workflow redesign
- Backfilling historical `stage_completed` events

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Create per-initiative as-built detail | `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-015.md` | Record W0–W3 capability/code/test/verify detail — **KEEP**, written once per initiative |
| Update as-built index row | `docs/specification/as-built/implementation-status.md` | Add one capability-matrix section for INIT-GATEFLOW-015 (overwrite-in-place convention; never append a growing shared table) |
| Ensure live-verify coverage marker | `tests/verify/verify_skill_efficacy.py`, `tests/verify/verify_factory_effectiveness.py`, `tests/verify/verify_delivery_scorecard.py` | Each self-declares `prayog:covers: REQ-...` per `live-verify-coverage-contract.md` — do not edit `tests/README.md` for this |
| Update `tests/README.md` feature map (navigation only, not coverage SSOT) | `tests/README.md` | Add W0–W3 rows pointing to the three new verify scripts and updated unit test files, consistent with every prior initiative's feature-map entries |

> **ADR lifecycle** — ADR-017 and ADR-018 are already `Accepted` (technical review + PE acceptance, prior to this plan). No ADR promotion tasks in this plan.

---

## 7. Plan check summary

| Check | Status | Notes |
|-------|--------|-------|
| P1 | PASS | Every REQ-01…23 appears in §1; every wave's TASKs cite them via **Implements** |
| P2 | PASS | Every in-scope REQ has ≥1 TASK; every TASK Implements ≥1 REQ-*; no shadow `REQ-W*` |
| P3 | PASS | Every TASK has FILE paths, or explicit "none — inspection-only" (TASK-W0-04) |
| P4 | PASS | Every TASK has artifact/change, observable exit criteria, proving command/review, expected result, evidence location |
| P5 | PASS | unit/integration/smoke layers explicit per wave; integration names one boundary (real Postgres session) each time, never "the whole stack"; every wave changing product code (W1–W3) has ≥1 unit-layer Verification Coverage row |
| P6 | PASS | No task exceeds spec REQ-01…23 scope |
| P7 | PASS | Feasibility FF-01/FF-02 resolved via Accepted ADR-017/018 before this plan (§0); RISK-01…06 carry forward accepted operational risks with owner + default |
| P8 | PASS | §3 Dependencies states wave order (W0→W1→W2→W3) and cross-wave TASK dependencies |
| P9 | PASS | §6 lists per-initiative as-built detail + index row update, same PR as code tasks; not satisfied by editing `tests/README.md` alone (that row is navigation, not the coverage marker — the marker lives in the verify script itself) |
| P10 | PASS | Source freshness/command-contract table populated; each wave's Live-verification intent states environment class, prerequisites, safe test data, cleanup, stop conditions |
| P11 | PASS | MDC notes column populated per TASK citing `pydantic-schemas.mdc`, `repository-pattern.mdc`, `dependency-injection.mdc`, `http-api-conventions.mdc`, `fail-fast.mdc`, `database-migrations.mdc`, `architecture.mdc`, `testing-verify-flows.mdc` where relevant; no discrepancy found |
| P12 | PASS | TASK-W0-03/W2-05 cite **ADR-017** (Accepted); TASK-W3-04 cites **ADR-018** (Accepted); both files exist under `docs/specification/adr/`, `Status: Accepted`, linked in §0 with digests; no ADR promotion task added |
| P13 | PASS | §0 present; technical review path populated; PE sign-off `[x] complete — 2026-08-12`; both cited Accepted ADRs re-linted with `--verify-lint-evidence --require-sources` and source parity (REQ sentence + feasibility finding text) — PASS on both, command log recorded in §0 |
| P14 | PASS | §9 present; wave ids `W0`…`W3` match plan waves exactly; every TASK row has `codebase`, `spec_path`, `verify_command` (or N/A with reason), **Implements**; each wave has `tasks[]` + body task table |
| P15 | PASS | W0: `applicable: false` with reason (no product surface). W1/W2/W3: each declares exactly one new `live_verify_dir` FILE; overlap check run and recorded before each declaration (zero existing markers found for any of the three capabilities); `verify_command` is the live script, never `make test` |
| P16 | PASS | §9 validated with `scripts/workmanifest_contract.py` — see command log below |

**P16 validation command log:**

```text
$ PYTHONPATH=prayog-skills .venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md --base-path .
WorkManifest contract passed.
```

(First run failed 1 check — `TASK-W0-04`'s docs-only exit criteria did not contain the literal "docs-only" marker the validator requires for an empty `files: []` task; fixed by rewording the criteria text, no substance change. Second run passed clean, including the `--base-path .` live-verify coverage cross-check.)

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch alongside spec, feasibility,
> and TDD. Do **not** commit inside this skill. Label remains **`spec-pending`**
> until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-015-spec-gateflow  (Draft PR #228)
PR title: "[INIT-GATEFLOW-015] Spec — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics (gateflow)"
PR body:  link meta PRD PR #40; paste §1 Requirements table + wave goals summary

Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-15

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + TDD + Accepted ADRs (adr-017, adr-018) + this plan on current head
  [ ] §0 PE sign-off on TDD marked complete — required, no N/A path (technical review always exists)
  [ ] Wave order and dependencies make sense (W0→W1→W2→W3)
  [ ] Done-when / exit criteria are observable and testable (P4)
  [ ] Verification Coverage maps every criterion to a layer (P5)
  [ ] WorkManifest YAML (§9) passes workmanifest-contract-pass (P16) — prayog/v1
  [ ] P1–P16 checks all pass (including P15 co-ship when surface changes)

After spec-lgtm + Approve + merge — `/create-board-tickets` from §9 (post-merge only):
  Create one GitHub Issue per wave (W0, W1, W2, W3) using §9 titles, bodies, depends_on
  Search for existing initiative/wave issues first; create only missing issues
  Then Pass-1: /pre-implement → /loop-spec → wave-acceptance (human runs co-shipped script)
  Then Pass-2: /learning-extract → /ground-spec → wave-signoff (merge only)
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 all PASS; sources CURRENT; Accepted TDD/ADR-017/ADR-018 confirmed with re-verified lint evidence; plan ready for coding-readiness |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/228 |
| Spec PR head SHA | `e0e1d53c201d1d387079fecf8914ae0252cfeadd` (pre-publish of this plan — will advance once `/commit-workspace` runs) |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md` |
| Forge readiness | fill `handoff.forge` for `/commit-workspace` — do not commit inside this skill |
| Blocking items | none |

Provision labels when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

PE actions (all on **exact current head**):

1. Remove `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale`; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body (below)
3. Mark Draft PR **Ready for review**
4. Authorize merge (human or policy); then **`/create-board-tickets`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-015
spec_pr_head_sha: {SHA at time of PE Approve — fill after /commit-workspace}
meta_pr_head_sha: 63ebf8009a8d01721c432de0a92cb21649eb7613
impact_map_revision: 1
prd_digest: sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666
scope_digest: sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72
plan_digest: sha256:{hex — fill after /commit-workspace, digest of this file at that head}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-015-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-015.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md
```

Never infer approval from `spec-lgtm` alone — Approve, label, and artifact
digests must match the same head SHA.

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

---

## 9. WorkManifest seed

> **Primary:** `/create-board-tickets` creates **one GitHub Issue per wave** (`W0`, `W1`, `W2`, `W3`)
> from this section after spec merge. Wave bodies list every `TASK-*` with exit
> criteria for human traceability.

```yaml
# Generated by /spec-implementation-plan — 2026-08-12
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-015

metadata:
  title: INIT-GATEFLOW-015 — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics
  summary: |
    Fix a lossy stage-outcome persistence gap (CAP-01 prerequisite), then ship
    three additive, tenant-scoped, live-aggregated read APIs turning existing
    RunStore/checkpoint/learning data into decision-grade rates: Skill/Spec
    Efficacy, Factory Effectiveness, and a Delivery Scorecard. GET /metrics/runs
    is unchanged.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-015
  parent: EPIC
  labels:
    - initiative:INIT-GATEFLOW-015

epic:
  id: EPIC
  repo: gateflow
  title: "[feature] INIT-GATEFLOW-015 — Skill efficacy, factory effectiveness, and delivery-copilot productivity metrics"
  codebase: gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
  verify_command: N/A — no single command covers all waves; see per-wave verify_command
  body: |
    ## Objective

    Persist the full stage-outcome vocabulary, then ship three tenant-scoped
    metrics read APIs (skill efficacy, factory effectiveness, delivery
    scorecard) composed from existing RunStore/checkpoint/learning data.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Persist full RunOutcomeType vocabulary + lane payload (CAP-01 prerequisite) |
    | W1 | Skill/Spec Efficacy API |
    | W2 | Factory Effectiveness API |
    | W3 | Delivery Scorecard API (gateflow-owned half) |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md

work:
  # ── Wave W0 ──────────────────────────────────────────────────────────────
  - id: W0
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-015 W0] Persist full RunOutcomeType vocabulary + lane payload"
    depends_on: []
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    verify_command: "N/A — no product surface this wave (P15 N/A)"
    tasks:
      - id: TASK-W0-01
        implements: [REQ-01, REQ-02]
        depends_on: []
        files:
          - path: src/business_services/metrics_emitter.py
            action: modify
        exit:
          criteria:
            - "record_stage_duration maps all 6 RunOutcomeType values 1:1; existing success/failed cases unchanged"
          proof:
            kind: command
            command: "pytest tests/unit/test_metrics_emitter.py -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-01, REQ-02]
        depends_on: [TASK-W0-01]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "stage_outcome derives from handoff.outcome on agent success; FAILED unchanged on agent failure; success/failed regression fixtures pass"
          proof:
            kind: command
            command: "pytest tests/unit/test_run_orchestrator.py -k stage_outcome_vocabulary -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-16]
        depends_on: [TASK-W0-02]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "run_events.payload['lane'] present on stage_completed and run_stopped events when job payload carries lane"
          proof:
            kind: command
            command: "pytest tests/unit/test_run_orchestrator.py -k lane_payload -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-03]
        depends_on: [TASK-W0-01, TASK-W0-02, TASK-W0-03]
        files: []
        exit:
          criteria:
            - "docs-only / inspection task — W0 diff contains zero backfill/UPDATE statement against existing run_events/stages rows"
          proof:
            kind: review
            review: "PE reviews the W0 diff for absence of backfill/migration statements"
            expected: "reviewer confirms zero backfill statements"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W0.md § TASK-W0-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "Internal outcome-persistence fix; no new/changed HTTP route or public contract this wave (P15 N/A)"
    body: |
      ## Wave goal

      Persist the full RunOutcomeType vocabulary on stage_completed/stages and
      the run_stopped/stage_completed lane payload (ADR-017); no new route.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-01, REQ-02 | — | 6-value outcome mapping + regression | command |
      | TASK-W0-02 | REQ-01, REQ-02 | TASK-W0-01 | stage_outcome from handoff.outcome | command |
      | TASK-W0-03 | REQ-16 | TASK-W0-02 | lane persisted in JSONB payload | command |
      | TASK-W0-04 | REQ-03 | TASK-W0-01, TASK-W0-02, TASK-W0-03 | zero backfill statements | review |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-015-gateflow.md

  # ── Wave W1 ──────────────────────────────────────────────────────────────
  - id: W1
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-015 W1] Skill/Spec Efficacy API"
    depends_on:
      - W0
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    verify_command: ".venv/bin/python -m tests.verify.verify_skill_efficacy"
    tasks:
      - id: TASK-W1-01
        implements: [REQ-04, REQ-07, REQ-08, REQ-09]
        depends_on: []
        files:
          - path: src/models/skill_efficacy_models.py
            action: create
        exit:
          criteria:
            - "SkillEfficacyResponse validates a 2-node fixture with a filtered entry and an unjoined bucket"
          proof:
            kind: command
            command: "pytest tests/unit/test_skill_efficacy_service.py -k models -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-04, REQ-05, REQ-06, REQ-10]
        depends_on: []
        files:
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
        exit:
          criteria:
            - "Tenant-scoped node aggregation query returns only the requesting tenant's rows"
          proof:
            kind: command
            command: "pytest tests/unit/test_skill_efficacy_service.py -k tenant_scope -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-08, REQ-09]
        depends_on: []
        files:
          - path: src/database/postgres/repository/learning_repository.py
            action: modify
        exit:
          criteria:
            - "Org-wide codify-rate query returns per-node, flat, and unjoined rows correctly for a 3-item fixture"
          proof:
            kind: command
            command: "pytest tests/unit/test_skill_efficacy_service.py -k codify_rate -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-04, REQ-05, REQ-06, REQ-07]
        depends_on: [TASK-W1-01, TASK-W1-02, TASK-W1-03]
        files:
          - path: src/business_services/skill_efficacy_service.py
            action: create
        exit:
          criteria:
            - "First-pass/findings rate match hand-computed fixture exactly; malformed filter -> named-clean empty, not error"
          proof:
            kind: command
            command: "pytest tests/unit/test_skill_efficacy_service.py -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-03]
        depends_on: [TASK-W1-04]
        files:
          - path: src/business_services/skill_efficacy_service.py
            action: modify
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
        exit:
          criteria:
            - "outcome_vocabulary_available_since reports 'not yet observed' with zero rows, exact timestamp otherwise"
          proof:
            kind: command
            command: "pytest tests/unit/test_skill_efficacy_service.py -k outcome_boundary -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-05"
      - id: TASK-W1-06
        implements: [REQ-04, REQ-10]
        depends_on: [TASK-W1-04]
        files:
          - path: src/api/v1/metrics_routes.py
            action: modify
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
          - path: src/api/dependencies.py
            action: modify
        exit:
          criteria:
            - "GET /api/v1/metrics/skill-efficacy: 200 tenant-scoped with valid JWT; 401 without"
          proof:
            kind: command
            command: "pytest tests/unit/test_skill_efficacy_service.py -k route -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W1.md § TASK-W1-06"
      - id: TASK-W1-07
        implements: [REQ-04, REQ-07, REQ-10]
        depends_on: [TASK-W1-06]
        files:
          - path: tests/verify/verify_skill_efficacy.py
            action: create
        exit:
          criteria:
            - "Live script asserts 401/200/shape; marker prayog:covers: present"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_skill_efficacy"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: ".venv/bin/python -m tests.verify.verify_skill_efficacy"
        covers: [REQ-04, REQ-07, REQ-10]
        prerequisites:
          - "API up (make run); SMOKE_TENANT_ADMIN_TOKEN set; ≥1 prior run recorded for the smoke tenant"
        safe_test_data:
          - "Reuses existing smoke tenant — no new synthetic identity needed (read-only endpoint)"
        steps:
          - "Run verify_skill_efficacy.py against local stack"
        expected_observations:
          - "Script exits 0; prints PASS for 401/200/shape assertions"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "None required — read-only endpoint, no durable state written"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx -> stop; do not proceed to W2"
    body: |
      ## Wave goal

      GET /api/v1/metrics/skill-efficacy — tenant-scoped, per-node first-pass
      rate, findings rate, retry avg, learning codify rate.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-04, REQ-07, REQ-08, REQ-09 | — | models validate | command |
      | TASK-W1-02 | REQ-04, REQ-05, REQ-06, REQ-10 | — | tenant-scoped aggregation | command |
      | TASK-W1-03 | REQ-08, REQ-09 | — | org-wide codify query | command |
      | TASK-W1-04 | REQ-04, REQ-05, REQ-06, REQ-07 | TASK-W1-01, TASK-W1-02, TASK-W1-03 | service composition | command |
      | TASK-W1-05 | REQ-03 | TASK-W1-04 | outcome boundary | command |
      | TASK-W1-06 | REQ-04, REQ-10 | TASK-W1-04 | route + DI | command |
      | TASK-W1-07 | REQ-04, REQ-07, REQ-10 | TASK-W1-06 | live verify | command |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-015-gateflow.md

  # ── Wave W2 ──────────────────────────────────────────────────────────────
  - id: W2
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-015 W2] Factory Effectiveness API"
    depends_on:
      - W1
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    verify_command: ".venv/bin/python -m tests.verify.verify_factory_effectiveness"
    tasks:
      - id: TASK-W2-01
        implements: [REQ-11, REQ-13, REQ-14, REQ-15, REQ-16]
        depends_on: []
        files:
          - path: src/models/factory_effectiveness_models.py
            action: create
        exit:
          criteria:
            - "Models validate a fixture with an open/waiting dwell entry (no fabricated zero/negative)"
          proof:
            kind: command
            command: "pytest tests/unit/test_factory_effectiveness_service.py -k models -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-11, REQ-12]
        depends_on: [TASK-W2-01]
        files:
          - path: src/business_services/factory_effectiveness_service.py
            action: create
        exit:
          criteria:
            - "Automated external-action hop does not break unattended streak; manual dispatch does"
          proof:
            kind: command
            command: "pytest tests/unit/test_factory_effectiveness_service.py -k unattended -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-13]
        depends_on: [TASK-W2-01]
        files:
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
        exit:
          criteria:
            - "stop_reason breakdown groups by raw string, byte-identical to source"
          proof:
            kind: command
            command: "pytest tests/unit/test_factory_effectiveness_service.py -k stop_reason -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-03"
      - id: TASK-W2-04
        implements: [REQ-14, REQ-15]
        depends_on: [TASK-W2-01]
        files:
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
        exit:
          criteria:
            - "Dwell time computed correctly with continuation; open/waiting reported without one"
          proof:
            kind: command
            command: "pytest tests/unit/test_factory_effectiveness_service.py -k dwell_time -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-04"
      - id: TASK-W2-05
        implements: [REQ-16]
        depends_on: [TASK-W2-01]
        files:
          - path: src/business_services/factory_effectiveness_service.py
            action: modify
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
        exit:
          criteria:
            - "p50/p95 wave cycle time grouped by lane matches hand-computed fixture; missing lane -> explicit unknown bucket"
          proof:
            kind: command
            command: "pytest tests/unit/test_factory_effectiveness_service.py -k lane_cycle_time -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-05"
      - id: TASK-W2-06
        implements: [REQ-11, REQ-17]
        depends_on: [TASK-W2-02, TASK-W2-03, TASK-W2-04, TASK-W2-05]
        files:
          - path: src/api/v1/metrics_routes.py
            action: modify
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
          - path: src/api/dependencies.py
            action: modify
        exit:
          criteria:
            - "GET /api/v1/metrics/factory-effectiveness: 200 tenant-scoped with valid JWT; 401 without"
          proof:
            kind: command
            command: "pytest tests/unit/test_factory_effectiveness_service.py -k route -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W2.md § TASK-W2-06"
      - id: TASK-W2-07
        implements: [REQ-11, REQ-13, REQ-17]
        depends_on: [TASK-W2-06]
        files:
          - path: tests/verify/verify_factory_effectiveness.py
            action: create
        exit:
          criteria:
            - "Live script asserts 401/200/shape; marker prayog:covers: present"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_factory_effectiveness"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: ".venv/bin/python -m tests.verify.verify_factory_effectiveness"
        covers: [REQ-11, REQ-13, REQ-17]
        prerequisites:
          - "API up (make run); SMOKE_TENANT_ADMIN_TOKEN set; ≥1 prior run recorded"
        safe_test_data:
          - "Reuses existing smoke tenant"
        steps:
          - "Run verify_factory_effectiveness.py against local stack"
        expected_observations:
          - "Script exits 0; prints PASS for 401/200/shape assertions"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "None required — read-only endpoint"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx -> stop; do not proceed to W3"
    body: |
      ## Wave goal

      GET /api/v1/metrics/factory-effectiveness — unattended Pass-1 rate,
      stop_reason breakdown, gate dwell time, wave cycle time by lane.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-11, REQ-13, REQ-14, REQ-15, REQ-16 | — | models validate | command |
      | TASK-W2-02 | REQ-11, REQ-12 | TASK-W2-01 | unattended streak | command |
      | TASK-W2-03 | REQ-13 | TASK-W2-01 | stop_reason breakdown | command |
      | TASK-W2-04 | REQ-14, REQ-15 | TASK-W2-01 | dwell time | command |
      | TASK-W2-05 | REQ-16 | TASK-W2-01 | lane cycle time | command |
      | TASK-W2-06 | REQ-11, REQ-17 | TASK-W2-02, TASK-W2-03, TASK-W2-04, TASK-W2-05 | route + DI | command |
      | TASK-W2-07 | REQ-11, REQ-13, REQ-17 | TASK-W2-06 | live verify | command |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-015-gateflow.md

  # ── Wave W3 ──────────────────────────────────────────────────────────────
  - id: W3
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-015 W3] Delivery Scorecard API (gateflow-owned half)"
    depends_on:
      - W2
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-015-gateflow.md
    verify_command: ".venv/bin/python -m tests.verify.verify_delivery_scorecard"
    tasks:
      - id: TASK-W3-01
        implements: [REQ-18, REQ-22]
        depends_on: []
        files:
          - path: src/models/delivery_scorecard_models.py
            action: create
        exit:
          criteria:
            - "Models validate all-three-framings shape; intent_to_merge_lead_time key never present"
          proof:
            kind: command
            command: "pytest tests/unit/test_delivery_scorecard_service.py -k models -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-01"
      - id: TASK-W3-02
        implements: [REQ-19]
        depends_on: [TASK-W3-01]
        files:
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
        exit:
          criteria:
            - "Only post-checkpoint-pass findings/blocked re-entry counted as rework"
          proof:
            kind: command
            command: "pytest tests/unit/test_delivery_scorecard_service.py -k rework -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-02"
      - id: TASK-W3-03
        implements: [REQ-20]
        depends_on: [TASK-W3-01]
        files:
          - path: src/business_services/delivery_scorecard_service.py
            action: create
        exit:
          criteria:
            - "Count matches initiatives with a persisted closure/completion readout"
          proof:
            kind: command
            command: "pytest tests/unit/test_delivery_scorecard_service.py -k closed_with_evidence -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-03"
      - id: TASK-W3-04
        implements: [REQ-21]
        depends_on: [TASK-W3-01]
        files:
          - path: src/database/postgres/repository/tenant_repository.py
            action: modify
          - path: src/business_services/delivery_scorecard_service.py
            action: modify
        exit:
          criteria:
            - "Coverage % matches precise scoped definition; never counts another tenant's tickets"
          proof:
            kind: command
            command: "pytest tests/unit/test_delivery_scorecard_service.py -k factory_coverage -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-04"
      - id: TASK-W3-05
        implements: [REQ-18, REQ-23]
        depends_on: [TASK-W3-02, TASK-W3-03, TASK-W3-04]
        files:
          - path: src/api/v1/metrics_routes.py
            action: modify
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
          - path: src/api/dependencies.py
            action: modify
        exit:
          criteria:
            - "GET /api/v1/metrics/delivery-scorecard: 200 tenant-scoped with valid JWT; 401 without"
          proof:
            kind: command
            command: "pytest tests/unit/test_delivery_scorecard_service.py -k route -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-015-W3.md § TASK-W3-05"
      - id: TASK-W3-06
        implements: [REQ-18, REQ-21, REQ-23]
        depends_on: [TASK-W3-05]
        files:
          - path: tests/verify/verify_delivery_scorecard.py
            action: create
        exit:
          criteria:
            - "Live script asserts 401/200/shape; marker prayog:covers: present"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_delivery_scorecard"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: ".venv/bin/python -m tests.verify.verify_delivery_scorecard"
        covers: [REQ-18, REQ-21, REQ-23]
        prerequisites:
          - "API up (make run); SMOKE_TENANT_ADMIN_TOKEN set; ≥1 closed initiative and ≥1 EPIC ticket for the smoke tenant/board"
        safe_test_data:
          - "Reuses existing smoke tenant + board fixtures"
        steps:
          - "Run verify_delivery_scorecard.py against local stack"
        expected_observations:
          - "Script exits 0; prints PASS for 401/200/shape assertions"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "None required — read-only endpoint"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx -> stop"
    body: |
      ## Wave goal

      GET /api/v1/metrics/delivery-scorecard — rework rate, initiatives-closed-
      with-evidence, factory coverage % (gateflow-owned half).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W3-01 | REQ-18, REQ-22 | — | models validate | command |
      | TASK-W3-02 | REQ-19 | TASK-W3-01 | rework post-checkpoint-only | command |
      | TASK-W3-03 | REQ-20 | TASK-W3-01 | closed-with-evidence | command |
      | TASK-W3-04 | REQ-21 | TASK-W3-01 | factory coverage % | command |
      | TASK-W3-05 | REQ-18, REQ-23 | TASK-W3-02, TASK-W3-03, TASK-W3-04 | route + DI | command |
      | TASK-W3-06 | REQ-18, REQ-21, REQ-23 | TASK-W3-05 | live verify | command |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-015-gateflow.md

  # (one work: entry per wave — NOT one per TASK row; tasks[] + verification + body table required)
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md
    # digest omitted here — plan_digest is minted at PE Approve attestation
    # time (§10), not at draft-authoring time; see artifact-write-contract.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-015
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/228"
    spec_pr_head: "e0e1d53c201d1d387079fecf8914ae0252cfeadd"
    waves: [W0, W1, W2, W3]
    req_count: 23
    adr_required_count: 2
    adr_files:
      - docs/specification/adr/adr-017-wave-lane-attribution-for-metrics.md
      - docs/specification/adr/adr-018-cap04-board-ticket-tenant-scoping.md
    p_checks: pass
    p16_workmanifest_contract: pass
    source_freshness: CURRENT
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
```
