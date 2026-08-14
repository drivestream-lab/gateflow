# Ground report — INIT-GATEFLOW-017 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Identity directory + grant/detach |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Initiative | INIT-GATEFLOW-017 |
| Date | 2026-08-14 |
| Wave head (exact) | Accept tip `b224fe633ea6a3076df4d9afd9d4d9159366484c` (`wave-accepted`); Pass-2 tip `2e23724adbaeeef3c91893585198f7b0a2718d71` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/250 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-18 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-22, REQ-24, REQ-25, REQ-28, REQ-29, REQ-30 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 622 passed; `make check` exit 0 |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR [#250](https://github.com/drivestream-lab/gateflow/pull/250) tip `b224fe6` | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Enter name + email + password; zero programmes | `IdentityDirectoryService.enter_identity`; `POST /api/v1/identities`; `test_enter_identity_creates_tenant_admin_without_grants`; `verify_identity_directory` | pass |
| REQ-02 | Email unique | enter 409 `duplicate email`; `test_enter_duplicate_email_409`; live duplicate probe | pass |
| REQ-03 | Identifier must be an email | enter 422 `not an email`; `test_enter_named_refusals`; login already W0 | pass |
| REQ-04 | List / search by name or email | `list_identities`; `GET /api/v1/identities?q=`; unit + live list/search | pass |
| REQ-05 | Entered role `tenant_admin`; seeded `platform_admin` not grantable | enter sets `TENANT_ADMIN`; grant 422 `platform_admin not grantable`; unit + live | pass |
| REQ-06 | Grant existing identity to onboarded programme | `grant`; `POST /programmes/{id}/grants`; no mint; unit + live | pass |
| REQ-07 | Grant idempotent | `test_grant_idempotent_and_does_not_mint`; live double-grant same id | pass |
| REQ-08 | Unknown identity refused | grant 422 `unknown identity`; `test_grant_unknown_identity_422` | pass |
| REQ-09 | One identity, many programmes | unique pair persist (W0) + second grant path; live regrant after detach | pass |
| REQ-10 | Detach; identity remains | `detach`; `DELETE …/grants/{identity_id}`; `test_detach_leaves_identity`; live | pass |
| REQ-11 | Who-can-enter / which-programmes | `list_members` / `list_grants`; GET programme grants + identity grants; live | pass |
| REQ-12 | Suspend kills sign-in and open session | `suspend_identity` increments `session_epoch`; W0 session gate; live login 401 `suspended` | pass |
| REQ-13 | Unsuspend restores sign-in | `unsuspend_identity` does not increment epoch; `test_unsuspend_does_not_increment_epoch`; live unsuspend | pass |
| REQ-14 | Password-set kills prior JWT | `set_password` increments epoch; live old password fails | pass |
| REQ-22 | `tenant_admin` cannot directory-admin | `require_directory_admin` 403 `wrong actor`; `test_identity_routes`; live | pass |
| REQ-24 | Suspended identity may still be granted/detached | `test_grant_while_suspended_allowed` | pass |
| REQ-25 | Name required at enter | 422 `missing name`; `test_enter_named_refusals` | pass |
| REQ-28 | Unknown programme refused | grant/detach 422 `unknown programme`; unit | pass |
| REQ-29 | Missing password refused | 422 `missing password`; unit | pass |
| REQ-30 | Password never returned | `IdentityReadModel` omits password; unit + live `_no_password` | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Grant does not remint; epoch increment on suspend/password-set | ADR-019 Option B | pass |
| Postgres is sole durable store | ADR-001 | pass |
| JWT-only product edge | ADR-014 | pass |
| Models in `src/models/` only; directory read omits password | `pydantic-schemas.mdc` | pass |
| Body-only writes; GET query for list | `http-api-conventions.mdc` | pass |
| `*_service` + `@inject` + DI bind | `architecture.mdc` / `dependency-injection.mdc` | pass |
| ORM confined to repository | `repository-pattern.mdc` | pass |
| New live script; no unit-as-live | `testing-verify-flows.mdc` | pass |
| Named refusals; no silent create-on-grant | `fail-fast.mdc` | pass |
| Did not globally rename `role_forbidden` | Pre-Implement W1 must-not | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Identity row create / get_by_id / get_by_credential | Ground-Report-017-W0 | yes — list/update methods added compile-safe |
| Membership unique pair | Ground-Report-017-W0 | yes — list/delete added compile-safe |
| Session gate (suspend / epoch mismatch) | Ground-Report-017-W0 | yes — W1 increments epoch on suspend/password-set |
| JWT mint (no programme claim) | Ground-Report-017-W0 | yes — grant does not call mint |
| Login snapshot `{grants: []}` | Ground-Report-017-W0 | yes — not populated (W3) |
| `IdentityStatusType` `active` \| `suspended` | Ground-Report-017-W0 | yes — reused; not rewritten |
| Wipe does not delete identity rows | Ground-Report-017-W0 | yes — unchanged; explicit membership wipe is W2 |
| 014 attach door still mounted | Ground-Report-017-W0 | yes — `POST …/tenant-admins` remains (W2 deletes) |

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
| Enter identity | `IdentityDirectoryService` / `POST /api/v1/identities` | enter_identity | display name, email, password | IdentityRead (role `tenant_admin`, grants empty) | Email unique (409 `duplicate email`); 422 `missing name` / `not an email` / `missing password`; no password on output | W2 provision rewrite |
| List / search identities | same / `GET /api/v1/identities` | list_identities | optional query | list of IdentityRead | Name contains or email exact, case-insensitive; empty list not an error; no password | W2+ |
| Suspend / unsuspend / password-set | same / `POST …/suspend` `/unsuspend` `PUT …/password` | suspend / unsuspend / set_password | identity id (+ password for set) | IdentityRead | Suspend and password-set increment `session_epoch`; unsuspend does not; grants unchanged | W2+ |
| Grant / detach | same / `POST|DELETE /api/v1/programmes/{id}/grants` | grant / detach | programme id + identity id | membership pair | Idempotent grant; no JWT mint; 422 `unknown identity` / `unknown programme` / `platform_admin not grantable`; suspend does not block grant | W2 door delete uses this, not attach |
| Membership views | same / GET identity grants + programme grants | list_grants / list_members | identity id or programme id | membership pairs or IdentityRead list | Password absent; identity remains after last detach | W2 wipe collaborator |
| Directory actor | `require_directory_admin` | identity and grant routes | AuthContext | same or 403 `wrong actor` | Does not rename global `role_forbidden` | W3 delivery `wrong actor` stays separate |
| Identity read shape | `IdentityReadModel` | directory HTTP | — | id, display_name, email, status, role, grants | `extra=forbid`; no password / hash | W2+ |
| 014 attach door | `POST /api/v1/programmes/{id}/tenant-admins` | attach_tenant_admin | credential + password | attach response | Still mounted; W2 deletes | W2 |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge
> readiness for publication. Do **not** commit, push, merge, or apply labels
> from this skill. Human approved was `wave-acceptance`. At `wave-signoff`
> the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/250 @ `2e23724adbaeeef3c91893585198f7b0a2718d71` — **expected reviewed head SHA** (Pass-2 tip; accept tip remains `b224fe6`)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W1.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W1.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W1 `human_approved` from wave-acceptance (index pointer + `Implementation-Status-INIT-GATEFLOW-017.md`)
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

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W2 `/pre-implement`

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W1 assigned REQs only (01–14 except 15–21; plus 22, 24, 25, 28–30) |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-019 / 001 / 014 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed W0 contracts + 8 produced for W2 |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; no commit from this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W1.md
  blockers: []
  signals:
    wave: W1
    contracts_produced: 8
    assigned_reqs:
      - REQ-01
      - REQ-02
      - REQ-03
      - REQ-04
      - REQ-05
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-09
      - REQ-10
      - REQ-11
      - REQ-12
      - REQ-13
      - REQ-14
      - REQ-22
      - REQ-24
      - REQ-25
      - REQ-28
      - REQ-29
      - REQ-30
    reviewed_head_sha: 2e23724adbaeeef3c91893585198f7b0a2718d71
    pr_url: https://github.com/drivestream-lab/gateflow/pull/250
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/246"
```
