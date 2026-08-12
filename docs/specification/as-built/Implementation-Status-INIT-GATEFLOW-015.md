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
| W1 | Skill/Spec Efficacy API | not started | — |
| W2 | Factory Effectiveness API | not started | — |
| W3 | Delivery Scorecard API | not started | — |

## W0 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Full outcome vocabulary on stage_completed | REQ-01, REQ-02 | `metrics_emitter.record_stage_duration` | `test_metrics_emitter` | N/A (P15) | 6-value map; unset→None |
| stage_outcome from handoff.outcome | REQ-01, REQ-02 | `run_orchestrator._run_orchestrated_stage` | `test_run_orchestrator` (-k stage_outcome_vocabulary) | N/A | Agent failure stays FAILED |
| lane in JSONB payload | REQ-16 (write) | orchestrator + emitter `lane=` | -k lane_payload | N/A | ADR-017 Option C |
| No backfill | REQ-03 (half) | inspection | TASK-W0-04 review | N/A | Forward-write only |
