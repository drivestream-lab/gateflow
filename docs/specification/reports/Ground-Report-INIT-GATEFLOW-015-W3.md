# Ground report — INIT-GATEFLOW-015 W3

| Field | Value |
|-------|-------|
| Wave | W3 — Delivery Scorecard API |
| Spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Initiative | INIT-GATEFLOW-015 |
| Date | 2026-08-12 |
| Wave head (exact) | Accept tip `fa78255b7802e3e276940f0d8c3121ef4fe39e7f` (`wave-accepted`); Pass-2 docs tip TBD after `commit_workspace` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/237 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-14 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-18, REQ-19, REQ-20, REQ-21, REQ-22, REQ-23 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 582 passed; `test_delivery_scorecard_service` 6 passed |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #237 tip `fa78255` | Human approved at wave-acceptance; live verify human-owned |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-18 | `GET /metrics/delivery-scorecard` as_of + cumulative + 90d delta, tenant-scoped | `DeliveryScorecardService.get_delivery_scorecard`; route; models; unit + `verify_delivery_scorecard` FILE | pass |
| REQ-19 | Rework only post-checkpoint findings/blocked re-entry | `compute_rework_rate`; `-k rework` | pass |
| REQ-20 | Initiatives closed-with-evidence via closure/completion composition | `_initiative_has_closure_evidence` + `count_closed_with_evidence`; `-k closed_with_evidence` | pass |
| REQ-21 | Factory coverage % EPIC+run scoped; ADR-018 org+repo | `resolve_tenant_id_for_org_repo`; `compute_factory_coverage_pct`; `-k factory_coverage` | pass |
| REQ-22 | Intent→merge lead time absent | models `extra="forbid"`; dump has no `intent_to_merge_lead_time`; `-k models` + verify | pass |
| REQ-23 | Tenant-scoped | route passes `auth.tenant_id`; EPIC filter via ADR-018; `-k route` | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Tenant scoping via `runs.tenant_id` + ADR-018 org+repo read | ADR-016, ADR-018 | pass |
| No fabricated intent→merge field | fail-fast.mdc / REQ-22 | pass |
| Pre-checkpoint findings not counted as rework | REQ-19 | pass |
| Factory coverage not presented as company-wide | REQ-21 | pass |
| Models in `src/models/`; DI `@inject`; repo aggregates | MDC set | pass |
| Opt-in verify; not in `verify_all` | testing-verify-flows.mdc | pass |
| No new board-ticket `tenant_id` column | ADR-018 Option A | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Metrics route + DI pattern | Ground-Report-W2 | yes — mirrored for delivery-scorecard |
| Tenant-scoped event/run join | Ground-Report-W1/W2 | yes — scorecard stage rows + list_runs |
| Full outcome vocabulary | Ground-Report-W0 | yes — findings/blocked + success(=pass) |
| Pin human-checkpoint nodes | WorkflowEngine / CTR-01 | yes — rework checkpoint set |
| Closure / completion services | source | yes — composed for REQ-20 |
| Org+repo → tenant lookup | ADR-018 + TenantRepository | yes — `resolve_tenant_id_for_org_repo` |

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
| Delivery-scorecard HTTP API | `metrics_routes` / `DeliveryScorecardService` | `GET /api/v1/metrics/delivery-scorecard` | TENANT_ADMIN JWT | `DeliveryScorecardResponse` (as_of, three metrics × cumulative+90d) | Tenant-scoped; no intent→merge field | Initiative complete — consumers (e.g. deferred gateflow-ops) |
| Rework post-checkpoint rate | `compute_rework_rate` | scorecard stage rows + checkpoint node ids | float rate | Pre-checkpoint loops excluded | Closure consumers |
| Closed-with-evidence count | closure/completion composition | tenant runs → per-initiative evidence | count framing | Not chat claims | Closure consumers |
| Factory coverage % | ADR-018 resolve + EPIC list | scoped EPIC refs + initiatives with runs | pct framing | Never counts other tenants' EPICs | Closure consumers |
| Org+repo tenant resolve | `TenantRepository.resolve_tenant_id_for_org_repo` | org, repo | tenant_id or None; ambiguous → ValueError | Read-time only | Future board-scoped reads |
| CAP-02/03/04 metrics triad complete | skill-efficacy + factory-effectiveness + delivery-scorecard | three GET routes | TENANT_ADMIN | Consistent DI/route pattern | Initiative closure |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/237
- Accept tip (`wave-accepted`): `fa78255b7802e3e276940f0d8c3121ef4fe39e7f`
- Reviewed head SHA (Pass-2 tip after Learning/Ground publish): *stamp after commit_workspace*
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W3.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-015-W3.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-015-W3.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W3 `human_approved` from wave-acceptance (recorded in index + `Implementation-Status-INIT-GATEFLOW-015.md`)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete (final wave / initiative consumers)
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — after Pass-2 docs land on tip via `commit_workspace`; merge/publish only at human `wave-signoff`. Final implement wave for INIT-GATEFLOW-015 — after merge, initiative-closure path applies.

## G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W3 assigned REQs only |
| G2 Ground command / evidence | PASS — ground_command N/A; manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-18–REQ-23 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-016, ADR-018 |
| G6 MDC boundaries | PASS |
| G7 Contracts consumed / produced | PASS — 6 contracts produced (final wave) |
| G8 Learning citations | PASS — empty items cited |
| G9 Stable GF-* | PASS — none open |
| G10 Complete handoff | PASS — envelope below; merge package prepared |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W3.md
  blockers: []
  signals:
    wave: W3
    contracts_produced: 6
    assigned_reqs:
      - REQ-18
      - REQ-19
      - REQ-20
      - REQ-21
      - REQ-22
      - REQ-23
    accept_tip: fa78255b7802e3e276940f0d8c3121ef4fe39e7f
    pr_url: https://github.com/drivestream-lab/gateflow/pull/237
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/233"
```
