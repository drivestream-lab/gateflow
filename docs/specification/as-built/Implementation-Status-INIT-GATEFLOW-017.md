# Implementation status — INIT-GATEFLOW-017

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Updated | 2026-08-14 |

## Wave status

| Wave | Goal | Status | Evidence |
|------|------|--------|----------|
| W0 | Membership schema + identity JWT session | **human_approved** | Board [#245](https://github.com/drivestream-lab/gateflow/issues/245); PR [#249](https://github.com/drivestream-lab/gateflow/pull/249) accept tip `3da2d02` label `wave-accepted`; Ground-Report W0 **pass**; Learning-Extract W0 `items: []` |
| W1 | Identity directory + grant/detach | not started | Board [#246](https://github.com/drivestream-lab/gateflow/issues/246) |
| W2 | Delete 014 doors + wipe collaborator | not started | Board [#247](https://github.com/drivestream-lab/gateflow/issues/247) |
| W3 | Enter programme + isolation + as-built | not started | Board [#248](https://github.com/drivestream-lab/gateflow/issues/248) |

## W0 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Identity columns + memberships | REQ-21 | `user_identity_schema`, `programme_membership_schema`, Alembic `9713e795e01c` | `test_user_identity_repository`, `test_programme_membership_repository` | — | Human applies `run_postgres_migration.sh` |
| Session epoch + no programme claim | REQ-12, REQ-14, REQ-16 | middleware + `require_role` / `require_programme_scope` + mint | `test_auth_middleware`, `test_auth_dependencies`, `test_auth_identity_service` | `verify_jwt_login` | ADR-019 Option B |
| Login snapshot `{grants: []}` + email | REQ-03, REQ-18 | `AuthIdentityService.login` | `test_auth_identity_service` | `verify_jwt_login` | Enter/grant is W1; enter-programme is W3 |
