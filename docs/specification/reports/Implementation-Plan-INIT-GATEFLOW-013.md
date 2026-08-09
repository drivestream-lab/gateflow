---
goal: INIT-GATEFLOW-013 — implementation plan
initiative: INIT-GATEFLOW-013
status: Planned
date_created: 2026-08-09
source_spec: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-013.md
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md
prd_digest: sha256:3789897ca98d12fe7f2f9aae62551184986a3703b45d50f387c56e615ca40845
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-013.md
impact_map_revision: 1
repo_scope_digest: sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e
approved_meta_pr_head: 59301dce846043b8a4e70057a81dfa67a4868ece
branch: chore/INIT-GATEFLOW-013-spec-gateflow
review_deadline: 2026-08-12
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-013

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | CURRENT — tip `cf39fee6b5384a10a1d8439c28d02b02bba58166` matches PR #198; H1–H3/G1 match Meta Gate 1 |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-013.md` | CURRENT — walk-time companion on same tip |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md` | CURRENT — Status: Accepted |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-013.md` / `1` | CURRENT |
| Repo scope digest | `sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e` | CURRENT |
| Approved meta PR head | `59301dce846043b8a4e70057a81dfa67a4868ece` | CURRENT — Meta PR #33 |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED (`tests/unit/` via Makefile) |
| `verify_command` | per-wave live scripts under `tests/verify/` (P15 co-ship) | RESOLVED |
| `ground_command` | N/A — Pass-2 `/ground-spec` updates as-built after wave-acceptance; no Makefile ground target | RESOLVED |

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md` |
| Technical review status | Accepted |
| PE sign-off | [x] complete — 2026-08-09 (@nikd10x Cursor chat) |
| Resolved ADRs | [`adr-012-programme-catalogue-discovery-authority.md`](../adr/adr-012-programme-catalogue-discovery-authority.md) (Accepted); [`adr-013-dual-harness-readiness-evaluators.md`](../adr/adr-013-dual-harness-readiness-evaluators.md) (Accepted) |
| ADR product-boundary re-check | Both ADRs: `changes_user_visible_behavior: false`, `spec_amendment_required: false`. Plan-time `adr_boundary_lint.py --verify-lint-evidence --require-sources` PASS (ADR-012 4 sources; ADR-013 6 sources) against REQ rows + feasibility Spec quotes |
| Outstanding PM questions | PM-1 (non-blocking) — inventory hand-typed `repos[]` dependents before W1 merge |
| Outstanding domain questions | D-1 (non-blocking) — OQ-9 legacy force-recheck without connect; default filesystem-only until connect |

> Do not start W0 implementation until PE sign-off is marked complete above (satisfied).
> Coding starts only after Gate 2 `spec-lgtm` + merge + `/create-board-tickets`.

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Connect clones/syncs programme meta via existing git client | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-02 | Connect uses existing tenant credential / auth | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-03 | No separate programme credential type | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-04 | Connect fail-closed with named reason; no partial copy | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-05 | Catalogue candidates from synced programme records | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-06 | Malformed catalogue rejected; no partial list | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-07 | Catalogue reflects latest sync (not frozen at first connect) | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |
| REQ-08 | Select/save subset of candidates as active repos | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-09 | Out-of-catalogue select rejected | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-10 | Re-selection validated against current catalogue | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-11 | New select runs GithubPatProbe; failure rejects | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-12 | Registration rejects repos[] payload | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-13 | Selection is sole path to gain repos | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-14 | Newly selected repos set up via resolve_workspace | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W2 |
| REQ-15 | Setup failures isolated per repo | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W2 |
| REQ-16 | Per-repo setup results reported | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W2 |
| REQ-17 | Launchpad status readiness for selection-admitted repos | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-18 | Status client inspect-only (no apply/mutate) | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-19 | Status check failures isolated per repo | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-20 | tool_unavailable distinct from repo not-ready | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-21 | Status result becomes stored readiness for new repos | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-22 | Pre-INIT repos keep filesystem readiness untouched | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-23 | On-demand readiness refresh for status-sourced repos | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W3 |
| REQ-24 | Catalogue refresh re-syncs programme copy | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W4 |
| REQ-25 | Refresh does not alter existing selections | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W4 |
| REQ-26 | Deselect changes membership only (clone/readiness untouched) | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-27 | Deselect blocked while ACTIVE run for that repo | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W1 |
| REQ-28 | Exactly one programme connection per tenant (upsert) | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` | W0 |

---

## 2. Implementation phases

### Phase W0 — Connect + catalogue discovery

**GOAL-W0:** Tenant connects once to programme meta (clone/fetch + optional ref), persists a single programme connection, and can read a fail-closed catalogue of candidate repos from the synced checkout (ADR-012).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Add `tenant_programme_connections` ORM + repository/DTO mapping + human DDL note (1:1 tenant); no fake app-repo row | REQ-01, REQ-28 | — | `src/database/postgres/schema/tenant_schema.py` modify; `src/database/postgres/repository/tenant_repository.py` modify; `postgres_migrations/env.py` modify; `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-programme-connection.md` create | Schema registers on metadata; repo can upsert/get connection DTO; DDL note lists columns/indexes for human Alembic | review / PE DDL note review | DDL note complete; schema import in env.py; no `versions/` edit by agent | Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-01 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make check` | repository-pattern: ORM only in schema/repo; database-migrations: agent never writes versions/ | TDD §8 dedicated table | `feature/INIT-GATEFLOW-013-w0-programme-connect` |
| TASK-W0-02 | Extend `TenantGitWorkspaceClient.resolve_workspace` with optional `ref` + post-sync checkout | REQ-01 | TASK-W0-01 | `src/infra_services/tenant_git_workspace_client.py` modify; `tests/unit/test_tenant_git_workspace_client.py` modify | When `ref` set, workspace checked out to that ref after clone/fetch; default-branch path unchanged when omitted | command / `make test` | unit tests for ref + no-ref paths pass | Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-02 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | infra-services: git client stays infra | TDD FF-05 / §3.2 | same |
| TASK-W0-03 | Implement CatalogueParser + candidate Pydantic models (read-only YAML → DTO; fail-closed) | REQ-05, REQ-06, REQ-07 | TASK-W0-01 | `src/engine/catalogue_parser.py` create (or `src/business_services/catalogue_parser.py`); `src/models/programme_catalogue_models.py` create; `tests/unit/test_catalogue_parser.py` create | Valid fixture yields exact candidate list; missing/malformed yields named error and empty/no partial list | command / `make test` | parser unit suite green | Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-03 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | pydantic-schemas: models in src/models only | ADR-012 Option A discovery-input; not GATEFLOW_* knobs | same |
| TASK-W0-04 | Programme connect + catalogue-read business service + tenant-scoped HTTP routes + DI bind | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-28 | TASK-W0-02, TASK-W0-03 | `src/business_services/programme_onboarding_service.py` create (or extend tenant_service); `src/models/programme_connection_models.py` create; `src/api/v1/programme_routes.py` create; `src/api/v1/__init__.py` modify; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify | Connect upserts one connection, syncs meta with tenant PAT, fail-closed cleanup on git failure; catalogue GET returns candidates or 422 named shape error; no PAT in responses | command / `make check` | check clean; OpenAPI shows connect + catalogue | Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-04 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make check` | http-api-conventions: body models; architecture: routes→business only; ADR-011 tenant bearer | ADR-012 for catalogue authority | same |
| TASK-W0-05 | Unit tests for connect upsert, fail-closed cleanup, auth reuse, catalogue happy/malformed | REQ-02, REQ-03, REQ-04, REQ-28 | TASK-W0-04 | `tests/unit/test_programme_onboarding.py` create | Named failure reasons asserted; second connect updates same row; no new credential fields | command / `make test` | unit suite green | Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-05 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | | | same |
| TASK-W0-06 | Co-ship live `verify_programme_connect` + feature-map rows | REQ-01, REQ-04, REQ-05, REQ-06, REQ-28 | TASK-W0-04 | `tests/verify/verify_programme_connect.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live script exercises connect + catalogue against running API with synthetic tenant; exit 0 on pass | command / `.venv/bin/python -m tests.verify.verify_programme_connect` | exit 0; asserts connection fields + candidate list | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `.venv/bin/python -m tests.verify.verify_programme_connect` | testing-verify-flows | | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/database/postgres/schema/tenant_schema.py` | modify |
| FILE-W0-02 | `src/database/postgres/repository/tenant_repository.py` | modify |
| FILE-W0-03 | `postgres_migrations/env.py` | modify |
| FILE-W0-04 | `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-programme-connection.md` | create |
| FILE-W0-05 | `src/infra_services/tenant_git_workspace_client.py` | modify |
| FILE-W0-06 | `src/engine/catalogue_parser.py` | create |
| FILE-W0-07 | `src/models/programme_catalogue_models.py` | create |
| FILE-W0-08 | `src/models/programme_connection_models.py` | create |
| FILE-W0-09 | `src/business_services/programme_onboarding_service.py` | create |
| FILE-W0-10 | `src/api/v1/programme_routes.py` | create |
| FILE-W0-11 | `src/api/v1/__init__.py` | modify |
| FILE-W0-12 | `src/di/modules/business_services_module.py` | modify |
| FILE-W0-13 | `src/di/dependency_container.py` | modify |
| FILE-W0-14 | `tests/unit/test_catalogue_parser.py` | create |
| FILE-W0-15 | `tests/unit/test_programme_onboarding.py` | create |
| FILE-W0-16 | `tests/unit/test_tenant_git_workspace_client.py` | modify |
| FILE-W0-17 | `tests/verify/verify_programme_connect.py` | create |
| FILE-W0-18 | `tests/README.md` | modify |
| FILE-W0-19 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-01–07, REQ-28 / TASK-W0-02..05 |
| TEST-W0-I | integration/contract | N/A — catalogue parse is pure filesystem fixture; git boundary covered by unit doubles | — |
| TEST-W0-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_programme_connect` | connect + catalogue product surface (P15) |

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01 connect sync | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-02/03 credential reuse | TEST-W0-U | N/A | N/A | N/A | inspection of models in unit |
| REQ-04 fail-closed | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-05/06/07 catalogue | TEST-W0-U | N/A | TEST-W0-L | N/A | REQ-07 fully with W4 refresh; W0 proves non-frozen parser input path |
| REQ-28 single connection | TEST-W0-U | N/A | TEST-W0-L | N/A | |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | yes — new connect/catalogue HTTP surface |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against the wave PR head under test |
| Prerequisites | API+Postgres up; tenant PAT with read on programme meta; `tests/config.yaml` |
| Safe test data | Ephemeral tenant + disposable programme meta fixture/org |
| Steps / command | `.venv/bin/python -m tests.verify.verify_programme_connect` |
| Expected observations | 2xx connect; connection org/repo/ref; catalogue non-empty or known fixture; bad shape → 422 named |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Delete ephemeral tenant / workspace dirs per script |
| Stop conditions | Non-zero exit or unexpected 5xx → stop; do not start Pass-2 |

---

### Phase W1 — Select/deselect + retire hand-typed repos[]

**GOAL-W1:** Operators admit/deselect active repos from the current catalogue only; registration rejects `repos[]`; PAT probe gates new admits; deselect blocked when ACTIVE run. Setup/status batch hooks reserved for W2/W3 (TDD: same request — wire sequentially).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Retire `repos[]` at registration (reject non-empty / remove required); close other add-repo paths | REQ-12, REQ-13 | — (wave depends_on W0) | `src/models/tenant_models.py` modify; `src/business_services/tenant_service.py` modify; `tests/unit/test_tenant_service.py` modify; `tests/verify/verify_tenant_registry.py` modify | Registration with `repos` → 422/400; registration without repos succeeds; no alternate API adds `tenant_repos` | command / `make test` | unit + registry verify path updated | Wave-Execution-INIT-GATEFLOW-013-W1.md § TASK-W1-01 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | http-api-conventions breaking body change | AF-1 | `feature/INIT-GATEFLOW-013-w1-repo-selection` |
| TASK-W1-02 | Select/deselect APIs: catalogue subset validation, PAT probe on new admits, active-run deselect guard, membership-only deselect | REQ-08, REQ-09, REQ-10, REQ-11, REQ-26, REQ-27 | TASK-W1-01 | `src/business_services/programme_onboarding_service.py` modify; `src/models/programme_selection_models.py` create; `src/api/v1/programme_routes.py` modify; `src/database/postgres/repository/tenant_repository.py` modify | Out-of-catalogue → 422 0 change; probe fail → 422 0 change; deselect with ACTIVE → 422; deselect success leaves clone/readiness; per-repo admit results include pending_setup until W2 | command / `make check` | check clean | Wave-Execution-INIT-GATEFLOW-013-W1.md § TASK-W1-02 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make check` | fail-fast named reasons | TDD §3.1 select body; selection+setup coupling deferred wiring | same |
| TASK-W1-03 | Unit tests for select/deselect/probe/active-run/registration reject | REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-26, REQ-27 | TASK-W1-02 | `tests/unit/test_programme_selection.py` create | All REQ branches assertable with mocks | command / `make test` | suite green | Wave-Execution-INIT-GATEFLOW-013-W1.md § TASK-W1-03 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | | | same |
| TASK-W1-04 | Co-ship `verify_repo_selection` + README/as-built | REQ-08, REQ-09, REQ-11, REQ-12, REQ-26, REQ-27 | TASK-W1-02 | `tests/verify/verify_repo_selection.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live script: register without repos, connect (W0), select in-catalogue, reject out-of-catalogue, deselect | command / `.venv/bin/python -m tests.verify.verify_repo_selection` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `.venv/bin/python -m tests.verify.verify_repo_selection` | testing-verify-flows; PM-1 inventory before merge | | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/models/tenant_models.py` | modify |
| FILE-W1-02 | `src/business_services/tenant_service.py` | modify |
| FILE-W1-03 | `src/models/programme_selection_models.py` | create |
| FILE-W1-04 | `src/business_services/programme_onboarding_service.py` | modify |
| FILE-W1-05 | `src/api/v1/programme_routes.py` | modify |
| FILE-W1-06 | `src/database/postgres/repository/tenant_repository.py` | modify |
| FILE-W1-07 | `tests/unit/test_programme_selection.py` | create |
| FILE-W1-08 | `tests/unit/test_tenant_service.py` | modify |
| FILE-W1-09 | `tests/verify/verify_tenant_registry.py` | modify |
| FILE-W1-10 | `tests/verify/verify_repo_selection.py` | create |
| FILE-W1-11 | `tests/README.md` | modify |
| FILE-W1-12 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-08–13, 26–27 |
| TEST-W1-I | integration/contract | N/A — PAT probe boundary via unit doubles; live covers real probe when configured | — |
| TEST-W1-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_repo_selection` | selection + registration surface (P15) |

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-08–11 select/probe | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-12–13 registration | TEST-W1-U | N/A | TEST-W1-L | N/A | also verify_tenant_registry |
| REQ-26–27 deselect | TEST-W1-U | N/A | TEST-W1-L | N/A | ACTIVE-run may be unit-primary if hard to stage live |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W0 live path available; PAT; API up |
| Safe test data | Ephemeral tenant + catalogue fixture repos |
| Steps / command | `.venv/bin/python -m tests.verify.verify_repo_selection` |
| Expected observations | select ok; out-of-catalogue 422; registration with repos rejected |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Delete ephemeral tenant |
| Stop conditions | Non-zero / unexpected 5xx |

---

### Phase W2 — Setup chosen repos (batch)

**GOAL-W2:** Newly admitted repos run `resolve_workspace` independently; per-repo results; wire into selection response (TDD same-request coupling).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Wire per-repo `resolve_workspace` into selection for newly admitted repos; isolate failures; report per-repo setup results | REQ-14, REQ-15, REQ-16 | — (depends_on W1) | `src/business_services/programme_onboarding_service.py` modify; `src/models/programme_selection_models.py` modify | Mixed batch: one setup fail does not block others; response lists per-repo setup outcome/reason; workspace present on success | command / `make check` | check clean | Wave-Execution-INIT-GATEFLOW-013-W2.md § TASK-W2-01 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make check` | infra reuse TenantGitWorkspaceClient | ADR-010 workspace authority unchanged | `feature/INIT-GATEFLOW-013-w2-repo-setup` |
| TASK-W2-02 | Unit tests for setup isolation + result shape | REQ-14, REQ-15, REQ-16 | TASK-W2-01 | `tests/unit/test_programme_selection.py` modify | Mocked git failures isolated | command / `make test` | suite green | Wave-Execution-INIT-GATEFLOW-013-W2.md § TASK-W2-02 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | | | same |
| TASK-W2-03 | Extend live verify for setup batch (same or sibling script) | REQ-14, REQ-15, REQ-16 | TASK-W2-01 | `tests/verify/verify_repo_selection.py` modify (or `tests/verify/verify_repo_setup.py` create); `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live assert clone/fetch under tenant workspace for newly selected repo; mixed-fail path unit-covered if unsafe live | command / `.venv/bin/python -m tests.verify.verify_repo_selection` | exit 0; setup ok observation | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `.venv/bin/python -m tests.verify.verify_repo_selection` | P15: extend selection verify to assert setup surface | | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/business_services/programme_onboarding_service.py` | modify |
| FILE-W2-02 | `src/models/programme_selection_models.py` | modify |
| FILE-W2-03 | `tests/unit/test_programme_selection.py` | modify |
| FILE-W2-04 | `tests/verify/verify_repo_selection.py` | modify |
| FILE-W2-05 | `tests/README.md` | modify |
| FILE-W2-06 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-14–16 |
| TEST-W2-I | integration/contract | N/A — git boundary via existing client + unit doubles | — |
| TEST-W2-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_repo_selection` | setup-on-select surface |

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-14 setup mechanism | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-15/16 isolation + reports | TEST-W2-U | N/A | TEST-W2-L | N/A | mixed fail primarily unit |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | yes — setup path on selection |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W0+W1; writable workspace_root; PAT |
| Safe test data | Ephemeral tenant + selectable fixture repo |
| Steps / command | `.venv/bin/python -m tests.verify.verify_repo_selection` (setup assertions) |
| Expected observations | Selected repo directory present under tenant workspace |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Remove workspace dirs / tenant |
| Stop conditions | Non-zero / unexpected 5xx |

---

### Phase W3 — Real Launchpad status readiness + dual evaluators

**GOAL-W3:** Inspect-only Launchpad status for selection-admitted repos; provenance switch vs filesystem for pre-INIT; on-demand refresh; tool_unavailable distinct (ADR-013).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | Create `LaunchpadStatusClient` (inspect-only argv); settings path; DI; image/docs note for preinstalled CLI | REQ-17, REQ-18, REQ-20 | — (depends_on W2) | `src/infra_services/launchpad_status_client.py` create; `src/configs/app_settings.py` modify; `src/di/modules/infra_module.py` modify; `src/di/dependency_container.py` modify; `docs/specification/reports/OPS-NOTE-INIT-GATEFLOW-013-launchpad-cli.md` create | Client never invokes apply; missing binary → `tool_unavailable`; health/status fail-closed | command / `make test` | unit argv-guard + tool_unavailable mapping green | Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-01 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | infra BaseInfraService lifecycle; settings via get_instance() | ADR-013 Option B separate client; TDD FF-06 | `feature/INIT-GATEFLOW-013-w3-status-readiness` |
| TASK-W3-02 | Persist `readiness_source` (or equivalent provenance) at admission; wire status into selection batch; `mark_harness_verified` only for status path; on-demand refresh endpoint | REQ-17, REQ-19, REQ-21, REQ-22, REQ-23 | TASK-W3-01 | `src/database/postgres/schema/tenant_schema.py` modify; `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-readiness-source.md` create; `src/business_services/programme_onboarding_service.py` modify; `src/business_services/tenant_service.py` modify; `src/api/v1/programme_routes.py` modify; `src/models/` modify | New admits get status evaluator; pre-INIT rows never written by status path; refresh replaces stored answer in place for status-sourced repos | command / `make check` | check clean | Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-02 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make check` | migrations: schema+env only | ADR-013 provenance; TDD §8 column | same |
| TASK-W3-03 | Dual evaluator switch in wave-start / orchestrator harness gates; fail-closed when never-checked selected repo | REQ-21, REQ-22 | TASK-W3-02 | `src/business_services/wave_start_service.py` modify; `src/business_services/run_orchestrator.py` modify (paths as as-built) | Provenance selects status vs filesystem; legacy force-recheck never calls status (D-1 default); never-checked → block start | command / `make test` | unit provenance matrix green | Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-03 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | | ADR-013 dual evaluators | same |
| TASK-W3-04 | Unit tests: dual gate, argv guard, tool_unavailable, legacy untouched | REQ-18, REQ-19, REQ-20, REQ-21, REQ-22, REQ-23 | TASK-W3-03 | `tests/unit/test_launchpad_status_client.py` create; `tests/unit/test_harness_dual_gate.py` create | Exact call assertions for evaluator choice | command / `make test` | suite green | Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-04 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make test` | | | same |
| TASK-W3-05 | Co-ship `verify_harness_status` (+ retain filesystem verify for legacy) | REQ-17, REQ-18, REQ-20, REQ-21, REQ-23 | TASK-W3-02 | `tests/verify/verify_harness_status.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live: select-admitted repo gets status-sourced readiness; tool missing path unit/ops; filesystem verify still passes for legacy fixture | command / `.venv/bin/python -m tests.verify.verify_harness_status` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `.venv/bin/python -m tests.verify.verify_harness_status` | Launchpad CLI preinstalled in env | | same |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/infra_services/launchpad_status_client.py` | create |
| FILE-W3-01b | `src/configs/app_settings.py` | modify |
| FILE-W3-02 | `src/di/modules/infra_module.py` | modify |
| FILE-W3-03 | `src/di/dependency_container.py` | modify |
| FILE-W3-04 | `src/database/postgres/schema/tenant_schema.py` | modify |
| FILE-W3-05 | `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-readiness-source.md` | create |
| FILE-W3-06 | `docs/specification/reports/OPS-NOTE-INIT-GATEFLOW-013-launchpad-cli.md` | create |
| FILE-W3-07 | `src/business_services/programme_onboarding_service.py` | modify |
| FILE-W3-08 | `src/business_services/wave_start_service.py` | modify |
| FILE-W3-09 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W3-10 | `tests/unit/test_launchpad_status_client.py` | create |
| FILE-W3-11 | `tests/unit/test_harness_dual_gate.py` | create |
| FILE-W3-12 | `tests/verify/verify_harness_status.py` | create |
| FILE-W3-13 | `tests/README.md` | modify |
| FILE-W3-14 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-17–23 |
| TEST-W3-I | integration/contract | contract test vs real CLI when binary present (optional in CI) | REQ-17/20 boundary |
| TEST-W3-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_harness_status` | status readiness surface (P15) |

#### Verification Coverage (W3)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-17/18 status inspect | TEST-W3-U | TEST-W3-I optional | TEST-W3-L | N/A | |
| REQ-19/20 isolation + tool | TEST-W3-U | N/A | TEST-W3-L | N/A | tool_unavailable may be unit-only |
| REQ-21/22 dual provenance | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-23 on-demand refresh | TEST-W3-U | N/A | TEST-W3-L | N/A | |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | Launchpad CLI on PATH/settings; programme meta synced; W0–W2 |
| Safe test data | Selection-admitted fixture repo |
| Steps / command | `.venv/bin/python -m tests.verify.verify_harness_status` |
| Expected observations | Stored readiness reflects status; legacy filesystem path unchanged |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Ephemeral tenant |
| Stop conditions | Non-zero / unexpected 5xx |

---

### Phase W4 — Catalogue refresh

**GOAL-W4:** Connected tenant can re-sync programme records; selections unchanged; new candidates appear (REQ-07 full proof).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W4-01 | Catalogue refresh API: re-sync connection checkout; fail-closed on git error without touching selections/readiness | REQ-07, REQ-24, REQ-25 | — (depends_on W3) | `src/business_services/programme_onboarding_service.py` modify; `src/api/v1/programme_routes.py` modify; `src/models/programme_connection_models.py` modify | Refresh updates last_synced_at + tree; active list unchanged; catalogue may grow | command / `make check` | check clean | Wave-Execution-INIT-GATEFLOW-013-W4.md § TASK-W4-01 | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `make check` | | ADR-012 discovery from latest sync | `feature/INIT-GATEFLOW-013-w4-catalogue-refresh` |
| TASK-W4-02 | Unit + live verify refresh | REQ-07, REQ-24, REQ-25 | TASK-W4-01 | `tests/unit/test_programme_onboarding.py` modify; `tests/verify/verify_catalogue_refresh.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live: refresh after fixture catalogue growth shows new candidate; selection IDs unchanged | command / `.venv/bin/python -m tests.verify.verify_catalogue_refresh` | exit 0 | wave-accepted on tip | gateflow | docs/specification/product/INIT-GATEFLOW-013-gateflow.md | `.venv/bin/python -m tests.verify.verify_catalogue_refresh` | | | same |

#### Files (W4)

| ID | Path | Action |
|----|------|--------|
| FILE-W4-01 | `src/business_services/programme_onboarding_service.py` | modify |
| FILE-W4-02 | `src/api/v1/programme_routes.py` | modify |
| FILE-W4-03 | `tests/unit/test_programme_onboarding.py` | modify |
| FILE-W4-04 | `tests/verify/verify_catalogue_refresh.py` | create |
| FILE-W4-05 | `tests/README.md` | modify |
| FILE-W4-06 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W4)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W4-U | unit | `make test` | REQ-07, 24–25 |
| TEST-W4-I | integration/contract | N/A | — |
| TEST-W4-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_catalogue_refresh` | refresh surface (P15) |

#### Verification Coverage (W4)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-24 refresh sync | TEST-W4-U | N/A | TEST-W4-L | N/A | |
| REQ-25 selections untouched | TEST-W4-U | N/A | TEST-W4-L | N/A | |
| REQ-07 latest copy | TEST-W4-U | N/A | TEST-W4-L | N/A | completes W0 partial |

#### Live-verification intent (W4)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | Connected tenant; mutable fixture catalogue remote or simulated |
| Safe test data | Ephemeral tenant |
| Steps / command | `.venv/bin/python -m tests.verify.verify_catalogue_refresh` |
| Expected observations | New candidates after refresh; prior selection membership unchanged |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | Ephemeral tenant |
| Stop conditions | Non-zero / unexpected 5xx |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | Human Alembic for `tenant_programme_connections` (W0 DDL note) | W0 live verify until applied |
| DEP-02 | Human Alembic for `readiness_source` (W3 DDL note) | W3 dual-gate live |
| DEP-03 | Launchpad CLI preinstalled in API/worker images (FF-06) | W3 live status path |
| DEP-04 | Meta CTR-01 catalogue YAML shape available in programme checkout | W0 catalogue live |
| DEP-05 | PM-1 inventory of `repos[]` dependents (non-blocking) | W1 merge hygiene |
| DEP-06 | Wave order W0→W1→W2→W3→W4 | each subsequent wave |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Selection+setup+status same-request latency | Per-repo isolation; report partial; keep timeouts explicit in settings |
| RISK-02 | ADR-004 confusion when parsing meta YAML | Cite ADR-012 in TASK-W0-03; parser never loads GATEFLOW_* |
| RISK-03 | Dual evaluator mis-branching marks legacy ready wrongly | `readiness_source` at admission; unit provenance matrix; never write status path to pre-INIT |
| RISK-04 | Launchpad binary missing in runtime | OPS note + fail-closed `tool_unavailable` (REQ-20) |
| RISK-05 | Breaking registration contract (repos[]) | Update verify_tenant_registry + PM-1 inventory before W1 merge |
| RISK-06 | D-1 legacy force-recheck ambiguity | Default filesystem-only until connect; document in OPS/as-built |

---

## 5. Out of scope

- `gateflow-ops` UI
- Launchpad mutate/apply / install
- `prayog-skills` contract or pin changes
- Provider-side changes in `prayog-meta` / `launchpad` (consume CTR-01/CTR-02 only)
- Agent-authored files under `postgres_migrations/versions/`

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Update implementation-status.md | `docs/specification/as-built/implementation-status.md` | mark each wave in_progress → complete in same PR as code |
| Update tests/README.md | `tests/README.md` | feature-map rows for verify_programme_connect, verify_repo_selection, verify_harness_status, verify_catalogue_refresh |
| DDL notes | `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-*.md` | human Alembic inputs (W0, W3) |
| Ops note | `docs/specification/reports/OPS-NOTE-INIT-GATEFLOW-013-launchpad-cli.md` | CLI preinstall (W3) |

> **ADR lifecycle** — Accepted ADR-012/013 already exist; do not add ADR promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ coverage in §1 + TASK Implements | PASS |
| P2 every REQ ≥1 TASK; every TASK ≥1 REQ | PASS |
| P3 FILE paths per TASK | PASS |
| P4 objective exit evidence | PASS |
| P5 Verification Coverage + unit floor | PASS |
| P6 scope ≤ spec REQ-01–28 | PASS |
| P7 feas blockers → Accepted ADRs / TDD_ONLY; residual RISK | PASS |
| P8 wave order W0→W4 | PASS |
| P9 as-built/README in wave FILE lists | PASS |
| P10 self-contained + command contract | PASS |
| P11 MDC notes on architectural TASKs | PASS |
| P12 ADR-012/013 Accepted cited | PASS |
| P13 TDD Accepted; PE sign-off; lint re-verify PASS | PASS |
| P14 WorkManifest §9 shape | PASS |
| P15 co-ship live verify per surface wave | PASS |
| P16 workmanifest_contract.py | PASS (validated at plan write) |

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` to Draft spec PR
> `https://github.com/drivestream-lab/gateflow/pull/198` branch `chore/INIT-GATEFLOW-013-spec-gateflow`. Do **not** commit inside this skill. Label remains
> **`spec-pending`** until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-013-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/198
PR title: "[INIT-GATEFLOW-013] Spec — Programme-first onboarding and real readiness checks (gateflow)"

Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-12

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + TDD + Accepted ADRs + this plan on current head
  [ ] §0 PE sign-off on TDD marked complete
  [ ] Wave order and dependencies make sense
  [ ] Done-when / exit criteria observable (P4)
  [ ] Verification Coverage maps every criterion (P5)
  [ ] WorkManifest YAML (§9) passes workmanifest_contract.py (P16)
  [ ] P1–P16 all PASS (P15 co-ship)

After spec-lgtm + Approve + merge — `/create-board-tickets` from §9 (post-merge only).
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 PASS; Accepted TDD/ADRs; sources CURRENT |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/198 |
| Spec PR head SHA | `cf39fee6b5384a10a1d8439c28d02b02bba58166` (plan not yet on tip — publish via `/commit-workspace` first) |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md` |
| Forge readiness | `handoff.forge` → `/commit-workspace` onto `chore/INIT-GATEFLOW-013-spec-gateflow` |
| Blocking items | none for planning; PE must publish plan then set `spec-lgtm` |

Provision labels when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

PE actions (all on **exact current head** after plan publish):

1. Remove `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale`; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body (below)
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/create-board-tickets`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-013
spec_pr_head_sha: <SHA after plan commit>
meta_pr_head_sha: 59301dce846043b8a4e70057a81dfa67a4868ece
impact_map_revision: 1
prd_digest: sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1
scope_digest: sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e
plan_digest: sha256:3789897ca98d12fe7f2f9aae62551184986a3703b45d50f387c56e615ca40845
artifacts:
  - docs/specification/product/INIT-GATEFLOW-013-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-013.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

---

## 9. WorkManifest seed

> Primary: `/create-board-tickets` after spec merge. Validate with
> `python prayog-skills/scripts/workmanifest_contract.py` on this plan.

```yaml
# Generated by /spec-implementation-plan — 2026-08-09
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-013

metadata:
  title: INIT-GATEFLOW-013 — Programme-first onboarding and real readiness
  summary: |
    Gateflow adds programme connect, catalogue-driven repo selection, batch
    setup via existing git workspace client, and dual harness readiness
    (Launchpad status for selection-admitted repos; filesystem for pre-INIT).
  playbook:
    - docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md

target:
  org: drivestream-lab
  project: drivestream-lab Board

defaults:
  initiative: INIT-GATEFLOW-013
  parent: EPIC
  labels:
    - INIT-GATEFLOW-013

epic:
  id: EPIC
  repo: gateflow
  title: "[feature] INIT-GATEFLOW-013 — Programme-first onboarding and real readiness"
  codebase: gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_programme_connect
  body: |
    ## Objective

    Programme-first tenant onboarding: connect meta, catalogue candidates,
    select/deselect without hand-typed repos[], setup via resolve_workspace,
    real Launchpad status readiness for new admits, catalogue refresh.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Connect + catalogue |
    | W1 | Select/deselect; retire repos[] |
    | W2 | Setup chosen repos |
    | W3 | Real readiness + dual evaluators |
    | W4 | Catalogue refresh |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md
    - ADR-012, ADR-013 (Accepted)

work:
  - id: W0
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-013 W0] Connect programme + catalogue discovery"
    depends_on: []
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_programme_connect
    tasks:
      - id: TASK-W0-01
        implements: [REQ-01, REQ-28]
        depends_on: []
        files:
          - path: src/database/postgres/schema/tenant_schema.py
            action: modify
          - path: src/database/postgres/repository/tenant_repository.py
            action: modify
          - path: postgres_migrations/env.py
            action: modify
          - path: docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-programme-connection.md
            action: create
        exit:
          criteria:
            - "tenant_programme_connections ORM + repo upsert/get DTO; DDL note for human Alembic; no versions/ edit"
          proof:
            kind: review
            review: "PE reviews DDL-NOTE-INIT-GATEFLOW-013-programme-connection.md + schema registration in env.py + repository upsert/get"
            expected: "DDL note complete; schema imported; repository methods present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-01]
        depends_on: [TASK-W0-01]
        files:
          - path: src/infra_services/tenant_git_workspace_client.py
            action: modify
          - path: tests/unit/test_tenant_git_workspace_client.py
            action: modify
        exit:
          criteria:
            - "optional ref checkout after clone/fetch; default branch path unchanged when omitted"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; ref unit tests pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-05, REQ-06, REQ-07]
        depends_on: [TASK-W0-01]
        files:
          - path: src/engine/catalogue_parser.py
            action: create
          - path: src/models/programme_catalogue_models.py
            action: create
          - path: tests/unit/test_catalogue_parser.py
            action: create
        exit:
          criteria:
            - "valid fixture → exact candidates; malformed/missing → named error, no partial list"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; catalogue parser suite green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-28]
        depends_on: [TASK-W0-02, TASK-W0-03]
        files:
          - path: src/business_services/programme_onboarding_service.py
            action: create
          - path: src/models/programme_connection_models.py
            action: create
          - path: src/api/v1/programme_routes.py
            action: create
          - path: src/api/v1/__init__.py
            action: modify
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
        exit:
          criteria:
            - "connect upserts one connection; fail-closed cleanup; catalogue GET; no PAT in responses"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-02, REQ-03, REQ-04, REQ-28]
        depends_on: [TASK-W0-04]
        files:
          - path: tests/unit/test_programme_onboarding.py
            action: create
        exit:
          criteria:
            - "unit asserts named failures, single connection upsert, no new credential fields"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W0.md § TASK-W0-05"
      - id: TASK-W0-06
        implements: [REQ-01, REQ-04, REQ-05, REQ-06, REQ-28]
        depends_on: [TASK-W0-04]
        files:
          - path: tests/verify/verify_programme_connect.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "live verify_programme_connect exercises connect + catalogue; exit 0"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_programme_connect"
            expected: "exit 0; connection + catalogue assertions"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_programme_connect
        covers: [REQ-01, REQ-04, REQ-05, REQ-06, REQ-28]
        prerequisites:
          - "API + Postgres up; tenant PAT; tests/config.yaml"
        safe_test_data:
          - "ephemeral tenant + programme meta fixture"
        steps:
          - "Run verify_programme_connect"
        expected_observations:
          - "connect 2xx; catalogue list or named 422 on bad shape"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "delete ephemeral tenant / workspace dirs"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Connect to programme meta and read catalogue candidates (REQ-01–07, REQ-28).

      ## Tasks (from plan §2)

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-01, REQ-28 | — | connection schema + DDL note | review |
      | TASK-W0-02 | REQ-01 | TASK-W0-01 | optional git ref | make test |
      | TASK-W0-03 | REQ-05, REQ-06, REQ-07 | TASK-W0-01 | CatalogueParser fail-closed | make test |
      | TASK-W0-04 | REQ-01–07, REQ-28 | TASK-W0-02, TASK-W0-03 | connect + catalogue API | make check |
      | TASK-W0-05 | REQ-02, REQ-03, REQ-04, REQ-28 | TASK-W0-04 | onboarding unit tests | make test |
      | TASK-W0-06 | REQ-01, REQ-04, REQ-05, REQ-06, REQ-28 | TASK-W0-04 | live verify_programme_connect | live script |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-013-gateflow.md

  - id: W1
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-013 W1] Select/deselect repos; retire repos[]"
    depends_on: [W0]
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_repo_selection
    tasks:
      - id: TASK-W1-01
        implements: [REQ-12, REQ-13]
        depends_on: []
        files:
          - path: src/models/tenant_models.py
            action: modify
          - path: src/business_services/tenant_service.py
            action: modify
          - path: tests/unit/test_tenant_service.py
            action: modify
          - path: tests/verify/verify_tenant_registry.py
            action: modify
        exit:
          criteria:
            - "registration rejects repos[]; no alternate API admits tenant_repos"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; registration reject assertions"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-08, REQ-09, REQ-10, REQ-11, REQ-26, REQ-27]
        depends_on: [TASK-W1-01]
        files:
          - path: src/business_services/programme_onboarding_service.py
            action: modify
          - path: src/models/programme_selection_models.py
            action: create
          - path: src/api/v1/programme_routes.py
            action: modify
          - path: src/database/postgres/repository/tenant_repository.py
            action: modify
        exit:
          criteria:
            - "catalogue-gated select; PAT probe; deselect membership-only; ACTIVE-run blocks deselect"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-26, REQ-27]
        depends_on: [TASK-W1-02]
        files:
          - path: tests/unit/test_programme_selection.py
            action: create
        exit:
          criteria:
            - "unit covers select/deselect/probe/active-run/registration reject"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-08, REQ-09, REQ-11, REQ-12, REQ-26, REQ-27]
        depends_on: [TASK-W1-02]
        files:
          - path: tests/verify/verify_repo_selection.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "live verify_repo_selection exit 0"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_repo_selection"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_repo_selection
        covers: [REQ-08, REQ-09, REQ-11, REQ-12, REQ-26, REQ-27]
        prerequisites:
          - "W0 path; API up; PAT"
        safe_test_data:
          - "ephemeral tenant + catalogue fixture"
        steps:
          - "Run verify_repo_selection"
        expected_observations:
          - "select ok; out-of-catalogue 422; repos[] registration rejected"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "delete ephemeral tenant"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Select/deselect from catalogue; retire hand-typed repos[] (REQ-08–13, 26–27).

      ## Tasks (from plan §2)

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-12, REQ-13 | — | retire repos[] | make test |
      | TASK-W1-02 | REQ-08–11, 26–27 | TASK-W1-01 | select/deselect API | make check |
      | TASK-W1-03 | REQ-08–13, 26–27 | TASK-W1-02 | selection unit tests | make test |
      | TASK-W1-04 | REQ-08,09,11,12,26,27 | TASK-W1-02 | live verify_repo_selection | live script |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-013-gateflow.md

  - id: W2
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-013 W2] Setup chosen repos (batch)"
    depends_on: [W1]
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_repo_selection
    tasks:
      - id: TASK-W2-01
        implements: [REQ-14, REQ-15, REQ-16]
        depends_on: []
        files:
          - path: src/business_services/programme_onboarding_service.py
            action: modify
          - path: src/models/programme_selection_models.py
            action: modify
        exit:
          criteria:
            - "newly admitted repos resolve_workspace independently; per-repo setup results"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-14, REQ-15, REQ-16]
        depends_on: [TASK-W2-01]
        files:
          - path: tests/unit/test_programme_selection.py
            action: modify
        exit:
          criteria:
            - "unit proves setup isolation and result shape"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-14, REQ-15, REQ-16]
        depends_on: [TASK-W2-01]
        files:
          - path: tests/verify/verify_repo_selection.py
            action: modify
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "live asserts workspace present for newly selected repo"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_repo_selection"
            expected: "exit 0; setup observation"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_repo_selection
        covers: [REQ-14, REQ-15, REQ-16]
        prerequisites:
          - "W0+W1; workspace_root writable; PAT"
        safe_test_data:
          - "ephemeral tenant + selectable fixture repo"
        steps:
          - "Run verify_repo_selection with setup assertions"
        expected_observations:
          - "selected repo directory present under tenant workspace"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "remove workspace dirs / tenant"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Setup newly selected repos via resolve_workspace (REQ-14–16).

      ## Tasks (from plan §2)

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-14–16 | — | wire setup batch | make check |
      | TASK-W2-02 | REQ-14–16 | TASK-W2-01 | setup unit tests | make test |
      | TASK-W2-03 | REQ-14–16 | TASK-W2-01 | live setup assertions | live script |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-013-gateflow.md

  - id: W3
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-013 W3] Launchpad status readiness + dual evaluators"
    depends_on: [W2]
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_harness_status
    tasks:
      - id: TASK-W3-01
        implements: [REQ-17, REQ-18, REQ-20]
        depends_on: []
        files:
          - path: src/infra_services/launchpad_status_client.py
            action: create
          - path: src/configs/app_settings.py
            action: modify
          - path: src/di/modules/infra_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
          - path: docs/specification/reports/OPS-NOTE-INIT-GATEFLOW-013-launchpad-cli.md
            action: create
        exit:
          criteria:
            - "inspect-only LaunchpadStatusClient; tool_unavailable when missing; DI bound"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; argv-guard + tool_unavailable tests pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-01"
      - id: TASK-W3-02
        implements: [REQ-17, REQ-19, REQ-21, REQ-22, REQ-23]
        depends_on: [TASK-W3-01]
        files:
          - path: src/database/postgres/schema/tenant_schema.py
            action: modify
          - path: docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-readiness-source.md
            action: create
          - path: src/business_services/programme_onboarding_service.py
            action: modify
          - path: src/business_services/tenant_service.py
            action: modify
          - path: src/api/v1/programme_routes.py
            action: modify
        exit:
          criteria:
            - "readiness_source at admission; status in selection batch; refresh in place; pre-INIT untouched"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-02"
      - id: TASK-W3-03
        implements: [REQ-21, REQ-22]
        depends_on: [TASK-W3-02]
        files:
          - path: src/business_services/wave_start_service.py
            action: modify
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "provenance switch at harness gates; never-checked selected repo fail-closed"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; provenance matrix green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-03"
      - id: TASK-W3-04
        implements: [REQ-18, REQ-19, REQ-20, REQ-21, REQ-22, REQ-23]
        depends_on: [TASK-W3-03]
        files:
          - path: tests/unit/test_launchpad_status_client.py
            action: create
          - path: tests/unit/test_harness_dual_gate.py
            action: create
        exit:
          criteria:
            - "unit covers dual gate, argv guard, tool_unavailable, legacy untouched"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W3.md § TASK-W3-04"
      - id: TASK-W3-05
        implements: [REQ-17, REQ-18, REQ-20, REQ-21, REQ-23]
        depends_on: [TASK-W3-02]
        files:
          - path: tests/verify/verify_harness_status.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "live verify_harness_status exit 0 for selection-admitted status path"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_harness_status"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_harness_status
        covers: [REQ-17, REQ-18, REQ-20, REQ-21, REQ-23]
        prerequisites:
          - "Launchpad CLI available; W0–W2 complete; programme meta synced"
        safe_test_data:
          - "selection-admitted fixture repo"
        steps:
          - "Run verify_harness_status"
        expected_observations:
          - "status-sourced readiness for new admit; legacy filesystem path unchanged"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "delete ephemeral tenant"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Real Launchpad status readiness + dual evaluators (REQ-17–23).

      ## Tasks (from plan §2)

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W3-01 | REQ-17,18,20 | — | LaunchpadStatusClient | make test |
      | TASK-W3-02 | REQ-17,19,21–23 | TASK-W3-01 | provenance + status batch + refresh | make check |
      | TASK-W3-03 | REQ-21,22 | TASK-W3-02 | dual gate | make test |
      | TASK-W3-04 | REQ-18–23 | TASK-W3-03 | unit dual/status | make test |
      | TASK-W3-05 | REQ-17,18,20,21,23 | TASK-W3-02 | live verify_harness_status | live script |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-013-gateflow.md

  - id: W4
    kind: issue
    repo: gateflow
    title: "[INIT-GATEFLOW-013 W4] Catalogue refresh"
    depends_on: [W3]
    codebase: gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_catalogue_refresh
    tasks:
      - id: TASK-W4-01
        implements: [REQ-07, REQ-24, REQ-25]
        depends_on: []
        files:
          - path: src/business_services/programme_onboarding_service.py
            action: modify
          - path: src/api/v1/programme_routes.py
            action: modify
          - path: src/models/programme_connection_models.py
            action: modify
        exit:
          criteria:
            - "refresh re-syncs programme copy; selections/readiness untouched on success path"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-013-W4.md § TASK-W4-01"
      - id: TASK-W4-02
        implements: [REQ-07, REQ-24, REQ-25]
        depends_on: [TASK-W4-01]
        files:
          - path: tests/unit/test_programme_onboarding.py
            action: modify
          - path: tests/verify/verify_catalogue_refresh.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "unit + live verify_catalogue_refresh exit 0; new candidates without selection change"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_catalogue_refresh"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_catalogue_refresh
        covers: [REQ-07, REQ-24, REQ-25]
        prerequisites:
          - "connected tenant; catalogue fixture that can grow"
        safe_test_data:
          - "ephemeral tenant"
        steps:
          - "Run verify_catalogue_refresh"
        expected_observations:
          - "new candidates after refresh; prior selection membership unchanged"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "delete ephemeral tenant"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Catalogue refresh without mutating selections (REQ-07, 24–25).

      ## Tasks (from plan §2)

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W4-01 | REQ-07,24,25 | — | refresh API | make check |
      | TASK-W4-02 | REQ-07,24,25 | TASK-W4-01 | unit + live verify | live script |

      ## Done when

      - [ ] All W4 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-013-gateflow.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md
    digest: sha256:cd034104061f224a4ea877bb596769cbf6c0741b80a8064ec2e7a36613774b1e
  blockers: []
  signals:
    plan_ready: true
    coding_readiness: true
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    head_ref: chore/INIT-GATEFLOW-013-spec-gateflow
    include_paths:
      - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md
```
