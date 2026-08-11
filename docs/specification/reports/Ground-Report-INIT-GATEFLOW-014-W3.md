# Ground report — INIT-GATEFLOW-014 W3

| Field | Value |
|-------|-------|
| Wave | W3 — Dead-door deletion + wipe cutover |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Initiative | INIT-GATEFLOW-014 |
| Date | 2026-08-11 |
| Wave head (exact) | Accept tip `52b969d45cc6de8fab73840d1877b3eefd350def` (`wave-accepted`); Pass-2 reviewed head = tip after Learning/Ground publish (pending `/commit-workspace`) |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/224 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-13 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-34, REQ-35, REQ-46 (WorkManifest TASK-W3-01…02 `implements`) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | Wave-Execution / `make test` | Pass-1: **540** passed; re-confirmed targeted unit at Pass-2 gather (`test_tenant_routes` + `test_programme_wipe_service` → 8 passed) |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #224 tip `52b969d` (2026-08-11 @nikd10x) | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile `ground_command` is N/A. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-34 | Open (unauthenticated) tenant register is removed | `programme_token.py` / `tenant_token.py` deleted; `tenant_routes.py` has no `POST ""` register; `test_tenant_routes` (-k register) asserts 404/405 with platform_admin JWT; `verify_dead_doors_deleted.py` | pass |
| REQ-35 | 012/013 lab tenants/shared-secret rows wiped at cutover | `ProgrammeWipeService.wipe_programme` deletes programme + tenant + identities + non-ACTIVE runs; `POST /api/v1/programmes/{id}/wipe`; `verify_wipe_cutover.py` | pass |
| REQ-46 | Wipe while any run is in flight rejected; 0 wipe | `find_active_run_for_tenant` → `ConflictError` 409 `reason=active_run`; unit `test_wipe_refuses_when_active_run_present`; live script inserts ACTIVE then asserts 409 | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Structural removal of programme-token / tenant-bearer deps | ADR-014 Consequences | pass — modules deleted; zero `src/api` imports remain |
| Wipe mid-run fail-closed named reason | `fail-fast.mdc` | pass — `ConflictError` / 409 |
| ORM confined to repositories | `repository-pattern.mdc` | pass — delete helpers on repos only |
| Business service DI + lifecycle | `dependency-injection.mdc` | pass — `ProgrammeWipeService` bound + `_BUSINESS_SERVICE_TYPES` |
| Wipe mutation on admin routes | `http-api-conventions.mdc` | pass — `POST …/wipe` with `ProgrammeWipeResult` from `src/models/` |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| JWT product edge; old doors refused (modules still present) | Ground-Report-W2 | yes — W3 deleted the leftover modules |
| Role + programme scope / `require_role(PLATFORM_ADMIN)` | Ground-Report-W2 | yes — wipe route uses platform_admin |
| Tenant-attributed runs / ACTIVE for wipe guard | Ground-Report-W2 | yes — `find_active_run_for_tenant` on `runs.tenant_id` |
| Programme store (id → tenant_id) | Ground-Report-W1 | yes — wipe loads programme then child tenant |

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
| Dead doors removed | deleted `programme_token` / `tenant_token`; `tenant_routes` | `POST /api/v1/tenants` absent | any caller | 404/405 (with JWT) or middleware 401 (no auth) | Open register not restorable without new route; modules gone from tree | W4 teaching prove-absence |
| Programme wipe | `ProgrammeWipeService` + `programme_admin_routes` | `POST /api/v1/programmes/{programme_id}/wipe` | platform_admin JWT + programme id | `ProgrammeWipeResult` or 409/404 | ACTIVE run → 409 `active_run`, 0 wipe; idle clears programme+tenant+secrets | W4 rewrite verify surfaces |
| ACTIVE-run wipe guard | `RunRepository.find_active_run_for_tenant` | wipe precondition | tenant_id | RunModel or none | Wipe never proceeds while ACTIVE exists for tenant | W4+ |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/224
- Accept tip (`wave-accepted`): `52b969d45cc6de8fab73840d1877b3eefd350def`
- Reviewed head SHA (Pass-2 tip): pending `/commit-workspace` publish of Learning-Extract + Ground-Report (record SHA after publish)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W3.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W3.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-014-W3.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W3 `human_approved` from wave-acceptance
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above (after Pass-2 publish)
- [ ] Confirm human_approved already recorded at wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W4 `/pre-implement` after Pass-2 docs land on tip

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W3 assigned REQs only (REQ-34, REQ-35, REQ-46) |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-014 structural deletion |
| G6 | PASS — domain MDC (fail-fast, repository, DI, http-api) |
| G7 | PASS — consumed W2 contracts + produced W3 contracts |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; commit via follow-on commit-workspace only |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W3.md
  blockers: []
  signals:
    wave: W3
    contracts_produced: 3
    assigned_reqs:
      - REQ-34
      - REQ-35
      - REQ-46
    accept_tip: 52b969d45cc6de8fab73840d1877b3eefd350def
    pr_url: https://github.com/drivestream-lab/gateflow/pull/224
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/218"
```
