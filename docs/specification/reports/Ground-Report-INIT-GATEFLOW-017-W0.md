# Ground report — INIT-GATEFLOW-017 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Membership schema + identity JWT session |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Initiative | INIT-GATEFLOW-017 |
| Date | 2026-08-14 |
| Wave head (exact) | Accept tip `3da2d02fb90220a8f035596e5b9c61464d760d9e` (`wave-accepted`); Pass-2 tip `f28afde7b666e9e9ca4ed0ff054c623daa6af87c` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/249 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-18 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-03, REQ-12, REQ-14, REQ-16, REQ-18, REQ-21 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 602 passed; `make check` exit 0 |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR [#249](https://github.com/drivestream-lab/gateflow/pull/249) tip `3da2d02` | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-03 | Identifier must be an email | `AuthIdentityService.login` refuses non-email with 422 `not an email`; `test_login_non_email_identifier_422`; `verify_jwt_login` marker includes REQ-03 | pass |
| REQ-12 | Suspend kills sign-in and open session | `require_role` → `assert_live_session` 401 `suspended`; login 401 `suspended`; `test_require_role_suspended_401`; `test_login_suspended_raises_unauthorized`. Epoch increment on suspend is W1 | pass (W0 mechanism) |
| REQ-14 | Password-set kills prior JWT | JWT `session_epoch` vs row; mismatch → 401 `session_epoch_mismatch`; `test_require_role_epoch_mismatch_401`. Password-set increment is W1 | pass (W0 mechanism) |
| REQ-16 | One sign-in; programme scope is authorization not remint | `mint_user_jwt` writes `session_epoch`, no `tenant_id`; middleware no longer 401s missing `tenant_id`; `require_programme_scope` loads membership; `test_tenant_admin_missing_tenant_id_not_401`; `verify_jwt_login` asserts no `tenant_id` claim. Enter-programme is W3 | pass |
| REQ-18 | Zero grants: signed in, no delivery | `LoginResponse.grants` default empty; login always returns `grants: []` in W0; unit + `verify_jwt_login` require `grants` array | pass |
| REQ-21 | Leftover 1:1 binds wiped (schema); 014 door delete later | `user_identities.tenant_id` dropped; `programme_memberships` unique `(identity_id, programme_id)`; Alembic `9713e795e01c`; `delete_for_tenant` removed. Door delete is W2 | pass (W0 schema slice) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| No programme claim; membership scope; `session_epoch`; no Redis denylist | ADR-019 Option B | pass |
| Postgres is sole durable store | ADR-001 | pass |
| JWT-only product edge (claim clause superseded only) | ADR-014 | pass |
| `runs.tenant_id` still from path tenant after membership | ADR-016 | pass — `require_tenant_resolved` uses path tenant; enter-programme W3 |
| ORM confined to repository | `repository-pattern.mdc` | pass |
| Models in `src/models/` only; `IdentityStatusType` | `pydantic-schemas.mdc` | pass |
| Agent created Alembic via create script; human applies | `database-migrations.mdc` | pass — `9713e795e01c` |
| Login body model; no models under `src/api/` | `http-api-conventions.mdc` | pass |
| Live script extended, not unit-as-live | `testing-verify-flows.mdc` | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| AuthMiddleware JWT verify + AuthContext | INIT-GATEFLOW-014 Ground-Report W0 + live source | yes — extended: drop TENANT_ADMIN missing-`tenant_id` 401; add `session_epoch` |
| User identity persist | 014 W0 identity store | yes — `tenant_id` removed; `display_name` / `status` / `session_epoch` added |
| Login `POST /api/auth/login` | 014 W0 login API | yes — response now includes `grants` array |
| Wipe / attach still mounted | 014 W3 wipe; 014 W1 attach | yes — compile-safe: wipe does not delete identities; attach does not write `tenant_id` (doors remain until W2) |

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
| Identity row | `UserIdentityRepository` | create / get_by_id / get_by_credential_identifier | credential, password hash, role, display name, status, session epoch | UserIdentityReadModel | No `tenant_id` column; unique credential; status `active` \| `suspended` | W1 directory |
| Membership grant | `ProgrammeMembershipRepository` | create_membership / get_by_identity_and_programme | identity id + programme id | ProgrammeMembershipReadModel | Unique pair; FK identity restrict; FK programme cascade | W1 grant/detach |
| Session gate | `require_role` / `assert_live_session` | protected routes | AuthContext (`sub`, role, session_epoch) | same context or 401 | Inactive → `suspended`; epoch mismatch → `session_epoch_mismatch`; missing identity → `unknown identity` | W1 suspend/password increment |
| Programme scope | `require_programme_scope` | path tenant | user id + path tenant | AuthContext or 403 `not_granted` | Membership row for programme of that tenant; JWT `tenant_id` unused | W1+ / W3 enter |
| JWT mint | `AuthIdentityService.mint_user_jwt` | mint / seed / login | user id, role, session epoch | JWT `sub` / `role` / `session_epoch` + iss/aud/iat/exp | No programme / `tenant_id` claim | W1+ / W3 |
| Login snapshot | `POST /api/auth/login` | login | email + password | access_token + `grants` array or 401/422 | Non-email → 422 `not an email`; suspended → 401; W0 `grants` always empty | W1 populate later; W3 enter |
| Status vocabulary | `IdentityStatusType` | identity row + session gate | wire string | `active` \| `suspended` | Closed enum; add members only by spec | W1 |
| Wipe vs identity | `ProgrammeWipeService.wipe_programme` | wipe | programme id | wipe result | Does not delete identity rows; membership cascade via programme FK | W2 explicit membership delete |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge
> readiness for publication. Do **not** commit, push, merge, or apply labels
> from this skill. Human approved was `wave-acceptance`. At `wave-signoff`
> the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/249 @ `f28afde7b666e9e9ca4ed0ff054c623daa6af87c` — **expected reviewed head SHA** (Pass-2 tip; accept tip remains `3da2d02`)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W0.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-017-W0.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W0 `human_approved` from wave-acceptance (index pointer + `Implementation-Status-INIT-GATEFLOW-017.md`)
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

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W1 `/pre-implement`

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W0 assigned REQs only (03, 12, 14, 16, 18, 21) |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-019 / 001 / 014 / 016 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed 014 contracts + 8 produced for W1 |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; no commit from this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W0.md
  blockers: []
  signals:
    wave: W0
    contracts_produced: 8
    assigned_reqs:
      - REQ-03
      - REQ-12
      - REQ-14
      - REQ-16
      - REQ-18
      - REQ-21
    reviewed_head_sha: f28afde7b666e9e9ca4ed0ff054c623daa6af87c
    pr_url: https://github.com/drivestream-lab/gateflow/pull/249
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/245"
```
