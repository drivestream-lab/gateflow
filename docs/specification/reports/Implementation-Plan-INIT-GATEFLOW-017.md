---
goal: INIT-GATEFLOW-017 — One human, many programmes, one login
initiative: INIT-GATEFLOW-017
status: Planned
date_created: 2026-08-14
source_spec: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-017.md
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md
prd_digest: sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-017.md
impact_map_revision: 1
repo_scope_digest: sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834
approved_meta_pr_head: 601b00e0a74510a6af1c33bc80ca27260995c094
branch: chore/INIT-GATEFLOW-017-spec-gateflow
review_deadline: 2026-08-19
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-017

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` | CURRENT |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-017.md` | CURRENT |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md` (`Status: Accepted`) | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-017.md` / `1` | CURRENT |
| Repo scope digest | `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` | CURRENT |
| Approved meta PR head | `601b00e0a74510a6af1c33bc80ca27260995c094` | CURRENT — meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42) merged |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | `.venv/bin/python -m tests.verify.<script>` (per wave; not `make test`) | RESOLVED |
| `ground_command` | N/A — `/ground-spec` uses as-built + spec citations; no dedicated ground script in this repo | N/A |

Spec PR: [#243](https://github.com/drivestream-lab/gateflow/pull/243), published tip `9e86e6d354d44226a5a4a66bab0c73d1112569db` (Accepted TDD + ADR-019). This plan is local until `/commit-workspace`.

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md` |
| Technical review status | **Accepted** |
| PE sign-off | [x] complete — 2026-08-14, @nikd10x, Cursor chat, Draft spec PR #243 |
| Resolved ADRs | [`adr-019-identity-jwt-programme-scope-and-session-epoch.md`](../adr/adr-019-identity-jwt-programme-scope-and-session-epoch.md) (Accepted — membership lookup + `session_epoch`; no remint; no Redis denylist). FF-02/FF-03 are TDD_ONLY (wipe collaborator; verify helper) — no extra ADR |
| ADR product-boundary re-check | ADR-019: `changes_user_visible_behavior: false`, `spec_amendment_required: false`. Re-ran `adr_boundary_lint.py --verify-lint-evidence` at plan time with REQ-12/14/16 sentences + feasibility spec quote + `--approved-req-id REQ-01`…`REQ-30` — PASS (`sha256:2fbe1ecdb1a73335982e365dd57bcbff12d4b51e328c95be124cc2efa9e86d25`) |
| Outstanding PM questions | PM-1/PM-2/PM-3 deferred non-blocking (016/014 PRD docs; ops must not ship invite) |
| Outstanding domain questions | none |

> Do not start W0 implementation until PE sign-off is marked complete above (it is).

**P15 overlap check (plan time):** `PYTHONPATH=prayog-skills python3 prayog-skills/scripts/verify_coverage_query.py tests/verify --capability {identity,grant,directory,login,wipe,isolation,attach,door}`.

| Surface | Existing artifact | Disposition |
|---------|-------------------|-------------|
| Login / snapshot / zero-grant session | `tests/verify/verify_jwt_login.py` (`prayog:covers:` 014 REQ-01/02/03/43) | **extend** (W0, W3) |
| Factory enter/list/grant/detach/suspend | `--capability grant` → no matches; `--capability identity` → no directory script | **create** `tests/verify/verify_identity_directory.py` (W1) — no existing artifact covers this surface |
| 014 attach + onboard | `verify_programme_onboarding.py` | **extend** (W2) — drop attach JWT provision |
| Wipe | `verify_wipe_cutover.py` | **extend** (W2) |
| Dead / old doors | `verify_dead_doors_deleted.py`, `verify_old_doors_refused.py` | **extend** (W2) |
| Cross-programme isolation | `verify_cross_programme_isolation.py` | **extend** (W3) |

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Enter identity (name, email, password); zero programmes | spec | W1 |
| REQ-02 | Email unique | spec | W1 |
| REQ-03 | Identifier must be an email | spec | W0, W1 |
| REQ-04 | List / search identities | spec | W1 |
| REQ-05 | Entered role is `tenant_admin`; seeded `platform_admin` not grantable | spec | W1 |
| REQ-06 | Grant existing identity to onboarded programme | spec | W1 |
| REQ-07 | Grant idempotent | spec | W1 |
| REQ-08 | Unknown identity refused | spec | W1 |
| REQ-09 | One identity, many programmes | spec | W1 |
| REQ-10 | Detach; identity remains | spec | W1, W2 |
| REQ-11 | Who-can-enter / which-programmes views | spec | W1 |
| REQ-12 | Suspend kills sign-in and open session | spec | W0, W1 |
| REQ-13 | Unsuspend restores sign-in | spec | W1 |
| REQ-14 | Password-set kills prior JWT | spec | W0, W1 |
| REQ-15 | Detach/suspend does not cancel in-flight waves | spec | W2 |
| REQ-16 | One sign-in; programme scope is authorization not remint | spec | W0, W3 |
| REQ-17 | Same identity, two granted programmes | spec | W3 |
| REQ-18 | Zero grants: signed in, no delivery | spec | W0, W3 |
| REQ-19 | Granted `tenant_admin` still runs 013/016 delivery | spec | W3 |
| REQ-20 | Historic `POST /tenants/{id}/users` gone | spec | W2 |
| REQ-21 | 014 create+bind door deleted; leftover 1:1 binds wiped | spec | W0, W2 |
| REQ-22 | `tenant_admin` cannot directory-admin | spec | W1 |
| REQ-23 | `platform_admin` cannot run delivery | spec | W3 |
| REQ-24 | Suspended identity may still be granted/detached | spec | W1 |
| REQ-25 | Name required at enter | spec | W1 |
| REQ-26 | `tenant_admin` does not see factory roster | spec | W3 |
| REQ-27 | Programme onboard APIs unchanged | spec | W2 |
| REQ-28 | Unknown programme refused on grant/detach | spec | W1 |
| REQ-29 | Missing password refused | spec | W1 |
| REQ-30 | Password never returned on list/search/membership | spec | W1 |

---

## 2. Implementation phases

### Phase W0 — Membership schema + identity JWT session (ADR-019)

**GOAL-W0:** Programme scope is a membership row, not a `tenant_id` claim. Login mints `sub`/`role`/`session_epoch` only. Leftover 1:1 `user_identities.tenant_id` binds are wiped (not migrated).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Add `display_name`, `status`, `session_epoch`; drop `tenant_id`; create `programme_memberships`; Alembic via create script (human applies) | REQ-21 | — | `src/database/postgres/schema/user_identity_schema.py` modify; `src/database/postgres/schema/programme_membership_schema.py` create; `postgres_migrations/env.py` modify | Autogenerated revision creates membership table and drops `user_identities.tenant_id`; no dual-model column left | command | `./scripts/create_postgres_migration.sh "identity membership and session epoch"` | exit 0; revision under `postgres_migrations/versions/` | Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-01 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | N/A (unit-only task) | `database-migrations.mdc` — agent creates, human applies | ADR-001 (Postgres durable); ADR-019 | `feature/INIT-GATEFLOW-017-w0-session-membership` |
| TASK-W0-02 | Repositories: identity update/list; membership CRUD; remove `delete_for_tenant` | REQ-21 | TASK-W0-01 | `src/database/postgres/repository/user_identity_repository.py` modify; `src/database/postgres/repository/programme_membership_repository.py` create; `tests/unit/test_programme_membership_repository.py` create | Repo doubles can insert `(identity_id, programme_id)` uniquely and load by pair | command | `make test` | exit 0; unique-pair test green | Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-02 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | N/A (unit-only task) | `repository-pattern.mdc` | ADR-019 | `feature/INIT-GATEFLOW-017-w0-session-membership` |
| TASK-W0-03 | Drop middleware 401 for missing `tenant_id`; `require_role` loads identity (inactive + epoch); `require_programme_scope` loads membership | REQ-12, REQ-14, REQ-16 | TASK-W0-02 | `src/common/auth/middleware.py` modify; `src/common/auth/dependencies.py` modify; `tests/unit/test_auth_middleware.py` modify | `test_tenant_admin_missing_tenant_id_401` inverted; epoch mismatch and inactive status return 401 | command | `make check && make test` | exit 0; inverted test + new epoch/status cases green | Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-03 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | N/A (unit-only task) | `architecture.mdc` JWT verify | ADR-019 Option B | `feature/INIT-GATEFLOW-017-w0-session-membership` |
| TASK-W0-04 | `mint_user_jwt` writes `session_epoch`, no programme claim; login returns snapshot `{grants: []}` | REQ-03, REQ-16, REQ-18 | TASK-W0-03 | `src/business_services/auth_identity_service.py` modify; `src/models/auth_models.py` modify; `src/api/auth/login_routes.py` modify; `tests/unit/test_auth_identity_service.py` modify | Valid login 200 with token + empty grants; non-email identifier 422 `not an email`; JWT has no `tenant_id` | command | `pytest tests/unit/test_auth_identity_service.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-04 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_jwt_login` | `http-api-conventions.mdc` body models | ADR-019 | `feature/INIT-GATEFLOW-017-w0-session-membership` |
| TASK-W0-05 | Extend `verify_jwt_login`: platform_admin login still works; snapshot present; marker adds REQ-03, REQ-18 | REQ-03, REQ-18 | TASK-W0-04 | `tests/verify/verify_jwt_login.py` modify | Live login 200; response has `access_token` and `grants` array; marker includes REQ-03 and REQ-18 | command | `.venv/bin/python -m tests.verify.verify_jwt_login` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_jwt_login` | `testing-verify-flows.mdc` | ADR-019 | `feature/INIT-GATEFLOW-017-w0-session-membership` |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/database/postgres/schema/user_identity_schema.py` | modify |
| FILE-W0-02 | `src/database/postgres/schema/programme_membership_schema.py` | create |
| FILE-W0-03 | `postgres_migrations/env.py` | modify |
| FILE-W0-04 | `src/database/postgres/repository/user_identity_repository.py` | modify |
| FILE-W0-05 | `src/database/postgres/repository/programme_membership_repository.py` | create |
| FILE-W0-06 | `tests/unit/test_programme_membership_repository.py` | create |
| FILE-W0-07 | `src/common/auth/middleware.py` | modify |
| FILE-W0-08 | `src/common/auth/dependencies.py` | modify |
| FILE-W0-09 | `tests/unit/test_auth_middleware.py` | modify |
| FILE-W0-10 | `src/business_services/auth_identity_service.py` | modify |
| FILE-W0-11 | `src/models/auth_models.py` | modify |
| FILE-W0-12 | `src/api/auth/login_routes.py` | modify |
| FILE-W0-13 | `tests/unit/test_auth_identity_service.py` | modify |
| FILE-W0-14 | `tests/verify/verify_jwt_login.py` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-03, REQ-12, REQ-14, REQ-16, REQ-18, REQ-21 |
| TEST-W0-I | integration/contract | N/A — Alembic apply is human; no extra in-process I/O layer | — |
| TEST-W0-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_jwt_login` | REQ-03, REQ-18 |

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-03 login email shape | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-12 / REQ-14 epoch+status | TEST-W0-U | N/A | N/A | N/A | Live suspend/password in W1 |
| REQ-16 no remint / no tenant claim | TEST-W0-U | N/A | TEST-W0-L | N/A | Enter-programme in W3 |
| REQ-18 zero-grant snapshot | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-21 leftover bind wipe (schema) | TEST-W0-U | N/A | N/A | N/A | Door delete in W2 |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | yes — login response shape changes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | `make run`; human `./scripts/run_postgres_migration.sh head`; `auth.platform_admin` in `tests/config.yaml` |
| Safe test data | seeded `platform_admin` only |
| Steps / command | `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Expected observations | 200 login; token; `grants` present (may be empty) |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | none (seeded admin reused) |
| Stop conditions | Non-zero exit or 5xx → stop; do not start Pass-2 |

---

### Phase W1 — Identity directory + grant/detach

**GOAL-W1:** `platform_admin` enters, lists, suspends, sets password, grants, and detaches. Grant does not mint a JWT.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Pydantic directory/membership models + `IdentityStatusType` | REQ-01, REQ-30 | — | `src/models/identity_models.py` create; `src/models/identity_status_types.py` create | Models `extra=forbid`; no `password`/`password_hash` on read models | command | `make check` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-01 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | N/A (unit-only task) | `pydantic-schemas.mdc` — models in `src/models/` only | ADR-019 (membership DTO, not claim) | `feature/INIT-GATEFLOW-017-w1-identity-directory` |
| TASK-W1-02 | `IdentityDirectoryService` enter/list/search/suspend/unsuspend/set-password | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-12, REQ-13, REQ-14, REQ-25, REQ-29, REQ-30 | TASK-W1-01 | `src/business_services/identity_directory_service.py` create; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify; `tests/unit/test_identity_directory_service.py` create | Named refusals: `duplicate email`, `not an email`, `missing name`, `missing password`; suspend/password-set increment `session_epoch` | command | `pytest tests/unit/test_identity_directory_service.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-02 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | N/A (unit-only task) | `*_service` suffix; `@inject` | ADR-019 | `feature/INIT-GATEFLOW-017-w1-identity-directory` |
| TASK-W1-03 | Grant/detach/list-members/list-grants; refuse seeded `platform_admin` | REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-24, REQ-28 | TASK-W1-02 | `src/business_services/identity_directory_service.py` modify; `tests/unit/test_identity_directory_service.py` modify | Grant idempotent; unknown identity/programme 422; no JWT minted; suspend does not block grant | command | `pytest tests/unit/test_identity_directory_service.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-03 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | N/A (unit-only task) | body-only writes | ADR-019 (no remint on grant) | `feature/INIT-GATEFLOW-017-w1-identity-directory` |
| TASK-W1-04 | Routes: `/api/v1/identities` + `/api/v1/programmes/{id}/grants`; `wrong actor` | REQ-22 | TASK-W1-03 | `src/api/v1/identity_routes.py` create; `src/api/v1/programme_admin_routes.py` modify; `src/api/v1/__init__.py` modify | `tenant_admin` 403 `wrong actor` on enter/grant; `platform_admin` 200 | command | `pytest tests/unit/test_identity_routes.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-04 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_identity_directory` | `http-api-conventions.mdc` | ADR-019 | `feature/INIT-GATEFLOW-017-w1-identity-directory` |
| TASK-W1-05 | Create `verify_identity_directory` (overlap: no grant/directory artifact) | REQ-01, REQ-02, REQ-04, REQ-05, REQ-06, REQ-09, REQ-10, REQ-11, REQ-12, REQ-14, REQ-22, REQ-30 | TASK-W1-04 | `tests/verify/verify_identity_directory.py` create | Live enter → list → grant → detach → suspend → password-set; marker `prayog:covers:` lists those REQs | command | `.venv/bin/python -m tests.verify.verify_identity_directory` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_identity_directory` | `testing-verify-flows.mdc` | ADR-019 | `feature/INIT-GATEFLOW-017-w1-identity-directory` |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/models/identity_models.py` | create |
| FILE-W1-02 | `src/models/identity_status_types.py` | create |
| FILE-W1-03 | `src/business_services/identity_directory_service.py` | create |
| FILE-W1-04 | `src/di/modules/business_services_module.py` | modify |
| FILE-W1-05 | `src/di/dependency_container.py` | modify |
| FILE-W1-06 | `tests/unit/test_identity_directory_service.py` | create |
| FILE-W1-07 | `src/api/v1/identity_routes.py` | create |
| FILE-W1-08 | `src/api/v1/programme_admin_routes.py` | modify |
| FILE-W1-09 | `src/api/v1/__init__.py` | modify |
| FILE-W1-10 | `tests/unit/test_identity_routes.py` | create |
| FILE-W1-11 | `tests/verify/verify_identity_directory.py` | create |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-01…14, 22, 24, 25, 28, 29, 30 |
| TEST-W1-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_identity_directory` | REQ-01, REQ-02, REQ-04, REQ-05, REQ-06, REQ-09, REQ-10, REQ-11, REQ-12, REQ-14, REQ-22, REQ-30 |

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01, 02, 25, 29 enter | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-03 email on enter | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-04, 11, 30 list/search/membership | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-05, 06, 07, 08, 09, 10, 24, 28 grant/detach | TEST-W1-U | N/A | TEST-W1-L | N/A | REQ-07/08/24/28 unit-primary |
| REQ-12, 13, 14 suspend/password | TEST-W1-U | N/A | TEST-W1-L | N/A | REQ-13 unit + live unsuspend |
| REQ-22 wrong actor | TEST-W1-U | N/A | TEST-W1-L | N/A | |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | yes — new identity/grant HTTP surface |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W0 migrated DB; `make run`; `platform_admin` credentials; at least one onboarded programme |
| Safe test data | synthetic email identities; no prod mutation |
| Steps / command | `.venv/bin/python -m tests.verify.verify_identity_directory` |
| Expected observations | enter/grant/detach/suspend/password named outcomes |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | detach synthetic grants; leave or delete synthetic identities per script |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

### Phase W2 — Delete 014 doors + wipe collaborator + verify helper

**GOAL-W2:** Create+bind and historic handle-attach are gone. Wipe deletes memberships only. Verify provision is enter → grant → login.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Delete `attach_tenant_admin` and `POST /programmes/{id}/tenant-admins` | REQ-21 | — | `src/business_services/programme_service.py` modify; `src/api/v1/programme_admin_routes.py` modify; `tests/unit/test_programme_service.py` modify | Route absent (404/405); no attach method | command | `make test` | exit 0; attach tests negated | Wave-Execution-INIT-GATEFLOW-017-W2.md § TASK-W2-01 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | N/A | ADR-019 (no remint door) | `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` |
| TASK-W2-02 | Delete `POST /tenants/{id}/users` | REQ-20 | — | `src/api/v1/tenant_routes.py` modify | Historic attach path gone | command | `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W2.md § TASK-W2-02 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | N/A | N/A | `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` |
| TASK-W2-03 | Wipe deletes memberships only; identity rows remain; ACTIVE 409 unchanged | REQ-10, REQ-15, REQ-21 | TASK-W2-01 | `src/business_services/programme_wipe_service.py` modify; `tests/unit/test_programme_wipe_service.py` modify | After wipe, identity row exists; memberships for that programme gone; in-flight ACTIVE run still 409 | command | `pytest tests/unit/test_programme_wipe_service.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W2.md § TASK-W2-03 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | TDD FF-02 | ADR-019 (membership SSOT) | `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` |
| TASK-W2-04 | Rewrite `provision_programme_tenant_admin` to enter → grant → login | REQ-21 | TASK-W2-01 | `tests/_helpers/verify_jwt_auth.py` modify; `tests/verify/verify_programme_onboarding.py` modify; `tests/verify/verify_wipe_cutover.py` modify; `tests/verify/verify_dead_doors_deleted.py` modify; `tests/verify/verify_old_doors_refused.py` modify | Helper never calls attach; onboard live still creates programme (REQ-27); dead-door scripts assert 014/012 paths gone | command | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | TDD FF-03 | ADR-019 | `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/business_services/programme_service.py` | modify |
| FILE-W2-02 | `src/api/v1/programme_admin_routes.py` | modify |
| FILE-W2-03 | `tests/unit/test_programme_service.py` | modify |
| FILE-W2-04 | `src/api/v1/tenant_routes.py` | modify |
| FILE-W2-05 | `src/business_services/programme_wipe_service.py` | modify |
| FILE-W2-06 | `tests/unit/test_programme_wipe_service.py` | modify |
| FILE-W2-07 | `tests/_helpers/verify_jwt_auth.py` | modify |
| FILE-W2-08 | `tests/verify/verify_programme_onboarding.py` | modify |
| FILE-W2-09 | `tests/verify/verify_wipe_cutover.py` | modify |
| FILE-W2-10 | `tests/verify/verify_dead_doors_deleted.py` | modify |
| FILE-W2-11 | `tests/verify/verify_old_doors_refused.py` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-15, REQ-20, REQ-21 |
| TEST-W2-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | REQ-20, REQ-21 |

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-20 historic users door | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-21 create+bind gone | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-10 identity remains after wipe | TEST-W2-U | N/A | N/A | N/A | wipe script extended; wave command is dead-doors |
| REQ-15 in-flight wave | TEST-W2-U | N/A | N/A | N/A | ACTIVE 409 unchanged |
| REQ-27 onboard unchanged | N/A | N/A | TEST-W2-L (onboarding script still run in helper rewrite) | N/A | inspect via existing onboard script |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | yes — deleted HTTP doors |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W1 live; `make run` |
| Safe test data | POST to deleted paths only |
| Steps / command | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` |
| Expected observations | 014 attach and 012 users paths absent/refused |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | none |
| Stop conditions | Non-zero exit → stop |

---

### Phase W3 — Enter programme + delivery isolation + as-built

**GOAL-W3:** Signed-in identity enters a granted programme without remint; delivery isolation and 013/016 acts hold; as-built records the cut.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | `GET /api/auth/me` + `POST /api/auth/session/programme` (grant check, no remint) | REQ-16, REQ-18, REQ-26 | — | `src/api/auth/login_routes.py` modify; `src/business_services/auth_identity_service.py` modify; `src/models/auth_models.py` modify; `tests/unit/test_auth_identity_service.py` modify | Enter granted programme 200 snapshot; not granted 403 `not granted`; no new JWT; `tenant_admin` me has no factory roster | command | `pytest tests/unit/test_auth_identity_service.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-017-W3.md § TASK-W3-01 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` | body-only POST | ADR-019 Option B | `feature/INIT-GATEFLOW-017-w3-enter-programme` |
| TASK-W3-02 | Extend isolation + jwt_login: two grants, delivery, `platform_admin` `wrong actor` | REQ-16, REQ-17, REQ-19, REQ-23 | TASK-W3-01 | `tests/verify/verify_cross_programme_isolation.py` modify; `tests/verify/verify_jwt_login.py` modify | Live: enter granted, refuse other, two-programme delivery, platform_admin delivery 403 | command | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` | P15 extend isolation | ADR-016 (path tenant after membership); ADR-019 | `feature/INIT-GATEFLOW-017-w3-enter-programme` |
| TASK-W3-03 | As-built detail + index row | REQ-19, REQ-27 | TASK-W3-02 | `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-017.md` create; `docs/specification/as-built/implementation-status.md` modify | Index has one 017 row pointing at the detail file | review | PE reviews as-built row vs live verify | one index row; detail lists W0–W3 | Wave-Execution-INIT-GATEFLOW-017-W3.md § TASK-W3-03 | gateflow | docs/specification/product/INIT-GATEFLOW-017-gateflow.md | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` | P9 as-built | N/A | `feature/INIT-GATEFLOW-017-w3-enter-programme` |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/api/auth/login_routes.py` | modify |
| FILE-W3-02 | `src/business_services/auth_identity_service.py` | modify |
| FILE-W3-03 | `src/models/auth_models.py` | modify |
| FILE-W3-04 | `tests/unit/test_auth_identity_service.py` | modify |
| FILE-W3-05 | `tests/verify/verify_cross_programme_isolation.py` | modify |
| FILE-W3-06 | `tests/verify/verify_jwt_login.py` | modify |
| FILE-W3-07 | `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-017.md` | create |
| FILE-W3-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-16, REQ-18, REQ-26 |
| TEST-W3-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` | REQ-16, REQ-17, REQ-19, REQ-23 |

#### Verification Coverage (W3)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-16 enter granted / not granted | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-17 two programmes | N/A | N/A | TEST-W3-L | N/A | |
| REQ-18 zero grants no delivery | TEST-W3-U | N/A | TEST-W3-L | N/A | jwt_login extended |
| REQ-19 delivery acts | N/A | N/A | TEST-W3-L | N/A | |
| REQ-23 platform_admin delivery | N/A | N/A | TEST-W3-L | N/A | |
| REQ-26 no factory roster on tenant me | TEST-W3-U | N/A | N/A | N/A | |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | yes — enter-programme + isolation |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W1+W2 live; two programmes; `make run` |
| Safe test data | synthetic grants |
| Steps / command | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` |
| Expected observations | granted enter works; cross-programme 403; platform_admin delivery 403 |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | detach synthetic grants |
| Stop conditions | Non-zero exit → stop |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | Human applies W0 Alembic (`run_postgres_migration.sh head`) | W0 live + all later waves |
| DEP-02 | W0 session model on `develop`/wave merge | W1 directory |
| DEP-03 | W1 enter+grant live | W2 door delete (verify helper rewrite) |
| DEP-04 | gateflow-ops identity screens | Out of this repo — IM-03: after this provider is live |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Lab DB has 014 1:1 binds; dual-model temptation | W0 drops `tenant_id`; no migrate-to-membership path (REQ-21) |
| RISK-02 | Existing verify scripts still call attach JWT | W2 rewrites helper in the same wave as door delete (FF-03) |
| RISK-03 | Wipe accidentally deletes identity rows | W2 unit asserts row remains (FF-02) |
| RISK-04 | Live.covers vs 014 markers disjoint at plan time | W0/W2/W3 covers include an intersecting 014 marker id until the wave rewrites the marker |
| RISK-05 | Ops ships invite/screens on 1:1 bind | Out of repo; IM-02/IM-03; PM-3 |

---

## 5. Out of scope

- gateflow-ops console (consumer)
- SSO / IdP
- Delete-identity, change email, self-serve password
- Extra roles beyond `platform_admin` / `tenant_admin`
- Rewrite 013/016 delivery except invite absence
- Encrypting secrets
- Programme wipe deleting the identity (forbidden)

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Create per-initiative as-built detail | `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-017.md` | W3 — KEEP |
| Update as-built index row | `docs/specification/as-built/implementation-status.md` | W3 — one row, pointer |
| Live-verify coverage marker | co-shipped/extended `tests/verify/*` | Self-declare `prayog:covers:` — do not edit `tests/README.md` for coverage |

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 | PASS — REQ-01…30 in §1; each wave Implements those REQs |
| P2 | PASS — every REQ has ≥1 TASK; every TASK Implements ≥1 REQ |
| P3 | PASS — every TASK has FILE paths |
| P4 | PASS — observable exit + proof + expected + evidence_expected |
| P5 | PASS — unit + smoke mapped; integration N/A (Alembic human) |
| P6 | PASS — no ops/SSO/delete-identity |
| P7 | PASS — FF-01 ADR-019; FF-02/03 TDD_ONLY in W2; PM deferred |
| P8 | PASS — W0→W1→W2→W3 |
| P9 | PASS — as-built in W3 |
| P10 | PASS — commands resolved; live prereqs stated |
| P11 | PASS — MDC notes on TASKs |
| P12 | PASS — ADR-019 Accepted on head `9e86e6d` |
| P13 | PASS — TDD Accepted; lint `--verify-lint-evidence` PASS |
| P14 | PASS — §9 waves W0–W3 match |
| P15 | PASS — overlap recorded; one new verify file (W1); others extend |
| P16 | PASS — `workmanifest_contract.py` (run after write) |

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` to Draft spec PR #243.
> Do **not** commit inside this skill. Label remains **`spec-pending`** until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-017-spec-gateflow
PR title: "[INIT-GATEFLOW-017] Spec — One human, many programmes, one login (gateflow)"
Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-19
```

After spec-lgtm + Approve + merge — **`/create-board-tickets`** from §9 (post-merge only).

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16; Accepted TDD/ADR-019; sources CURRENT |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/243 |
| Spec PR head SHA | `9e86e6d354d44226a5a4a66bab0c73d1112569db` (plan not yet on this SHA) |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md` |
| Forge readiness | `handoff.forge.action: commit_workspace` |
| Blocking items | none after `/commit-workspace` publishes this plan |

PE actions (all on **exact current head** after plan publish):

1. Remove `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale`; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/create-board-tickets`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-017
spec_pr_head_sha: {SHA after plan commit}
meta_pr_head_sha: 601b00e0a74510a6af1c33bc80ca27260995c094
impact_map_revision: 1
prd_digest: sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67
scope_digest: sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834
plan_digest: sha256:{hex of this plan file}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-017-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-017.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md
  - docs/specification/adr/adr-019-identity-jwt-programme-scope-and-session-epoch.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md
```

---

## 9. WorkManifest seed

```yaml
# Generated by /spec-implementation-plan — 2026-08-14
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-017

metadata:
  title: INIT-GATEFLOW-017 — One human, many programmes, one login
  summary: |
    Replace 014 create+bind with enter-then-grant. Identity JWT has no
    programme claim; scope is a membership row; session_epoch invalidates
    decoded JWTs. Wipe removes grants only. Historic attach doors are deleted.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-017-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-017
  parent: EPIC
  labels:
    - INIT-GATEFLOW-017

epic:
  id: EPIC
  repo: gateflow
  title: "[feature] INIT-GATEFLOW-017 — One human, many programmes, one login"
  codebase: gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_identity_directory
  body: |
    ## Objective

    Enter-then-grant identity APIs; N programme memberships on one identity
    JWT; suspend/password invalidate sessions; delete 014 create+bind.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Membership schema + identity JWT session (ADR-019) |
    | W1 | Identity directory + grant/detach |
    | W2 | Delete 014 doors + wipe collaborator + verify helper |
    | W3 | Enter programme + delivery isolation + as-built |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md

work:
  - id: W0
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-017 W0] Membership schema + identity JWT session"
    depends_on: []
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_jwt_login
    tasks:
      - id: TASK-W0-01
        implements: [REQ-21]
        depends_on: []
        files:
          - path: src/database/postgres/schema/user_identity_schema.py
            action: modify
          - path: src/database/postgres/schema/programme_membership_schema.py
            action: create
          - path: postgres_migrations/env.py
            action: modify
        exit:
          criteria:
            - "Alembic create script emits a revision that adds programme_memberships and drops user_identities.tenant_id"
          proof:
            kind: command
            command: ./scripts/create_postgres_migration.sh "identity membership and session epoch"
            expected: "exit 0; new file under postgres_migrations/versions/"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-21]
        depends_on: [TASK-W0-01]
        files:
          - path: src/database/postgres/repository/user_identity_repository.py
            action: modify
          - path: src/database/postgres/repository/programme_membership_repository.py
            action: create
          - path: tests/unit/test_programme_membership_repository.py
            action: create
        exit:
          criteria:
            - "Repository inserts a unique (identity_id, programme_id) pair and loads it back"
          proof:
            kind: command
            command: make test
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-12, REQ-14, REQ-16]
        depends_on: [TASK-W0-02]
        files:
          - path: src/common/auth/middleware.py
            action: modify
          - path: src/common/auth/dependencies.py
            action: modify
          - path: tests/unit/test_auth_middleware.py
            action: modify
        exit:
          criteria:
            - "TENANT_ADMIN without tenant_id claim is not 401; epoch mismatch and inactive status are 401"
          proof:
            kind: command
            command: make check && make test
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-03, REQ-16, REQ-18]
        depends_on: [TASK-W0-03]
        files:
          - path: src/business_services/auth_identity_service.py
            action: modify
          - path: src/models/auth_models.py
            action: modify
          - path: src/api/auth/login_routes.py
            action: modify
          - path: tests/unit/test_auth_identity_service.py
            action: modify
        exit:
          criteria:
            - "Login 200 includes access_token and grants array; minted JWT has no tenant_id"
          proof:
            kind: command
            command: pytest tests/unit/test_auth_identity_service.py -q
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-03, REQ-18]
        depends_on: [TASK-W0-04]
        files:
          - path: tests/verify/verify_jwt_login.py
            action: modify
        exit:
          criteria:
            - "Live login 200 with grants field; marker includes REQ-03 and REQ-18"
          proof:
            kind: command
            command: .venv/bin/python -m tests.verify.verify_jwt_login
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: make check
      unit: make test
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_jwt_login
        covers: [REQ-03, REQ-18]
        prerequisites:
          - "make run"
          - "human applied ./scripts/run_postgres_migration.sh head"
          - "auth.platform_admin in tests/config.yaml"
        safe_test_data:
          - "seeded platform_admin only"
        steps:
          - "Run verify_jwt_login"
        expected_observations:
          - "200 login with access_token and grants array"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "none — seeded admin reused"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Membership schema + identity JWT session (ADR-019).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-21 | — | Alembic revision adds memberships, drops tenant_id | command / create_postgres_migration.sh |
      | TASK-W0-02 | REQ-21 | TASK-W0-01 | Unique membership pair persists | command / make test |
      | TASK-W0-03 | REQ-12, REQ-14, REQ-16 | TASK-W0-02 | Missing tenant_id not 401; epoch/status 401 | command / make check && make test |
      | TASK-W0-04 | REQ-03, REQ-16, REQ-18 | TASK-W0-03 | Login snapshot; no tenant_id claim | command / pytest test_auth_identity_service |
      | TASK-W0-05 | REQ-03, REQ-18 | TASK-W0-04 | Live login + grants field | command / verify_jwt_login |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-017-gateflow.md

  - id: W1
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-017 W1] Identity directory + grant/detach"
    depends_on:
      - W0
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_identity_directory
    tasks:
      - id: TASK-W1-01
        implements: [REQ-01, REQ-30]
        depends_on: []
        files:
          - path: src/models/identity_models.py
            action: create
          - path: src/models/identity_status_types.py
            action: create
        exit:
          criteria:
            - "Read models forbid extra fields and omit password and password_hash"
          proof:
            kind: command
            command: make check
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-12, REQ-13, REQ-14, REQ-25, REQ-29, REQ-30]
        depends_on: [TASK-W1-01]
        files:
          - path: src/business_services/identity_directory_service.py
            action: create
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
          - path: tests/unit/test_identity_directory_service.py
            action: create
        exit:
          criteria:
            - "Enter/list/suspend/password-set return named refusals; session_epoch increments on suspend and password-set"
          proof:
            kind: command
            command: pytest tests/unit/test_identity_directory_service.py -q
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-24, REQ-28]
        depends_on: [TASK-W1-02]
        files:
          - path: src/business_services/identity_directory_service.py
            action: modify
          - path: tests/unit/test_identity_directory_service.py
            action: modify
        exit:
          criteria:
            - "Grant is idempotent; unknown identity or programme is 422; grant does not mint a JWT"
          proof:
            kind: command
            command: pytest tests/unit/test_identity_directory_service.py -q
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-22]
        depends_on: [TASK-W1-03]
        files:
          - path: src/api/v1/identity_routes.py
            action: create
          - path: src/api/v1/programme_admin_routes.py
            action: modify
          - path: src/api/v1/__init__.py
            action: modify
          - path: tests/unit/test_identity_routes.py
            action: create
        exit:
          criteria:
            - "tenant_admin receive 403 wrong actor on enter and grant; platform_admin succeed"
          proof:
            kind: command
            command: pytest tests/unit/test_identity_routes.py -q
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-01, REQ-02, REQ-04, REQ-05, REQ-06, REQ-09, REQ-10, REQ-11, REQ-12, REQ-14, REQ-22, REQ-30]
        depends_on: [TASK-W1-04]
        files:
          - path: tests/verify/verify_identity_directory.py
            action: create
        exit:
          criteria:
            - "Live enter, list, grant, detach, suspend, and password-set succeed with named outcomes"
          proof:
            kind: command
            command: .venv/bin/python -m tests.verify.verify_identity_directory
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: make check
      unit: make test
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_identity_directory
        covers: [REQ-01, REQ-02, REQ-04, REQ-05, REQ-06, REQ-09, REQ-10, REQ-11, REQ-12, REQ-14, REQ-22, REQ-30]
        prerequisites:
          - "W0 migrated database"
          - "make run"
          - "platform_admin credentials"
          - "at least one onboarded programme"
        safe_test_data:
          - "synthetic email identities"
        steps:
          - "Run verify_identity_directory"
        expected_observations:
          - "enter/grant/detach/suspend/password-set named outcomes"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "detach synthetic grants"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Identity directory + grant/detach.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-01, REQ-30 | — | Read models omit password | command / make check |
      | TASK-W1-02 | REQ-01…05, 12–14, 25, 29, 30 | TASK-W1-01 | Named enter/suspend/password refusals | command / pytest |
      | TASK-W1-03 | REQ-05…11, 24, 28 | TASK-W1-02 | Grant idempotent; no JWT | command / pytest |
      | TASK-W1-04 | REQ-22 | TASK-W1-03 | wrong actor 403 | command / pytest |
      | TASK-W1-05 | REQ-01, 02, 04–06, 09–12, 14, 22, 30 | TASK-W1-04 | Live directory journey | command / verify_identity_directory |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-017-gateflow.md

  - id: W2
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-017 W2] Delete 014 doors + wipe collaborator"
    depends_on:
      - W1
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
    tasks:
      - id: TASK-W2-01
        implements: [REQ-21]
        depends_on: []
        files:
          - path: src/business_services/programme_service.py
            action: modify
          - path: src/api/v1/programme_admin_routes.py
            action: modify
          - path: tests/unit/test_programme_service.py
            action: modify
        exit:
          criteria:
            - "POST /api/v1/programmes/{id}/tenant-admins is absent (404 or 405)"
          proof:
            kind: command
            command: make test
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-20]
        depends_on: []
        files:
          - path: src/api/v1/tenant_routes.py
            action: modify
        exit:
          criteria:
            - "POST /api/v1/tenants/{id}/users is absent (404 or 405)"
          proof:
            kind: command
            command: make test
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-10, REQ-15, REQ-21]
        depends_on: [TASK-W2-01]
        files:
          - path: src/business_services/programme_wipe_service.py
            action: modify
          - path: tests/unit/test_programme_wipe_service.py
            action: modify
        exit:
          criteria:
            - "Wipe removes memberships for that programme and leaves the identity row; ACTIVE run still 409"
          proof:
            kind: command
            command: pytest tests/unit/test_programme_wipe_service.py -q
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W2.md § TASK-W2-03"
      - id: TASK-W2-04
        implements: [REQ-21, REQ-27]
        depends_on: [TASK-W2-01]
        files:
          - path: tests/_helpers/verify_jwt_auth.py
            action: modify
          - path: tests/verify/verify_programme_onboarding.py
            action: modify
          - path: tests/verify/verify_wipe_cutover.py
            action: modify
          - path: tests/verify/verify_dead_doors_deleted.py
            action: modify
          - path: tests/verify/verify_old_doors_refused.py
            action: modify
        exit:
          criteria:
            - "Provision helper uses enter then grant then login; dead-door live script reports 014 and 012 paths gone"
          proof:
            kind: command
            command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: make check
      unit: make test
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
        covers: [REQ-08, REQ-20, REQ-21, REQ-34, REQ-35, REQ-37]
        prerequisites:
          - "W1 live"
          - "make run"
        safe_test_data:
          - "POST to deleted paths only"
        steps:
          - "Run verify_dead_doors_deleted"
        expected_observations:
          - "014 attach and 012 users paths absent or refused"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "none"
        stop_conditions:
          - "Non-zero exit → stop"
    body: |
      ## Wave goal

      Delete 014 doors + wipe collaborator + verify helper.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-21 | — | attach route gone | command / make test |
      | TASK-W2-02 | REQ-20 | — | historic users route gone | command / make test |
      | TASK-W2-03 | REQ-10, REQ-15, REQ-21 | TASK-W2-01 | wipe keeps identity row | command / pytest |
      | TASK-W2-04 | REQ-21, REQ-27 | TASK-W2-01 | helper enter-grant-login; doors gone live | command / verify_dead_doors_deleted |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-017-gateflow.md

  - id: W3
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-017 W3] Enter programme + isolation + as-built"
    depends_on:
      - W2
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_cross_programme_isolation
    tasks:
      - id: TASK-W3-01
        implements: [REQ-16, REQ-18, REQ-26]
        depends_on: []
        files:
          - path: src/api/auth/login_routes.py
            action: modify
          - path: src/business_services/auth_identity_service.py
            action: modify
          - path: src/models/auth_models.py
            action: modify
          - path: tests/unit/test_auth_identity_service.py
            action: modify
        exit:
          criteria:
            - "POST /api/auth/session/programme returns 200 for a grant and 403 not granted without reminting a JWT"
          proof:
            kind: command
            command: pytest tests/unit/test_auth_identity_service.py -q
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W3.md § TASK-W3-01"
      - id: TASK-W3-02
        implements: [REQ-16, REQ-17, REQ-19, REQ-23]
        depends_on: [TASK-W3-01]
        files:
          - path: tests/verify/verify_cross_programme_isolation.py
            action: modify
          - path: tests/verify/verify_jwt_login.py
            action: modify
        exit:
          criteria:
            - "Live enter granted succeeds; other programme 403; platform_admin delivery 403"
          proof:
            kind: command
            command: .venv/bin/python -m tests.verify.verify_cross_programme_isolation
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W3-03
        implements: [REQ-19, REQ-27]
        depends_on: [TASK-W3-02]
        files:
          - path: docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-017.md
            action: create
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "implementation-status.md has exactly one INIT-GATEFLOW-017 index row pointing at the detail file"
          proof:
            kind: review
            review: "PE reviews as-built index row against W0-W3 live verify"
            expected: "one index row; detail lists W0-W3"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-017-W3.md § TASK-W3-03"
    verification:
      check: make check
      unit: make test
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_cross_programme_isolation
        covers: [REQ-03, REQ-16, REQ-17, REQ-19, REQ-23]
        prerequisites:
          - "W1 and W2 live"
          - "two onboarded programmes"
          - "make run"
        safe_test_data:
          - "synthetic grants"
        steps:
          - "Run verify_cross_programme_isolation"
        expected_observations:
          - "granted enter works; cross-programme 403; platform_admin delivery 403"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "detach synthetic grants"
        stop_conditions:
          - "Non-zero exit → stop"
    body: |
      ## Wave goal

      Enter programme + delivery isolation + as-built.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W3-01 | REQ-16, REQ-18, REQ-26 | — | enter-programme no remint | command / pytest |
      | TASK-W3-02 | REQ-16, REQ-17, REQ-19, REQ-23 | TASK-W3-01 | live isolation | command / verify_cross_programme_isolation |
      | TASK-W3-03 | REQ-19, REQ-27 | TASK-W3-02 | as-built index row | review |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-017-gateflow.md
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_pr_head: "9e86e6d354d44226a5a4a66bab0c73d1112569db"
    source_freshness: current
    ready_for_pe_review: true
    ready_for_plan: true
    new_adr: false
    accepted_adr_files:
      - docs/specification/adr/adr-019-identity-jwt-programme-scope-and-session-epoch.md
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```
