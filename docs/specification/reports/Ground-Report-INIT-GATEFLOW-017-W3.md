# Ground report — INIT-GATEFLOW-017 W3

| Field | Value |
|-------|-------|
| Wave | W3 — Enter programme + isolation + as-built |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Initiative | INIT-GATEFLOW-017 |
| Date | 2026-08-14 |
| Wave head (exact) | Accept tip `e0d7a24490ebe17426108fe1095ef785675d889c` (`wave-accepted`); Pass-2 tip `4b0aca4689b1f14bd36fb0c741ad5a05231f9f81` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/253 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-18 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-16, REQ-17, REQ-18, REQ-19, REQ-23, REQ-26, REQ-27 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 626 passed; `make check` exit 0 |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR [#253](https://github.com/drivestream-lab/gateflow/pull/253) tip `e0d7a24` | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-16 | One sign-in; enter a granted programme; refuse not granted | `POST /api/auth/session/programme`; `test_enter_programme_granted_returns_snapshot_without_remint`; `test_enter_programme_not_granted_403`; isolation live script | pass |
| REQ-17 | Same identity, two granted programmes | Isolation script grants A+B then hits delivery on both path tenants | pass |
| REQ-18 | Zero grants: signed in, no delivery | Login/me return `grants: []` when none; enter ungranted 403; `verify_jwt_login` me + enter refuse | pass |
| REQ-19 | Granted tenant_admin still runs 013/016 delivery | Isolation hits `GET /tenants/{id}/programme/connection` after grant — not 403 | pass |
| REQ-23 | platform_admin cannot run delivery | Isolation asserts platform_admin connection 403; existing `require_tenant_resolved` | pass |
| REQ-26 | tenant_admin me has no factory roster | `AuthSessionSnapshot` has no identities list; `test_me_returns_snapshot_without_password_or_roster` | pass |
| REQ-27 | Onboard APIs unchanged | W2 contract held; as-built index is one 017 pointer; no onboard route change this wave | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| No remint; JWT stays `sub` / `role` / `session_epoch` | ADR-019 Option B | pass |
| `runs.tenant_id` from path tenant after membership | ADR-016 | pass |
| JWT-only product edge | ADR-014 | pass |
| Postgres is sole durable store | ADR-001 | pass |
| Enter POST is body-only | `http-api-conventions.mdc` | pass |
| Models in `src/models/` only | `pydantic-schemas.mdc` | pass |
| `public_paths` lists actually public prefixes | `architecture.mdc` | pass — narrowed to `/api/auth/login` |
| Extend live scripts; no unit-as-live | `testing-verify-flows.mdc` | pass |
| 403 `not granted` / no silent enter | `fail-fast.mdc` | pass |
| One 017 as-built index row | artifact-write-contract | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| 014 attach door gone | Ground-Report-017-W2 | yes — isolation/jwt_login use `enter_grant_login`, not attach |
| Historic users door gone | Ground-Report-017-W2 | yes — unused this wave |
| Wipe collaborator | Ground-Report-017-W2 | yes — unused this wave; identity remains after wipe |
| Provision helper | Ground-Report-017-W2 | yes — enter → grant → login; return tuple unchanged |
| Grant path | Ground-Report-017-W2 | yes — isolation grants A then B via `/grants` |
| Onboard / catalogue | Ground-Report-017-W2 | yes — unchanged |
| Login snapshot | Ground-Report-017-W2 | yes — **populated this wave** from memberships |
| Directory enter | Ground-Report-017-W2 | yes — helper still POSTs `/identities` |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| — | — | Learning-Extract items empty — no open L-* |

## Contracts produced by this wave

Last engineering wave for INIT-GATEFLOW-017 on gateflow. Next consumer is initiative closure / `gateflow-ops` (CTR-04), not a W4.

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Session snapshot | `AuthIdentityService.me` | `GET /api/auth/me` | live Bearer | identity + grants | No password; no factory roster; no remint | closure / ops |
| Enter programme | `AuthIdentityService.enter_programme` | `POST /api/auth/session/programme` | body `{programme_id}` | snapshot + `entered_programme_id` | Grant required; 403 `not granted`; no new JWT | closure / ops |
| Login grants | `AuthIdentityService.login` | `POST /api/auth/login` | email + password | token + grants list | Grants from memberships; JWT still has no `tenant_id` | closure / ops |
| Public auth prefix | `app.py` AuthMiddleware | `public_paths` | — | login only is public | `/me` and `/session/programme` require Bearer | closure / ops |
| Delivery isolation | `require_tenant_resolved` | path tenant + membership | tenant_admin JWT | connection / delivery | platform_admin 403; ungranted path 403 | closure / ops |
| Isolation live script | `verify_cross_programme_isolation` | enter → grant → login → enter | two programmes | exit 0 | Does not call attach; detaches synthetic grants | closure |
| As-built 017 index | `implementation-status.md` | one pointer row | — | detail file | W0–W3 listed in `Implementation-Status-INIT-GATEFLOW-017.md` | closure |
| Provision helper (unchanged) | `enter_grant_login` | enter → grant → login | programme + email + password | identity JWT | No remint; no attach | closure / ops |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge
> readiness for publication. Do **not** commit, push, merge, or apply labels
> from this skill. Human approved was `wave-acceptance`. At `wave-signoff`
> the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/253 @ `4b0aca4689b1f14bd36fb0c741ad5a05231f9f81` — **expected reviewed head SHA** (Pass-2 tip; accept tip remains `e0d7a24`)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W3.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W3.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W3 `human_approved` from wave-acceptance (index pointer + `Implementation-Status-INIT-GATEFLOW-017.md`)
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

yes — G1–G10 satisfied; no Blocking GF-*; last eng wave; Contracts produced ready for initiative closure

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W3 assigned REQs only (16, 17, 18, 19, 23, 26, 27) |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-019 / 016 / 014 / 001 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed W2 contracts + 8 produced for closure |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; no commit from this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W3.md
  blockers: []
  signals:
    wave: W3
    contracts_produced: 8
    assigned_reqs:
      - REQ-16
      - REQ-17
      - REQ-18
      - REQ-19
      - REQ-23
      - REQ-26
      - REQ-27
    reviewed_head_sha: 4b0aca4689b1f14bd36fb0c741ad5a05231f9f81
    pr_url: https://github.com/drivestream-lab/gateflow/pull/253
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/248"
```
