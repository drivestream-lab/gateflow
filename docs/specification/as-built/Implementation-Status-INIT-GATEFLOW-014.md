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
| W1 | Programme validate-then-create + tenant_admin attach + agent catalogue | **human_approved** | Board [#216](https://github.com/drivestream-lab/gateflow/issues/216); Draft PR [#221](https://github.com/drivestream-lab/gateflow/pull/221) accept `ecb7fbd` / Pass-2 `6b926c6` label `wave-accepted`; Ground-Report W1 **pass**; Learning-Extract W1 `items: []` |
| W2 | Cut over under JWT; refuse old doors | **human_approved** | Board [#217](https://github.com/drivestream-lab/gateflow/issues/217); Draft PR [#222](https://github.com/drivestream-lab/gateflow/pull/222) accept `0c8e8a5` label `wave-accepted`; Ground-Report W2 **pass**; Learning-Extract W2 `items: []` — Pass-2 tip `eb51e9f`|
| W3 | Dead-door deletion + wipe | **human_approved** | Board [#218](https://github.com/drivestream-lab/gateflow/issues/218); Draft PR [#224](https://github.com/drivestream-lab/gateflow/pull/224) accept `52b969d` / Pass-2 `6ad5c96` label `wave-accepted`; Ground-Report W3 **pass**; Learning-Extract W3 `items: []` |
| W4 | Prove absence + teaching rewrite | **human_approved** | Board [#219](https://github.com/drivestream-lab/gateflow/issues/219); Draft PR [#226](https://github.com/drivestream-lab/gateflow/pull/226) accept tip `30a3ed2` / Pass-2 `2d37424` label `wave-accepted`; Ground-Report W4 **pass**; Learning-Extract W4 `items: []` |

## W0 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| RoleType on AuthContext | REQ-06 | `role_types.py`, `auth_models.py` | `test_auth_middleware` | — | ADR-014 |
| Bad JWT refused | REQ-05 | `AuthMiddleware` | `test_auth_middleware` | — | 401 UNAUTHORIZED |
| User identity persist | REQ-01 | schema + repository | `test_user_identity_repository` | — | Alembic `5c8536ec7078` |
| Seed platform_admin + JWT | REQ-01, REQ-47 | seed script + AuthIdentityService | `test_auth_identity_service` | `verify_jwt_login` | Idempotent |
| Login API | REQ-02, REQ-03, REQ-43 | `POST /api/auth/login` | `test_auth_identity_service` | `verify_jwt_login` | No UI |
| Claim shape | REQ-04, REQ-06, REQ-07 | middleware | claim_shape tests | `verify_jwt_login` | Product allowlist shrink = W2 |

## W1 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Programme persist | REQ-08,11,12,14 | `programme_schema` + repository | `test_programme_repository` | — | Human DDL |
| Validate-then-create | REQ-08,09,10,13 | `ProgrammeService` | `test_programme_service` | `verify_programme_onboarding` | Fail-closed |
| Admin create/list | REQ-08,17,18 | `programme_admin_routes` | `test_programme_admin_routes` | `verify_programme_onboarding` | JWT required |
| Attach tenant_admin | REQ-15,16,44,47 | `ProgrammeService.attach` | `test_programme_service` (-k attach) | `verify_programme_onboarding` | Idempotent |
| Agent catalogue | REQ-19,20,40,45 | catalogue schema/repo/service | catalogue unit tests | `verify_agent_catalogue` | No env fallback |
| Effective runner | REQ-21,22,41,42 | `resolve_effective_runner` | `test_platform_agent_catalogue_service` | `verify_agent_catalogue` | |
| Meta-connection rename | REQ-08 / AF-1 | `catalogue_connection_*` | existing onboarding/selection units | — | URLs unchanged |

## W2 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| JWT product edge | REQ-04,29,32,33 | `app.py` public_paths + route deps | programme/tenant token tests flipped | `verify_jwt_cutover` | Old doors refused, not deleted |
| Role / programme scope | REQ-23,24,30,31 | `require_role` / `require_programme_scope` | `test_auth_dependencies` | isolation verify | Path tenant mismatch → 403 |
| Per-programme ForgeClient | REQ-25 | `ForgeClientFactory` + `ProgrammePatTokenProvider` | `test_forge_client_factory` | — | ADR-015 |
| Tenant-scoped runs | REQ-23,24,31 | `RunSchema.tenant_id` + repo filters | metrics/run tenant_scope units | `verify_cross_programme_isolation` | Squashed Alembic `5e85268f844f` |
| Catalogue-only agents | REQ-26,41 | SlotValidator + CursorAgentRunner | slot/cursor unit tests | — | No env key gate |
| Webhooks untouched | REQ-28 | `github_routes` inspect | webhook ingress units | — | Still signature public |

## W3 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Dead-door deletion | REQ-34 | delete `programme_token`/`tenant_token`; remove `POST /tenants` | `test_tenant_routes` (-k register) | `verify_dead_doors_deleted` | Gone (404/405 with JWT), not refuse-only |
| Wipe cutover | REQ-35, REQ-46 | `ProgrammeWipeService` + `POST /programmes/{id}/wipe` | `test_programme_wipe_service` | `verify_wipe_cutover` | ACTIVE → 409 `active_run`; idle clears programme+tenant |

## W4 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| JWT teaching / happy path | REQ-36, REQ-38 | rewrite `tests/verify/*` + `tests/_helpers/verify_jwt_auth.py` | — (smoke-owned) | `verify_all` | Zero `PROGRAMME_SERVICE_TOKEN` under `tests/verify/` |
| Old-door refusal consolidated | REQ-37 | `verify_old_doors_refused.py` | — | `verify_old_doors_refused` | Token→401; bearer→401; `POST /tenants`→401/404/405 |
| Teaching docs JWT-only | REQ-38 | `tests/README.md` + as-built | — | review | No old-door invocation examples |
