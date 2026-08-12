# Ground report — INIT-GATEFLOW-015 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Factory Effectiveness API |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Initiative | INIT-GATEFLOW-015 |
| Date | 2026-08-12 |
| Wave head (exact) | Accept tip `293b01243a97ee00b7e7513a11d36d867b262940` (`wave-accepted`); Pass-2 docs tip TBD after `commit_workspace` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/236 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-14 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16 (read half), REQ-17 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 576 passed; `test_factory_effectiveness_service` 8 passed |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #236 tip `293b012` | Human approved at wave-acceptance; live verify human-owned |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-11 | `GET /metrics/factory-effectiveness` unattended rate, tenant-scoped, retention | `FactoryEffectivenessService.get_factory_effectiveness`; route; models; unit + `verify_factory_effectiveness` FILE | pass |
| REQ-12 | Unattended streak; automated external-action hops do not break | `evaluate_unattended_streak`; `-k unattended` (automated hop true; PE after forge_pending false) | pass |
| REQ-13 | `stop_reason` breakdown — raw passthrough | `list_run_stopped_for_tenant` + `aggregate_stop_reasons`; `-k stop_reason` | pass |
| REQ-14 | Gate dwell via initiative+wave continuation | `find_next_run_for_initiative_wave`; `_build_dwell_items` COMPUTED; `-k dwell_time` | pass |
| REQ-15 | No continuation → open/waiting; never fabricated zero | `DwellStateType.OPEN_WAITING` with `dwell_ms=None`; models fixture | pass |
| REQ-16 | Cycle time p50/p95 by lane (JSONB read) | `aggregate_lane_cycle_times`; missing lane → `unknown`; `-k lane_cycle_time`; ADR-017 | pass (read half; write = W0) |
| REQ-17 | Tenant-scoped | runs/events join `runs.tenant_id`; route passes `auth.tenant_id`; `-k route` | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Tenant scoping via `runs.tenant_id` join | ADR-016 | pass |
| Lane from JSONB payload — no new column | ADR-017 | pass |
| No fabricated zero/negative dwell for open/waiting | fail-fast.mdc / REQ-15 | pass |
| `stop_reason` no gateflow taxonomy | REQ-13 | pass |
| Automated hops excluded from PE-break | REQ-12 | pass |
| Models in `src/models/`; repo aggregates; DI `@inject` | MDC set | pass |
| Opt-in verify; not in `verify_all` | testing-verify-flows.mdc | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Tenant-scoped event join pattern | Ground-Report-W1 | yes — extended for run_stopped / event traces |
| Metrics route + DI pattern | Ground-Report-W1 | yes — mirrored for factory-effectiveness |
| Lane on stage_completed / run_stopped | Ground-Report-W0 | yes — cycle-time read; unknown bucket on read side |
| Pin node type / authorization | WorkflowEngine + CTR-01 | yes — unattended streak |
| Runs initiative/wave/duration | RunSchema | yes — dwell + cycle-time |

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
| Factory-effectiveness HTTP API | `metrics_routes` / `FactoryEffectivenessService` | `GET /api/v1/metrics/factory-effectiveness` | TENANT_ADMIN JWT | `FactoryEffectivenessResponse` (rate, stop_reason, dwell, lane cycle-time) | Tenant-scoped; empty/zero honest | W3 mirrors route/DI |
| Unattended Pass-1 streak | `evaluate_unattended_streak` | ordered event trace + pin node metadata | True/False/None (no gate) | Automated forge does not break; skill after forge_pending breaks | W3 may cite rate |
| stop_reason breakdown | `aggregate_stop_reasons` | run_stopped payloads | counts by raw string | Byte-identical passthrough | W3 scorecard may reuse |
| Gate dwell inference | `find_next_run_for_initiative_wave` | STOPPED run + initiative/wave + after | COMPUTED dwell_ms or OPEN_WAITING | Never fabricates zero for open | W3 |
| Lane cycle-time read | `aggregate_lane_cycle_times` | wave_duration_ms + payload.lane | p50/p95 by lane; missing → `unknown` | ADR-017 read-only | W3 |
| Metrics DI pattern (CAP-03) | module + container + dependencies | `get_factory_effectiveness_service` | singleton | Same shape for delivery-scorecard | W3 |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/236
- Accept tip (`wave-accepted`): `293b01243a97ee00b7e7513a11d36d867b262940`
- Reviewed head SHA (Pass-2 tip after Learning/Ground publish): 
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W2.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-015-W2.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-015-W2.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W2 `human_approved` from wave-acceptance (recorded in index + `Implementation-Status-INIT-GATEFLOW-015.md`)
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
| G1 Wave scope | PASS — W2 assigned REQs only |
| G2 Ground command / evidence | PASS — ground_command N/A; manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-11–REQ-17 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-016, ADR-017 |
| G6 MDC boundaries | PASS |
| G7 Contracts consumed / produced | PASS — 6 contracts produced for W3 |
| G8 Learning citations | PASS — empty items cited |
| G9 Stable GF-* | PASS — none open |
| G10 Complete handoff | PASS — envelope below; merge package prepared |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W2.md
  blockers: []
  signals:
    wave: W2
    contracts_produced: 6
    assigned_reqs:
      - REQ-11
      - REQ-12
      - REQ-13
      - REQ-14
      - REQ-15
      - REQ-16
      - REQ-17
    accept_tip: 293b01243a97ee00b7e7513a11d36d867b262940
    pr_url: https://github.com/drivestream-lab/gateflow/pull/236
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/232"
```
