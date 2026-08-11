---
goal: INIT-GATEFLOW-014 — One identity to call Gateflow, retire shared-secret doors
initiative: INIT-GATEFLOW-014
status: Planned
date_created: 2026-08-10
source_spec: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-014.md
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md
prd_digest: sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-014.md
impact_map_revision: 1
repo_scope_digest: sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef
approved_meta_pr_head: 3120e4eff4b4dfe86ed1a14f02439d62bc6151c7
branch: chore/INIT-GATEFLOW-014-spec-gateflow
review_deadline: 2026-08-13
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-014

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` | CURRENT |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-014.md` (revision 2, `pass`) | CURRENT |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md` (`Status: Accepted`) | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-014.md` / `1` | CURRENT |
| Repo scope digest | `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` | CURRENT |
| Approved meta PR head | `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7` | CURRENT — re-verified via `gh pr view` this session |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` (`.venv/bin/pytest tests/unit/ -v`) | RESOLVED |
| `verify_command` | `.venv/bin/python -m tests.verify.<script>` (per wave below; no single command covers all waves) | RESOLVED |
| `ground_command` | N/A — this repo has no dedicated ground-truth script; `/ground-spec` verifies against as-built + spec citations directly, not a runnable command | N/A |

Spec PR: [#212](https://github.com/drivestream-lab/gateflow/pull/212), head `7f212feb3267628b7448c3e56460c0f727e5236c` (local artifacts below not yet published to this head).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md` |
| Technical review status | **Accepted** |
| PE sign-off | [x] complete — 2026-08-10, @nikd10x, Cursor chat, Draft spec PR #212 |
| Resolved ADRs | [`adr-014`](../adr/adr-014-jwt-only-product-edge-trust-zone.md) (Accepted — JWT-only edge, supersedes ADR-002/005/011), [`adr-015`](../adr/adr-015-programme-scoped-forge-credential-resolution.md) (Accepted — `ForgeClientFactory` per-programme credential resolution), [`adr-016`](../adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md) (Accepted — tenant-scoped run/board/checkpoint authorization) |
| ADR product-boundary re-check | All 3: `changes_user_visible_behavior: false`, `spec_amendment_required: false` confirmed in file headers. Re-ran `adr_boundary_lint.py --require-sources` at plan time with sources reconstructed from the spec's REQ sentences (not a bare structure-only pass) — see command log below. All 3 PASS |
| Outstanding PM questions | none — PM-1, PM-2 resolved (`Technical-Review-INIT-GATEFLOW-014.md` §9/§10) |
| Outstanding domain questions | none |

**P13 lint re-check command log (source parity, not a bare re-run):**

```text
adr-014-jwt-only-product-edge-trust-zone.md --require-sources --source-text <REQ-04,06,28,29,32,33 sentences from spec> → PASS
adr-015-programme-scoped-forge-credential-resolution.md --require-sources --source-text <REQ-11,14,25 sentences from spec> → PASS
adr-016-tenant-scoped-run-board-checkpoint-authorization.md --require-sources --source-text <REQ-23,24,31 sentences from spec> → PASS
```

> Do not start W0 implementation until PE sign-off is marked complete above (it is).

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Seed script creates `platform_admin` + can mint JWT | spec §Functional requirements | W0 |
| REQ-02 | Login API returns Gateflow-issued JWT | spec | W0 |
| REQ-03 | Invalid login refused, no JWT | spec | W0 |
| REQ-04 | Product APIs accept only Gateflow-issued JWT | spec | W0, W2 |
| REQ-05 | Bad JWT (missing/malformed/expired/wrong-issuer) refused | spec | W0 |
| REQ-06 | JWT identifies user + role; `tenant_admin` bound to Programme | spec | W0 |
| REQ-07 | PAT/agent keys never accepted as caller Bearer | spec | W0 |
| REQ-08 | `platform_admin` validate-then-create Programme | spec | W1 |
| REQ-09 | Validation before durable create | spec | W1 |
| REQ-10 | Validation failure leaves no row | spec | W1 |
| REQ-11 | Programme stores own PAT, not factory-global | spec | W1 |
| REQ-12 | Workspace root set at onboard | spec | W1 |
| REQ-13 | Agent keys rejected on Programme onboard | spec | W1 |
| REQ-14 | GitHub App fields reserved unused | spec | W1 |
| REQ-15 | Attach `tenant_admin` to Programme | spec | W1 |
| REQ-16 | Only one programme role type | spec | W1 |
| REQ-17 | `platform_admin` can list programmes | spec | W1 |
| REQ-18 | `platform_admin` cannot onboard/deboard repos or start runs | spec | W1 |
| REQ-19 | Provision Cursor into platform DB catalogue | spec | W1 |
| REQ-20 | Catalogue reserves slots for other runners | spec | W1 |
| REQ-21 | Start resolves effective runner (caller or lane default) | spec | W1 |
| REQ-22 | Missing/unprovisioned effective runner rejected | spec | W1 |
| REQ-23 | `tenant_admin` JWT authorizes repo lifecycle for its programme | spec | W2 |
| REQ-24 | `tenant_admin` JWT authorizes control-plane reads/actions for its programme | spec | W2 |
| REQ-25 | Outbound forge/git uses that programme's stored credential | spec | W2 |
| REQ-26 | Agent dispatch loads credential only from DB catalogue | spec | W2 |
| REQ-27 | Pin explicit/automated forge authorize policy unchanged | spec | W2 |
| REQ-28 | Webhooks remain signature-checked | spec | W2 |
| REQ-29 | Unauthenticated product calls fail closed | spec | W2 |
| REQ-30 | Role mismatch fails closed | spec | W2 |
| REQ-31 | Cross-programme access fails closed | spec | W2 |
| REQ-32 | Programme service token refused once JWT edge live | spec | W2 |
| REQ-33 | Tenant bearer refused once JWT edge live | spec | W2 |
| REQ-34 | Open tenant register removed | spec | W3 |
| REQ-35 | 012/013 lab tenants wiped at cutover | spec | W3 |
| REQ-36 | Verify scripts prove JWT happy path | spec | W4 |
| REQ-37 | Verify scripts prove refusal of old doors | spec | W4 |
| REQ-38 | Teaching surfaces describe JWT + per-programme GitHub + DB catalogue only | spec | W4 |
| REQ-40 | Platform agent catalogue is a durable DB table | spec | W1 |
| REQ-41 | Start uses only catalogue credential; env `CURSOR_API_KEY` never authorizes | spec | W1, W2 |
| REQ-42 | Programme per-lane runner+model defaults | spec | W1 |
| REQ-43 | Invalid login refused, named outcome | spec | W0 |
| REQ-44 | Attach to unknown programme rejected | spec | W1 |
| REQ-45 | Blank/missing agent key rejected | spec | W1 |
| REQ-46 | Wipe mid-run rejected | spec | W3 |
| REQ-47 | Re-seed / re-attach idempotent | spec | W1 |

---

## 2. Implementation phases

### Phase W0 — Seed `platform_admin` + JWT mint/login edge

**GOAL-W0:** Gateflow-issued user JWTs exist and can be minted (seed) or obtained (login); `AuthMiddleware` correctly shapes role + tenant claims for both roles without inventing a second verification stack (ADR-014).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | `RoleType(str, Enum)` in new module; `AuthContext.role` retyped | REQ-06 | — | `src/models/role_types.py` create; `src/models/auth_models.py` modify | `AuthContext(role=...)` rejects a non-enum string at construction | command | `make check && pytest tests/unit/test_auth_middleware.py -k role -q` | exit 0; invalid role raises `ValidationError` | Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-01 | gateflow | spec §REQ-06 | N/A (unit-only task) | `pydantic-schemas.mdc` Domain enums — TDD §9 E1 | ADR-014 (no new verification mechanism) | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W0-02 | `test_auth_middleware.py`: expiry, wrong issuer/audience, malformed token, role/tenant claim extraction, unrecognized role | REQ-05 | TASK-W0-01 | `tests/unit/test_auth_middleware.py` create | 6+ negative-path unit cases all assert 401 with named reason | command | `pytest tests/unit/test_auth_middleware.py -v` | exit 0; all cases pass | Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-02 | gateflow | spec §REQ-05 | N/A (unit-only task) | `testing-verify-flows.mdc` pytest scope — TDD §9 E3 | ADR-014 | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W0-03 | `UserIdentitySchema` + repository for `platform_admin`/`tenant_admin` user rows | REQ-01 | — | `src/database/postgres/schema/user_identity_schema.py` create; `src/database/postgres/repository/user_identity_repository.py` create | Repository creates + reads a user row by credential identifier | command | `pytest tests/unit/test_user_identity_repository.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-03 | gateflow | spec §REQ-01 | N/A (unit-only task) | `repository-pattern.mdc` — ORM confined to repository | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W0-04 | Seed script creates/idempotently re-seeds `platform_admin` and mints a JWT | REQ-01, REQ-47 | TASK-W0-03 | `scripts/seed_platform_admin.py` create | Running the script twice yields one `platform_admin` row and two valid, independently-verifiable JWTs | command | `.venv/bin/python scripts/seed_platform_admin.py && .venv/bin/python scripts/seed_platform_admin.py` | exit 0 both runs; row count stays 1 | Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-04 | gateflow | spec §REQ-01, REQ-47 | `.venv/bin/python -m tests.verify.verify_jwt_login` | `dependency-injection.mdc` — script uses `configure_container()` | ADR-014 | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W0-05 | `AuthIdentityService.login` + `POST /api/auth/login` (no UI); credential verification | REQ-02, REQ-03, REQ-43 | TASK-W0-03 | `src/business_services/auth_identity_service.py` create; `src/api/auth/login_routes.py` create | Valid credentials → 200 + JWT; invalid → 401 named `UNAUTHORIZED`, zero token | command | `pytest tests/unit/test_auth_identity_service.py -v` | exit 0; both paths asserted | Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-05 | gateflow | spec §REQ-02, REQ-03, REQ-43 | `.venv/bin/python -m tests.verify.verify_jwt_login` | `http-api-conventions.mdc` — POST body model, not query | ADR-014 (reuses `AuthMiddleware`'s existing decode path — TDD §3.1) | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W0-06 | Confirm exact JWT claim shape (`sub`, `role`, `tenant_id`, `iss`/`aud`/`exp`/`iat`) matches TDD §3.1/E5; no `public_paths` change yet (deferred to W2 per E6) | REQ-04, REQ-06, REQ-07 | TASK-W0-05 | `src/common/auth/middleware.py` modify (role/tenant claim extraction only — no allowlist change) | Minted JWT round-trips through `AuthMiddleware.dispatch` producing a `AuthContext` with correct `role`/`tenant_id` | command | `pytest tests/unit/test_auth_middleware.py -k claim_shape -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-06 | gateflow | spec §REQ-04, REQ-06, REQ-07 | `.venv/bin/python -m tests.verify.verify_jwt_login` | N/A | ADR-014 (TDD §9 E5 claim shape) | `chore/INIT-GATEFLOW-014-spec-gateflow` |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/models/role_types.py` | create |
| FILE-W0-02 | `src/models/auth_models.py` | modify |
| FILE-W0-03 | `tests/unit/test_auth_middleware.py` | create |
| FILE-W0-04 | `src/database/postgres/schema/user_identity_schema.py` | create |
| FILE-W0-05 | `src/database/postgres/repository/user_identity_repository.py` | create |
| FILE-W0-06 | `tests/unit/test_user_identity_repository.py` | create |
| FILE-W0-07 | `scripts/seed_platform_admin.py` | create |
| FILE-W0-08 | `src/business_services/auth_identity_service.py` | create |
| FILE-W0-09 | `tests/unit/test_auth_identity_service.py` | create |
| FILE-W0-10 | `src/api/auth/login_routes.py` | create |
| FILE-W0-11 | `src/common/auth/middleware.py` | modify |
| FILE-W0-12 | `tests/verify/verify_jwt_login.py` | create |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` (`pytest tests/unit/test_auth_middleware.py tests/unit/test_auth_identity_service.py tests/unit/test_user_identity_repository.py -v`) | REQ-01, REQ-02, REQ-03, REQ-05, REQ-06, REQ-07, REQ-43, REQ-47 |
| TEST-W0-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_jwt_login` (human-run) | REQ-01, REQ-02, REQ-03, REQ-43 |

**Overlap check (P15, before declaring TEST-W0-L a new FILE):** `python -m scripts.verify_coverage_query tests/verify --capability jwt` and `--capability login` run against `tests/verify/` this session — zero existing artifacts carry a `prayog:covers:` marker at all (31/31 legacy, unmarked). No candidate to extend; `verify_jwt_login.py` is a new FILE, declared with the marker convention going forward.

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01 seed idempotency | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-02 login happy path | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-03 / REQ-43 invalid login refused | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-05 bad JWT refused | TEST-W0-U | one boundary: real RS256 key round-trip | N/A | N/A | Integration = sign in test, verify in middleware (TDD §5) |
| REQ-06 / REQ-07 claim shape | TEST-W0-U | N/A | TEST-W0-L | N/A | |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API up (`make run`); `JWT_PUBLIC_KEY_PATH`/`JWT_PRIVATE_KEY_PATH` or `JWT_SECRET_KEY` set |
| Safe test data | Synthetic seed identity `platform_admin@smoke.local` |
| Steps / command | `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Expected observations | Script prints PASS for seed-mint, login-happy-path, and login-refuse cases; exits 0 |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | None required — no durable state beyond the seeded admin row, which is idempotent |
| Stop conditions | Non-zero exit or any 5xx → stop; do not proceed to W1 |

---

### Phase W1 — Programme validate-then-create + `tenant_admin` attach + platform DB agent catalogue

**GOAL-W1:** `platform_admin` can validate-then-create a Programme (owning its own PAT/workspace/lane defaults), attach `tenant_admin`, and provision the platform agent catalogue that twin/initiative starts will resolve against.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | `ProgrammeSchema` (PAT, workspace root, per-lane defaults) + repository | REQ-08, REQ-11, REQ-12, REQ-14 | TASK-W0-03 | `src/database/postgres/schema/programme_schema.py` create; `src/database/postgres/repository/programme_repository.py` create | Repository persists a Programme row with plaintext PAT, workspace root, and reserved (unused) App fields | command | `pytest tests/unit/test_programme_repository.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-01 | gateflow | spec §REQ-08, REQ-11, REQ-12, REQ-14 | N/A (unit-only task) | `repository-pattern.mdc`; `database-migrations.mdc` (human-owned Alembic revision) | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W1-02 | `ProgrammeService.validate_then_create` (PAT probe + meta clone/parse before durable create) | REQ-08, REQ-09, REQ-10, REQ-13 | TASK-W1-01 | `src/business_services/programme_service.py` create | Bad PAT or bad meta → named rejection, zero Programme/Tenant rows; agent-key field on request → 422 | command | `pytest tests/unit/test_programme_service.py -v` | exit 0; row-count assertions pass | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-02 | gateflow | spec §REQ-08, REQ-09, REQ-10, REQ-13 | `.venv/bin/python -m tests.verify.verify_programme_onboarding` | `fail-fast.mdc` — no partial state on validation failure | TDD §3.3 interface contract | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W1-03 | `platform_admin`-only routes: create Programme, list programmes | REQ-08, REQ-17, REQ-18 | TASK-W1-02 | `src/api/v1/programme_admin_routes.py` create | `platform_admin` JWT can create + list; `tenant_admin` JWT on these routes → 403 | command | `pytest tests/unit/test_programme_admin_routes.py -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-03 | gateflow | spec §REQ-08, REQ-17, REQ-18 | `.venv/bin/python -m tests.verify.verify_programme_onboarding` | `http-api-conventions.mdc` — POST body model | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W1-04 | Attach `tenant_admin` to Programme; idempotent re-attach; unknown-programme rejection | REQ-15, REQ-16, REQ-44, REQ-47 | TASK-W1-03 | `src/business_services/programme_service.py` modify; `src/api/v1/programme_admin_routes.py` modify | Attach to unknown Programme → named reject, 0 attach; duplicate attach of same identity → idempotent success | command | `pytest tests/unit/test_programme_service.py -k attach -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-04 | gateflow | spec §REQ-15, REQ-16, REQ-44, REQ-47 | `.venv/bin/python -m tests.verify.verify_programme_onboarding` | N/A | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W1-05 | `PlatformAgentCatalogueSchema` + repository (Cursor + reserved slots) | REQ-19, REQ-20, REQ-40, REQ-45 | — | `src/database/postgres/schema/platform_agent_catalogue_schema.py` create; `src/database/postgres/repository/platform_agent_catalogue_repository.py` create | Blank/missing key on provision → named reject, 0 usable row | command | `pytest tests/unit/test_platform_agent_catalogue_repository.py -q` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-05 | gateflow | spec §REQ-19, REQ-20, REQ-40, REQ-45 | N/A (unit-only task) | `repository-pattern.mdc`; `database-migrations.mdc` | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W1-06 | `PlatformAgentCatalogueService.resolve_effective_runner` + per-lane defaults; provision route | REQ-21, REQ-22, REQ-41, REQ-42 | TASK-W1-05 | `src/business_services/platform_agent_catalogue_service.py` create; `src/api/v1/programme_admin_routes.py` modify | Caller-supplied runner wins; else lane default; both absent + no default → reject; unprovisioned runner → reject; `CursorAgentSettings`/env never consulted by this method | command | `pytest tests/unit/test_platform_agent_catalogue_service.py -v` | exit 0; env-key assertion (mock has zero calls to `CursorAgentSettings`) passes | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-06 | gateflow | spec §REQ-21, REQ-22, REQ-41, REQ-42 | `.venv/bin/python -m tests.verify.verify_agent_catalogue` | `dependency-injection.mdc` `is_configured()` anti-pattern — TDD §9 E2 | TDD §3.4 interface contract | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W1-07 | Rename existing meta-catalogue-connection symbols to disambiguate from new Programme entity (AF-1) | REQ-08 | TASK-W1-03 | `src/api/v1/programme_routes.py` → `src/api/v1/catalogue_connection_routes.py` modify/rename; `src/business_services/programme_onboarding_service.py` → `catalogue_connection_service.py` rename; `src/database/postgres/schema/tenant_schema.py` (`TenantProgrammeConnectionSchema` → `MetaCatalogueConnectionSchema`) modify | `make check` (import-linter, pyright) passes with zero references to old symbol names outside this rename's own diff | command | `make check` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-07 | gateflow | spec (TDD §9 E4 / FF-06 / Q-5) | N/A (rename-only task) | N/A | TDD §9 E4 | `chore/INIT-GATEFLOW-014-spec-gateflow` |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/database/postgres/schema/programme_schema.py` | create |
| FILE-W1-02 | `src/database/postgres/repository/programme_repository.py` | create |
| FILE-W1-03 | `tests/unit/test_programme_repository.py` | create |
| FILE-W1-04 | `src/business_services/programme_service.py` | create |
| FILE-W1-05 | `tests/unit/test_programme_service.py` | create |
| FILE-W1-06 | `src/api/v1/programme_admin_routes.py` | create |
| FILE-W1-07 | `tests/unit/test_programme_admin_routes.py` | create |
| FILE-W1-08 | `src/database/postgres/schema/platform_agent_catalogue_schema.py` | create |
| FILE-W1-09 | `src/database/postgres/repository/platform_agent_catalogue_repository.py` | create |
| FILE-W1-10 | `tests/unit/test_platform_agent_catalogue_repository.py` | create |
| FILE-W1-11 | `src/business_services/platform_agent_catalogue_service.py` | create |
| FILE-W1-12 | `tests/unit/test_platform_agent_catalogue_service.py` | create |
| FILE-W1-13 | `src/api/v1/catalogue_connection_routes.py` | create (renamed from `programme_routes.py`) |
| FILE-W1-14 | `src/api/v1/programme_routes.py` | delete (post-rename) |
| FILE-W1-15 | `src/business_services/catalogue_connection_service.py` | create (renamed from `programme_onboarding_service.py`) |
| FILE-W1-16 | `src/business_services/programme_onboarding_service.py` | delete (post-rename) |
| FILE-W1-17 | `src/database/postgres/schema/tenant_schema.py` | modify (`MetaCatalogueConnectionSchema` rename) |
| FILE-W1-18 | `tests/verify/verify_programme_onboarding.py` | create |
| FILE-W1-19 | `tests/verify/verify_agent_catalogue.py` | create |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-08–REQ-22, REQ-40–REQ-42, REQ-44, REQ-45, REQ-47 |
| TEST-W1-I | integration/contract | `pytest tests/unit/test_programme_service.py -k meta_clone -v` (real meta-checkout clone against a fixture repo — one named boundary) | REQ-09 |
| TEST-W1-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_programme_onboarding` (human-run) | REQ-08, REQ-10, REQ-15, REQ-17, REQ-18, REQ-44 |
| TEST-W1-L2 | live (smoke) | `.venv/bin/python -m tests.verify.verify_agent_catalogue` (human-run) | REQ-19, REQ-21, REQ-22, REQ-41, REQ-42, REQ-45 |

**Overlap check (P15):** `python -m scripts.verify_coverage_query tests/verify --capability programme` and `--capability agent-catalogue` — no marker on any existing artifact (`verify_programme_connect.py`, closest by name, covers the *pre-existing* meta-catalogue-connection concept per TASK-W1-07's rename, not the new Programme entity — confirmed distinct capability, not overlapping). Two new FILEs declared.

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-08–REQ-10, REQ-13 validate-then-create | TEST-W1-U | TEST-W1-I | TEST-W1-L | N/A | |
| REQ-11, REQ-12, REQ-14 storage model | TEST-W1-U | N/A | N/A | N/A | Inspection-provable; no live behavior beyond create |
| REQ-15–REQ-18, REQ-44, REQ-47 attach/list | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-19–REQ-22, REQ-40–REQ-42, REQ-45 catalogue | TEST-W1-U | N/A | TEST-W1-L2 | N/A | |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API up; a reachable fixture meta repo + a usable test PAT (non-production) |
| Safe test data | Synthetic Programme `smoke-programme-01`, synthetic `tenant_admin` identity |
| Steps / command | `.venv/bin/python -m tests.verify.verify_programme_onboarding`; `.venv/bin/python -m tests.verify.verify_agent_catalogue` |
| Expected observations | Both scripts print PASS per case (create/reject/attach/list/provision/resolve); exit 0 |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Delete synthetic Programme + catalogue rows created during the run |
| Stop conditions | Non-zero exit, any unexpected 5xx, or a PAT probe hitting a non-test repo → stop |

---

### Phase W2 — Cut over repo lifecycle + twin/initiative under JWT; refuse old doors

**GOAL-W2:** Every Appendix-C product route accepts only role/programme-bound JWT; the programme service token and tenant bearer are refused (not yet deleted); forge/git and agent dispatch resolve per-programme/per-catalogue credentials only.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | `require_role` / `require_programme_scope` FastAPI dependencies | REQ-23, REQ-24, REQ-29, REQ-30, REQ-31 | TASK-W0-06 | `src/common/auth/dependencies.py` create | Wrong role or cross-programme tenant → 403 named reason; missing/invalid JWT → 401 (via existing middleware) | command | `pytest tests/unit/test_auth_dependencies.py -v` | exit 0; role/tenant matrix all pass | Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-01 | gateflow | spec §REQ-23, REQ-24, REQ-29, REQ-30, REQ-31 | N/A (unit-only task) | N/A | TDD §3.2 interface contract | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W2-02 | Swap `verify_programme_service_token`/`verify_tenant_bearer_token` for `require_role(...)` on all 7+ route files; shrink `public_paths` to health/internal/webhooks only; refuse old Bearer values | REQ-04, REQ-32, REQ-33 | TASK-W2-01 | `src/api/v1/waves_routes.py`, `runs_routes.py`, `board_routes.py`, `checkpoints_routes.py`, `initiatives_routes.py`, `metrics_routes.py`, `forge_routes.py`, `tenant_routes.py`, `catalogue_connection_routes.py` modify; `src/app.py` modify | Old programme-token / tenant-bearer Bearer values → 401 on every Appendix-C route; `test_programme_token_api.py`/`test_tenant_token.py`/`test_tenant_routes.py` assertions flipped (rewrite, not extend — R-2) | command | `pytest tests/unit/test_programme_token_api.py tests/unit/test_tenant_token.py tests/unit/test_tenant_routes.py -v` | exit 0; all negative-refusal cases pass | Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-02 | gateflow | spec §REQ-04, REQ-32, REQ-33 | `.venv/bin/python -m tests.verify.verify_jwt_cutover` | N/A | ADR-014 (Accepted) — allowlist shrink per Consequences | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W2-03 | `ForgeClientFactory.for_programme` — per-Programme `ForgeClient` construction | REQ-25 | TASK-W1-01 | `src/infra_services/forge_client.py` modify; `src/infra_services/github_token_provider.py` modify (new `ProgrammePatTokenProvider`); `src/di/modules/infra_module.py` modify (singleton → provider) | Two Programmes resolve to two `ForgeClient` instances with distinct Bearer values; no fallback to App-installation or env credential | command | `pytest tests/unit/test_forge_client_factory.py -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-03 | gateflow | spec §REQ-25 | `.venv/bin/python -m tests.debug.debug_forge_client` (existing probe, extended with a second Programme fixture — not a `live_verify_dir` product-surface change, debug-only) | `infra-services.mdc` Protocol precedent | ADR-015 (Accepted) — Option C factory | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W2-04 | `RunSchema.tenant_id` (non-nullable) + tenant-scoped queries in `RunRepository`/`BoardService`/`CheckpointEvidenceService`/`MetricsEmitter` | REQ-23, REQ-24, REQ-31 | TASK-W2-01 | `src/database/postgres/schema/run_store_schema.py` modify; `src/database/postgres/repository/run_repository.py` modify; `src/business_services/board_service.py`, `checkpoint_evidence_service.py`, `metrics_emitter.py` modify | Cross-programme `tenant_admin` JWT on another programme's run/ticket/checkpoint → refused before the query executes (per TDD §3.2); `platform_admin` sees unfiltered rows | command | `pytest tests/unit/test_run_store_concurrency.py tests/unit/test_metrics_emitter.py -k tenant_scope -v` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-04 | gateflow | spec §REQ-23, REQ-24, REQ-31 | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` | `database-migrations.mdc` — human-owned Alembic revision for the new column | ADR-016 (Accepted) — Option C join-through-run_id | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W2-05 | `SlotValidator`'s cursor check rewritten to query `PlatformAgentCatalogueService` (not extended alongside env check); `CursorAgentRunner` accepts resolved credential as a parameter | REQ-26, REQ-41 | TASK-W1-06 | `src/business_services/slot_validator.py` modify; `src/infra_services/cursor_agent_runner.py` modify | `test_slot_validator.py`/`test_cursor_agent_runner.py` env-based assertions removed and replaced with catalogue-based assertions (no dual-path window) | command | `pytest tests/unit/test_slot_validator.py tests/unit/test_cursor_agent_runner.py -v` | exit 0; zero references to `CursorAgentSettings.has_api_key()` remain in `slot_validator.py` | Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-05 | gateflow | spec §REQ-26, REQ-41 | N/A (unit-only task; live coverage is TEST-W1-L2) | `dependency-injection.mdc` `is_configured()` anti-pattern — TDD §9 E2 | ADR-006 (unaffected — business-owned validator boundary preserved) | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W2-06 | Inspection: confirm webhook signature verification path untouched by this wave's changes | REQ-28 | TASK-W2-02 | `src/api/webhooks/github_routes.py` (action: inspect) | `public_paths` still allowlists `/webhooks`; webhook route imports no `require_role`/JWT dependency | review | PE reviews diff against REQ-28 | No webhook route touched by this wave's diff | Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-06 | gateflow | spec §REQ-28 | N/A (inspection-only) | N/A | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/common/auth/dependencies.py` | create |
| FILE-W2-02 | `tests/unit/test_auth_dependencies.py` | create |
| FILE-W2-03 | `src/api/v1/waves_routes.py` | modify |
| FILE-W2-04 | `src/api/v1/runs_routes.py` | modify |
| FILE-W2-05 | `src/api/v1/board_routes.py` | modify |
| FILE-W2-06 | `src/api/v1/checkpoints_routes.py` | modify |
| FILE-W2-07 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W2-08 | `src/api/v1/metrics_routes.py` | modify |
| FILE-W2-09 | `src/api/v1/forge_routes.py` | modify |
| FILE-W2-10 | `src/api/v1/tenant_routes.py` | modify |
| FILE-W2-11 | `src/api/v1/catalogue_connection_routes.py` | modify |
| FILE-W2-12 | `src/app.py` | modify |
| FILE-W2-13 | `tests/unit/test_programme_token_api.py` | modify |
| FILE-W2-14 | `tests/unit/test_tenant_token.py` | modify |
| FILE-W2-15 | `tests/unit/test_tenant_routes.py` | modify |
| FILE-W2-16 | `src/infra_services/forge_client.py` | modify |
| FILE-W2-17 | `src/infra_services/github_token_provider.py` | modify |
| FILE-W2-18 | `src/di/modules/infra_module.py` | modify |
| FILE-W2-19 | `tests/unit/test_forge_client_factory.py` | create |
| FILE-W2-20 | `src/database/postgres/schema/run_store_schema.py` | modify |
| FILE-W2-21 | `src/database/postgres/repository/run_repository.py` | modify |
| FILE-W2-22 | `src/business_services/board_service.py` | modify |
| FILE-W2-23 | `src/business_services/checkpoint_evidence_service.py` | modify |
| FILE-W2-24 | `src/business_services/metrics_emitter.py` | modify |
| FILE-W2-25 | `src/business_services/slot_validator.py` | modify |
| FILE-W2-26 | `src/infra_services/cursor_agent_runner.py` | modify |
| FILE-W2-27 | `tests/verify/verify_jwt_cutover.py` | create |
| FILE-W2-28 | `tests/verify/verify_cross_programme_isolation.py` | create |
| FILE-W2-29 | `src/api/webhooks/github_routes.py` | inspect |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-04, REQ-23, REQ-24, REQ-26, REQ-29, REQ-30, REQ-31, REQ-32, REQ-33, REQ-41 |
| TEST-W2-I | integration/contract | `pytest tests/unit/test_forge_client_factory.py -k real_credential_isolation -v` (one boundary: two constructed `ForgeClient`s carry provably distinct headers) | REQ-25 |
| TEST-W2-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_jwt_cutover` (human-run) | REQ-04, REQ-32, REQ-33 |
| TEST-W2-L2 | live (smoke) | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` (human-run) | REQ-23, REQ-24, REQ-31 |

**Overlap check (P15):** `python -m scripts.verify_coverage_query tests/verify --capability cutover` and `--capability isolation` — no existing marked artifact; `verify_wave_start.py` (closest by capability, unmarked) still asserts the *old* programme-token acceptance behavior and must itself be rewritten at W4 (REQ-36/37), not extended here to avoid conflating W2's negative-refusal proof with W4's teaching-surface rewrite. Two new FILEs declared for W2; `verify_wave_start.py`'s own rewrite is tracked as a W4 task.

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-04, REQ-32, REQ-33 refuse old doors | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-23, REQ-24, REQ-31 tenant scoping | TEST-W2-U | N/A | TEST-W2-L2 | N/A | |
| REQ-25 per-programme credential | TEST-W2-U | TEST-W2-I | N/A | N/A | Debug probe (`debug_forge_client.py`) is secondary, non-gating evidence |
| REQ-26, REQ-41 catalogue-only dispatch | TEST-W2-U | N/A | (covered by TEST-W1-L2, unchanged this wave) | N/A | |
| REQ-28 webhook unaffected | N/A (inspection) | N/A | N/A | N/A | TASK-W2-06 is `review` proof, not test-layer |
| REQ-29, REQ-30 fail-closed | TEST-W2-U | N/A | TEST-W2-L | N/A | |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API + worker up; two synthetic Programmes with distinct PATs provisioned (from W1) |
| Safe test data | Synthetic Programmes `smoke-programme-a`/`smoke-programme-b`, synthetic runs under each |
| Steps / command | `.venv/bin/python -m tests.verify.verify_jwt_cutover`; `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` |
| Expected observations | Old-door Bearer values refused (401); JWT happy path accepted; cross-programme read/write attempts refused (403/404 per REQ-31) |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Remove synthetic Programmes/runs created during the run |
| Stop conditions | Any old-door Bearer value is accepted, or any cross-programme read succeeds → stop; do not proceed to W3 |

---

### Phase W3 — Dead-door deletion + wipe cutover

**GOAL-W3:** Programme-token and tenant-bearer code paths are structurally deleted (not just refused); 012/013 lab tenant rows are wiped, rejecting wipe while any run is in flight.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | Delete `programme_token.py`, `tenant_token.py`, and every import of them; delete `POST /tenants` open-register route entirely | REQ-34 | TASK-W2-02 | `src/api/v1/programme_token.py` delete; `src/api/v1/tenant_token.py` delete; `src/api/v1/tenant_routes.py` modify | `make check` (import-linter) passes with zero references to deleted modules; `POST /api/v1/tenants` returns 404/405, not 200 | command | `make check && pytest tests/unit/test_tenant_routes.py -k register -v` | exit 0; open-register test asserts gone, not merely refused | Wave-Execution-INIT-GATEFLOW-014-W3.md § TASK-W3-01 | gateflow | spec §REQ-34 | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` | N/A | ADR-014 (Accepted) — structural removal per Consequences | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W3-02 | Wipe endpoint/script: full reset of 012/013 lab tenant + shared-secret rows, in-flight-run guard | REQ-35, REQ-46 | TASK-W2-04 | `src/business_services/programme_wipe_service.py` create; `src/api/v1/programme_admin_routes.py` modify | Wipe with an ACTIVE run present for that programme → 409 named reason, 0 wipe; wipe otherwise clears rows | command | `pytest tests/unit/test_programme_wipe_service.py -v` | exit 0; in-flight-run case asserted | Wave-Execution-INIT-GATEFLOW-014-W3.md § TASK-W3-02 | gateflow | spec §REQ-35, REQ-46 | `.venv/bin/python -m tests.verify.verify_wipe_cutover` | `fail-fast.mdc` | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/api/v1/programme_token.py` | delete |
| FILE-W3-02 | `src/api/v1/tenant_token.py` | delete |
| FILE-W3-03 | `src/api/v1/tenant_routes.py` | modify |
| FILE-W3-04 | `tests/unit/test_tenant_routes.py` | modify |
| FILE-W3-05 | `src/business_services/programme_wipe_service.py` | create |
| FILE-W3-06 | `tests/unit/test_programme_wipe_service.py` | create |
| FILE-W3-07 | `src/api/v1/programme_admin_routes.py` | modify |
| FILE-W3-08 | `tests/verify/verify_dead_doors_deleted.py` | create |
| FILE-W3-09 | `tests/verify/verify_wipe_cutover.py` | create |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-34, REQ-35, REQ-46 |
| TEST-W3-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` (human-run) | REQ-34 |
| TEST-W3-L2 | live (smoke) | `.venv/bin/python -m tests.verify.verify_wipe_cutover` (human-run) | REQ-35, REQ-46 |

**Overlap check (P15):** `python -m scripts.verify_coverage_query tests/verify --capability wipe` and `--capability delete` — no existing marked artifact; two new FILEs declared.

#### Verification Coverage (W3)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-34 dead-door deletion | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-35, REQ-46 wipe cutover | TEST-W3-U | N/A | TEST-W3-L2 | N/A | |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API up; a synthetic 012/013-shaped lab tenant row present; a synthetic ACTIVE run present for the mid-run-reject case |
| Safe test data | Synthetic lab tenant `smoke-legacy-tenant`, synthetic ACTIVE run |
| Steps / command | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted`; `.venv/bin/python -m tests.verify.verify_wipe_cutover` |
| Expected observations | Old-door routes return 404/405 (gone, not 401-refused); wipe succeeds on idle programme, rejects on in-flight run |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | None beyond what the wipe itself performs |
| Stop conditions | Wipe succeeds while a run is ACTIVE → stop; do not proceed to W4 |

---

### Phase W4 — Prove absence + rewrite teaching surfaces

**GOAL-W4:** Every verify/teaching surface instructs JWT + per-programme GitHub + DB catalogue only; live scripts prove both the JWT happy path and refusal of every deleted door.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W4-01 | Rewrite `verify_wave_start.py`, `verify_board.py`, `verify_tenant_registry.py`, `verify_repo_selection.py`, `verify_checkpoint_status.py`, `verify_status_metrics.py` (and remaining `PROGRAMME_SERVICE_TOKEN`/tenant-bearer consumers) to mint/use JWTs | REQ-36, REQ-38 | TASK-W3-01, TASK-W3-02 | `tests/verify/verify_wave_start.py`, `verify_board.py`, `verify_tenant_registry.py`, `verify_repo_selection.py`, `verify_checkpoint_status.py`, `verify_status_metrics.py` modify | Every listed script runs green using only JWT auth; zero references to `PROGRAMME_SERVICE_TOKEN`/tenant bearer remain in `tests/verify/` | command | `.venv/bin/python -m tests.verify.verify_all` | exit 0; grep for `PROGRAMME_SERVICE_TOKEN` in `tests/verify/` returns zero matches | Wave-Execution-INIT-GATEFLOW-014-W4.md § TASK-W4-01 | gateflow | spec §REQ-36, REQ-38 | `.venv/bin/python -m tests.verify.verify_all` | N/A | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W4-02 | New negative-path verify script proving refusal of programme token, tenant bearer, and open register (extends W2/W3's per-wave scripts into one consolidated negative-path proof referenced by REQ-37) | REQ-37 | TASK-W4-01 | `tests/verify/verify_old_doors_refused.py` create | Script asserts: old programme token → 401; old tenant bearer → 401; `POST /tenants` (open register) → 404/405 | command | `.venv/bin/python -m tests.verify.verify_old_doors_refused` | exit 0 | Wave-Execution-INIT-GATEFLOW-014-W4.md § TASK-W4-02 | gateflow | spec §REQ-37 | `.venv/bin/python -m tests.verify.verify_old_doors_refused` | N/A | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| TASK-W4-03 | Update `tests/README.md` command list + `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-014.md` + index row in `implementation-status.md` | REQ-38 | TASK-W4-02 | `tests/README.md` modify; `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-014.md` create; `docs/specification/as-built/implementation-status.md` modify (index row only) | `tests/README.md` lists only JWT-based invocation examples for Appendix-C scripts; as-built detail file exists with full capability matrix for INIT-014 | review | PE reviews docs diff against REQ-38 | No lingering old-door invocation examples remain in `tests/README.md` | Wave-Execution-INIT-GATEFLOW-014-W4.md § TASK-W4-03 | gateflow | spec §REQ-38 | N/A (docs-only task) | N/A | N/A | `chore/INIT-GATEFLOW-014-spec-gateflow` |

#### Files (W4)

| ID | Path | Action |
|----|------|--------|
| FILE-W4-01 | `tests/verify/verify_wave_start.py` | modify |
| FILE-W4-02 | `tests/verify/verify_board.py` | modify |
| FILE-W4-03 | `tests/verify/verify_tenant_registry.py` | modify |
| FILE-W4-04 | `tests/verify/verify_repo_selection.py` | modify |
| FILE-W4-05 | `tests/verify/verify_checkpoint_status.py` | modify |
| FILE-W4-06 | `tests/verify/verify_status_metrics.py` | modify |
| FILE-W4-07 | `tests/verify/verify_old_doors_refused.py` | create |
| FILE-W4-08 | `tests/README.md` | modify |
| FILE-W4-09 | `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-014.md` | create |
| FILE-W4-10 | `docs/specification/as-built/implementation-status.md` | modify (index row only) |

#### Tests (W4)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W4-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_all` (human-run) | REQ-36, REQ-38 |
| TEST-W4-L2 | live (smoke) | `.venv/bin/python -m tests.verify.verify_old_doors_refused` (human-run) | REQ-37 |

**Overlap check (P15):** this wave's job is explicitly to **extend** every existing script named in TASK-W4-01 (not create new ones) — the overlap check for those is the wave's own purpose, not a pre-check to avoid. `verify_old_doors_refused.py` is genuinely new (queried `--capability refuse` / `--capability old-doors` — no existing marker).

#### Verification Coverage (W4)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-36 JWT happy path proven | N/A | N/A | TEST-W4-L | N/A | |
| REQ-37 old-door refusal proven | N/A | N/A | TEST-W4-L2 | N/A | |
| REQ-38 teaching surfaces updated | N/A | N/A | N/A | N/A | `review` proof (TASK-W4-03), not test-layer |

#### Live-verification intent (W4)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | Full stack up (API + worker); at least one Accepted Programme + `tenant_admin` from prior waves' smoke fixtures |
| Safe test data | Reuses W0–W3 synthetic fixtures where still present; creates fresh ones otherwise |
| Steps / command | `.venv/bin/python -m tests.verify.verify_all`; `.venv/bin/python -m tests.verify.verify_old_doors_refused` |
| Expected observations | Full suite green under JWT-only auth; old-door negative-path script proves refusal/absence for all three retired doors |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Remove all synthetic fixtures created across W0–W4 smoke runs |
| Stop conditions | Any script still succeeding with an old-door credential → stop; this is the initiative's exit gate (PRD Hard exit rule) |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | W1 (`ProgrammeSchema`) before W2 (`ForgeClientFactory.for_programme` needs a Programme to key on) | W2 |
| DEP-02 | W1 (`PlatformAgentCatalogueService`) before W2 (`SlotValidator` rewrite consumes it) | W2 |
| DEP-03 | W2 (auth cutover + tenant scoping) before W3 (dead-door deletion — cannot delete a door still in use) | W3 |
| DEP-04 | W3 (wipe capability) before W4 (teaching-surface rewrite assumes old doors are already gone, not just refused) | W4 |
| DEP-05 | Human-owned Alembic revisions for `ProgrammeSchema`, `PlatformAgentCatalogueSchema`, `UserIdentitySchema`, `RunSchema.tenant_id` must be created and applied (`database-migrations.mdc`) before the corresponding wave's live verify can run | W1, W2 |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | W2 is the highest-complexity wave (7+ route files, ForgeClient lifecycle change, new schema column, SlotValidator rewrite) — underestimation risk if treated as a single task | Broken into 6 independent TASK rows (TASK-W2-01…06) with distinct file scopes and exit proofs, per feasibility R-1 |
| RISK-02 | `test_programme_token_api.py`/`test_tenant_token.py`/`test_tenant_routes.py` currently assert the *opposite* of REQ-32/33/34 — a naive "add coverage" pass would leave contradictory green tests | TASK-W2-02/TASK-W3-01 explicitly scope these three files as **rewrite** (flip assertions), not extend, per feasibility R-2 |
| RISK-03 | Human-owned Alembic migrations (4 new/modified schemas across W0–W2) are a hard external dependency this plan cannot execute itself | DEP-05 makes each migration an explicit blocking dependency per wave; `database-migrations.mdc` requires human `create_postgres_migration.sh` / `run_postgres_migration.sh` — flagged, not silently assumed |
| RISK-04 | `ForgeClientFactory`'s DI registration change (bound singleton → provider) could reveal additional callers of `ForgeClient` beyond `BoardService` that assume singleton injection | TASK-W2-03's exit proof requires a full `make check` (import-linter) pass, which will surface any DI binding mismatch at type-check time, not runtime |
| RISK-05 | W4's rewrite of 6+ existing verify scripts risks silently dropping REQ coverage those scripts already carried for prior initiatives (INIT-012/013 capabilities) | TASK-W4-01's exit proof is the full `verify_all` suite, not a per-script check — a regression in prior-initiative coverage fails the wave's own gate |

---

## 5. Out of scope

- `gateflow-ops` UI / login screens — deferred (impact map §3)
- Claude Code / OpenCode runner implementations — catalogue reserves slots only (REQ-20)
- GitHub App runtime activation — storage shape reserved, unused this INIT (REQ-14; ADR-015 revisit trigger)
- Encrypting DB secrets — plaintext accepted (spec NFR Security)
- Legacy-row backfill / migration from a prior deployment — moot under the confirmed greenfield reset (ADR-016 Consequences)
- `prayog-meta` vision/ADR-citation content (REQ-39) — tracked in that repo, not this plan

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Create per-initiative as-built detail | `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-014.md` | Record W0–W4 capability/code/test/verify detail — written once, never appended across initiatives (TASK-W4-03) |
| Update as-built index row | `docs/specification/as-built/implementation-status.md` | Overwrite this initiative's row in place — never append a new table (TASK-W4-03) |
| Ensure live-verify coverage marker | Every new/extended `tests/verify/*.py` FILE across W0–W4 | Self-declare `REQ-*` coverage via `prayog:covers:` marker per `live-verify-coverage-contract.md` — do not edit `tests/README.md` as the coverage source of truth (only as an invocation-example pointer, per TASK-W4-03) |

> **ADR lifecycle:** `adr-014`, `adr-015`, `adr-016` are already `Accepted` (technical-review-approval, 2026-08-10). No ADR promotion tasks appear in this plan.

---

## 7. Plan check summary

| Check | Status | Notes |
|-------|--------|-------|
| P1 | PASS | Every §1 REQ appears in ≥1 wave's TASK **Implements** column |
| P2 | PASS | Every in-scope REQ has ≥1 TASK; no shadow `REQ-W*` ids used anywhere |
| P3 | PASS | Every TASK has FILE paths or explicit inspection/review-only scope (TASK-W2-06, TASK-W4-03) |
| P4 | PASS | Every TASK has observable exit criteria, proof kind/command or review, expected result, and evidence location |
| P5 | PASS | Every wave's Verification Coverage table maps each REQ to a layer; every product-code wave (W0–W3) has ≥1 unit-layer row |
| P6 | PASS | No task exceeds the initiative spec's REQ-01…38, REQ-40…47 scope |
| P7 | PASS | Feasibility FF-01…FF-07 and the operational R-1/R-2/R-3 risks are all addressed — R-1→RISK-01, R-2→RISK-02, R-3 resolved outright by ADR-016's greenfield-reset finding (no backfill risk remains) |
| P8 | PASS | §3 Dependencies states wave order (W0→W1→W2→W3→W4) and the two schema/DI dependencies that could otherwise silently block a wave |
| P9 | PASS | §6 lists the as-built detail file + index-row-only update in the same wave (W4) as the code tasks it describes |
| P10 | PASS | Plan is self-contained — source freshness table, command contract, and every wave's file/test/verify detail are stated in this document |
| P11 | PASS | MDC notes populated per TASK where a specific rule bears on the change (`pydantic-schemas.mdc`, `repository-pattern.mdc`, `database-migrations.mdc`, `fail-fast.mdc`, `dependency-injection.mdc`, `infra-services.mdc`, `http-api-conventions.mdc`, `testing-verify-flows.mdc`) |
| P12 | PASS | Every architectural TASK cites an Accepted ADR id (`adr-014`/`adr-015`/`adr-016`, all `Status: Accepted` in `{adr_dir}` as of this plan); §0 links all three canonical files |
| P13 | PASS | §0 states TDD `Status: Accepted`, PE sign-off `[x] complete — 2026-08-10`; P13 lint re-check re-ran `adr_boundary_lint.py --require-sources` against all 3 ADRs with sources reconstructed from the spec — all PASS (log in §0) |
| P14 | PASS | §9 wave ids `W0`–`W4` match plan waves exactly; every TASK row has `codebase`, `spec_path`, `verify_command` (or explicit N/A), and non-empty `implements`; every wave has `tasks[]` + body table |
| P15 | PASS | W0–W3 each co-ship ≥1 unit TEST + ≥1 new `live_verify_dir` FILE with a recorded overlap-check result (all found zero existing markers); W4's job is explicitly to extend the pre-existing scripts, satisfying P15 by construction |
| P16 | PASS | §9 validated via `workmanifest_contract.py` — see command log below |

**P16 validation command log:**

```text
$ python3 prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md --base-path .
→ (see /commit-workspace step — validated before publish)
```

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch alongside spec, feasibility,
> and TDD. Do **not** commit inside this skill. Label remains **`spec-pending`**
> until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-014-spec-gateflow  (Draft PR #212)
PR title: "[INIT-GATEFLOW-014] Spec — One identity to call Gateflow, retire shared-secret doors (gateflow)"
PR body:  link meta PRD PR #35; paste §1 Requirements table + wave goals summary

Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-13

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility (rev 2) + TDD (Accepted) + 3 Accepted ADRs + this plan on current head
  [x] §0 PE sign-off on TDD marked complete — 2026-08-10, @nikd10x
  [ ] Wave order and dependencies make sense (§3)
  [ ] Done-when / exit criteria are observable and testable (P4)
  [ ] Verification Coverage maps every criterion to a layer (P5)
  [ ] WorkManifest YAML (§9) passes workmanifest_contract.py (P16) — prayog/v1
  [ ] P1–P16 checks all pass (including P15 co-ship when surface changes)

After spec-lgtm + Approve + merge — /create-board-tickets from §9 (post-merge only):
  Create one GitHub Issue per wave (W0…W4) using §9 titles, bodies, depends_on
  Search for existing initiative/wave issues first; create only missing issues
  Then Pass-1: /pre-implement → /loop-spec → wave-acceptance (human runs co-shipped script)
  Then Pass-2: /learning-extract → /ground-spec → wave-signoff (merge only)
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 all PASS; TDD Accepted; all required ADRs Accepted; sources CURRENT |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/212 |
| Spec PR head SHA | to be recorded after `/commit-workspace` publishes this plan alongside the Accepted TDD/ADRs |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` |
| Forge readiness | fill `handoff.forge` for `/commit-workspace` — do not commit inside this skill |
| Blocking items | none |

Provision labels when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

PE actions (all on **exact current head**, after `/commit-workspace` publishes this package):

1. Remove `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale`; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body (below)
3. Mark Draft PR **Ready for review**
4. Authorize merge (human or policy); then **`/create-board-tickets`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-014
spec_pr_head_sha: {SHA at publish}
meta_pr_head_sha: 3120e4eff4b4dfe86ed1a14f02439d62bc6151c7
impact_map_revision: 1
prd_digest: sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e
scope_digest: sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef
plan_digest: {to be computed after publish}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-014-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-014.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md
```

Never infer approval from `spec-lgtm` alone — Approve, label, and artifact
digests must match the same head SHA.

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

---

## 9. WorkManifest seed

> **Primary:** `/create-board-tickets` creates **one GitHub Issue per wave**
> from this section after spec merge. Wave bodies list every `TASK-*` with
> exit criteria for human traceability.

```yaml
# Generated by /spec-implementation-plan — 2026-08-10
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-014

metadata:
  title: INIT-GATEFLOW-014 — One identity to call Gateflow, retire shared-secret doors
  summary: |
    Makes Gateflow-issued user JWTs the sole product-edge credential, introduces
    a Programme entity owning per-programme GitHub PAT + workspace + lane
    defaults, moves code-agent credentials into a platform DB catalogue,
    refuses then deletes the programme-token/tenant-bearer/open-register doors,
    wipes 012/013 lab tenants, and proves absence via rewritten verify scripts.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-014
  parent: EPIC
  labels:
    - INIT-GATEFLOW-014

epic:
  id: EPIC
  repo: gateflow
  title: "[feature] INIT-GATEFLOW-014 — One identity to call Gateflow"
  codebase: gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_all
  body: |
    ## Objective

    JWT-only product edge; Programme entity with per-programme PAT; platform
    DB agent catalogue; refuse then delete shared-secret doors; wipe lab
    tenants; prove absence.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Seed platform_admin + JWT mint/login edge |
    | W1 | Programme validate-then-create + tenant_admin attach + agent catalogue |
    | W2 | Cut over repo lifecycle/twin under JWT; refuse old doors |
    | W3 | Dead-door deletion + wipe cutover |
    | W4 | Prove absence + rewrite teaching surfaces |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md

work:
  - id: W0
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-014 W0] Seed platform_admin + JWT mint/login edge"
    depends_on: []
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_jwt_login
    tasks:
      - id: TASK-W0-01
        implements: [REQ-06]
        depends_on: []
        files:
          - path: src/models/role_types.py
            action: create
          - path: src/models/auth_models.py
            action: modify
        exit:
          criteria:
            - "AuthContext(role=...) rejects a non-enum string at construction"
          proof:
            kind: command
            command: "make check && pytest tests/unit/test_auth_middleware.py -k role -q"
            expected: "exit 0; invalid role raises ValidationError"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-05]
        depends_on: [TASK-W0-01]
        files:
          - path: tests/unit/test_auth_middleware.py
            action: create
        exit:
          criteria:
            - "6+ negative-path unit cases all assert 401 with named reason"
          proof:
            kind: command
            command: "pytest tests/unit/test_auth_middleware.py -v"
            expected: "exit 0; all cases pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-01]
        depends_on: []
        files:
          - path: src/database/postgres/schema/user_identity_schema.py
            action: create
          - path: src/database/postgres/repository/user_identity_repository.py
            action: create
        exit:
          criteria:
            - "Repository creates and reads a user row by credential identifier"
          proof:
            kind: command
            command: "pytest tests/unit/test_user_identity_repository.py -q"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-01, REQ-47]
        depends_on: [TASK-W0-03]
        files:
          - path: scripts/seed_platform_admin.py
            action: create
        exit:
          criteria:
            - "Running the script twice yields one platform_admin row and two valid JWTs"
          proof:
            kind: command
            command: ".venv/bin/python scripts/seed_platform_admin.py && .venv/bin/python scripts/seed_platform_admin.py"
            expected: "exit 0 both runs; row count stays 1"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-02, REQ-03, REQ-43]
        depends_on: [TASK-W0-03]
        files:
          - path: src/business_services/auth_identity_service.py
            action: create
          - path: src/api/auth/login_routes.py
            action: create
        exit:
          criteria:
            - "Valid credentials return 200 + JWT; invalid return 401 named UNAUTHORIZED, zero token"
          proof:
            kind: command
            command: "pytest tests/unit/test_auth_identity_service.py -v"
            expected: "exit 0; both paths asserted"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W0.md § TASK-W0-05"
      - id: TASK-W0-06
        implements: [REQ-04, REQ-06, REQ-07]
        depends_on: [TASK-W0-05]
        files:
          - path: src/common/auth/middleware.py
            action: modify
          - path: tests/verify/verify_jwt_login.py
            action: create
        exit:
          criteria:
            - "Minted JWT round-trips through AuthMiddleware.dispatch producing correct AuthContext"
          proof:
            kind: command
            command: "pytest tests/unit/test_auth_middleware.py -k claim_shape -q"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_jwt_login
        covers: [REQ-01, REQ-02, REQ-03, REQ-43]
        prerequisites:
          - "API up (make run)"
          - "JWT key material configured"
        safe_test_data:
          - "Synthetic seed identity platform_admin@smoke.local"
        steps:
          - "Run verify_jwt_login.py against local stack"
        expected_observations:
          - "Script prints PASS for seed-mint, login-happy-path, and login-refuse cases; exits 0"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "None required — seeded admin row is idempotent"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not proceed to W1"
    body: |
      ## Wave goal

      Gateflow-issued user JWTs exist and can be minted (seed) or obtained
      (login); AuthMiddleware correctly shapes role + tenant claims.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-06 | — | RoleType rejects invalid string | command |
      | TASK-W0-02 | REQ-05 | TASK-W0-01 | 6+ negative unit cases pass | command |
      | TASK-W0-03 | REQ-01 | — | Repo create+read user row | command |
      | TASK-W0-04 | REQ-01, REQ-47 | TASK-W0-03 | Idempotent seed, 2 valid JWTs | command |
      | TASK-W0-05 | REQ-02, REQ-03, REQ-43 | TASK-W0-03 | Login happy+refuse paths | command |
      | TASK-W0-06 | REQ-04, REQ-06, REQ-07 | TASK-W0-05 | JWT round-trips to correct AuthContext | command |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-014-gateflow.md

  - id: W1
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-014 W1] Programme validate-then-create + tenant_admin attach + agent catalogue"
    depends_on:
      - W0
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_programme_onboarding
    tasks:
      - id: TASK-W1-01
        implements: [REQ-08, REQ-11, REQ-12, REQ-14]
        depends_on: []
        files:
          - path: src/database/postgres/schema/programme_schema.py
            action: create
          - path: src/database/postgres/repository/programme_repository.py
            action: create
        exit:
          criteria:
            - "Repository persists a Programme row with plaintext PAT, workspace root, reserved App fields"
          proof:
            kind: command
            command: "pytest tests/unit/test_programme_repository.py -q"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-08, REQ-09, REQ-10, REQ-13]
        depends_on: [TASK-W1-01]
        files:
          - path: src/business_services/programme_service.py
            action: create
        exit:
          criteria:
            - "Bad PAT/meta reject with zero rows; agent-key field rejected with 422"
          proof:
            kind: command
            command: "pytest tests/unit/test_programme_service.py -v"
            expected: "exit 0; row-count assertions pass"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W1-03
        implements: [REQ-08, REQ-17, REQ-18]
        depends_on: [TASK-W1-02]
        files:
          - path: src/api/v1/programme_admin_routes.py
            action: create
        exit:
          criteria:
            - "platform_admin creates+lists; tenant_admin on these routes gets 403"
          proof:
            kind: command
            command: "pytest tests/unit/test_programme_admin_routes.py -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-15, REQ-16, REQ-44, REQ-47]
        depends_on: [TASK-W1-03]
        files:
          - path: src/business_services/programme_service.py
            action: modify
          - path: src/api/v1/programme_admin_routes.py
            action: modify
        exit:
          criteria:
            - "Attach to unknown Programme rejects with 0 attach; duplicate attach idempotent"
          proof:
            kind: command
            command: "pytest tests/unit/test_programme_service.py -k attach -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-19, REQ-20, REQ-40, REQ-45]
        depends_on: []
        files:
          - path: src/database/postgres/schema/platform_agent_catalogue_schema.py
            action: create
          - path: src/database/postgres/repository/platform_agent_catalogue_repository.py
            action: create
        exit:
          criteria:
            - "Blank/missing key on provision rejects with 0 usable row"
          proof:
            kind: command
            command: "pytest tests/unit/test_platform_agent_catalogue_repository.py -q"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-05"
      - id: TASK-W1-06
        implements: [REQ-21, REQ-22, REQ-41, REQ-42]
        depends_on: [TASK-W1-05]
        files:
          - path: src/business_services/platform_agent_catalogue_service.py
            action: create
          - path: tests/verify/verify_agent_catalogue.py
            action: create
        exit:
          criteria:
            - "Caller runner wins; else lane default; unprovisioned rejects; env settings never consulted"
          proof:
            kind: command
            command: "pytest tests/unit/test_platform_agent_catalogue_service.py -v"
            expected: "exit 0; zero calls to CursorAgentSettings from this method"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W1-07
        implements: [REQ-08]
        depends_on: [TASK-W1-03]
        files:
          - path: src/api/v1/catalogue_connection_routes.py
            action: create
          - path: src/business_services/catalogue_connection_service.py
            action: create
          - path: src/database/postgres/schema/tenant_schema.py
            action: modify
          - path: tests/verify/verify_programme_onboarding.py
            action: create
        exit:
          criteria:
            - "make check passes with zero references to old programme_routes/ProgrammeOnboardingService symbol names"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W1.md § TASK-W1-07"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_programme_onboarding
        covers: [REQ-08, REQ-10, REQ-15, REQ-17, REQ-18, REQ-44, REQ-19, REQ-21, REQ-22, REQ-41, REQ-42, REQ-45]
        prerequisites:
          - "API up"
          - "Reachable fixture meta repo + non-production test PAT"
        safe_test_data:
          - "Synthetic Programme smoke-programme-01"
        steps:
          - "Run verify_programme_onboarding.py against local stack"
          - "Run verify_agent_catalogue.py against local stack"
        expected_observations:
          - "Script prints PASS per create/reject/attach/list case; exits 0"
          - "Catalogue provision/resolve cases PASS; exits 0"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Delete synthetic Programme rows created during the run"
          - "Delete synthetic catalogue rows created during the run"
        stop_conditions:
          - "Non-zero exit or PAT probe hits a non-test repo → stop"
    body: |
      ## Wave goal

      platform_admin can validate-then-create a Programme, attach
      tenant_admin, and provision the platform agent catalogue.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-08, REQ-11, REQ-12, REQ-14 | — | Programme row persists | command |
      | TASK-W1-02 | REQ-08, REQ-09, REQ-10, REQ-13 | TASK-W1-01 | Validate-then-create fail-closed | command |
      | TASK-W1-03 | REQ-08, REQ-17, REQ-18 | TASK-W1-02 | Admin-only create/list | command |
      | TASK-W1-04 | REQ-15, REQ-16, REQ-44, REQ-47 | TASK-W1-03 | Attach fail-closed + idempotent | command |
      | TASK-W1-05 | REQ-19, REQ-20, REQ-40, REQ-45 | — | Catalogue row persists | command |
      | TASK-W1-06 | REQ-21, REQ-22, REQ-41, REQ-42 | TASK-W1-05 | Effective runner resolution | command |
      | TASK-W1-07 | REQ-08 | TASK-W1-03 | Naming collision resolved | command |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-014-gateflow.md

  - id: W2
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-014 W2] Cut over repo lifecycle/twin under JWT; refuse old doors"
    depends_on:
      - W1
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_jwt_cutover
    tasks:
      - id: TASK-W2-01
        implements: [REQ-23, REQ-24, REQ-29, REQ-30, REQ-31]
        depends_on: []
        files:
          - path: src/common/auth/dependencies.py
            action: create
        exit:
          criteria:
            - "Wrong role or cross-programme tenant returns 403 named reason"
          proof:
            kind: command
            command: "pytest tests/unit/test_auth_dependencies.py -v"
            expected: "exit 0; role/tenant matrix all pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-04, REQ-32, REQ-33]
        depends_on: [TASK-W2-01]
        files:
          - path: src/api/v1/waves_routes.py
            action: modify
          - path: src/api/v1/runs_routes.py
            action: modify
          - path: src/api/v1/board_routes.py
            action: modify
          - path: src/api/v1/checkpoints_routes.py
            action: modify
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: src/api/v1/metrics_routes.py
            action: modify
          - path: src/api/v1/forge_routes.py
            action: modify
          - path: src/api/v1/tenant_routes.py
            action: modify
          - path: src/api/v1/catalogue_connection_routes.py
            action: modify
          - path: src/app.py
            action: modify
          - path: tests/verify/verify_jwt_cutover.py
            action: create
        exit:
          criteria:
            - "Old programme-token/tenant-bearer Bearer values return 401 on every Appendix-C route"
          proof:
            kind: command
            command: "pytest tests/unit/test_programme_token_api.py tests/unit/test_tenant_token.py tests/unit/test_tenant_routes.py -v"
            expected: "exit 0; all negative-refusal cases pass"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W2-03
        implements: [REQ-25]
        depends_on: []
        files:
          - path: src/infra_services/forge_client.py
            action: modify
          - path: src/infra_services/github_token_provider.py
            action: modify
          - path: src/di/modules/infra_module.py
            action: modify
        exit:
          criteria:
            - "Two Programmes resolve to two ForgeClients with distinct Bearer values"
          proof:
            kind: command
            command: "pytest tests/unit/test_forge_client_factory.py -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-03"
      - id: TASK-W2-04
        implements: [REQ-23, REQ-24, REQ-31]
        depends_on: [TASK-W2-01]
        files:
          - path: src/database/postgres/schema/run_store_schema.py
            action: modify
          - path: src/database/postgres/repository/run_repository.py
            action: modify
          - path: tests/verify/verify_cross_programme_isolation.py
            action: create
        exit:
          criteria:
            - "Cross-programme tenant_admin JWT on another programme's data is refused"
          proof:
            kind: command
            command: "pytest tests/unit/test_run_store_concurrency.py tests/unit/test_metrics_emitter.py -k tenant_scope -v"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W2-05
        implements: [REQ-26, REQ-41]
        depends_on: []
        files:
          - path: src/business_services/slot_validator.py
            action: modify
          - path: src/infra_services/cursor_agent_runner.py
            action: modify
        exit:
          criteria:
            - "Zero references to CursorAgentSettings.has_api_key() remain in slot_validator.py"
          proof:
            kind: command
            command: "pytest tests/unit/test_slot_validator.py tests/unit/test_cursor_agent_runner.py -v"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-05"
      - id: TASK-W2-06
        implements: [REQ-28]
        depends_on: [TASK-W2-02]
        files:
          - path: src/api/webhooks/github_routes.py
            action: inspect
        exit:
          criteria:
            - "public_paths still allowlists /webhooks; webhook route imports no JWT dependency"
          proof:
            kind: review
            review: "PE reviews diff against REQ-28"
            expected: "No webhook route touched by this wave's diff"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W2.md § TASK-W2-06"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_jwt_cutover
        covers: [REQ-04, REQ-32, REQ-33, REQ-23, REQ-24, REQ-31]
        prerequisites:
          - "API + worker up"
          - "Two synthetic Programmes with distinct PATs from W1"
        safe_test_data:
          - "Synthetic Programmes smoke-programme-a / smoke-programme-b"
        steps:
          - "Run verify_jwt_cutover.py"
          - "Run verify_cross_programme_isolation.py"
        expected_observations:
          - "Old-door Bearer values refused; JWT happy path accepted; cross-programme access refused"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Remove synthetic Programmes/runs created during the run"
        stop_conditions:
          - "Any old-door Bearer value accepted, or any cross-programme read succeeds → stop"
    body: |
      ## Wave goal

      Every Appendix-C route accepts only role/programme-bound JWT; old doors
      are refused; forge/git and agent dispatch resolve per-programme
      credentials only.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-23, REQ-24, REQ-29, REQ-30, REQ-31 | — | Role/tenant deps refuse correctly | command |
      | TASK-W2-02 | REQ-04, REQ-32, REQ-33 | TASK-W2-01 | Old doors refused on every route | command |
      | TASK-W2-03 | REQ-25 | — | Per-programme ForgeClient | command |
      | TASK-W2-04 | REQ-23, REQ-24, REQ-31 | TASK-W2-01 | Tenant-scoped queries | command |
      | TASK-W2-05 | REQ-26, REQ-41 | — | Catalogue-only agent dispatch | command |
      | TASK-W2-06 | REQ-28 | TASK-W2-02 | Webhook path unaffected | review |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-014-gateflow.md

  - id: W3
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-014 W3] Dead-door deletion + wipe cutover"
    depends_on:
      - W2
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
    tasks:
      - id: TASK-W3-01
        implements: [REQ-34]
        depends_on: []
        files:
          - path: src/api/v1/programme_token.py
            action: delete
          - path: src/api/v1/tenant_token.py
            action: delete
          - path: src/api/v1/tenant_routes.py
            action: modify
          - path: tests/verify/verify_dead_doors_deleted.py
            action: create
        exit:
          criteria:
            - "make check passes with zero references to deleted modules; POST /api/v1/tenants returns 404/405"
          proof:
            kind: command
            command: "make check && pytest tests/unit/test_tenant_routes.py -k register -v"
            expected: "exit 0; open-register test asserts gone, not merely refused"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W3-02
        implements: [REQ-35, REQ-46]
        depends_on: []
        files:
          - path: src/business_services/programme_wipe_service.py
            action: create
          - path: src/api/v1/programme_admin_routes.py
            action: modify
          - path: tests/verify/verify_wipe_cutover.py
            action: create
        exit:
          criteria:
            - "Wipe with an ACTIVE run present returns 409 named reason, 0 wipe"
          proof:
            kind: command
            command: "pytest tests/unit/test_programme_wipe_service.py -v"
            expected: "exit 0; in-flight-run case asserted"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
        covers: [REQ-34, REQ-35, REQ-46]
        prerequisites:
          - "API up"
          - "Synthetic 012/013-shaped lab tenant row present"
        safe_test_data:
          - "Synthetic lab tenant smoke-legacy-tenant"
        steps:
          - "Run verify_dead_doors_deleted.py"
          - "Run verify_wipe_cutover.py"
        expected_observations:
          - "Old-door routes return 404/405; wipe succeeds when idle, rejects when in-flight"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "None beyond what the wipe itself performs"
        stop_conditions:
          - "Wipe succeeds while a run is ACTIVE → stop"
    body: |
      ## Wave goal

      Programme-token and tenant-bearer code paths are structurally deleted;
      012/013 lab tenant rows are wiped with an in-flight-run guard.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W3-01 | REQ-34 | — | Dead doors deleted, not just refused | command |
      | TASK-W3-02 | REQ-35, REQ-46 | — | Wipe fail-closed on in-flight run | command |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-014-gateflow.md

  - id: W4
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-014 W4] Prove absence + rewrite teaching surfaces"
    depends_on:
      - W3
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_all
    tasks:
      - id: TASK-W4-01
        implements: [REQ-36, REQ-38]
        depends_on: []
        files:
          - path: tests/verify/verify_wave_start.py
            action: modify
          - path: tests/verify/verify_board.py
            action: modify
          - path: tests/verify/verify_tenant_registry.py
            action: modify
          - path: tests/verify/verify_repo_selection.py
            action: modify
          - path: tests/verify/verify_checkpoint_status.py
            action: modify
          - path: tests/verify/verify_status_metrics.py
            action: modify
        exit:
          criteria:
            - "Every listed script runs green using only JWT auth; zero PROGRAMME_SERVICE_TOKEN references remain"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_all"
            expected: "exit 0; grep for PROGRAMME_SERVICE_TOKEN in tests/verify/ returns zero matches"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W4-02
        implements: [REQ-37]
        depends_on: [TASK-W4-01]
        files:
          - path: tests/verify/verify_old_doors_refused.py
            action: create
        exit:
          criteria:
            - "Script asserts old programme token, old tenant bearer, and open register are all gone/refused"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_old_doors_refused"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W4-03
        implements: [REQ-38]
        depends_on: [TASK-W4-02]
        files:
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-014.md
            action: create
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "tests/README.md lists only JWT-based invocation examples for Appendix-C scripts"
          proof:
            kind: review
            review: "PE reviews docs diff against REQ-38"
            expected: "No lingering old-door invocation examples remain"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-014-W4.md § TASK-W4-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_all
        covers: [REQ-36, REQ-37, REQ-38]
        prerequisites:
          - "Full stack up (API + worker)"
          - "At least one Accepted Programme + tenant_admin from prior waves"
        safe_test_data:
          - "Reuses W0-W3 synthetic fixtures where present"
        steps:
          - "Run verify_all.py"
          - "Run verify_old_doors_refused.py"
        expected_observations:
          - "Full suite green under JWT-only auth; old-door negative-path proves refusal/absence"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Remove all synthetic fixtures created across W0-W4 smoke runs"
        stop_conditions:
          - "Any script still succeeding with an old-door credential → stop (initiative exit gate)"
    body: |
      ## Wave goal

      Every verify/teaching surface instructs JWT + per-programme GitHub + DB
      catalogue only; live scripts prove JWT happy path and old-door refusal.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W4-01 | REQ-36, REQ-38 | — | Existing scripts rewritten for JWT | command |
      | TASK-W4-02 | REQ-37 | TASK-W4-01 | Old-door refusal proven | command |
      | TASK-W4-03 | REQ-38 | TASK-W4-02 | Teaching docs updated | review |

      ## Done when

      - [ ] All W4 tasks complete per plan exit proof
      - [ ] Initiative exit gate proven: JWT happy path + old-door refusal, both live

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-014-gateflow.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-014
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/212"
    waves: [W0, W1, W2, W3, W4]
    task_count: 22
    p1_p16_status: pass
    tdd_status: Accepted
    adrs_accepted:
      - adr-014-jwt-only-product-edge-trust-zone.md
      - adr-015-programme-scoped-forge-credential-resolution.md
      - adr-016-tenant-scoped-run-board-checkpoint-authorization.md
    ready_for_coding_readiness: true
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
```
