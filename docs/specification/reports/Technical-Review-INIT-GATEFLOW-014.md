# Technical Design Document — INIT-GATEFLOW-014

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Spec digest | `sha256:ba84792a5372ace145280aaa09730de368e5500f87c9cab4b6c6d7284e3258df` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-014.md` |
| PRD digest | `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-014.md` / `1` |
| Repo scope digest | `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Approved meta PR head | `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7` |
| Source freshness | CURRENT — spec PR #212 head `7f212feb3267628b7448c3e56460c0f727e5236c` unchanged; H1/H2/H3/G1 re-verified this session |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-10 |
| Branch | `chore/INIT-GATEFLOW-014-spec-gateflow` (spec PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-014` |
| Status | **Accepted** — PE (@nikd10x) explicit acceptance via Cursor chat, 2026-08-10, Draft spec PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) |
| Review deadline | 2026-08-17 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

> **Confirmation pass (second `/spec-technical-review` invocation, same day):**
> `Initiative-Feasibility-Report-INIT-GATEFLOW-014.md` revision 2 (`pass`,
> zero unresolved findings) has since completed — the incremental-feasibility
> gate this TDD's prior routing note called for is now satisfied, not merely
> proposed. This pass independently re-verified (not assumed from the prior
> pass): freshness (spec PR #212 and meta PR #35 heads unchanged), all 3 ADRs
> + this TDD via fresh `adr_boundary_lint.py` runs (identical digests — zero
> drift), and a fresh manual T12 re-read of all 4 files. Two stale artifacts
> were found and corrected: §5's test policy still described legacy-row/
> null-`tenant_id` test cases that are moot post-ADR-016; the routing caveat
> below and in Forge instructions described the feasibility gate as pending
> when it has since closed. No new engineering or product-boundary issue was
> found.

---

## 1. Problem statement

Three independently-authenticated Bearer schemes (dormant JWT, one static
programme-token, one per-tenant keyed bearer) currently coexist across seven
route modules with no shared authorization context, and none of the durable
run/board/checkpoint records carry an attribution column that a single
identity model could authorize against (REQ-04, REQ-24, REQ-29, REQ-31,
REQ-32, REQ-33). Outbound GitHub credential resolution is a second,
independent single-process-lifetime resolution problem: one DI-singleton
client resolves one Bearer token at startup for every caller, which cannot
vary per caller identity (REQ-11, REQ-14, REQ-25).

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/common/auth/middleware.py`, `config.py` | exists, dormant on product routes | extend — allowlist shrink, role/programme claim extraction | infra (edge) |
| `src/models/auth_models.py` | exists (`AuthContext.role: str`) | extend — `role` becomes `RoleType(str, Enum)` | models |
| `src/models/role_types.py` | new | create — `RoleType` enum (`PLATFORM_ADMIN`, `TENANT_ADMIN`) | models |
| `src/common/auth/dependencies.py` | does not exist | create — `require_role()`, `require_programme_scope()` FastAPI dependencies | infra (edge) |
| `src/api/auth/` | does not exist | create — login route (no UI) | api |
| `src/business_services/auth_identity_service.py` | does not exist | create — seed + login orchestration, credential verification | business |
| `src/database/postgres/schema/user_identity_schema.py` | does not exist | create — `platform_admin`/`tenant_admin` user rows | database/schema |
| `src/database/postgres/schema/programme_schema.py` | does not exist | create — Programme entity (PAT, workspace root, lane defaults) | database/schema |
| `src/business_services/programme_service.py` | does not exist | create — validate-then-create orchestration, attach, list | business |
| `src/api/v1/programme_admin_routes.py` | does not exist | create — `platform_admin`-only Programme/attach/list/agent routes | api |
| `src/database/postgres/schema/platform_agent_catalogue_schema.py` | does not exist | create — agent catalogue + per-lane defaults | database/schema |
| `src/business_services/platform_agent_catalogue_service.py` | does not exist | create — provision + effective-runner resolution | business |
| `src/business_services/slot_validator.py` | exists — hardcoded env check for `cursor` | extend — replace with catalogue lookup (FF-04) | business |
| `src/infra_services/cursor_agent_runner.py` | exists — reads `CursorAgentSettings` directly | extend — accepts resolved credential from caller, does not read settings for authorization | infra |
| `src/infra_services/forge_client.py`, `github_token_provider.py` | singleton, one process-global credential | extend — `ForgeClientFactory` resolves per-Programme instance (ADR-015) | infra |
| `src/database/postgres/schema/run_store_schema.py` (`RunSchema`) | no tenant/programme column | extend — add `tenant_id` FK (ADR-016) | database/schema |
| `src/business_services/board_service.py`, `checkpoint_evidence_service.py`, `metrics_emitter.py` | query by `org`/`repo`/`initiative_id` only | extend — join through `run_id` → `tenant_id` → Programme for scoped reads | business |
| `src/api/v1/waves_routes.py`, `runs_routes.py`, `board_routes.py`, `checkpoints_routes.py`, `initiatives_routes.py`, `metrics_routes.py`, `forge_routes.py` | `Depends(verify_programme_service_token)` | extend — `Depends(require_role(RoleType.TENANT_ADMIN))` + programme-scope check | api |
| `src/api/v1/tenant_routes.py`, `programme_routes.py` (existing meta-catalogue-connection routes) | `Depends(verify_tenant_bearer_token)`; module named `programme_routes.py` collides with new Programme entity vocabulary (FF-06/Q-5) | extend auth; **rename** `programme_routes.py` → `catalogue_connection_routes.py`, `ProgrammeOnboardingService` → `CatalogueConnectionService` (naming resolution, §9 AF-1) | api |
| `src/api/v1/programme_token.py`, `tenant_token.py` | exist, sole auth dependencies today | **delete** at W3 (REQ-34/dead-door deletion) | api |

**Boundary diagram (text):**

```
Caller (Bearer JWT)
  → [AuthMiddleware] → AuthContext{user_id, role: RoleType, tenant_id}
      → [require_role / require_programme_scope deps] → route handler
          → [ProgrammeService] → [ProgrammeRepository] → programmes (PAT, workspace, lane defaults)
          → [PlatformAgentCatalogueService] → [PlatformAgentCatalogueRepository] → agent catalogue
          → [BoardService/CheckpointEvidenceService/MetricsEmitter] → RunRepository.tenant_id join → Programme
          → [ForgeClientFactory.for_programme(programme_id)] → ForgeClient(programme_pat) → GitHub REST
```

---

## 3. Public interface contracts

### 3.1 `AuthMiddleware` → `AuthContext`

**Method / entry point:** `AuthMiddleware.dispatch` (unchanged signature)
**Arguments:**
- `request`: incoming HTTP request — invariant: `Authorization: Bearer <jwt>` required on any path not in the (shrunk) allowlist

**Return:**
- `request.state.auth`: `AuthContext{user_id: UUID, role: RoleType, tenant_id: Optional[UUID], owner_id: Optional[UUID]}` — `role` is `RoleType.TENANT_ADMIN` or `RoleType.PLATFORM_ADMIN`; `tenant_id` required (non-null) when `role == TENANT_ADMIN`
- Error: 401 `UNAUTHORIZED` on missing/malformed/expired/wrong-issuer/wrong-audience token, or on a `TENANT_ADMIN` token missing a tenant binding claim

**Invariants:**
- `role` must validate against `RoleType`; an unrecognized role string is a 401, not a silent pass-through
- `tenant_id` claim, when present, must resolve to an existing Tenant row before being trusted downstream (verified by the calling dependency, not the middleware itself — middleware only decodes and shapes the claim)

### 3.2 `require_role` / `require_programme_scope` (FastAPI dependencies)

**Method / entry point:** `require_role(*allowed: RoleType) -> Callable`, `require_programme_scope(path_tenant_id: UUID) -> Callable`
**Arguments:**
- `allowed`: one or more `RoleType` values a route accepts
- `path_tenant_id`: the tenant identifier named in the route path or resolved from a `run_id`/`org`+`repo` lookup

**Return:**
- On success: no value (dependency passes); `request.state.auth` remains the source of truth for the handler
- Error: 403 `FORBIDDEN` (named reason) when `request.state.auth.role` is not in `allowed`, or when `request.state.auth.tenant_id != path_tenant_id`

**Invariants:**
- Replaces `verify_programme_service_token` and `verify_tenant_bearer_token` on every route listed in spec Appendix C; no route imports both an old and a new dependency simultaneously past W2

### 3.3 `ProgrammeService.validate_then_create`

**Method / entry point:** `validate_then_create(request: ProgrammeOnboardRequest) -> ProgrammeCreateResult`
**Arguments:**
- `request.meta_location`, `request.workspace_root`, `request.github_pat` — all required; invariant: `github_pat` must probe-succeed and `meta_location` must clone/parse before any row is written

**Return:**
- `ProgrammeCreateResult{programme_id, repo_catalogue}` on success
- Error: named `ValidationError`/`UnprocessableEntityError` on PAT or meta failure — zero Programme or Tenant rows persisted

**Invariants:**
- No agent-key field is accepted on this contract (REQ-13) — a request carrying one is a 422, not a silently-dropped field
- Validation (PAT probe + meta clone/parse) completes fully before the transaction that creates the Programme row opens

### 3.4 `PlatformAgentCatalogueService.resolve_effective_runner`

**Method / entry point:** `resolve_effective_runner(programme_id: UUID, lane: LaneType, caller_runner: Optional[str], caller_model: Optional[str]) -> EffectiveRunner`
**Arguments:**
- `caller_runner`/`caller_model`: optional per-call override; when both absent, resolution falls through to the Programme's stored per-lane default

**Return:**
- `EffectiveRunner{runner_id, model_id, credential}` — `credential` is read from the catalogue row for `runner_id`, never from process settings
- Error: named `UnprocessableEntityError` when the resolved `runner_id` is unprovisioned or its catalogue key is blank

**Invariants:**
- `CursorAgentSettings`/env `CURSOR_API_KEY` is never consulted by this method — REQ-41 is enforced at this boundary, not downstream in `CursorAgentRunner`

### 3.5 `ForgeClientFactory.for_programme`

**Method / entry point:** `for_programme(programme_id: UUID) -> ForgeClient`
**Arguments:**
- `programme_id`: resolves the Programme's stored PAT as the Bearer source

**Return:**
- A `ForgeClient` instance scoped to that Programme's credential — structurally identical to today's `ForgeClient` public methods; only construction changes
- Error: named error when the Programme has no usable PAT (should not occur post-validate-then-create, but the factory does not silently fall back to an App-installation or env credential)

**Invariants:**
- No caller obtains a `ForgeClient` bound to any credential other than the Programme it named (ADR-015)

### 3.6 `RunRepository` / `BoardService` / `CheckpointEvidenceService` — tenant-scoped reads

**Method / entry point:** existing list/get methods gain a required `tenant_id: UUID` (or `AuthContext`) parameter
**Arguments:**
- `tenant_id`: the caller's bound tenant (from `AuthContext`); `platform_admin` callers pass no tenant filter and see all rows (per REQ-17/REQ-18's platform-admin list scope)

**Return:**
- Rows filtered to `RunSchema.tenant_id == tenant_id` (directly) or via `run_id` join (board/checkpoint) — unchanged response shape otherwise
- Error: none new — an empty result set for a scope mismatch, not an error (cross-programme access is refused at the auth-dependency layer per 3.2, before reaching this query)

**Invariants:**
- `tenant_id` is non-nullable on every row (REQ-35's cutover wipe means the
  column is introduced against an already-reset database — PM-confirmed,
  §10 PM-2); no null-tenant filter branch exists in this method

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-01 | ADR_REQUIRED | `docs/specification/adr/adr-014-jwt-only-product-edge-trust-zone.md` | `[REQ-04, REQ-06, REQ-28, REQ-29, REQ-32, REQ-33]` | REQ-04, REQ-06, REQ-28, REQ-29, REQ-32, REQ-33 | No new verification mechanism; formal supersession of ADR-002/005/011 only (Option A) — see revision note below | **Accepted** | `sha256:d515f3792ed6a83e532469c0a69193914f6fa2aa15449a8d67aa2c8046cc5f67` |
| FF-02 | ADR_REQUIRED | `docs/specification/adr/adr-015-programme-scoped-forge-credential-resolution.md` | `[REQ-11, REQ-14, REQ-25]` | REQ-11, REQ-14, REQ-25 | `ForgeClientFactory` per-Programme resolution (Option C) | **Accepted** | `sha256:275d49b933484ffe0dc7dc273c5c6ad9a84374802f4b76b4b2ad17e4aee8e377` |
| Q-4 (spec) | ADR_REQUIRED | `docs/specification/adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md` | `[REQ-23, REQ-24, REQ-31]` | REQ-23, REQ-24, REQ-31 | `tenant_id` on `RunSchema`, non-nullable; board/checkpoint derive via `run_id` join (Option C) | **Accepted** | `sha256:e68a20da519bfc1647f917407fe2e891162b8e9964c77ae47e12f1233eef5439` |

> **Revision note (self-critique pass, post-first-draft):** the first drafts
> of all three ADRs were re-audited against the product/architecture boundary
> after initial publication. ADR-014's original "Options considered" (how
> many ADR files record the supersession) was not a genuine engineering
> trade-off and was replaced with the actual open question (does the JWT edge
> cutover need new verification machinery, or does it reuse
> `AuthMiddleware`/`AuthContext`). ADR-015's Option A (GitHub App
> multi-installation) was reworded to make explicit it is foreclosed by
> REQ-14, not a live choice. ADR-016's Consequences originally stated a
> legacy-row read-access policy (`tenant_id IS NULL` rows "visible only
> through `platform_admin`-scoped reads") that **no approved REQ backs** —
> product-boundary leakage the mechanical lint cannot detect (§13 "three
> gaps" per `checks.md`); it was removed and routed to PM as PM-2.
>
> **PM-2 resolved (interactive, this session):** PM confirmed this is a
> greenfield, pre-production cutover — the database is fully reset (schema
> and tables) as part of INIT-014, not migrated in place over live rows. No
> `tenant_id IS NULL` row can ever exist, so the legacy-row read-access
> question is moot rather than answered a particular way. ADR-016 was
> updated accordingly: `tenant_id` is **non-nullable**, the "Product decisions
> excluded" entry for legacy-row access was removed (nothing is excluded
> because nothing remains undecided), and a revisit trigger was added for the
> scenario this assumption would invalidate (a future initiative importing
> historical rows from a prior deployment). All three ADRs re-linted clean
> after every edit in this note (digests above are current).
| FF-03 | TDD_ONLY | §9 row E1 | `[REQ-06]` | none | `AuthContext.role: RoleType(str, Enum)`, field renamed per `_type` convention pattern (kept as `role` — closed vocabulary already unambiguous in context; see §9 rationale) | Resolved | N/A |
| FF-04 | TDD_ONLY | §9 row E2 | `[REQ-26, REQ-41]` | none | `SlotValidator`'s cursor check rewritten to query the catalogue, not extended alongside the env check | Resolved | N/A |
| FF-05 | TDD_ONLY | §9 row E3 | `[REQ-05]` | none | New `tests/unit/test_auth_middleware.py` scheduled as an explicit early W0 task | Resolved | N/A |
| FF-06 / Q-5 | TDD_ONLY | §9 row E4 | `[REQ-08]` | none | Rename existing catalogue-connection symbols; new Programme entity keeps the PRD's own product term | Resolved | N/A |
| Q-1 (spec) | TDD_ONLY | §9 row E5 | `[REQ-02, REQ-06]` | REQ-02, REQ-06 | Concrete JWT claim shape (§3.1) | Resolved | N/A |
| Q-2 (spec) | TDD_ONLY | §9 row E6 | `[REQ-28]` | REQ-28 | Allowlist retains only health/internal/webhook paths | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: 3
- TDD_ONLY: 6
- DEFERRED_WITH_DEFAULT: 0
- Draft ADR files created: 3 (`adr-014`, `adr-015`, `adr-016`)
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-------------------|--------------------|-------------|------------------------|
| `AuthMiddleware` | expiry, wrong issuer/audience, malformed token, role/tenant claim extraction, unrecognized role string — all with test-double JWTs, no real key material | one boundary: real RS256 key pair round-trip (sign in test, verify in middleware) | JWT login → protected-route happy path; refuse missing/invalid | exact match on claim extraction; exact match on 401/403 reason codes |
| `require_role` / `require_programme_scope` | role mismatch, tenant mismatch, platform_admin-vs-tenant_admin cross-calls — test doubles for `AuthContext` | none (pure dependency logic, no I/O) | cross-role and cross-programme refusal (REQ-30, REQ-31) | exact match on refuse/allow outcome |
| `ProgrammeService.validate_then_create` | bad PAT, bad meta, agent-key-supplied-rejected, idempotent re-seed | one boundary: real meta-checkout clone against a fixture repo | validate-then-create happy path + negative paths | exact match on created/rejected outcome and row counts |
| `PlatformAgentCatalogueService` | unprovisioned runner, blank key, lane-default resolution, caller-override-wins | none | provision + effective-runner resolution at wave start | exact match on resolved runner/model or reject reason |
| `ForgeClientFactory` | Programme PAT missing → named error; two Programmes resolve to two distinct clients with distinct Bearer values | one boundary: real GitHub REST call behind existing `debug_forge_client.py`-style probe (unchanged transport) | unchanged — existing forge probe extended with a second Programme fixture | exact match on which credential was used per call |
| `RunRepository`/`BoardService`/`CheckpointEvidenceService` tenant scoping | cross-tenant filter, platform_admin unfiltered read (no null-`tenant_id` case — column is non-nullable, ADR-016) | one boundary: real Postgres query against fixture rows across two Programmes | REQ-31 cross-programme negative-path script | exact match on row set returned |

**AI-output determinism policy:** not applicable — this initiative does not introduce new AI-generated content; `EffectiveRunner` resolution and credential lookups are deterministic table reads.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|------------------------------|-------------------|----------|
| Missing/invalid/expired/wrong-issuer JWT | `AuthMiddleware` | 401 JSON response, short-circuits before route handler | terminal for that request — caller must re-authenticate |
| Role/tenant scope mismatch | `require_role`/`require_programme_scope` | 403 JSON response with named reason | terminal for that request |
| Programme validate-then-create failure (bad PAT/meta) | `ProgrammeService` | raised `ValidationError`/`UnprocessableEntityError`, mapped to 422 at the route | terminal — no partial row; caller retries with corrected input |
| Effective runner unresolved/unprovisioned | `PlatformAgentCatalogueService` | raised `UnprocessableEntityError`, 422 at wave-start route | terminal — 0 run enqueued |
| Programme PAT missing at forge dispatch | `ForgeClientFactory` | raised named error, propagated to the calling business service | terminal for that operation — should not occur post-validate-then-create; a Should-fix invariant violation if it does |
| Wipe attempted mid-run | wipe service (new, W3) | raised `ConflictError`, 409 at the wipe route | terminal — 0 wipe; caller retries after the run completes |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|--------------------|-------|
| `AuthMiddleware` | INFO (accept) / WARNING (refuse) | `user_id`, `role`, `tenant_id`, `reason` (on refuse) | never logs the raw JWT or its signature |
| `require_role`/`require_programme_scope` | WARNING (refuse) | `user_id`, `role`, `requested_tenant_id`, `bound_tenant_id` | |
| `ProgrammeService` | INFO (create/attach outcome) / WARNING (validation reject) | `programme_id`, `reason` (on reject) | never logs the PAT value |
| `PlatformAgentCatalogueService` | INFO (provision/resolve) / WARNING (reject) | `runner_id`, `programme_id`, `lane`, `reason` (on reject) | never logs the agent key value |
| `ForgeClientFactory` | INFO (client resolved) | `programme_id` | never logs the PAT value |
| `RunRepository`/`BoardService`/`CheckpointEvidenceService` | INFO (scoped read) | `tenant_id`, `row_count` | |

No module in this table introduces a new silent-catch — all failure paths in §6 log at WARNING or ERROR before raising or returning an error response, per `logging-loguru.mdc` and `fail-fast.mdc`.

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|---------------------|-------------------------------|--------------------|------------|
| `RoleType` (enum) | `src/models/role_types.py` | edge (`AuthMiddleware` decode) + repository (user identity read) | append-only member additions; no value renames without a migration note |
| `ProgrammeSchema` (new table) | `src/database/postgres/repository/programme_repository.py` | repository (create/read); business validates PAT/meta before repository write | human-owned Alembic revision at introduction |
| `PlatformAgentCatalogueSchema` (new table) | `src/database/postgres/repository/platform_agent_catalogue_repository.py` | repository; business validates blank-key rejection before write | human-owned Alembic revision at introduction |
| `RunSchema.tenant_id` (new column) | `src/database/postgres/repository/run_repository.py` | repository (set at run creation); business supplies the value from `AuthContext` | human-owned Alembic revision; **non-nullable** — introduced against an already-reset database (REQ-35 cutover, PM-confirmed), no legacy-row compatibility path (ADR-016) |
| `UserIdentitySchema` (new table) | `src/database/postgres/repository/user_identity_repository.py` | repository; business validates credential format before write | human-owned Alembic revision at introduction |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|--------------|------------------------|------------------------|
| E1 (FF-03) | PE | resolved | Should `AuthContext.role` be typed as an enum? | Yes — `RoleType(str, Enum)` per `pydantic-schemas.mdc`. Field name stays `role` (not `role_type`) because `AuthContext` is a single-purpose model where `role` is unambiguous in context, consistent with the MDC's own carve-out ("If the domain word is already unambiguous, a short name is acceptable") | plan | N/A — resolved now | `src/models/auth_models.py:16`; `pydantic-schemas.mdc` |
| E2 (FF-04) | PE | resolved | Should `SlotValidator`'s cursor check be replaced or extended? | Replaced. The env-based `has_api_key()` check for `adapter_id == "cursor"` is deleted and rewritten to query `PlatformAgentCatalogueService`. No dual-path window. | plan (implementation task, not additive) | N/A — resolved now | `src/business_services/slot_validator.py:107-122` |
| E3 (FF-05) | PE | resolved | When does `AuthMiddleware` get dedicated unit coverage? | `tests/unit/test_auth_middleware.py` is an explicit early W0 plan task, not incidental route-test coverage. | plan (W0) | N/A — resolved now | feasibility FF-05 |
| E4 (FF-06/Q-5) | PE | resolved | Which "programme" symbol set is renamed to resolve the three-way naming collision? | The **existing** meta-catalogue-connection code is renamed (`programme_routes.py` → `catalogue_connection_routes.py`; `ProgrammeOnboardingService` → `CatalogueConnectionService`; `TenantProgrammeConnectionSchema` → `MetaCatalogueConnectionSchema`), not the new entity — the new entity keeps the PRD's own product term "Programme" because renaming *that* would be a product-vocabulary change outside PE's authority (see governance.md Ownership rule). ADR-004's title is documentation-only and needs no code change; noted for awareness only. | plan | N/A — resolved now | FF-06; `docs/specification/adr/adr-004-programme-config-authority.md` (title only, no code symbol collision) |
| E5 (Q-1) | PE | resolved | Exact JWT claim schema? | `sub` = user id (UUID string), `role` = `RoleType` value, `tenant_id` = UUID string (present only for `tenant_admin`), standard `iss`/`aud`/`exp`/`iat`. No new claim beyond what `AuthMiddleware` already decodes (`sub`, `tenant_id`, `role`) — `owner_id` legacy claim path is unaffected since no role in this INIT maps to `_OWNER_ROLES`. | plan (W0) | N/A — resolved now | `src/common/auth/middleware.py:99-144` |
| E6 (Q-2) | PE | resolved | Exact `public_paths` allowlist after cutover? | `["/health", "/internal", "/webhooks"]` only — every `Appendix C` prefix (`/api/v1/waves`, `/initiatives`, `/runs`, `/metrics`, `/board`, `/checkpoints`, `/tenants`, and the new Programme-admin routes) is removed from the allowlist at W2. | plan (W2) | N/A — resolved now | `src/app.py:76-87` |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|--------------|------------------------|----------|------------------------|
| PM-1 (spec Q-7) | PM | **resolved** | Direct team notice that this INIT supersedes INIT-GATEFLOW-012 G3 and wipes lab 012/013 tenant rows | no | before W2/W3 cutover | — | impact-map IM-04; spec Q-7 | Resolved interactively this session: PM confirmed a **full greenfield DB reset** (schema/tables, not selective tenant rows) — broader than REQ-35's literal "012/013 lab tenants" wording, since there is no production or backward-compatibility constraint at all. Proceed as-is; no separate notice needed |
| PM-2 | PM | **resolved** | Who may read a run/board/checkpoint row created before the `tenant_id` column exists? | no (was **yes**) | — | — | ADR-016 (original draft); discovered during self-critique | **Resolved as moot**, not answered a particular way: PM confirmed the database is fully reset before this INIT's migrations run, so no `tenant_id IS NULL` row can ever exist. ADR-016 updated — `tenant_id` is non-nullable; the excluded-decision entry was removed since nothing remains undecided |

> **Note on PM-1's answer exceeding REQ-35's literal scope:** REQ-35 says
> "existing 012/013 lab tenants/shared-secret rows are wiped." PM's answer
> here ("nuking db, schema, tables etc... greenfield development... not in
> production") describes a broader operation than that sentence literally
> states. This does not require a spec amendment — REQ-35's product outcome
> (old lab tenants gone, re-onboard via Programme path) is a strict subset of
> what a full reset achieves, so nothing approved is contradicted. It is
> recorded here as operational context for whoever runs the actual reset
> (human-owned, per `database-migrations.mdc` — not a product API call), not
> as a new requirement.

---

## 11. Routed out — domain clarifications (SME)

None this initiative.

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-------------------|-----------------|
| AF-1 | planned-auto-fix | Rename `programme_routes.py`/`ProgrammeOnboardingService`/`TenantProgrammeConnectionSchema` to `catalogue_connection_routes.py`/`CatalogueConnectionService`/`MetaCatalogueConnectionSchema` | `src/api/v1/programme_routes.py`, `src/business_services/programme_onboarding_service.py`, `src/database/postgres/schema/tenant_schema.py` | N/A — planned for implementation plan, not performed in this review |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | PASS |
| Engineering decisions resolved | 9 resolved (3 ADR_REQUIRED Draft, 6 TDD_ONLY), 0 deferred |
| Draft ADR files written | 3 / 3 required |
| Product-boundary integrity (T12) | PASS after correction — the first draft of ADR-016 failed T12's manual gap (2): it invented a legacy-row read-access policy under a real REQ with `changes_user_visible_behavior` left `false`. Corrected by removing the invented policy and routing it as PM-2. Mechanical lint PASS on all 3 ADRs (evidence below) |
| PM questions outstanding | **0** — PM-1 and PM-2 both resolved interactively this session (§9/§10); PM confirmed a full greenfield DB reset, which makes PM-2 moot (no legacy row can exist) rather than answered a particular way |
| Domain questions outstanding | 0 |
| Selected workflow outcome | **`pass`** — both PM items resolved; zero unresolved blocking findings remain. **Process note (resolved):** PM-2 was originally resolved via an interactive chat decision, not a separate `/spec-human-decision` artifact. The incremental `/initiative-feasibility` re-run this TDD previously called for has since completed (revision 2, `pass`, zero unresolved findings) — that gate is now closed, not merely proposed. This confirmation pass of `/spec-technical-review` is the direct continuation of that outcome's `next_candidates`, per the pin |
| Ready for PE review | **YES — and PE has explicitly accepted** (@nikd10x, 2026-08-10, Cursor chat, Draft spec PR #212) |
| **Ready for /spec-implementation-plan** | **YES — TDD `Status: Accepted`; `adr-014`/`adr-015`/`adr-016` all `Status: Accepted`; ADR-002/005/011 flipped to `Status: Superseded` / `superseded_by: adr-014` per their Lifecycle clauses. Exact approved head SHA will be recorded once `/commit-workspace` publishes this package** |

**T12 lint evidence (mechanical, `adr_boundary_lint.py`, current):**

| ADR | Sources checked | Result | Digest |
|-----|-------------------|--------|--------|
| `adr-014-jwt-only-product-edge-trust-zone.md` | 2/2 | PASS | `sha256:d515f3792ed6a83e532469c0a69193914f6fa2aa15449a8d67aa2c8046cc5f67` |
| `adr-015-programme-scoped-forge-credential-resolution.md` | 2/2 | PASS | `sha256:275d49b933484ffe0dc7dc273c5c6ad9a84374802f4b76b4b2ad17e4aee8e377` |
| `adr-016-tenant-scoped-run-board-checkpoint-authorization.md` | 1/1 | PASS | `sha256:e68a20da519bfc1647f917407fe2e891162b8e9964c77ae47e12f1233eef5439` |

A mechanical lint PASS is necessary but not sufficient (per `checks.md`'s own
documented limits) — it caught none of the three issues found in the
self-critique pass (§4 revision note) because all three were semantic
(fabricated trade-off, foreclosed option presented as live, invented
behavior under correctly-cited REQs), not structural or lexical.

These digests are not yet recorded in each ADR's `Lint evidence` field — that
happens at PE acceptance time (Draft → Accepted), re-run against the final
head per each ADR's own Acceptance finalization block, not copied from this
table.

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 — every affected module named with current/change/owner |
| T2 Interface contracts | PASS | §3 — 6 boundary crossings specified with shapes and invariants |
| T3 NEW-ADR dispositions | PASS | 3 ADR_REQUIRED (all Draft files exist), 6 TDD_ONLY (all resolved in §9) |
| T4 Test policy | PASS | §5 — unit/integration/live-verify boundary named per module; "integration" scoped to one named boundary each |
| T5 Error handling | PASS | §6 — every new failure mode has a named propagation path and recovery classification |
| T6 Observability | PASS | §7 — log level + structured fields per module; no silent-catch introduced |
| T7 Data contract ownership | PASS | §8 — owner, validation layer, versioning stated for every new schema |
| T8 Dependency graph | PASS | No new circular imports; `ForgeClientFactory`/`ProgrammeService`/`PlatformAgentCatalogueService` sit in business/infra per ADR-003's existing layer split; import-linter layers unaffected |
| T9 Engineering questions zero | PASS | All 9 PE-lane items in §4/§9 resolved; PM-1 and PM-2 correctly routed out of PE scope (not silently PE-resolved) and now both resolved by PM |
| T10 PE review readiness | PASS | §13 reports `ready_for_pe_review: true` with an explicit routing note about the `spec-human-decision` → `initiative-feasibility` pin edge — accurate, not an overclaim |
| T11 ADR artifact integrity | PASS | 3/3 required files exist under `docs/specification/adr/`, Draft, linked to finding/TDD, all sections present, lint-clean |
| T12 Product-boundary integrity | PASS after correction | First draft of ADR-016 failed the manual gap (2) test in `checks.md` (invented behavior under a real REQ, flags left `false`) — mechanical lint could not and did not catch it. Corrected by removing the invented policy and opening PM-2, which PM then resolved as moot (greenfield reset). ADR-016 updated to `tenant_id` non-nullable; all 3 ADRs + TDD mechanically lint-clean |

**T12 TDD self-scan:** `adr_boundary_lint.py --tdd` was run against this file
(`--source-text` = approved REQ sentences, `--require-sources`) — **PASS, 1
source checked**. The free-text sections above (§1, §5, §9) were additionally
manually re-read using the same strike-the-REQ-id test used for the ADRs.

---

## Forge / PR instructions

> **Outcome is `pass`; the prior routing caveat is now closed.** PM-1 and
> PM-2 were resolved interactively (PM confirmed a full greenfield DB reset
> predates this INIT's migrations, which makes PM-2 moot — no legacy row can
> exist). The incremental `/initiative-feasibility` re-run this TDD previously
> flagged as the formally correct next step has since run (revision 2,
> `pass`) and routed back here — this confirmation pass is that continuation,
> not a shortcut around it.

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. Gate 2 label stays **`spec-pending`**
> until the implementation plan exists. PE accepts architecture by publishing
> **Accepted** TDD/ADR files — not by setting `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-014-spec-gateflow
PR title: "[INIT-GATEFLOW-014] Spec — One identity to call Gateflow, retire shared-secret doors (gateflow)"
PR body:  link meta PRD PR #35; paste §13 Implementation readiness verdict when TDD is ready

PM-1 and PM-2: resolved interactively this session (§9/§10) — no meta PRD PR
comment needed unless PM wants a durable written record of the greenfield-DB-
reset confirmation for future reference.

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @drivestream-lab/prayog-pe-team  ← must give explicit Approve, not just silence

Review deadline: 2026-08-17
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — required Draft files exist; TDD-only/deferred rationales are valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — every required file/link/digest is valid
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*
  [ ] T12 mechanical: scripts/adr_boundary_lint.py run on every ADR (with
      --require-sources and --approved-req-id) AND on the TDD (--tdd) —
      confirm Lint evidence on each Accepted ADR, don't just take PASS on faith
  [ ] T12 manual (lint cannot see these): loose paraphrase in unfamiliar
      vocabulary; invented behavior under a real REQ with flags left false;
      multiple decisions narrated in one un-duplicated Recommendation section

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates ADR metadata Draft → Accepted and TDD Status → Accepted
    (only when changes_user_visible_behavior and spec_amendment_required are false,
    Approval evidence / Approved head are populated, and Lint evidence is recorded —
    not a placeholder)
  Publish acceptance package via Forge to spec branch (label remains spec-pending)
  At the same acceptance moment: update ADR-002, ADR-005, ADR-011 to Status:
    Superseded / superseded_by: ADR-014 per their own Lifecycle clauses

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → /create-board-tickets from merged plan §9
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-014
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/212"
    spec_pr_head: "7f212feb3267628b7448c3e56460c0f727e5236c"
    source_freshness: current
    adr_required_count: 3
    tdd_only_count: 6
    deferred_with_default_count: 0
    draft_adr_files:
      - docs/specification/adr/adr-014-jwt-only-product-edge-trust-zone.md
      - docs/specification/adr/adr-015-programme-scoped-forge-credential-resolution.md
      - docs/specification/adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md
    self_critique_corrections:
      - adr-014: replaced fabricated file-count "options" with the genuine
        verification-mechanism question
      - adr-015: reworded Option A to disclose it is foreclosed by REQ-14,
        not a live choice
      - adr-016: removed an invented legacy-row read-access policy that had
        no approved REQ backing; routed as PM-2, then resolved as moot
    pm_items_resolved_interactively:
      - PM-1
      - PM-2
    routing_note: >
      PM-2 was resolved via interactive chat decision. The incremental
      initiative-feasibility re-run this review previously called for has
      since completed (revision 2, pass, zero unresolved findings) and its
      next_candidates routed back to spec-technical-review. This confirmation
      pass (second invocation) independently re-verified freshness, all 3 ADR
      lints, and the TDD self-scan with zero drift from the prior pass.
    confirmation_pass: true
    pe_acceptance:
      accepted_by: "@nikd10x"
      accepted_at: "2026-08-10"
      evidence: "Explicit PE acceptance via Cursor chat, Draft spec PR #212"
      adrs_accepted:
        - adr-014-jwt-only-product-edge-trust-zone.md
        - adr-015-programme-scoped-forge-credential-resolution.md
        - adr-016-tenant-scoped-run-board-checkpoint-authorization.md
      adrs_superseded:
        - adr-002-edge-trust-model.md
        - adr-005-programme-token-control-plane-mutations.md
        - adr-011-tenant-scoped-bearer-token-trust-zone.md
    ready_for_pe_review: true
    ready_for_plan: true
    pm_open_items: []
    domain_open_items: []
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
```
