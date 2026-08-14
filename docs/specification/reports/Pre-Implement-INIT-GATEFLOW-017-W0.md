## Pre-implement — gateflow / W0 — Membership schema + identity JWT session

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W0.md` |
| Initiative | INIT-GATEFLOW-017 |
| Wave | W0 |
| Date | 2026-08-14 |
| Outcome | `pass` |
| Outcome reason | Spec merged with `spec-lgtm`, board seeded, WorkManifest clean, PE sign-off complete, P15 live command is `verify_jwt_login`, H1–H3 match live durable roots. |
| Wave head context | Bound by Forge/human context: `develop` @ `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) MERGED (`mergeCommit` = current `develop`); plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; `mergeCommit` `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244); W0–W3 [#245](https://github.com/drivestream-lab/gateflow/issues/245)–[#248](https://github.com/drivestream-lab/gateflow/issues/248) on **drivestream-lab Board** (org project #3); W0 body lists TASK-W0-01…05 and `Part of #244` |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md --base-path .` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — TASK-W0-01…05 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `.venv/bin/python -m tests.verify.verify_jwt_login` (extend existing; not `make test`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan § Source freshness |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — H3 `1`; H2 `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` (impact-map gateflow row) |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67` (`prayog-meta/prd/INIT-GATEFLOW-017.md`); G1 `601b00e0a74510a6af1c33bc80ca27260995c094` (meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42) merge parent) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_jwt_login` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` uses as-built + spec citations; no dedicated ground script |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` | [x] `tests/verify/verify_jwt_login.py` (FILE-W0-14, **extend**) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] N/A — W0 first 017 wave |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-14, @nikd10x, Cursor chat, Draft spec PR #243 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Forge readiness (when seed / wave head absent):** not required. Wave head is `develop`. Coding branch `feature/INIT-GATEFLOW-017-w0-session-membership` is cut by `/loop-spec` / Forge — not this skill.

**Board seed note (non-blocking):** GitHub GraphQL `parent` on #245 is `null`. This `gh` cannot set native sub-issues; seed used body `Part of #244` plus project #3 items. EPIC + all four wave issues exist with TASK projection. Do not re-seed.

---

### Contracts consumed (from prior Ground Report)

> W0 has no INIT-GATEFLOW-017 Ground Report. Baseline is live `source_roots` plus
> INIT-GATEFLOW-014 as-built (`human_approved` for 014 W0–W4). Confirmed against
> source, not spec text alone. Codegraph (`data-repos-prayog-gateflow`) used as
> assist; every row below re-read from files.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Identity row is 1:1 programme bind | `UserIdentitySchema` (`src/database/postgres/schema/user_identity_schema.py`) | `credential_identifier`, `password_hash`, `role`, optional `tenant_id` | Unique credential; no `display_name` / `status` / `session_epoch`; no membership table | source | [x] yes — W0 drops `tenant_id` and adds membership + session columns |
| Identity persist | `UserIdentityRepository` (`src/database/postgres/repository/user_identity_repository.py`) | `create_identity(..., tenant_id=)`; `get_by_credential_identifier`; `delete_for_tenant` | `UserIdentityReadModel` including `tenant_id` | source | [x] yes — no `get_by_id`; wipe + attach still call these |
| JWT verify (no repo) | `AuthMiddleware.dispatch` (`src/common/auth/middleware.py`) | Bearer JWT; `sub` / `role` / optional `tenant_id` | `request.state.auth` = `AuthContext` or 401 `UNAUTHORIZED`; **401 when `TENANT_ADMIN` and `tenant_id` missing** (lines 105–106) | source | [x] yes — invert this 401 (ADR-019); do not add repo I/O here |
| Role gate (JWT only) | `require_role` (`src/common/auth/dependencies.py`) | `AuthContext.role` vs allowed set | same context or 403 `role_forbidden` | source | [x] yes — no identity-row load; W0 must refuse inactive status and `session_epoch` mismatch |
| Programme scope (claim) | `require_programme_scope` / `require_path_programme_scope` / `require_tenant_resolved` | JWT `tenant_id` vs path tenant | context or 403 `tenant_scope_mismatch` | source | [x] yes — W0 switches to membership row `(user_id, path tenant)` |
| Mint + login | `AuthIdentityService.mint_user_jwt` / `login` (`src/business_services/auth_identity_service.py`) | user_id, role, optional tenant_id; login body identifier + password | JWT may include `tenant_id`; `LoginResponse` is `access_token` + `token_type` only | source | [x] yes — W0 mints `session_epoch`, no programme claim; snapshot `{grants: []}` |
| Login HTTP | `POST /api/auth/login` (`src/api/auth/login_routes.py`) | `LoginRequest` JSON body | `LoginResponse` 200 | source | [x] yes — identifier is unconstrained `str` (REQ-03 email check is W0) |
| Auth DTOs | `AuthContext`, `LoginRequest`, `LoginResponse`, `UserIdentityReadModel` (`src/models/auth_models.py`) | as declared | `extra=forbid` | source | [x] yes — no `session_epoch` / `grants` / `display_name` / `status` yet |
| 014 create+bind door (still live) | `ProgrammeService.attach_tenant_admin` (`src/business_services/programme_service.py`) | credential + password + programme | creates identity with `tenant_id`; mints JWT **with** `tenant_id` | source | [x] yes — **not deleted in W0**; compile-safe after schema drop (see Unconfirmed) |
| Wipe deletes identities | `ProgrammeWipeService.wipe_programme` → `delete_for_tenant` | programme tenant | identity rows for that tenant deleted | source | [x] yes — FF-02 / W2 owns correct wipe; W0 remove of `delete_for_tenant` breaks this caller |
| Live login smoke | `tests/verify/verify_jwt_login.py` | seeded `platform_admin` | 200 + JWT; marker `prayog:covers:` 014 REQ-01/02/03/43 | source + `tests/README.md` | [x] yes — **extend**; keep intersection; add 017 REQ-03 and REQ-18 |
| Unit invert target | `test_tenant_admin_missing_tenant_id_401` (`tests/unit/test_auth_middleware.py`) | TENANT_ADMIN JWT without `tenant_id` | asserts 401 | source | [x] yes — invert to not-401 |
| Schema registration | `postgres_migrations/env.py` | import side effect | `user_identity_schema` registered | source | [x] yes — W0 must import new membership schema |
| Repo DI | `RepositoryModule.provide_user_identity_repository` (`src/di/modules/repository_module.py`) | `PostgresService` session factory | singleton repo | source | [x] yes — new membership repo needs a provider (not in §9 file list) |

**Unconfirmed contracts** (no 017 Ground Report; adjacent callers not in W0 file list):

- `ProgrammeService.attach_tenant_admin` and `ProgrammeWipeService.wipe_programme` still consume `tenant_id` / `delete_for_tenant`. Declared W0 files omit them. `/loop-spec` must keep `make test` / pyright green with **compile-safe** edits only: stop passing `tenant_id` into identity create/mint; stop calling `delete_for_tenant`. Do **not** implement enter/grant (W1) or door delete (W2). Wipe must not delete identity rows once `tenant_id` is gone (aligns with FF-02; membership cascade wipe remains W2).
- `RepositoryModule` has no membership binding. Bind `ProgrammeMembershipRepository` in the same change as TASK-W0-02 even though `src/di/modules/repository_module.py` is not in the §9 file list.
- `require_role` / `require_programme_scope` become identity/membership reads. Dependencies must go through a business service or repository — **not** ORM schema (`repository-pattern.mdc`, `architecture.mdc`). Middleware stays JWT-only (ADR-019).
- `IdentityStatusType` is listed as W1 FILE-W1-02. TASK-W0-03 needs a closed status vocabulary for inactive refusal. Introduce the enum in W0 if `require_role` checks it; do not invent values beyond spec suspend / not-suspended.
- `AuthContext.session_epoch` is needed when middleware extracts the claim (TASK-W0-03) even though `auth_models.py` is listed under TASK-W0-04.
- `UserIdentityRepository.get_by_id` does not exist; TASK-W0-02 must add it for `require_role` load-by-`sub`.
- Provision helper `tests/_helpers/verify_jwt_auth.py` `provision_programme_tenant_admin` is **W2 / FF-03** — do not rewrite in W0.
- Historic `POST /api/v1/tenants/{id}/users` and `POST /api/v1/programmes/{id}/tenant-admins` stay mounted until W2.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `architecture.mdc` — JWT verify only in middleware; routers → business → repo
  - [x] `database-migrations.mdc` — agent runs `./scripts/create_postgres_migration.sh`; human runs `./scripts/run_postgres_migration.sh` (this skill / agent must not apply)
  - [x] `repository-pattern.mdc` — ORM only in repos; Pydantic at the repo boundary
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only; enums `str, Enum` + `Type` suffix; `Field(default=...)`
  - [x] `dependency-injection.mdc` — `@inject`; settings via `get_instance()`; bind new repo in `RepositoryModule`
  - [x] `http-api-conventions.mdc` — login body stays a Pydantic model
  - [x] `testing-verify-flows.mdc` — extend live script; do not duplicate full HTTP journeys in pytest
  - [x] `fail-fast.mdc` — no silent fallback if membership/identity missing
  - [x] `strong-typing.mdc` — no `dict` service APIs
  - [x] `python-imports.mdc` — top-of-file imports; DI bootstrap exception only
  - [x] `logging-loguru.mdc` — static message + kwargs
  - skipped: `infra-services.mdc` (no new outbound client); `python-tooling.mdc` (commands already resolved); `spec-driven-development.mdc` / `code-guidelines-index.mdc` (process index)
- [x] ADRs (keyword-matched — identity / JWT / session / membership / durable store / tenant scope):
  - [x] ADR-019 — Accepted — Option B: no programme claim; membership scope; `session_epoch`; no Redis denylist
  - [x] ADR-001 — Accepted — Postgres is sole durable store (rejects Redis session denylist)
  - [x] ADR-014 — Accepted — JWT-only product edge; W0 supersedes **only** the `TENANT_ADMIN`-must-carry-`tenant_id` clause
  - [x] ADR-016 — Accepted — `runs.tenant_id` still from **path tenant after** membership check
  - skipped: ADR-002–013, 015, 017, 018 (not this slice)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` — W0 spends REQ-03, REQ-12, REQ-14, REQ-16, REQ-18, REQ-21
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/245 — TASK list (projection only):
  - [ ] TASK-W0-01 — implements REQ-21 — depends_on: [] — files: `user_identity_schema.py` modify; `programme_membership_schema.py` create; `postgres_migrations/env.py` modify — exit: Alembic create script adds `programme_memberships` and drops `user_identities.tenant_id` — proof: `./scripts/create_postgres_migration.sh "identity membership and session epoch"`
  - [ ] TASK-W0-02 — implements REQ-21 — depends_on: [TASK-W0-01] — files: `user_identity_repository.py` modify; `programme_membership_repository.py` create; `test_programme_membership_repository.py` create — exit: unique `(identity_id, programme_id)` pair persists — proof: `make test`
  - [ ] TASK-W0-03 — implements REQ-12, REQ-14, REQ-16 — depends_on: [TASK-W0-02] — files: `middleware.py` modify; `dependencies.py` modify; `test_auth_middleware.py` modify — exit: missing `tenant_id` not 401; epoch mismatch and inactive status are 401 — proof: `make check && make test`
  - [ ] TASK-W0-04 — implements REQ-03, REQ-16, REQ-18 — depends_on: [TASK-W0-03] — files: `auth_identity_service.py` modify; `auth_models.py` modify; `login_routes.py` modify; `test_auth_identity_service.py` modify — exit: login 200 with `access_token` + `grants` array; minted JWT has no `tenant_id` — proof: `pytest tests/unit/test_auth_identity_service.py -q`
  - [ ] TASK-W0-05 — implements REQ-03, REQ-18 — depends_on: [TASK-W0-04] — files: `tests/verify/verify_jwt_login.py` modify — exit: live login 200 with `grants`; marker includes REQ-03 and REQ-18 — proof: `.venv/bin/python -m tests.verify.verify_jwt_login` (human at `wave-acceptance`)

**DAG for `/loop-spec`:** TASK-W0-01 → TASK-W0-02 → TASK-W0-03 → TASK-W0-04 → TASK-W0-05.

---

### Governance alignment

- [x] Slice spec does not contradict ADR-019 / ADR-001 / ADR-014 (partial supersession) / ADR-016
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed
- [x] ADR-019 is **Accepted** in `docs/specification/adr/adr-019-identity-jwt-programme-scope-and-session-epoch.md` (PE @nikd10x, 2026-08-14, PR #243). Lint evidence `sha256:2fbe1ecdb1a73335982e365dd57bcbff12d4b51e328c95be124cc2efa9e86d25`

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — no REQ rewrite in W0 unless a contract word changes; as-built is the maturity update
- [ ] `docs/specification/as-built/implementation-status.md` — add INIT-GATEFLOW-017 W0 verification row (not `human_approved` until `wave-acceptance`)
- [ ] `tests/README.md` — feature map: `verify_jwt_login` now also covers 017 REQ-03 / REQ-18 snapshot
- [ ] Unit — invert `test_tenant_admin_missing_tenant_id_401`; add epoch/status 401 cases; membership unique-pair; login snapshot + no `tenant_id` claim; email 422 `not an email`
- [ ] Live — extend `tests/verify/verify_jwt_login.py` (do not create a new script); marker must include REQ-03 and REQ-18 and keep intersection with existing 014 REQ-01/02/03/43
- [ ] ADR — do not rewrite Accepted ADR-019; no new ADR in W0

---

### Must not

- [ ] Implement against spec wording that contradicts Accepted ADR-019 (no remint; no Redis denylist; no programme claim)
- [ ] Duplicate unit verification assertions in live smoke (live = seed + login 200 + `grants` field present)
- [ ] Assume 014 attach/wipe still compile after dropping `tenant_id` without updating those callers
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Run `./scripts/run_postgres_migration.sh` (human-owned)
- [ ] Delete `POST /api/v1/programmes/{id}/tenant-admins` or historic `POST /api/v1/tenants/{id}/users` (W2)
- [ ] Rewrite `provision_programme_tenant_admin` (W2 / FF-03)
- [ ] Ship enter/list/grant/detach/suspend/password-set APIs (W1)
- [ ] Populate login `grants` from memberships (W0 snapshot is `{grants: []}`; enter-programme is W3)
- [ ] Put Pydantic models under `src/api/`
- [ ] Change `public_paths` product-prefix allowlist

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Schema/repo membership pair; inverted missing-`tenant_id`; epoch/status 401; login snapshot; no `tenant_id` claim; email refusal | `make test` |
| Live verify | Seeded `platform_admin` login 200 with `access_token` and `grants` array (human-run at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` uses as-built + spec citations |

> P15 applies (login response shape changes). N/A or unit-only for live verify would block this gate — it does not. Agent implements the extend in `/loop-spec`; does **not** run live verify as success. Human applies `./scripts/run_postgres_migration.sh head` before smoke.

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Apply `./scripts/run_postgres_migration.sh head` (human-owned)
- [ ] `make run` with JWT key material and `auth.platform_admin` in `tests/config.yaml`
- [ ] Run `.venv/bin/python -m tests.verify.verify_jwt_login`
- [ ] Confirm 200 login, `access_token`, `grants` array present (may be empty)
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-017
- Issue: [#245](https://github.com/drivestream-lab/gateflow/issues/245) (EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244))
- Spec path: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_jwt_login`
- ADRs in scope: ADR-019 (primary), ADR-001, ADR-014 (partial supersession), ADR-016
- Wave head: bound by Forge/human context — `develop` @ `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` (Forge/human may bind `feature/INIT-GATEFLOW-017-w0-session-membership` before coding)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W0 gates satisfied |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-017-W0.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here. Do not create the feature branch here.

---

### Merge order (if cross-module / cross-service)

N/A — W0 is gateflow-only. `gateflow-ops` consumes CTR-01–04 later; no ops change in this wave.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    wave: W0
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/244"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/245"
    board_seed: seeded
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_lgtm_at_merge: true
    pe_signoff: complete
    workmanifest_contract: pass
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_jwt_login"
    ground_command: null
    wave_head: develop
    codegraph_provider: data-repos-prayog-gateflow
    grounding_depth: source-confirmed
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-017): Pre-Implement W0 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W0.md
```
