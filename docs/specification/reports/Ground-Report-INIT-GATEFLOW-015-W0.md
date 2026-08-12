# Ground report — INIT-GATEFLOW-015 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Persist full RunOutcomeType vocabulary + lane payload |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Initiative | INIT-GATEFLOW-015 |
| Date | 2026-08-12 |
| Wave head (exact) | Accept tip `0d9bbc7dd03e2fb247645df82915ac8594f348cd` (`wave-accepted`); Pass-2 docs tip `c3a072052763e5304f2cd49d741e6f8ad3faebc4` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/234 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-14 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-01, REQ-02, REQ-03 (no-backfill half), REQ-16 (write half) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 558 passed; this session outcome/lane subset 19 passed |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #234 tip `0d9bbc7` | Human approved at wave-acceptance; P15 N/A |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Full `RunOutcomeType` on `stage_completed` + `stages.outcome_type` | `MetricsEmitter.record_stage_duration` 6-value map; `RunOrchestrator._run_orchestrated_stage` + `_stage_outcome_from_handoff_outcome`; `test_metrics_emitter` vocabulary; `test_run_orchestrator` `-k stage_outcome_vocabulary` | pass |
| REQ-02 | Existing success/failed recording unchanged | success/failed regression cases in `test_metrics_emitter`; agent-failure path stays FAILED and ignores handoff | pass |
| REQ-03 | Pre-fix events not backfilled; no silent default | TASK-W0-04 inspection: zero `UPDATE`/`backfill`/`ALTER` in W0 write path; forward-write only (boundary reporting half = W1) | pass (W0 half) |
| REQ-16 | Lane grouping signal persisted for later cycle-time read | Job `lane` → `stage_completed` payload via `record_stage_duration(lane=…)` and `run_stopped` payload in `_finalize_run`; `-k lane_payload` unit; ADR-017 Option C (no schema column) | pass (write half; read = W2) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Persist `lane` in existing JSONB payload — no new column / Alembic | ADR-017 | pass |
| Reuse `RunOutcomeType` enum — no second vocabulary | `pydantic-schemas.mdc` | pass |
| No silent collapse of real outcomes to `None` when handoff declares them | `fail-fast.mdc` | pass — `pass`→SUCCESS; unknown handoff outcome raises |
| Walker continuation still gated on agent binary success | REQ-01 + control-plane | pass — `stage_summary["success"]` = agent_ok |
| No new HTTP route / `GET /metrics/runs` unchanged | plan P15 N/A / REQ-02 | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| `RunOutcomeType` enum (`success/failed/stopped/blocked/findings/pending`) | `src/models/run_store_types.py` | yes — reused |
| `MetricsEmitter.record_stage_duration` stage_completed write | prior metrics as-built | yes — widened mapping + optional lane |
| `RunOrchestrator._run_orchestrated_stage` / `_finalize_run` event writes | prior orchestrator as-built | yes — outcome from handoff; lane on finalize |
| Job payload may carry `lane` | wave-start → job payload | yes — read only when non-empty |

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
| Stage outcome vocabulary | `MetricsEmitter` / `RunOrchestrator` | `record_stage_duration`; `_run_orchestrated_stage` | outcome string; on agent success: handoff.outcome (`pass`/`success`/`failed`/`findings`/`stopped`/`blocked`/`pending`) | `stages.outcome_type` + `stage_completed.outcome_type` full enum; metrics payload `outcome` | Agent failure → FAILED regardless of handoff; unset/unknown emitter string → None (caller silence); unrecognized handoff outcome → raise | W1 (rates / boundary reporting) |
| Lane on stage_completed | `MetricsEmitter.record_stage_duration` | `lane=` keyword | optional non-empty lane string from job payload | JSONB payload includes `lane` only when present | Never fabricates `"unknown"` | W2 (cycle-time by lane) |
| Lane on run_stopped | `RunOrchestrator._finalize_run` | finalize with `job_payload` | job payload optional `lane` | `run_stopped` JSONB payload may include `lane` | Absent when job omits lane; STOP path passes `job_payload` | W2 |
| No historical backfill | W0 write path | N/A (inspection) | N/A | N/A | Zero UPDATE/backfill of pre-existing `run_events`/`stages` rows | W1 excludes pre-fix None from outcome-aware rates |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/234
- Accept tip (`wave-accepted`): `0d9bbc7dd03e2fb247645df82915ac8594f348cd`
- Reviewed head SHA (Pass-2 tip after Learning/Ground publish): `c3a072052763e5304f2cd49d741e6f8ad3faebc4`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W0.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-015-W0.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-015-W0.md`
- Optional/legacy Live-Verify path: n/a (P15 N/A)
- As-built: W0 `human_approved` from wave-acceptance (recorded in index + `Implementation-Status-INIT-GATEFLOW-015.md`)
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
| G1 Wave scope | PASS — W0 assigned REQs only |
| G2 Ground command / evidence | PASS — ground_command N/A; manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-01,02,03,16 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-017 |
| G6 MDC boundaries | PASS — pydantic-schemas / fail-fast / no migration |
| G7 Contracts consumed / produced | PASS — 4 contracts produced for W1/W2 |
| G8 Learning citations | PASS — empty items cited |
| G9 Stable GF-* | PASS — none open |
| G10 Complete handoff | PASS — envelope below; merge package prepared |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W0.md
  blockers: []
  signals:
    wave: W0
    contracts_produced: 4
    assigned_reqs:
      - REQ-01
      - REQ-02
      - REQ-03
      - REQ-16
    accept_tip: 0d9bbc7dd03e2fb247645df82915ac8594f348cd
    pr_url: https://github.com/drivestream-lab/gateflow/pull/234
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/230"
```
