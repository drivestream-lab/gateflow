# Implementation status — INIT-GATEFLOW-014

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Updated | 2026-08-11 |

## Wave status

| Wave | Goal | Status | Evidence |
|------|------|--------|----------|
| W0 | Seed platform_admin + JWT mint/login edge | **human_approved** | Board [#215](https://github.com/drivestream-lab/gateflow/issues/215); Draft PR [#220](https://github.com/drivestream-lab/gateflow/pull/220) accept `f96edc7` / Pass-2 `6156d12` label `wave-accepted`; Ground-Report W0 **pass**; Learning-Extract W0 `items: []` |
| W1 | Programme validate-then-create + tenant_admin attach + agent catalogue | not started | — |
| W2 | Cut over under JWT; refuse old doors | not started | — |
| W3 | Dead-door deletion + wipe | not started | — |
| W4 | Prove absence + teaching rewrite | not started | — |

## W0 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| RoleType on AuthContext | REQ-06 | `role_types.py`, `auth_models.py` | `test_auth_middleware` | — | ADR-014 |
| Bad JWT refused | REQ-05 | `AuthMiddleware` | `test_auth_middleware` | — | 401 UNAUTHORIZED |
| User identity persist | REQ-01 | schema + repository | `test_user_identity_repository` | — | Alembic `5c8536ec7078` |
| Seed platform_admin + JWT | REQ-01, REQ-47 | seed script + AuthIdentityService | `test_auth_identity_service` | `verify_jwt_login` | Idempotent |
| Login API | REQ-02, REQ-03, REQ-43 | `POST /api/auth/login` | `test_auth_identity_service` | `verify_jwt_login` | No UI |
| Claim shape | REQ-04, REQ-06, REQ-07 | middleware | claim_shape tests | `verify_jwt_login` | Product allowlist shrink = W2 |
