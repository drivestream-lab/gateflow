# Implementation status — INIT-GATEFLOW-017

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Updated | 2026-08-14 |

## Wave status

| Wave | Goal | Status | Evidence |
|------|------|--------|----------|
| W0 | Membership schema + identity JWT session | **human_approved** | Board [#245](https://github.com/drivestream-lab/gateflow/issues/245); PR [#249](https://github.com/drivestream-lab/gateflow/pull/249) accept tip `3da2d02` label `wave-accepted` (+ Pass-2 tip `f28afde`); Ground-Report W0 **pass**; Learning-Extract W0 `items: []` |
| W1 | Identity directory + grant/detach | **human_approved** | Board [#246](https://github.com/drivestream-lab/gateflow/issues/246); PR [#250](https://github.com/drivestream-lab/gateflow/pull/250) accept tip `b224fe6` label `wave-accepted` (+ Pass-2 tip `2e23724`); Ground-Report W1 **pass**; Learning-Extract W1 `items: []` |
| W2 | Delete 014 doors + wipe collaborator | **human_approved** | Board [#247](https://github.com/drivestream-lab/gateflow/issues/247); PR [#251](https://github.com/drivestream-lab/gateflow/pull/251) accept tip `a40ab9c` label `wave-accepted` (+ Pass-2 tip `77e2c49`); Ground-Report W2 **pass**; Learning-Extract W2 `items: []` |
| W3 | Enter programme + isolation + as-built | implemented | Board [#248](https://github.com/drivestream-lab/gateflow/issues/248); not `human_approved` until `wave-acceptance` |

## W0 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Identity columns + memberships | REQ-21 | `user_identity_schema`, `programme_membership_schema`, Alembic `9713e795e01c` | `test_user_identity_repository`, `test_programme_membership_repository` | — | Human applies `run_postgres_migration.sh` |
| Session epoch + no programme claim | REQ-12, REQ-14, REQ-16 | middleware + `require_role` / `require_programme_scope` + mint | `test_auth_middleware`, `test_auth_dependencies`, `test_auth_identity_service` | `verify_jwt_login` | ADR-019 Option B |
| Login snapshot `{grants: []}` + email | REQ-03, REQ-18 | `AuthIdentityService.login` | `test_auth_identity_service` | `verify_jwt_login` | Enter/grant is W1; enter-programme is W3 |

## W1 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Enter / list / search identities | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-25, REQ-29, REQ-30 | `IdentityDirectoryService`, `identity_routes` | `test_identity_directory_service`, `test_identity_routes` | `verify_identity_directory` | Role is `tenant_admin`; password omitted |
| Grant / detach / membership views | REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-24, REQ-28 | directory service + `/programmes/{id}/grants` | `test_identity_directory_service` | `verify_identity_directory` | No JWT mint; 014 attach door still mounted |
| Suspend / unsuspend / password-set | REQ-12, REQ-13, REQ-14 | directory service increments `session_epoch` | `test_identity_directory_service` | `verify_identity_directory` | ADR-019 kill switch |
| Wrong actor | REQ-22 | `require_directory_admin` | `test_identity_routes` | `verify_identity_directory` | 403 `wrong actor` |

## W2 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| 014 attach door deleted | REQ-21 | `ProgrammeService` / `programme_admin_routes` — no `attach_tenant_admin` | `test_attach_tenant_admin_method_removed` | `verify_dead_doors_deleted` | Grant stays at `/programmes/{id}/grants` |
| Historic users door deleted | REQ-20 | `tenant_routes` — no `POST …/users` | `test_historic_users_route_gone_with_jwt` | `verify_dead_doors_deleted` | A-7 |
| Wipe keeps identity | REQ-10, REQ-15, REQ-21 | `ProgrammeWipeService` deletes memberships then programme | `test_programme_wipe_service` | `verify_wipe_cutover` | ACTIVE 409 unchanged |
| Provision helper | REQ-21, REQ-27 | `enter_grant_login` in `verify_jwt_auth` | — | `verify_programme_onboarding` | No remint; onboard create unchanged |

## W3 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Enter programme (no remint) | REQ-16, REQ-18 | `GET /api/auth/me`, `POST /api/auth/session/programme` | `test_auth_identity_service` | `verify_cross_programme_isolation` | ADR-019 Option B; 403 `not granted` |
| Grant snapshot on login/me | REQ-16, REQ-18, REQ-26 | `AuthIdentityService.login` / `me` | `test_auth_identity_service` | `verify_jwt_login` | No password; no factory roster |
| Two-programme delivery + platform_admin refuse | REQ-17, REQ-19, REQ-23 | membership + `require_tenant_resolved` | `test_auth_dependencies` | `verify_cross_programme_isolation` | Path tenant after membership (ADR-016) |
