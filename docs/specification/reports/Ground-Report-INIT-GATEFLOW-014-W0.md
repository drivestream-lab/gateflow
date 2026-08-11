# Ground report — INIT-GATEFLOW-014 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Seed platform_admin + JWT mint/login edge |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Initiative | INIT-GATEFLOW-014 |
| Date | 2026-08-11 |
| Wave head (exact) | Accept tip `f96edc7394e7b61cd759028c048da6c942a0486a` (`wave-accepted`); Pass-2 docs tip `6156d121dfe62e98ded33ef2f30f8e06f06b3ae1` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/220 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-13 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-43, REQ-47 (platform_admin re-seed slice from WorkManifest TASK-W0-04) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | Pass-1: 507 passed; this session auth subset 17 passed |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #220 tip `f96edc7` (2026-08-11 @nikd10x) | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile/`ground_command` is N/A for this repo. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Seed creates `platform_admin` and can mint JWT | `scripts/seed_platform_admin.py`; `AuthIdentityService.ensure_platform_admin`; `test_auth_identity_service`; `verify_jwt_login` | pass |
| REQ-02 | Login API returns Gateflow-issued JWT | `POST /api/auth/login` (`login_routes.py`); `AuthIdentityService.login`; unit + verify script | pass |
| REQ-03 | Invalid login refused; no JWT | `UnauthorizedError` on bad password/unknown identity; unit asserts 401 `UNAUTHORIZED` | pass |
| REQ-04 | Product edge prepared for Gateflow JWT Bearer | Middleware verifies iss/aud/claims when path is protected; claim shape tests; **product `/api/v1/*` remain on `public_paths` until W2** (plan E6) | pass (W0 scope; full Appendix C cutover = W2) |
| REQ-05 | Bad JWT refused | `test_auth_middleware` — missing/malformed/expired/wrong-iss/wrong-aud → 401 | pass |
| REQ-06 | JWT identifies user + role; tenant_admin bound | `RoleType`; `AuthContext.role`; tenant_admin requires `tenant_id` claim; claim_shape tests | pass |
| REQ-07 | PAT/agent keys not accepted as caller Bearer | Non-JWT Bearer fails decode → 401 on protected paths; no alternate Bearer acceptors added in W0 | pass (W0 foundation; product-door refuse = W2) |
| REQ-43 | Invalid login named outcome, zero token | Same as REQ-03 — `UNAUTHORIZED` + no `access_token` | pass |
| REQ-47 | Re-seed `platform_admin` idempotent | `ensure_platform_admin` reuses row; unit idempotency; verify double-seed | pass (W0 seed slice; attach slice = W1) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Reuse existing AuthMiddleware decode path — no second verifier | ADR-014 | pass |
| Domain enums `RoleType(str, Enum)` | `pydantic-schemas.mdc` | pass |
| ORM confined to repository | `repository-pattern.mdc` | pass |
| Login POST body model in `src/models/` | `http-api-conventions.mdc` | pass |
| Human-owned Alembic for `user_identities` | `database-migrations.mdc` | pass — revision `5c8536ec7078` present; agents did not invent versions policy |
| Do not shrink product `public_paths` in W0 | plan E6 / Pre-Implement | pass — only `/api/auth` added |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| AuthMiddleware JWT verify + AuthContext | as-built / W0 baseline (no prior INIT-014 Ground Report) | yes — extended in place |
| JWTSettings issuer/audience/keys | `src/configs/jwt_settings.py` | yes |

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
| Role vocabulary | `role_types` / `AuthContext` | AuthContext construction; middleware role decode | role wire string | `RoleType` (`platform_admin` \| `tenant_admin`) | Unrecognized role → 401; no silent default role | W1+ |
| User identity store | `UserIdentityRepository` | create / get_by_credential_identifier | credential_identifier, password_hash, role, optional tenant_id | UserIdentityReadModel | Unique credential_identifier; password_hash never on HTTP responses | W1 attach |
| JWT mint | `AuthIdentityService.mint_user_jwt` | mint_user_jwt / ensure_platform_admin / login | user_id, role, optional tenant_id | Gateflow JWT (`sub`,`role`,`iss`,`aud`,`iat`,`exp`, optional `tenant_id`) | Matches AuthMiddleware claims; tenant_admin requires tenant_id | W1+ |
| Login API | `POST /api/auth/login` | login route | LoginRequest (credential_identifier, password) | LoginResponse.access_token or 401 UNAUTHORIZED | Invalid credentials → zero token | W1+ |
| Seed platform_admin | `scripts/seed_platform_admin.py` | CLI seed | env identifier/password defaults | prints user_id + access_token; idempotent row | Double-run → one row | W1 |
| Middleware claim gate | `AuthMiddleware.dispatch` | protected paths | Bearer JWT | AuthContext on request.state or 401 | iss/aud/exp/role/tenant_admin binding enforced | W2 refuse doors |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/220
- Accept tip (`wave-accepted`): `f96edc7394e7b61cd759028c048da6c942a0486a`
- Reviewed head SHA (Pass-2 tip after Learning/Ground publish): `6156d121dfe62e98ded33ef2f30f8e06f06b3ae1` — merge PR tip if a follow-up SHA-stamp commit lands on the same branch
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W0.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W0.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W0 `human_approved` from wave-acceptance (recorded in index + `Implementation-Status-INIT-GATEFLOW-014.md`)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W1 `/pre-implement`

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W0 assigned REQs only |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-014 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed baseline + contracts produced |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; no commit from this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W0.md
  blockers: []
  signals:
    wave: W0
    contracts_produced: 6
    assigned_reqs:
      - REQ-01
      - REQ-02
      - REQ-03
      - REQ-04
      - REQ-05
      - REQ-06
      - REQ-07
      - REQ-43
      - REQ-47
    reviewed_head_sha: 6156d121dfe62e98ded33ef2f30f8e06f06b3ae1
    pr_url: https://github.com/drivestream-lab/gateflow/pull/220
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/215"
```
