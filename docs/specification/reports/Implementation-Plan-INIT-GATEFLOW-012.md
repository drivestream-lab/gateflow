---
goal: INIT-GATEFLOW-012 — Tenant registry and workspace/branch lifecycle
initiative: INIT-GATEFLOW-012
status: Planned
date_created: 2026-08-08
source_spec: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
source_spec_digest: sha256:b8a490e7e7c7ceb02f18097d9164611086d2c7aecd1d9c2e0a6b0a7495a13190
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-012.md
feasibility_digest: sha256:7c043069cd9d85068f472ce2215fd7d984ed2c995c3c883a40117bdf1b84dfb6
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-012.md
technical_review_digest: sha256:3e2cafd26f19996dfa077e5cb24dda4b2b850b21025accd55dfb8e8fc025fb2d
prd_digest: sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-012.md
impact_map_revision: 1
repo_scope_digest: sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678
approved_meta_pr_head: 74402540efd98527014b4706d0d29bda1242b6cf
branch: chore/INIT-GATEFLOW-012-spec-gateflow
review_deadline: 2026-08-13
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-012

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` / `sha256:b8a490e7e7c7ceb02f18097d9164611086d2c7aecd1d9c2e0a6b0a7495a13190` | CURRENT |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-012.md` / `sha256:7c043069cd9d85068f472ce2215fd7d984ed2c995c3c883a40117bdf1b84dfb6` | CURRENT (walk-time) |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-012.md` / `sha256:3e2cafd26f19996dfa077e5cb24dda4b2b850b21025accd55dfb8e8fc025fb2d` | CURRENT — **Accepted** |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-012.md` / `1` | CURRENT |
| Repo scope digest | `sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678` | CURRENT |
| Approved meta PR head | `74402540efd98527014b4706d0d29bda1242b6cf` | CURRENT (G1) |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per wave under `tests/verify/` — W0 `verify_tenant_registry`; W1 `verify_workspace_lifecycle`; W2 `verify_branch_lifecycle`; W3 `verify_harness_readiness`; W4 extend `verify_wave_start`; W5 N/A (dormant) | RESOLVED |
| `ground_command` | N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target | N/A |

> H1–H3 / G1 verified 2026-08-08 against live meta PR [#32](https://github.com/drivestream-lab/prayog-meta/pull/32) head `7440254…` (`impact-map-lgtm`). Spec digest matches TDD/feasibility citations.

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | [`Technical-Review-INIT-GATEFLOW-012.md`](Technical-Review-INIT-GATEFLOW-012.md) |
| Technical review status | **Accepted** |
| PE sign-off | [x] complete — 2026-08-08 (@nikd10x via Cursor chat on Draft spec PR [#183](https://github.com/drivestream-lab/gateflow/pull/183)) |
| Resolved ADRs | [`adr-011-tenant-scoped-bearer-token-trust-zone.md`](../adr/adr-011-tenant-scoped-bearer-token-trust-zone.md) (**Accepted**; `changes_user_visible_behavior: false`; `spec_amendment_required: false`; Lint evidence `3/3 PASS sha256:6d4578b99287b664a3a0e324196ed3f0fbcdb6f2a7b3a5d555c5be11d793b56e` — re-verified at plan time with reconstructed REQ-03/REQ-04 + FF-02 quote sources) |
| ADR product-boundary re-check | PASS — P13 lint `--verify-lint-evidence --require-sources` exit 0 (3 sources) |
| Outstanding PM questions | PM-1 / Q-7 (G1 plaintext-PAT acknowledgment residual) — non-blocking; default = matching Gate-1 APPROVED review is sufficient |
| Outstanding domain questions | none — all resolved |

> Do not start W0 coding until this plan is on tip with `spec-lgtm` + Approve (coding-readiness), then merge + `/create-board-tickets`.

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Tenant registration accepts name, pat, repos[], workspace_root, optional board | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | W0 |
| REQ-02 | PAT persisted plaintext; never echoed in any response | same | W0 |
| REQ-03 | Tenant-scoped bearer token distinct from PROGRAMME_SERVICE_TOKEN | same | W0 |
| REQ-04 | User-attach; unattached/mismatched token → 401 before lane logic | same | W0 |
| REQ-05 | No per-repo ACL within a tenant | same | W0 |
| REQ-06 | Eager PAT read-access verify per repo before commit; itemized 422 | same | W0 |
| REQ-07 | workspace_root must be absolute → 400 otherwise | same | W0 |
| REQ-08 | Tenant board default applied when call omits override; explicit wins | same | W0 |
| REQ-09 | Nth tenant needs zero GithubSettings/env edits | same | W0 |
| REQ-32 | Tenant read/list returns repos, workspace_root, board; never PAT | same | W0 |
| REQ-10 | Omitted workspace_path + registered repo → resolve deterministic workspace | same | W1 |
| REQ-11 | Clone/refresh auth uses Tenant PAT (same as ForgeClient) | same | W1 |
| REQ-12 | Explicit workspace_path unchanged (additive regression) | same | W1 |
| REQ-13 | Valid existing checkout → fetch-in-place, not re-clone | same | W1 |
| REQ-14 | Invalid existing checkout → 422; tree untouched | same | W1 |
| REQ-15 | Omitted path + unregistered repo → 422; 0 enqueue | same | W1 |
| REQ-16 | New wave forks from live develop tip | same | W2 |
| REQ-17 | Deterministic branch naming; no second scheme | same | W2 |
| REQ-18 | Continuation reuses existing head ref; zero new branches | same | W2 |
| REQ-19 | Continuation composes with never-cloned workspace | same | W2 |
| REQ-20 | Harness-readiness after clone/refresh, before coding-hop, when not cached | same | W3 |
| REQ-21 | Missing harness artifacts fail; harness-enabled passes | same | W3 |
| REQ-22 | Verified cache + explicit re-check path | same | W3 |
| REQ-23 | NO_CONCURRENT_RUN broadened to org+repo ACTIVE | same | W4 |
| REQ-24 | Different repos never block each other | same | W4 |
| REQ-25 | No new worktree/lock/isolation mechanism | same | W4 |
| REQ-26 | ForgeClient.delete_branch via existing DELETE-ref transport | same | W5 |
| REQ-27 | delete_branch fails closed on missing/protected; no silent no-op | same | W5 |

---

## 2. Implementation phases

### Phase W0 — Tenant registry (data model + API)

**GOAL-W0:** Register tenants (PAT + repos + workspace_root + optional board), attach users, issue tenant bearer tokens (ADR-011), eager per-repo PAT probe, read/list without echoing PAT. **P15:** new HTTP surfaces co-ship `tests/verify/verify_tenant_registry.py`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Pydantic tenant models (register/attach/read/list); PAT forbidden on response models | REQ-01, REQ-02, REQ-07, REQ-32 | — | `src/models/tenant_models.py` create | Absolute-path validator rejects relative `workspace_root`; response models have no `pat` field | command / `make check && make test` | exit 0; model tests pass | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | `.venv/bin/python -m tests.verify.verify_tenant_registry` | pydantic-schemas.mdc, http-api-conventions.mdc | — | `feature/INIT-GATEFLOW-012-w0-tenant-registry` |
| TASK-W0-02 | ORM schema tenants / tenant_repos / tenant_users + env.py import; DDL note for human migration | REQ-01, REQ-02, REQ-09 | TASK-W0-01 | `src/database/postgres/schema/tenant_schema.py` create; `postgres_migrations/env.py` modify; `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md` create | Schema registers on `postgres_metadata`; DDL-NOTE lists upgrade/downgrade for human `versions/` | review / DDL-NOTE + `make check` | schema importable; no agent-authored `versions/` file | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | database-migrations.mdc, repository-pattern.mdc | ADR-001 | same |
| TASK-W0-03 | TenantRepository + DI RepositoryModule binding | REQ-01, REQ-02, REQ-04, REQ-32 | TASK-W0-02 | `src/database/postgres/repository/tenant_repository.py` create; `src/di/modules/repository_module.py` modify | Repo maps ORM↔Pydantic; PAT never returned on read DTOs | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | repository-pattern.mdc, dependency-injection.mdc | — | same |
| TASK-W0-04 | github_pat_probe infra (per-call credential; repo metadata GET default Q-2) | REQ-06 | — | `src/infra_services/github_pat_probe.py` create; `src/di/modules/infra_module.py` modify; `src/di/dependency_container.py` modify | `verify_read_access` returns ok/reason without persisting credential; doubled transport unit green | command / `make test` | exit 0; itemized reason on failure | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | infra-services.mdc, fail-fast.mdc | — | same |
| TASK-W0-05 | TenantService register (all-or-nothing + probe) + attach + read/list; board default storage | REQ-01, REQ-02, REQ-03, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-32 | TASK-W0-03, TASK-W0-04 | `src/business_services/tenant_service.py` create; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify | Probe failure → 0 rows; success returns one-time token; second tenant needs no env change | command / `make test` | exit 0; all-or-nothing + no-pat assertions | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-05 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | architecture.mdc, logging-loguru.mdc, fail-fast.mdc | ADR-011 (token issuance) | same |
| TASK-W0-06 | tenant_token dependency (ADR-011 Option A) + tenant routes + api_router mount | REQ-03, REQ-04, REQ-05, REQ-32 | TASK-W0-05 | `src/api/v1/tenant_token.py` create; `src/api/v1/tenant_routes.py` create; `src/api/v1/__init__.py` modify | POST/GET tenants + POST users; wrong/absent token → 401 before handler body; no AuthMiddleware reuse | command / `make test` | exit 0; 400/401/422 matrix | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-06 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | http-api-conventions.mdc, architecture.mdc | ADR-011 | same |
| TASK-W0-07 | Apply tenant board default when board-touching call omits project_owner/number; explicit override wins | REQ-08 | TASK-W0-05 | `src/business_services/board_service.py` modify (and/or board route helpers); unit tests modify | Omitted board fields resolve from tenant default; explicit request fields win | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-07 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | pydantic-schemas.mdc | A-5 / BoardTicketCreateRequest precedent | same |
| TASK-W0-08 | Unit tests for tenant service/routes/probe/token | REQ-01, REQ-02, REQ-03, REQ-04, REQ-06, REQ-07, REQ-32 | TASK-W0-06 | `tests/unit/test_tenant_service.py` create; `tests/unit/test_tenant_routes.py` create; `tests/unit/test_github_pat_probe.py` create; `tests/unit/test_tenant_token.py` create | Unit matrix covers happy + 400/401/422 + no-pat | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-08 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | testing-verify-flows.mdc | — | same |
| TASK-W0-09 | Co-ship live verify_tenant_registry + tests/README feature-map row | REQ-04, REQ-06, REQ-32 | TASK-W0-08 | `tests/verify/verify_tenant_registry.py` create; `tests/README.md` modify | Script registers, attaches, reads/lists; asserts 401/422 negatives; PAT absent from bodies | command / `.venv/bin/python -m tests.verify.verify_tenant_registry` | exit 0 | wave-accepted on tip | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | testing-verify-flows.mdc | — | same |
| TASK-W0-10 | As-built INIT-012 W0 row | REQ-01–REQ-09, REQ-32 | TASK-W0-09 | `docs/specification/as-built/implementation-status.md` modify | Row reflects W0 unit + live intent | review / as-built | accurate W0 status | Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-10 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_tenant_registry` | SDD | — | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/models/tenant_models.py` | create |
| FILE-W0-02 | `src/database/postgres/schema/tenant_schema.py` | create |
| FILE-W0-03 | `postgres_migrations/env.py` | modify |
| FILE-W0-04 | `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md` | create |
| FILE-W0-05 | `src/database/postgres/repository/tenant_repository.py` | create |
| FILE-W0-06 | `src/infra_services/github_pat_probe.py` | create |
| FILE-W0-07 | `src/business_services/tenant_service.py` | create |
| FILE-W0-08 | `src/api/v1/tenant_token.py` | create |
| FILE-W0-09 | `src/api/v1/tenant_routes.py` | create |
| FILE-W0-10 | `src/api/v1/__init__.py` | modify |
| FILE-W0-11 | `src/di/modules/repository_module.py` | modify |
| FILE-W0-12 | `src/di/modules/infra_module.py` | modify |
| FILE-W0-13 | `src/di/modules/business_services_module.py` | modify |
| FILE-W0-14 | `src/di/dependency_container.py` | modify |
| FILE-W0-15 | `src/business_services/board_service.py` | modify |
| FILE-W0-16 | `tests/unit/test_tenant_service.py` | create |
| FILE-W0-17 | `tests/unit/test_tenant_routes.py` | create |
| FILE-W0-18 | `tests/unit/test_github_pat_probe.py` | create |
| FILE-W0-19 | `tests/unit/test_tenant_token.py` | create |
| FILE-W0-20 | `tests/verify/verify_tenant_registry.py` | create |
| FILE-W0-21 | `tests/README.md` | modify |
| FILE-W0-22 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-01–09, REQ-32 / TASK-W0-01..08 |
| TEST-W0-I | integration/contract | repository against real Postgres session (named boundary in unit suite helpers) | REQ-01, REQ-32 |
| TEST-W0-L | live smoke | `.venv/bin/python -m tests.verify.verify_tenant_registry` | REQ-04, REQ-06, REQ-32 (P15) |

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01 | TEST-W0-U | TEST-W0-I | secondary | N/A | |
| REQ-02 | TEST-W0-U | N/A | TEST-W0-L | N/A | inspection + live body |
| REQ-03 | TEST-W0-U | N/A | TEST-W0-L | N/A | ADR-011 |
| REQ-04 | TEST-W0-U | N/A | TEST-W0-L | N/A | P15 |
| REQ-05 | TEST-W0-U + inspection | N/A | N/A | N/A | no repo ACL code path |
| REQ-06 | TEST-W0-U | N/A | TEST-W0-L | N/A | P15 |
| REQ-07 | TEST-W0-U | N/A | N/A | N/A | |
| REQ-08 | TEST-W0-U | N/A | secondary | N/A | |
| REQ-09 | inspection + TEST-W0-U | N/A | N/A | N/A | second-tenant unit |
| REQ-32 | TEST-W0-U | TEST-W0-I | TEST-W0-L | N/A | P15 |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new tenant HTTP routes (P15) |
| Environment class | local-compose (API + Postgres; GitHub PAT for probe) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR head |
| Prerequisites | API up; migrations applied (human DDL); test PAT with known repo access |
| Safe test data | Ephemeral tenant name/repos under a disposable workspace_root; no prod PAT |
| Steps / command | `.venv/bin/python -m tests.verify.verify_tenant_registry` |
| Expected observations | Register 200 + token once; attach; GET list/detail without pat; bad PAT → 422 itemized; bad token → 401 |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | Delete synthetic tenant rows / workspace_root scratch |
| Stop conditions | Non-zero exit or unexpected 5xx → stop; do not start Pass-2 |

---

### Phase W1 — Repo clone / refresh

**GOAL-W1:** Replace `Path.cwd()` fallback for Tenant-registered repos with clone-or-fetch via subprocess `git` + Tenant PAT; fail closed for unregistered/mismatched paths; self-serialize per org+repo (TF-01). **Hard gate:** `prayog-skills` contract PR remounted (0 BROKEN) before W1 exit (PE-1). **P15:** co-ship `verify_workspace_lifecycle.py`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Confirm prayog-skills pin remount: 0 BROKEN nodes for Tenant workspace-prep shapes | REQ-10 | — | `.harness-pin.yaml` inspect; `prayog-skills` submodule inspect | Remounted pin tip has 0 BROKEN for new shapes (CTR-01) | command / pin parse unit or `git -C prayog-skills rev-parse HEAD` + fixture pin assert | 0 BROKEN | Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | fail-fast.mdc | PE-1 / CTR-01 | `feature/INIT-GATEFLOW-012-w1-workspace-prep` |
| TASK-W1-02 | tenant_git_workspace_client (subprocess git; clone vs fetch; mismatch fail-closed; per-repo lock) | REQ-10, REQ-11, REQ-13, REQ-14 | TASK-W1-01 | `src/infra_services/tenant_git_workspace_client.py` create; `src/di/modules/infra_module.py` modify; `src/di/dependency_container.py` modify | Unit: clone/fetch branching; invalid checkout raises; lock serializes; no new Python git package | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | infra-services.mdc, fail-fast.mdc | FF-04 TDD_ONLY; TF-01 | same |
| TASK-W1-03 | RunOrchestrator: resolve workspace for registered repo; keep explicit path; 422 unregistered omitted | REQ-10, REQ-12, REQ-15 | TASK-W1-02 | `src/business_services/run_orchestrator.py` modify; wave-start/enqueue path as needed | `Path.cwd()` never reached for registered omitted-path; explicit path unchanged; unregistered omitted → 422 0 enqueue | command / `make test` | exit 0; regression + new cases | Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | fail-fast.mdc | FF-01 TDD_ONLY (gap-fill) | same |
| TASK-W1-04 | Unit tests workspace prep + orchestrator regression | REQ-10–REQ-15 | TASK-W1-03 | `tests/unit/test_tenant_git_workspace_client.py` create; `tests/unit/test_run_orchestrator.py` modify; `tests/unit/test_wave_start.py` modify | Full REQ-10–15 unit matrix green | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | testing-verify-flows.mdc | — | same |
| TASK-W1-05 | Co-ship verify_workspace_lifecycle + README | REQ-10, REQ-13, REQ-14, REQ-15 | TASK-W1-04 | `tests/verify/verify_workspace_lifecycle.py` create; `tests/README.md` modify | Live: clone then fetch; mismatch 422; unregistered omitted 422 | command / `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | exit 0 | wave-accepted on tip | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | testing-verify-flows.mdc | — | same |
| TASK-W1-06 | As-built W1 row | REQ-10–REQ-15 | TASK-W1-05 | `docs/specification/as-built/implementation-status.md` modify | Accurate W1 status | review | rows updated | Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-06 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | SDD | — | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `.harness-pin.yaml` | inspect |
| FILE-W1-02 | `src/infra_services/tenant_git_workspace_client.py` | create |
| FILE-W1-03 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W1-04 | `src/di/modules/infra_module.py` | modify |
| FILE-W1-05 | `src/di/dependency_container.py` | modify |
| FILE-W1-06 | `tests/unit/test_tenant_git_workspace_client.py` | create |
| FILE-W1-07 | `tests/unit/test_run_orchestrator.py` | modify |
| FILE-W1-08 | `tests/unit/test_wave_start.py` | modify |
| FILE-W1-09 | `tests/verify/verify_workspace_lifecycle.py` | create |
| FILE-W1-10 | `tests/README.md` | modify |
| FILE-W1-11 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-10–15 |
| TEST-W1-I | integration/contract | real fixture repo on disk via client boundary | REQ-13, REQ-14 |
| TEST-W1-L | live smoke | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` | REQ-10, REQ-13–15 (P15) |

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-10 | TEST-W1-U | N/A | TEST-W1-L | N/A | P15 |
| REQ-11 | TEST-W1-U + inspection | N/A | secondary | N/A | PAT auth |
| REQ-12 | TEST-W1-U | N/A | secondary | N/A | regression |
| REQ-13 | TEST-W1-U | TEST-W1-I | TEST-W1-L | N/A | |
| REQ-14 | TEST-W1-U | TEST-W1-I | TEST-W1-L | N/A | |
| REQ-15 | TEST-W1-U | N/A | TEST-W1-L | N/A | |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | **yes** — workspace resolution changes implement-lane behavior (P15) |
| Environment class | local-compose + persistent disk (A-2) + `git` binary + tenant PAT |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W0 tenant registered; API+worker; pin remounted; disposable remote fixture repo |
| Safe test data | Synthetic tenant workspace_root under scratch dir |
| Steps / command | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` |
| Expected observations | First start clones; second fetches; mismatch/unregistered → 422 |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | Remove scratch workspace_root; leave remote fixture intact |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

### Phase W2 — Branch create-or-reuse

**GOAL-W2:** New wave forks from live `develop`; continuation reuses existing head; composes with clone-on-fresh-workspace. **Depends on W1 + remounted pin.** **P15:** co-ship `verify_branch_lifecycle.py`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Branch resolve composing ensure_branch_from_base + branch_slug_from_head_ref (no third primitive) | REQ-16, REQ-17, REQ-18 | — | `src/business_services/run_orchestrator.py` modify (and/or small helper module under business_services) | New-wave creates from live develop tip; continuation creates zero refs; name matches convention | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W2.md § TASK-W2-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` | architecture.mdc | ADR-010 D2 aligned | `feature/INIT-GATEFLOW-012-w2-branch-resolve` |
| TASK-W2-02 | Unit tests new-vs-continuation + naming | REQ-16, REQ-17, REQ-18 | TASK-W2-01 | `tests/unit/test_run_orchestrator.py` modify; `tests/unit/test_pr_branch_naming.py` modify | Matrix green; missing remote continuation branch → named 422 | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W2.md § TASK-W2-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` | fail-fast.mdc | — | same |
| TASK-W2-03 | Co-ship verify_branch_lifecycle including never-cloned continuation (REQ-19) | REQ-16, REQ-18, REQ-19 | TASK-W2-02 | `tests/verify/verify_branch_lifecycle.py` create; `tests/README.md` modify | Live: new fork + continuation reuse + fresh-workspace continuation | command / `.venv/bin/python -m tests.verify.verify_branch_lifecycle` | exit 0 | wave-accepted on tip | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` | testing-verify-flows.mdc | — | same |
| TASK-W2-04 | As-built W2 row | REQ-16–REQ-19 | TASK-W2-03 | `docs/specification/as-built/implementation-status.md` modify | Accurate W2 status | review | rows updated | Wave-Execution-INIT-GATEFLOW-012-W2.md § TASK-W2-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` | SDD | — | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W2-02 | `tests/unit/test_run_orchestrator.py` | modify |
| FILE-W2-03 | `tests/unit/test_pr_branch_naming.py` | modify |
| FILE-W2-04 | `tests/verify/verify_branch_lifecycle.py` | create |
| FILE-W2-05 | `tests/README.md` | modify |
| FILE-W2-06 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-16–18 |
| TEST-W2-L | live smoke | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` | REQ-16, REQ-18, REQ-19 (P15) |

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-16 | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-17 | TEST-W2-U | N/A | N/A | N/A | naming |
| REQ-18 | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-19 | N/A | N/A | TEST-W2-L | N/A | verify-primary |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | **yes** — branch create-or-reuse on implement path (P15) |
| Environment class | local-compose + forge/GitHub + tenant workspace |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W1 complete; develop exists on fixture repo |
| Safe test data | Ephemeral initiative/wave ids; disposable branches |
| Steps / command | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` |
| Expected observations | New wave branch from live develop; continuation reuses; never-cloned continuation succeeds |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | Delete ephemeral branches / runs |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

### Phase W3 — Harness-readiness

**GOAL-W3:** Real harness artifact check (beyond path-exists); cache verified; explicit re-check. **P15:** co-ship `verify_harness_readiness.py`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | Extend LaunchpadClient.sync_harness to require harness artifacts; persist verified cache on tenant_repos (or agreed column); re-check API/path | REQ-20, REQ-21, REQ-22 | — | `src/infra_services/launchpad_client.py` modify; `src/database/postgres/schema/tenant_schema.py` modify; `src/database/postgres/repository/tenant_repository.py` modify; DDL-NOTE if column added | Non-ready fails named; ready passes; cache skips repeat; re-check forces probe | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | `.venv/bin/python -m tests.verify.verify_harness_readiness` | infra-services.mdc, database-migrations.mdc | A-3 / CTR-03 | `feature/INIT-GATEFLOW-012-w3-harness-ready` |
| TASK-W3-02 | Wire check after workspace resolve, before coding-hop dispatch | REQ-20 | TASK-W3-01 | `src/business_services/run_orchestrator.py` modify | Check executes before Enter-at skill for unverified repos | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_harness_readiness` | fail-fast.mdc | — | same |
| TASK-W3-03 | First-ever test_launchpad_client + orchestrator harness cases (FF-05) | REQ-20, REQ-21, REQ-22 | TASK-W3-02 | `tests/unit/test_launchpad_client.py` create; `tests/unit/test_run_orchestrator.py` modify | Positive + negative fixture matrix green | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_harness_readiness` | testing-verify-flows.mdc | FF-05 | same |
| TASK-W3-04 | Co-ship verify_harness_readiness + README | REQ-20, REQ-21 | TASK-W3-03 | `tests/verify/verify_harness_readiness.py` create; `tests/README.md` modify | Live positive (harness present) + negative (absent → 422) | command / `.venv/bin/python -m tests.verify.verify_harness_readiness` | exit 0 | wave-accepted on tip | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_harness_readiness` | testing-verify-flows.mdc | — | same |
| TASK-W3-05 | As-built W3 row | REQ-20–REQ-22 | TASK-W3-04 | `docs/specification/as-built/implementation-status.md` modify | Accurate W3 status | review | rows updated | Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-05 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_harness_readiness` | SDD | — | same |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/infra_services/launchpad_client.py` | modify |
| FILE-W3-02 | `src/database/postgres/schema/tenant_schema.py` | modify |
| FILE-W3-03 | `src/database/postgres/repository/tenant_repository.py` | modify |
| FILE-W3-04 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W3-05 | `tests/unit/test_launchpad_client.py` | create |
| FILE-W3-06 | `tests/unit/test_run_orchestrator.py` | modify |
| FILE-W3-07 | `tests/verify/verify_harness_readiness.py` | create |
| FILE-W3-08 | `tests/README.md` | modify |
| FILE-W3-09 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-20–22 |
| TEST-W3-I | integration/contract | filesystem fixture with/without `.harness-pin.yaml` | REQ-21 |
| TEST-W3-L | live smoke | `.venv/bin/python -m tests.verify.verify_harness_readiness` | REQ-20, REQ-21 (P15) |

#### Verification Coverage (W3)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-20 | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-21 | TEST-W3-U | TEST-W3-I | TEST-W3-L | N/A | |
| REQ-22 | TEST-W3-U | N/A | secondary | N/A | cache |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | **yes** — harness gate on implement path (P15) |
| Environment class | local-compose + fixture repos with/without harness |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | W1 workspace path available |
| Safe test data | Fixture trees only |
| Steps / command | `.venv/bin/python -m tests.verify.verify_harness_readiness` |
| Expected observations | Ready passes; absent artifacts → 422 named miss |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | Reset verified-cache flags on synthetic tenant_repos |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

### Phase W4 — Repo-scoped NO_CONCURRENT_RUN

**GOAL-W4:** Broaden `find_active_run` to org+repo ACTIVE; prove cross-repo non-blocking; no new isolation. **P15:** extend `verify_wave_start`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W4-01 | Historical-pattern regression fixture BEFORE query change (FF-06) | REQ-23, REQ-24 | — | `tests/unit/test_run_store_concurrency.py` create (or extend existing) | Fixture asserts today's narrower vs intended broader semantics on representative rows | command / `make test` | exit 0 (fixture may xfail until TASK-W4-02 lands — document flip) | Wave-Execution-INIT-GATEFLOW-012-W4.md § TASK-W4-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_start` | testing-verify-flows.mdc | FF-06 | `feature/INIT-GATEFLOW-012-w4-repo-concurrency` |
| TASK-W4-02 | Broaden find_active_run to org+repo only; keep NO_CONCURRENT_RUN code | REQ-23, REQ-24, REQ-25 | TASK-W4-01 | `src/database/postgres/repository/run_store_repository.py` modify; `src/business_services/wave_start_service.py` modify if call-site args change | Same-repo second start → PreconditionFailure; different repos both OK; no new lock/worktree types | command / `make check && make test` | exit 0; FF-06 fixture green | Wave-Execution-INIT-GATEFLOW-012-W4.md § TASK-W4-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_start` | fail-fast.mdc, repository-pattern.mdc | ADR-001 query-only | same |
| TASK-W4-03 | Extend verify_wave_start concurrency asserts + README | REQ-23, REQ-24 | TASK-W4-02 | `tests/verify/verify_wave_start.py` modify; `tests/README.md` modify | Live same-repo reject + cross-repo allow under knobs | command / `.venv/bin/python -m tests.verify.verify_wave_start` | exit 0 | wave-accepted on tip | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_start` | testing-verify-flows.mdc | — | same |
| TASK-W4-04 | As-built W4 row + inspection note REQ-25 | REQ-23–REQ-25 | TASK-W4-03 | `docs/specification/as-built/implementation-status.md` modify | Accurate W4 + no isolation infra claim | review | rows updated | Wave-Execution-INIT-GATEFLOW-012-W4.md § TASK-W4-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_start` | SDD | — | same |

#### Files (W4)

| ID | Path | Action |
|----|------|--------|
| FILE-W4-01 | `src/database/postgres/repository/run_store_repository.py` | modify |
| FILE-W4-02 | `src/business_services/wave_start_service.py` | modify |
| FILE-W4-03 | `tests/unit/test_run_store_concurrency.py` | create |
| FILE-W4-04 | `tests/unit/test_wave_start.py` | modify |
| FILE-W4-05 | `tests/verify/verify_wave_start.py` | modify |
| FILE-W4-06 | `tests/README.md` | modify |
| FILE-W4-07 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W4)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W4-U | unit | `make test` | REQ-23–25 |
| TEST-W4-I | integration/contract | repository against real Postgres session | REQ-23, REQ-24 |
| TEST-W4-L | live smoke | `.venv/bin/python -m tests.verify.verify_wave_start` | REQ-23, REQ-24 (P15) |

#### Verification Coverage (W4)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-23 | TEST-W4-U | TEST-W4-I | TEST-W4-L | N/A | |
| REQ-24 | TEST-W4-U | TEST-W4-I | TEST-W4-L | N/A | |
| REQ-25 | inspection | N/A | N/A | N/A | no new isolation |

#### Live-verification intent (W4)

| Field | Value |
|-------|-------|
| Applicable | **yes** — concurrency gate is a product surface on wave-start (P15) |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` |
| Prerequisites | Two wave-start capable identities/repos |
| Safe test data | Ephemeral runs; leave no ACTIVE orphans |
| Steps / command | `.venv/bin/python -m tests.verify.verify_wave_start` |
| Expected observations | Same-repo second start rejected with NO_CONCURRENT_RUN; cross-repo both succeed |
| Expected evidence | `wave-accepted on tip` |
| Cleanup | Cancel/complete synthetic ACTIVE runs |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

### Phase W5 — Dormant ForgeClient.delete_branch

**GOAL-W5:** Add `delete_branch` using existing DELETE-ref transport; fail closed; **zero live callers** this INIT (structural dormancy). **P15 N/A** — unit + code-guard only.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W5-01 | Implement ForgeClient.delete_branch via _git_ref_update_path DELETE | REQ-26 | — | `src/infra_services/forge_client.py` modify | Unit success path hits DELETE ref URL/method | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-012-W5.md § TASK-W5-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` | `N/A — P15 N/A; dormant zero live callers` | infra-services.mdc | ADR-009 method-only | `feature/INIT-GATEFLOW-012-w5-delete-branch` |
| TASK-W5-02 | Fail-closed missing/protected + code-guard no shipped caller (Q-6) | REQ-27 | TASK-W5-01 | `tests/unit/test_forge_client.py` modify; `tests/unit/test_delete_branch_dormant.py` create | Missing/protected raises named error; AST/grep guard: no production caller of delete_branch | command / `make check && make test` | exit 0; guard asserts zero call sites outside tests | Wave-Execution-INIT-GATEFLOW-012-W5.md § TASK-W5-02 | drivestream-lab/gateflow | same | `N/A — P15 N/A; dormant zero live callers` | fail-fast.mdc | G5 dormancy | same |
| TASK-W5-03 | As-built W5 row (dormant) | REQ-26, REQ-27 | TASK-W5-02 | `docs/specification/as-built/implementation-status.md` modify; `tests/README.md` modify | Documents unit-only / dormant | review | rows updated | Wave-Execution-INIT-GATEFLOW-012-W5.md § TASK-W5-03 | drivestream-lab/gateflow | same | `N/A — P15 N/A; dormant zero live callers` | SDD | — | same |

#### Files (W5)

| ID | Path | Action |
|----|------|--------|
| FILE-W5-01 | `src/infra_services/forge_client.py` | modify |
| FILE-W5-02 | `tests/unit/test_forge_client.py` | modify |
| FILE-W5-03 | `tests/unit/test_delete_branch_dormant.py` | create |
| FILE-W5-04 | `docs/specification/as-built/implementation-status.md` | modify |
| FILE-W5-05 | `tests/README.md` | modify |

#### Tests (W5)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W5-U | unit | `make test` | REQ-26, REQ-27 |
| TEST-W5-L | live | N/A — P15 N/A | dormant |

#### Verification Coverage (W5)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-26 | TEST-W5-U | doubled transport | N/A | N/A | P15 N/A |
| REQ-27 | TEST-W5-U + code-guard | N/A | N/A | N/A | |

#### Live-verification intent (W5)

| Field | Value |
|-------|-------|
| Applicable | **no** — method ships dormant with zero live outcome edges / callers (P15 N/A; G5) |
| Mode | N/A |
| Cleanup / Stop | N/A |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | Human Alembic revision for tenant tables (W0 DDL-NOTE) before live W0 verify | W0 live acceptance |
| DEP-02 | `prayog-skills` contract PR (REQ-28–31 / CTR-01) remounted with 0 BROKEN | W1 / W2 exit (PE-1 hard gate) |
| DEP-03 | Persistent disk for workspace_root (A-2) | W1 fetch-in-place live |
| DEP-04 | `git` executable present in deploy/runtime image (FF-04) | W1 |
| DEP-05 | Wave order W0→W1→W2→W3→W4→W5 on board (W4 theoretically parallel after W0, kept linear) | board projection |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | G1 plaintext PAT storage (accepted product risk) | Never echo PAT; never log secret values; PM-1 audit comment optional |
| RISK-02 | G2 single PAT for Forge + local git blast radius | Documented accepted; no second credential path this INIT |
| RISK-03 | TF-01 race window before W4 broadens concurrency | Per-repo lock inside workspace client (TASK-W1-02) independent of W4 |
| RISK-04 | Broadened NO_CONCURRENT_RUN surfaces latent double-starts | FF-06 fixture before query change (TASK-W4-01) |
| RISK-05 | prayog-skills contract delayed | W0/W4/W5 can proceed; W1/W2 blocked at TASK-W1-01 |
| RISK-06 | MDC: agents must not write `postgres_migrations/versions/` | DDL-NOTE + human migration ownership |

---

## 5. Out of scope

- prayog-skills pin/node/action shapes (REQ-28–31)
- gateflow-ops UI
- GitHub App per tenant; PAT encryption/secrets-manager
- Per-repo ACL; activating branch purge live
- New worktree/isolation; JWT AuthMiddleware reactivation
- Breaking explicit workspace_path for unregistered callers

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Per-wave as-built rows | `docs/specification/as-built/implementation-status.md` | mark wave in_progress → complete |
| Feature map | `tests/README.md` | add verify commands for co-shipped scripts |
| DDL note W0 (+ W3 if column) | `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md` | human owns `versions/` |

> ADR-011 already Accepted — no promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 | PASS — all in-scope REQ-01–27, REQ-32 in §1 |
| P2 | PASS — every REQ has ≥1 TASK; every TASK Implements ≥1 REQ-* |
| P3 | PASS — FILE paths or docs/DDL notes per TASK |
| P4 | PASS — observable exit + proof + expected + evidence_expected |
| P5 | PASS — Verification Coverage per wave; unit rows present for code waves |
| P6 | PASS — no scope beyond spec |
| P7 | PASS — FF/ops risks addressed or deferred with owner (RISK/DEP) |
| P8 | PASS — W0→W5 + DEP table |
| P9 | PASS — as-built + README in same-wave FILE lists |
| P10 | PASS — digests + commands populated; live prereqs stated |
| P11 | PASS — MDC notes on TASKs; migrations ownership flagged |
| P12 | PASS — ADR-011 Accepted linked; TDD_ONLY FF-01/FF-03 cited in notes |
| P13 | PASS — TDD Accepted; ADR boundary lint re-verified with sources |
| P14 | PASS — §9 WorkManifest present |
| P15 | PASS — W0–W4 co-ship live verify FILEs; W5 applicable=false dormancy |
| P16 | PASS — validated via `prayog-skills/scripts/workmanifest_contract.py` |

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` to the **Draft spec PR** branch alongside spec, feasibility, and TDD. Do **not** commit inside this skill. Label remains **`spec-pending`** until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-012-spec-gateflow  (Draft PR #183)
PR title: "[INIT-GATEFLOW-012] Spec — Tenant registry and workspace/branch lifecycle (gateflow)"
PR body:  link meta PRD PR #32; paste §1 Requirements table + wave goals summary

Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-13

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + TDD + Accepted ADR-011 + this plan on current head
  [ ] §0 PE sign-off on TDD marked complete
  [ ] Wave order and dependencies make sense (incl. PE-1 hard gate)
  [ ] Done-when / exit criteria observable (P4)
  [ ] Verification Coverage maps every criterion (P5)
  [ ] WorkManifest YAML (§9) passes workmanifest-contract-pass (P16)
  [ ] P1–P16 checks all pass (including P15 co-ship)

After spec-lgtm + Approve + merge — `/create-board-tickets` from §9 (post-merge only)
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 PASS; sources CURRENT; Accepted TDD + ADR-011; plan ready for coding-readiness |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/183 |
| Spec PR head SHA | `377ec79573b21e162c69049424a6462a977699e7` (pre-plan publish; Forge updates tip) |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` |
| Forge readiness | fill `handoff.forge` for `/commit-workspace` — do not commit inside this skill |
| Blocking items | none |

Provision labels when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

PE actions (all on **exact current head** after Forge publish):

1. Remove `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale`; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body (below)
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/create-board-tickets`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-012
spec_pr_head_sha: {SHA after plan publish}
meta_pr_head_sha: 74402540efd98527014b4706d0d29bda1242b6cf
impact_map_revision: 1
prd_digest: sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b
scope_digest: sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678
plan_digest: sha256:{compute on exact head after Forge publish}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-012-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-012.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-012.md
  - docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

---

## 9. WorkManifest seed

> **Primary:** `/create-board-tickets` creates **one GitHub Issue per wave** after spec merge.
> Validate: `python prayog-skills/scripts/workmanifest_contract.py` on this plan.
> `target.org` / `target.project` from `prayog-meta/config/governance-drivestream-lab.yaml`.

```yaml
# Generated by /spec-implementation-plan — 2026-08-08
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-012
metadata:
  title: INIT-GATEFLOW-012 — Tenant registry and workspace/branch lifecycle
  summary: |
    Gateflow gains a Tenant registry (PAT + repos + workspace root + board default)
    and the workspace/branch lifecycle that consumes it: clone/refresh, branch
    create-or-reuse, harness-readiness, repo-scoped NO_CONCURRENT_RUN, and a dormant
    ForgeClient.delete_branch method. Replaces Path.cwd() fallback for registered repos.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md

target:
  org: drivestream-lab
  project: drivestream-lab Board

defaults:
  initiative: INIT-GATEFLOW-012
  parent: EPIC
  labels:
    - INIT-GATEFLOW-012

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-012 — Tenant registry and workspace/branch lifecycle"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_tenant_registry
  body: |
    ## Objective

    Tenant registry + workspace/branch lifecycle for Tenant-registered repos
    (REQ-01–27, REQ-32). prayog-skills pin shapes (REQ-28–31) are out of this repo.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Tenant registry API + token trust zone |
    | W1 | Clone/refresh workspace prep |
    | W2 | Branch create-or-reuse |
    | W3 | Harness-readiness |
    | W4 | Repo-scoped NO_CONCURRENT_RUN |
    | W5 | Dormant delete_branch |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-012.md
    - ADR-011: docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-012 W0] Tenant registry (data model + API)"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_tenant_registry
    tasks:
      - id: TASK-W0-01
        implements: [REQ-01, REQ-02, REQ-07, REQ-32]
        depends_on: []
        files:
          - path: src/models/tenant_models.py
            action: create
        exit:
          criteria:
            - "Absolute workspace_root rejected when relative; response models expose no pat field"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; model tests pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-01, REQ-02, REQ-09]
        depends_on: [TASK-W0-01]
        files:
          - path: src/database/postgres/schema/tenant_schema.py
            action: create
          - path: postgres_migrations/env.py
            action: modify
          - path: docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md
            action: create
        exit:
          criteria:
            - "tenant schema modules register on postgres_metadata; DDL-NOTE lists human-owned upgrade/downgrade; no agent-authored versions/ file"
          proof:
            kind: review
            review: "PE confirms DDL-NOTE completeness and env.py import; make check exit 0"
            expected: "schema importable; versions/ untouched by agent"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-01, REQ-02, REQ-04, REQ-32]
        depends_on: [TASK-W0-02]
        files:
          - path: src/database/postgres/repository/tenant_repository.py
            action: create
          - path: src/di/modules/repository_module.py
            action: modify
        exit:
          criteria:
            - "Repository maps ORM to Pydantic; read DTOs never include pat"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-06]
        depends_on: []
        files:
          - path: src/infra_services/github_pat_probe.py
            action: create
          - path: src/di/modules/infra_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
        exit:
          criteria:
            - "verify_read_access returns per-repo ok/reason without persisting the submitted credential"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; itemized failure reasons covered"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-01, REQ-02, REQ-03, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-32]
        depends_on: [TASK-W0-03, TASK-W0-04]
        files:
          - path: src/business_services/tenant_service.py
            action: create
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
        exit:
          criteria:
            - "Probe failure writes 0 rows; success returns one-time tenant token; second tenant needs no env change"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; all-or-nothing + no-pat assertions pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-05"
      - id: TASK-W0-06
        implements: [REQ-03, REQ-04, REQ-05, REQ-32]
        depends_on: [TASK-W0-05]
        files:
          - path: src/api/v1/tenant_token.py
            action: create
          - path: src/api/v1/tenant_routes.py
            action: create
          - path: src/api/v1/__init__.py
            action: modify
        exit:
          criteria:
            - "POST/GET tenants and POST users mounted; wrong/absent tenant token yields 401 before handler body"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; 400/401/422 matrix green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-06"
      - id: TASK-W0-07
        implements: [REQ-08]
        depends_on: [TASK-W0-05]
        files:
          - path: src/business_services/board_service.py
            action: modify
        exit:
          criteria:
            - "Omitted board fields resolve from tenant default; explicit request fields override"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-07"
      - id: TASK-W0-08
        implements: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-06, REQ-07, REQ-32]
        depends_on: [TASK-W0-06]
        files:
          - path: tests/unit/test_tenant_service.py
            action: create
          - path: tests/unit/test_tenant_routes.py
            action: create
          - path: tests/unit/test_github_pat_probe.py
            action: create
          - path: tests/unit/test_tenant_token.py
            action: create
        exit:
          criteria:
            - "Unit matrix covers happy path plus 400/401/422 and no-pat response assertions"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-08"
      - id: TASK-W0-09
        implements: [REQ-04, REQ-06, REQ-32]
        depends_on: [TASK-W0-08]
        files:
          - path: tests/verify/verify_tenant_registry.py
            action: create
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live script registers, attaches, reads/lists without pat; asserts 401 and itemized 422 negatives"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_tenant_registry"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W0-10
        implements: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-32]
        depends_on: [TASK-W0-09]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built INIT-012 W0 row reflects unit-proven and live-verify intent"
          proof:
            kind: review
            review: "PE confirms as-built W0 row accuracy"
            expected: "accurate W0 status"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W0.md § TASK-W0-10"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_tenant_registry
        covers: [REQ-04, REQ-06, REQ-32]
        prerequisites:
          - "API up; human-applied tenant DDL; GitHub PAT for probe"
        safe_test_data:
          - "Ephemeral tenant + disposable workspace_root; non-prod PAT"
        steps:
          - "Run verify_tenant_registry against local stack"
        expected_observations:
          - "Register returns token once; GET bodies omit pat; bad PAT 422 itemized; bad token 401"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Delete synthetic tenant rows and scratch workspace_root"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Tenant registry: data model + API (register, attach user, eager PAT verify, read/list).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-01, REQ-02, REQ-07, REQ-32 | — | Absolute path + no pat on responses | command/make check&&make test |
      | TASK-W0-02 | REQ-01, REQ-02, REQ-09 | TASK-W0-01 | Schema + DDL-NOTE; no agent versions/ | review |
      | TASK-W0-03 | REQ-01, REQ-02, REQ-04, REQ-32 | TASK-W0-02 | Repo maps without pat | command/make test |
      | TASK-W0-04 | REQ-06 | — | Probe ok/reason itemized | command/make test |
      | TASK-W0-05 | REQ-01–09, REQ-32 (subset) | TASK-W0-03, TASK-W0-04 | All-or-nothing + token | command/make test |
      | TASK-W0-06 | REQ-03, REQ-04, REQ-05, REQ-32 | TASK-W0-05 | Routes + 401 before body | command/make test |
      | TASK-W0-07 | REQ-08 | TASK-W0-05 | Board default override precedence | command/make test |
      | TASK-W0-08 | REQ-01–04, REQ-06, REQ-07, REQ-32 | TASK-W0-06 | Unit matrix green | command/make check&&make test |
      | TASK-W0-09 | REQ-04, REQ-06, REQ-32 | TASK-W0-08 | Live verify exit 0 | command/verify_tenant_registry |
      | TASK-W0-10 | REQ-01–09, REQ-32 | TASK-W0-09 | As-built W0 accurate | review |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-012-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-012 W1] Repo clone/refresh workspace prep"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_workspace_lifecycle
    tasks:
      - id: TASK-W1-01
        implements: [REQ-10]
        depends_on: []
        files:
          - path: .harness-pin.yaml
            action: inspect
        exit:
          criteria:
            - "Remounted pin tip reports 0 BROKEN nodes for Tenant workspace-prep shapes (CTR-01 / PE-1)"
          proof:
            kind: command
            command: "make test"
            expected: "pin fixture/assert exit 0; 0 BROKEN"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-10, REQ-11, REQ-13, REQ-14]
        depends_on: [TASK-W1-01]
        files:
          - path: src/infra_services/tenant_git_workspace_client.py
            action: create
          - path: src/di/modules/infra_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
        exit:
          criteria:
            - "Clone vs fetch branching works; invalid checkout raises without mutating tree; per-repo lock serializes; no new Python git dependency"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-10, REQ-12, REQ-15]
        depends_on: [TASK-W1-02]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "Registered omitted-path never hits Path.cwd(); explicit path unchanged; unregistered omitted yields 422 with 0 enqueue"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; regression + new cases green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15]
        depends_on: [TASK-W1-03]
        files:
          - path: tests/unit/test_tenant_git_workspace_client.py
            action: create
          - path: tests/unit/test_run_orchestrator.py
            action: modify
          - path: tests/unit/test_wave_start.py
            action: modify
        exit:
          criteria:
            - "REQ-10–15 unit matrix green under make check && make test"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-10, REQ-13, REQ-14, REQ-15]
        depends_on: [TASK-W1-04]
        files:
          - path: tests/verify/verify_workspace_lifecycle.py
            action: create
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live script proves clone then fetch, mismatch 422, and unregistered omitted 422"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_workspace_lifecycle"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W1-06
        implements: [REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15]
        depends_on: [TASK-W1-05]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W1 row accurate"
          proof:
            kind: review
            review: "PE confirms as-built W1 row"
            expected: "rows updated"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W1.md § TASK-W1-06"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_workspace_lifecycle
        covers: [REQ-10, REQ-13, REQ-14, REQ-15]
        prerequisites:
          - "W0 tenant registered; API+worker; pin remounted; git binary; persistent disk"
        safe_test_data:
          - "Synthetic tenant workspace_root under scratch; fixture remote"
        steps:
          - "Run verify_workspace_lifecycle"
        expected_observations:
          - "First start clones; second fetches; mismatch/unregistered → 422"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Remove scratch workspace_root"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Repo clone (first use) + refresh (subsequent use); replace Path.cwd() for registered repos.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-10 | — | Pin 0 BROKEN (PE-1) | command/make test |
      | TASK-W1-02 | REQ-10, REQ-11, REQ-13, REQ-14 | TASK-W1-01 | git client + lock | command/make test |
      | TASK-W1-03 | REQ-10, REQ-12, REQ-15 | TASK-W1-02 | orchestrator resolution | command/make test |
      | TASK-W1-04 | REQ-10–15 | TASK-W1-03 | unit matrix | command/make check&&make test |
      | TASK-W1-05 | REQ-10, REQ-13–15 | TASK-W1-04 | live verify | command/verify_workspace_lifecycle |
      | TASK-W1-06 | REQ-10–15 | TASK-W1-05 | as-built | review |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-012-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-012 W2] Branch create-or-reuse"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_branch_lifecycle
    tasks:
      - id: TASK-W2-01
        implements: [REQ-16, REQ-17, REQ-18]
        depends_on: []
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "New wave forks from live develop tip; continuation creates zero new refs; branch name matches deterministic convention"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-16, REQ-17, REQ-18]
        depends_on: [TASK-W2-01]
        files:
          - path: tests/unit/test_run_orchestrator.py
            action: modify
          - path: tests/unit/test_pr_branch_naming.py
            action: modify
        exit:
          criteria:
            - "New-vs-continuation unit matrix green; missing remote continuation branch yields named 422"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-16, REQ-18, REQ-19]
        depends_on: [TASK-W2-02]
        files:
          - path: tests/verify/verify_branch_lifecycle.py
            action: create
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live proves new fork, continuation reuse, and never-cloned continuation composition"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_branch_lifecycle"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W2-04
        implements: [REQ-16, REQ-17, REQ-18, REQ-19]
        depends_on: [TASK-W2-03]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W2 row accurate"
          proof:
            kind: review
            review: "PE confirms as-built W2 row"
            expected: "rows updated"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W2.md § TASK-W2-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_branch_lifecycle
        covers: [REQ-16, REQ-18, REQ-19]
        prerequisites:
          - "W1 complete; develop exists on fixture repo; forge credentials"
        safe_test_data:
          - "Ephemeral initiative/wave ids; disposable branches"
        steps:
          - "Run verify_branch_lifecycle"
        expected_observations:
          - "New wave from live develop; continuation reuses; never-cloned continuation succeeds"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Delete ephemeral branches/runs"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Branch create-or-reuse (new wave vs continuation).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-16, REQ-17, REQ-18 | — | fork vs reuse | command/make test |
      | TASK-W2-02 | REQ-16, REQ-17, REQ-18 | TASK-W2-01 | unit matrix | command/make check&&make test |
      | TASK-W2-03 | REQ-16, REQ-18, REQ-19 | TASK-W2-02 | live verify | command/verify_branch_lifecycle |
      | TASK-W2-04 | REQ-16–19 | TASK-W2-03 | as-built | review |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-012-gateflow.md

  - id: W3
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-012 W3] Harness-readiness check"
    depends_on:
      - W2
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_harness_readiness
    tasks:
      - id: TASK-W3-01
        implements: [REQ-20, REQ-21, REQ-22]
        depends_on: []
        files:
          - path: src/infra_services/launchpad_client.py
            action: modify
          - path: src/database/postgres/schema/tenant_schema.py
            action: modify
          - path: src/database/postgres/repository/tenant_repository.py
            action: modify
        exit:
          criteria:
            - "Non-ready fails with named missing artifact; ready passes; cache skips repeat; re-check forces probe"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-01"
      - id: TASK-W3-02
        implements: [REQ-20]
        depends_on: [TASK-W3-01]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "Harness check runs after workspace resolve and before Enter-at skill for unverified repos"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-02"
      - id: TASK-W3-03
        implements: [REQ-20, REQ-21, REQ-22]
        depends_on: [TASK-W3-02]
        files:
          - path: tests/unit/test_launchpad_client.py
            action: create
          - path: tests/unit/test_run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "First-ever launchpad_client unit file + positive/negative harness fixtures green"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-03"
      - id: TASK-W3-04
        implements: [REQ-20, REQ-21]
        depends_on: [TASK-W3-03]
        files:
          - path: tests/verify/verify_harness_readiness.py
            action: create
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live positive (harness present) and negative (absent → 422) both pass"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_harness_readiness"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W3-05
        implements: [REQ-20, REQ-21, REQ-22]
        depends_on: [TASK-W3-04]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W3 row accurate"
          proof:
            kind: review
            review: "PE confirms as-built W3 row"
            expected: "rows updated"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W3.md § TASK-W3-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_harness_readiness
        covers: [REQ-20, REQ-21]
        prerequisites:
          - "W1 workspace path available; fixture repos with/without harness artifacts"
        safe_test_data:
          - "Fixture trees only"
        steps:
          - "Run verify_harness_readiness"
        expected_observations:
          - "Ready passes; absent artifacts → 422 named miss"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Reset verified-cache flags on synthetic tenant_repos"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Harness-readiness check after clone/refresh, before coding-hop.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W3-01 | REQ-20–22 | — | real check + cache | command/make test |
      | TASK-W3-02 | REQ-20 | TASK-W3-01 | wire before dispatch | command/make test |
      | TASK-W3-03 | REQ-20–22 | TASK-W3-02 | first unit file | command/make check&&make test |
      | TASK-W3-04 | REQ-20, REQ-21 | TASK-W3-03 | live verify | command/verify_harness_readiness |
      | TASK-W3-05 | REQ-20–22 | TASK-W3-04 | as-built | review |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-012-gateflow.md

  - id: W4
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-012 W4] Repo-scoped NO_CONCURRENT_RUN"
    depends_on:
      - W3
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_start
    tasks:
      - id: TASK-W4-01
        implements: [REQ-23, REQ-24]
        depends_on: []
        files:
          - path: tests/unit/test_run_store_concurrency.py
            action: create
        exit:
          criteria:
            - "Historical-pattern fixture exists asserting same-repo block and cross-repo non-block intent before query change"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0 (or documented xfail flipped by TASK-W4-02)"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W4.md § TASK-W4-01"
      - id: TASK-W4-02
        implements: [REQ-23, REQ-24, REQ-25]
        depends_on: [TASK-W4-01]
        files:
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
          - path: src/business_services/wave_start_service.py
            action: modify
        exit:
          criteria:
            - "Same-repo second start returns existing NO_CONCURRENT_RUN PreconditionFailure; different repos both authorized; no new isolation types introduced"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; FF-06 fixture green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W4.md § TASK-W4-02"
      - id: TASK-W4-03
        implements: [REQ-23, REQ-24]
        depends_on: [TASK-W4-02]
        files:
          - path: tests/verify/verify_wave_start.py
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live verify_wave_start asserts same-repo reject and cross-repo allow under knobs"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_wave_start"
            expected: "exit 0"
            evidence_expected: "wave-accepted on tip"
      - id: TASK-W4-04
        implements: [REQ-23, REQ-24, REQ-25]
        depends_on: [TASK-W4-03]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W4 row accurate including REQ-25 inspection note"
          proof:
            kind: review
            review: "PE confirms as-built W4 row and no isolation infra"
            expected: "rows updated"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W4.md § TASK-W4-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_start
        covers: [REQ-23, REQ-24]
        prerequisites:
          - "API up; two wave-start capable repos/identities"
        safe_test_data:
          - "Ephemeral runs; no ACTIVE orphans left behind"
        steps:
          - "Run verify_wave_start concurrency probes"
        expected_observations:
          - "Same-repo second start rejected with NO_CONCURRENT_RUN; cross-repo both succeed"
        evidence_expected: "wave-accepted on tip"
        cleanup:
          - "Cancel/complete synthetic ACTIVE runs"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Broaden NO_CONCURRENT_RUN to org+repo ACTIVE scope.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W4-01 | REQ-23, REQ-24 | — | FF-06 fixture first | command/make test |
      | TASK-W4-02 | REQ-23–25 | TASK-W4-01 | query broaden | command/make check&&make test |
      | TASK-W4-03 | REQ-23, REQ-24 | TASK-W4-02 | live verify_wave_start | command/verify_wave_start |
      | TASK-W4-04 | REQ-23–25 | TASK-W4-03 | as-built | review |

      ## Done when

      - [ ] All W4 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-012-gateflow.md

  - id: W5
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-012 W5] Dormant ForgeClient.delete_branch"
    depends_on:
      - W4
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    verify_command: N/A — P15 N/A; dormant zero live callers
    tasks:
      - id: TASK-W5-01
        implements: [REQ-26]
        depends_on: []
        files:
          - path: src/infra_services/forge_client.py
            action: modify
        exit:
          criteria:
            - "delete_branch succeeds via existing DELETE-ref transport path/method in unit doubles"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W5.md § TASK-W5-01"
      - id: TASK-W5-02
        implements: [REQ-27]
        depends_on: [TASK-W5-01]
        files:
          - path: tests/unit/test_forge_client.py
            action: modify
          - path: tests/unit/test_delete_branch_dormant.py
            action: create
        exit:
          criteria:
            - "Missing/protected branch raises named error; code-guard asserts zero production callers of delete_branch"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; dormancy guard green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W5.md § TASK-W5-02"
      - id: TASK-W5-03
        implements: [REQ-26, REQ-27]
        depends_on: [TASK-W5-02]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "As-built and tests README document unit-only dormant capability"
          proof:
            kind: review
            review: "PE confirms dormant documentation"
            expected: "rows updated"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-012-W5.md § TASK-W5-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "P15 N/A — delete_branch ships dormant with zero live callers this INIT (G5)"
    body: |
      ## Wave goal

      ForgeClient.delete_branch built and dormancy-proven (gateflow half only).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W5-01 | REQ-26 | — | DELETE-ref method | command/make test |
      | TASK-W5-02 | REQ-27 | TASK-W5-01 | fail-closed + dormancy guard | command/make check&&make test |
      | TASK-W5-03 | REQ-26, REQ-27 | TASK-W5-02 | as-built/docs | review |

      ## Done when

      - [ ] All W5 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-012-gateflow.md
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-012
    source_freshness: CURRENT
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/32"
    meta_pr_head: "74402540efd98527014b4706d0d29bda1242b6cf"
    map_revision: 1
    prd_digest: "sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b"
    scope_digest: "sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678"
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/183"
    adr_accepted:
      - docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md
    p_checks: pass
    nonblocking_questions: "PM-1"
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    # Pin: spec-implementation-plan forge.commit_workspace = required.
    # Publish this plan onto Draft spec PR #183 — invoke /commit-workspace.
    # This skill does not mutate GitHub.
```
