# Implementation status — INIT-GATEFLOW-015

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-015 |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Updated | 2026-08-12 |

## Wave status

| Wave | Goal | Status | Evidence |
|------|------|--------|----------|
| W0 | Persist full RunOutcomeType vocabulary + lane payload | **human_approved** | Board [#230](https://github.com/drivestream-lab/gateflow/issues/230); Draft PR [#234](https://github.com/drivestream-lab/gateflow/pull/234) accept `0d9bbc7` / Pass-2 `c3a0720` label `wave-accepted`; Ground-Report W0 **pass**; Learning-Extract W0 `items: []` |
| W1 | Skill/Spec Efficacy API | **human_approved** | Board [#231](https://github.com/drivestream-lab/gateflow/issues/231); Draft PR [#235](https://github.com/drivestream-lab/gateflow/pull/235) @ `202c4fa` label `wave-accepted`; Ground-Report W1 **pass**; Learning-Extract W1 `items: []` |
| W2 | Factory Effectiveness API | **human_approved** | Board [#232](https://github.com/drivestream-lab/gateflow/issues/232); Draft PR [#236](https://github.com/drivestream-lab/gateflow/pull/236) accept `293b012` / Pass-2 `e105d1f` label `wave-accepted`; Ground-Report W2 **pass**; Learning-Extract W2 `items: []` |
| W3 | Delivery Scorecard API | **human_approved** | Board [#233](https://github.com/drivestream-lab/gateflow/issues/233); Draft PR [#237](https://github.com/drivestream-lab/gateflow/pull/237) accept `fa78255` / Pass-2 `1914818` label `wave-accepted`; Ground-Report W3 **pass**; Learning-Extract W3 `items: []` |

## W1 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Skill efficacy response models | REQ-04,07,08,09 | `skill_efficacy_models.py` | -k models | — | `extra="forbid"` |
| Tenant-scoped stage_completed | REQ-04,05,06,10 | `RunEventRepository.list_stage_completed_for_tenant` | -k tenant_scope | verify | ADR-016 join |
| Learning codify rates | REQ-08,09 | `LearningRepository.aggregate_codify_rates` | -k codify_rate | — | unjoined bucket |
| Service composition + filters | REQ-04–07 | `SkillEfficacyService` | rates + filter | verify | named-clean empty |
| Outcome vocabulary boundary | REQ-03 | `min_extended_outcome_created_at` | -k outcome_boundary | — | not yet observed |
| Route + DI | REQ-04,10 | `metrics_routes` + DI | -k route | verify | TENANT_ADMIN |

## W0 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Full outcome vocabulary on stage_completed | REQ-01, REQ-02 | `metrics_emitter.record_stage_duration` | `test_metrics_emitter` | N/A (P15) | 6-value map; unset→None |
| stage_outcome from handoff.outcome | REQ-01, REQ-02 | `run_orchestrator._run_orchestrated_stage` | `test_run_orchestrator` (-k stage_outcome_vocabulary) | N/A | Agent failure stays FAILED |
| lane in JSONB payload | REQ-16 (write) | orchestrator + emitter `lane=` | -k lane_payload | N/A | ADR-017 Option C |
| No backfill | REQ-03 (half) | inspection | TASK-W0-04 review | N/A | Forward-write only |
