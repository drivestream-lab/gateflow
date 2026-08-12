# Ground report — INIT-GATEFLOW-015 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Skill/Spec Efficacy API |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Initiative | INIT-GATEFLOW-015 |
| Date | 2026-08-12 |
| Wave head (exact) | Accept tip `202c4fad7ca8de56efc94223f5f4a5031e15b317` (`wave-accepted`); Pass-2 docs tip `1d59073c59e88511b0aaac1a0394a40deab739ab` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/235 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-14 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-03 (boundary half), REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 568 passed; `test_skill_efficacy_service` 10 passed |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #235 tip `202c4fa` | Human approved at wave-acceptance; live verify human-owned |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-03 | Boundary reported; pre-fix `None` not treated as success | `min_extended_outcome_created_at`; `outcome_vocabulary_available_since`; `_aggregate_nodes` excludes `outcome_type is None`; `-k outcome_boundary` / `-k none_outcome` | pass (boundary half; W0 wrote no-backfill half) |
| REQ-04 | `GET /metrics/skill-efficacy` run count, rates, tenant-scoped, retention | `SkillEfficacyService.get_skill_efficacy`; route `GET /api/v1/metrics/skill-efficacy`; models; unit + `verify_skill_efficacy` FILE | pass |
| REQ-05 | First-pass = success with zero prior findings on node within run | `_count_first_pass_successes`; fixture findings→success → first_pass_rate 0.0 | pass |
| REQ-06 | Findings rate counts all findings regardless of checkpoint position | findings_rate = findings_count / stage_count over outcome-aware rows; no checkpoint filter | pass |
| REQ-07 | Filter/group by `model_id` / `prompt_revision` | Query params + `_apply_filters`; unknown filter → empty `by_workflow_node`; verify filter echo | pass |
| REQ-08 | Codify rate per node only for `target=="skill"`; others flat org-wide | `LearningRepository.aggregate_codify_rates`; `-k codify_rate` | pass |
| REQ-09 | Unmatched skill `ref` → unjoined bucket | same aggregate → `codify_unjoined`; 3-item fixture | pass |
| REQ-10 | Tenant-scoped; no cross-tenant leak | `list_stage_completed_for_tenant` join `runs.tenant_id`; route passes `auth.tenant_id`; `-k tenant_scope` / `-k route` | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Tenant scoping via `runs.tenant_id` join (no new column) | ADR-016 | pass |
| Models in `src/models/` only; `extra="forbid"` | `pydantic-schemas.mdc` | pass |
| Aggregation in repository; service composes | `repository-pattern.mdc` | pass |
| Never silently treat historical `None` as success | `fail-fast.mdc` / REQ-03 | pass |
| GET query filters only; TENANT_ADMIN | `http-api-conventions.mdc` | pass |
| Opt-in verify script; not in `verify_all` | `testing-verify-flows.mdc` | pass |
| New `SkillEfficacyService` (not methods on MetricsEmitter) | plan module decision | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Full stage outcome vocabulary on `stage_completed` | Ground-Report-W0 | yes — rates read `outcome_type` |
| No historical backfill | Ground-Report-W0 | yes — `None` excluded from outcome-aware rates |
| Tenant `run_id`-join scoping | ADR-016 + as-built | yes — `run_events`→`runs.tenant_id` |
| Existing metrics route auth pattern | `metrics_routes` `/metrics/runs` | yes — mirrored for skill-efficacy |
| `WorkflowEngine.known_node_ids()` for join keys | CTR-01 / pin consume | yes — unjoined when ref ∉ known |
| Lane on events | Ground-Report-W0 | N/A for W1 rates — consumed in W2 |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| — | — | Learning-Extract items empty — no open L-* |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Skill-efficacy HTTP API | `metrics_routes` / `SkillEfficacyService` | `GET /api/v1/metrics/skill-efficacy` | TENANT_ADMIN JWT; optional `model_id`/`prompt_revision` query | `SkillEfficacyResponse` with `by_workflow_node`, codify buckets, boundary field | Tenant-scoped; unknown filter → empty nodes (200); no 4xx on empty data | W2 mirrors route/DI pattern |
| Tenant-scoped stage_completed rows | `RunEventRepository` | `list_stage_completed_for_tenant` | tenant_id + since (retention cutoff) | list of stage_completed efficacy rows (node, outcome, model_id, prompt_revision, created_at) | Join via `runs.tenant_id` (ADR-016); never returns other tenants | W2 extends same join for factory aggregates |
| Outcome vocabulary boundary | `RunEventRepository` / service | `min_extended_outcome_created_at` | tenant_id | ISO timestamp or `"not yet observed"` | Extended = outcome present and not in `{success, failed}` | W2/W3 may reuse boundary reporting |
| Outcome-aware rate rules | `SkillEfficacyService._aggregate_nodes` | composition | efficacy rows | first_pass_rate, findings_rate, retry_avg, run_count, stage_count | Exclude `outcome_type is None`; first-pass excludes prior findings on same run+node | W2 does not recompute these rates |
| Learning codify aggregate | `LearningRepository.aggregate_codify_rates` | org-wide query + known node set | `known_workflow_nodes` from pin | per-node (skill), flat org-wide (non-skill), unjoined skill refs | Unmatched refs never dropped/errored | W2 does not consume; available for dashboards |
| Metrics DI pattern | BusinessServicesModule + `_BUSINESS_SERVICE_TYPES` + `api/dependencies` | `get_skill_efficacy_service` | N/A | singleton service | Same wiring shape for W2 factory-effectiveness | W2 |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/235
- Accept tip (`wave-accepted`): `202c4fad7ca8de56efc94223f5f4a5031e15b317`
- Reviewed head SHA (Pass-2 tip after Learning/Ground publish): `1d59073c59e88511b0aaac1a0394a40deab739ab`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W1.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-015-W1.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-015-W1.md`
- Optional/legacy Live-Verify path: n/a (script exists; evidence is human accept + unit)
- As-built: W1 `human_approved` from wave-acceptance (recorded in index + `Implementation-Status-INIT-GATEFLOW-015.md`)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — after Pass-2 docs land on tip via `commit_workspace`; merge/publish only at human `wave-signoff`

## G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W1 assigned REQs only |
| G2 Ground command / evidence | PASS — ground_command N/A; manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-03–REQ-10 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-016 reuse; ADR-017 N/A for W1 coding path |
| G6 MDC boundaries | PASS — pydantic / repo / http / fail-fast / testing |
| G7 Contracts consumed / produced | PASS — 6 contracts produced for W2 |
| G8 Learning citations | PASS — empty items cited |
| G9 Stable GF-* | PASS — none open |
| G10 Complete handoff | PASS — envelope below; merge package prepared |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W1.md
  blockers: []
  signals:
    wave: W1
    contracts_produced: 6
    assigned_reqs:
      - REQ-03
      - REQ-04
      - REQ-05
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-09
      - REQ-10
    accept_tip: 202c4fad7ca8de56efc94223f5f4a5031e15b317
    pr_url: https://github.com/drivestream-lab/gateflow/pull/235
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/231"
```
