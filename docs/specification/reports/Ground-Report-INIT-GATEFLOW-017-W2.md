# Ground report — INIT-GATEFLOW-017 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Delete 014 doors + wipe collaborator |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Initiative | INIT-GATEFLOW-017 |
| Date | 2026-08-14 |
| Wave head (exact) | Accept tip `a40ab9cd0a2b5ed8fc8e54f5510366ebf54b8965` (`wave-accepted`); Pass-2 tip `77e2c49fc89c7c37de701179680bef44b7cea68f` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/251 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-18 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-10, REQ-15, REQ-20, REQ-21, REQ-27 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 622 passed; `make check` exit 0 |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR [#251](https://github.com/drivestream-lab/gateflow/pull/251) tip `a40ab9c` | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-10 | Detach/wipe: identity remains | `ProgrammeWipeService` deletes memberships only; `test_wipe_clears_rows_when_idle` asserts membership delete; `verify_wipe_cutover` lists identity after wipe | pass |
| REQ-15 | In-flight wave not cancelled by membership change | Wipe still 409 `active_run` when ACTIVE run present; `test_wipe_refuses_when_active_run_present`; `verify_wipe_cutover` mid-run probe | pass |
| REQ-20 | Historic `POST /tenants/{id}/users` gone | Route removed from `tenant_routes.py`; `test_historic_users_route_gone_with_jwt`; `verify_dead_doors_deleted` 012 probe | pass |
| REQ-21 | 014 create+bind door deleted | `attach_tenant_admin` removed; no `POST …/tenant-admins` in `src/`; `test_attach_tenant_admin_method_removed`; grant path unchanged; `verify_dead_doors_deleted` 014 probe | pass |
| REQ-27 | Programme onboard APIs unchanged | `validate_then_create` / catalogue refresh still mounted; `verify_programme_onboarding` still creates programme; helper no longer attaches | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| No remint attach door; grant does not mint | ADR-019 Option B | pass |
| Postgres is sole durable store | ADR-001 | pass |
| JWT-only product edge | ADR-014 | pass |
| Wipe talks to repos only | `repository-pattern.mdc` | pass |
| Deleted doors are absent (404/405), not query refusals | `http-api-conventions.mdc` | pass |
| Extend live scripts; no unit-as-live | `testing-verify-flows.mdc` | pass |
| ACTIVE 409 unchanged; no silent identity delete | `fail-fast.mdc` | pass |
| Grant routes kept when attach removed | Pre-Implement W2 must-not | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Enter identity | Ground-Report-017-W1 | yes — helper `enter_grant_login` uses `POST /api/v1/identities` |
| Grant / detach (no mint) | Ground-Report-017-W1 | yes — helper grants; attach door deleted; `/grants` remains |
| Membership list/delete | Ground-Report-017-W1 | yes — wipe iterates `list_by_programme` + `delete_membership` |
| Directory actor | Ground-Report-017-W1 | yes — enter/grant still `require_directory_admin` |
| Identity read shape (no password) | Ground-Report-017-W1 | yes — unchanged |
| 014 attach door | Ground-Report-017-W1 | yes — **deleted this wave** (was mounted) |
| Wipe vs identity | Ground-Report-017-W0 / W1 | yes — explicit membership delete; identity rows remain |
| Login snapshot `{grants: []}` | Ground-Report-017-W0 | yes — not populated (W3) |

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
| 014 attach door gone | `programme_admin_routes` | former `POST /api/v1/programmes/{id}/tenant-admins` | — | 404 or 405 | No `attach_tenant_admin` method; no remint attach | W3 must not call attach |
| Historic users door gone | `tenant_routes` | former `POST /api/v1/tenants/{id}/users` | — | 404 or 405 | No invite / handle-attach path | W3 |
| Wipe collaborator | `ProgrammeWipeService.wipe_programme` | wipe | programme id | wipe result | Memberships for that programme gone; identity row remains; ACTIVE run 409 `active_run` | W3 isolation / unknown programme after wipe |
| Provision helper | `enter_grant_login` / `provision_programme_tenant_admin` | enter → grant → login | programme id + email + password | identity JWT + tenant id + programme id | No attach; no remint on grant; tenant id from programme create/GET, not JWT claim; return tuple unchanged | W3 live scripts reuse helper |
| Grant path (unchanged) | `IdentityDirectoryService` / `POST\|DELETE /programmes/{id}/grants` | grant / detach | programme id + identity id | membership pair | Still the only grant door; idempotent; no mint | W3 enter-programme uses membership |
| Onboard / catalogue (unchanged) | `ProgrammeService.validate_then_create` | create / refresh / list | onboard body | programme + catalogue | REQ-27 — APIs unchanged except identity/grant | W3 delivery after enter |
| Login snapshot | `POST /api/auth/login` | login | email + password | token + `grants` array | `grants` still empty | W3 populate / enter-programme |
| Directory enter | `POST /api/v1/identities` | enter_identity | name, email, password | IdentityRead | Still the enter door; no password on output | W3 |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge
> readiness for publication. Do **not** commit, push, merge, or apply labels
> from this skill. Human approved was `wave-acceptance`. At `wave-signoff`
> the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/251 @ `77e2c49fc89c7c37de701179680bef44b7cea68f` — **expected reviewed head SHA** (Pass-2 tip; accept tip remains `a40ab9c`)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W2.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W2.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W2 `human_approved` from wave-acceptance (index pointer + `Implementation-Status-INIT-GATEFLOW-017.md`)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W3 `/pre-implement`

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W2 assigned REQs only (10, 15, 20, 21, 27) |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-019 / 001 / 014 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed W1 contracts + 8 produced for W3 |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; no commit from this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W2.md
  blockers: []
  signals:
    wave: W2
    contracts_produced: 8
    assigned_reqs:
      - REQ-10
      - REQ-15
      - REQ-20
      - REQ-21
      - REQ-27
    reviewed_head_sha: 77e2c49fc89c7c37de701179680bef44b7cea68f
    pr_url: https://github.com/drivestream-lab/gateflow/pull/251
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/247"
```
