# Technical Design Document — INIT-GATEFLOW-017

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| Spec digest | `sha256:6fcc4e9f18215774676618dd917fe07c4fd3ba67c2a1e82c193173000b7bf1cd` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-017.md` |
| PRD digest | `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-017.md` / `1` |
| Repo scope digest | `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` |
| Approved meta PR head | `601b00e0a74510a6af1c33bc80ca27260995c094` |
| Source freshness | CURRENT — spec PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) head `3a7d4d0e98f720bf41eba8991ece6cabd7cb9576`; meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42) merged at G1 SHA; `spec-pending` / `impact-map-lgtm`; H1–H3 re-verified this pass |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-13 |
| Branch | `chore/INIT-GATEFLOW-017-spec-gateflow` (spec PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-017` |
| Status | Accepted |
| Review deadline | 2026-08-20 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

---

## 1. Problem statement

The edge maps `TENANT_ADMIN` to a single `tenant_id` JWT claim and a single
`user_identities.tenant_id` column (ADR-014 Option A; `AuthMiddleware`,
`mint_user_jwt`, `require_programme_scope`). That 1:1 binding cannot authorize
zero- or many-membership identities, cannot invalidate an already-decoded JWT
after status or password mutation, and causes programme wipe to delete identity
rows (`ProgrammeWipeService.delete_for_tenant`) (REQ-09, REQ-12, REQ-14,
REQ-16, REQ-18). Directory enter/grant/detach APIs do not exist;
`attach_tenant_admin` still mints a programme-bound token (REQ-01, REQ-06,
REQ-21).

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/common/auth/middleware.py` | exists — 401 if `TENANT_ADMIN` lacks `tenant_id` | extend — drop that 401; still decode `sub`/`role`/`session_epoch` | common/auth (edge) |
| `src/common/auth/dependencies.py` | exists — `require_role`, `require_programme_scope` (claim compare) | extend — `require_role` loads identity (suspend + epoch); `require_programme_scope` loads membership | common/auth (edge) |
| `src/models/auth_models.py` | exists — `LoginResponse` token-only; `UserIdentityReadModel` has `tenant_id` + `password_hash` | extend — login/session snapshot DTOs; directory read models **without** `password_hash` | models |
| `src/models/identity_models.py` | does not exist | create — enter/grant/detach/list/search/suspend/password bodies and membership reads | models |
| `src/models/role_types.py` | exists | unchanged | models |
| `src/business_services/auth_identity_service.py` | exists — seed + login + mint with `tenant_id` | extend — mint `session_epoch`; login returns snapshot; no programme claim | business |
| `src/business_services/identity_directory_service.py` | does not exist | create — enter, list/search, suspend/unsuspend, set-password, grant/detach, who-can-enter | business |
| `src/database/postgres/schema/user_identity_schema.py` | exists — `credential_identifier`, `tenant_id`, no name/status/epoch | extend — `display_name`, `status`, `session_epoch`; drop `tenant_id` | database/schema |
| `src/database/postgres/schema/programme_membership_schema.py` | does not exist | create — `(identity_id, programme_id)` unique | database/schema |
| `src/database/postgres/repository/user_identity_repository.py` | exists — `delete_for_tenant` | extend — list/search/update; **remove** `delete_for_tenant` | database/repository |
| `src/database/postgres/repository/programme_membership_repository.py` | does not exist | create | database/repository |
| `src/business_services/programme_service.py` | exists — `attach_tenant_admin` create+bind+JWT | **delete** `attach_tenant_admin` | business |
| `src/api/v1/programme_admin_routes.py` | exists — `POST /programmes/{id}/tenant-admins` | **delete** that route; add grant/detach/list-members under `/programmes/{id}/grants` | api |
| `src/api/v1/identity_routes.py` | does not exist | create — `platform_admin` directory routes | api |
| `src/api/auth/login_routes.py` | exists — token-only login | extend — snapshot on login; `GET /auth/me`; `POST /auth/session/programme` (grant check, no remint) | api |
| `src/api/v1/tenant_routes.py` | exists — `POST /{tenant_id}/users` | **delete** `attach_tenant_user` | api |
| `src/business_services/programme_wipe_service.py` | exists — `delete_for_tenant` | extend — delete memberships for wiped programme; do not delete identity rows | business |
| `src/di/dependency_container.py` / `BusinessServicesModule` | exists | extend — bind `IdentityDirectoryService` | di |
| `tests/_helpers/verify_jwt_auth.py` | exists — attach JWT provision | extend — enter → grant → login (FF-03) | tests |
| Programme onboard/catalogue, ADR-016 `runs.tenant_id`, forge PAT | exists | unchanged | — |

**Boundary diagram (text):**

```
Caller Bearer JWT (sub, role, session_epoch — no programme claim)
  → [AuthMiddleware decode] → AuthContext{user_id, role, tenant_id=None}
      → [require_role + identity row: status + session_epoch]
          → [require_programme_scope + membership row] → delivery routes
          → [IdentityDirectoryService] → UserIdentityRepository
                                       → ProgrammeMembershipRepository
          → [AuthIdentityService.login] → mint JWT + snapshot
          → [ProgrammeWipeService] → delete memberships; keep identity rows
          → [ProgrammeService] onboard/catalogue (unchanged)
```

**Grounding (NON-NEGOTIABLE 11):** re-read `middleware.py` (lines 105–106),
`dependencies.py` `require_programme_scope`, `mint_user_jwt`,
`user_identity_schema.py`, `programme_wipe_service.py` `delete_for_tenant`,
`programme_admin_routes.py` attach, `tenant_routes.py` `attach_tenant_user`,
`test_tenant_admin_missing_tenant_id_401`. No dormant N:N or epoch mechanism
exists. Redis is health/cache only (`RedisService`); not used for sessions.

---

## 3. Public interface contracts

### 3.1 `AuthMiddleware.dispatch`

**Method / entry point:** `AuthMiddleware.dispatch`
**Arguments:**
- `request`: HTTP request — Bearer required off the existing allowlist

**Return:**
- `request.state.auth`: `AuthContext{user_id, role, tenant_id: Optional, owner_id: Optional}` — `tenant_id` **may be null** for `TENANT_ADMIN`
- Error: 401 `UNAUTHORIZED` on missing/malformed/expired/wrong-iss/aud JWT; unrecognized `role`

**Invariants:**
- Does **not** 401 solely because `TENANT_ADMIN` lacks `tenant_id` (supersedes ADR-014 claim clause)
- Does **not** open a DB session (decode/shape only)

### 3.2 `require_role` (session gate)

**Method / entry point:** `require_role(*allowed: RoleType)`
**Arguments:**
- `allowed`: accepted `RoleType` values
- JWT `session_epoch` (integer claim, default 0 if absent on pre-cutover tokens — lab wipe leftover bind rows per REQ-21, so default is unused after cutover)

**Return:**
- `AuthContext` on success
- Error: 403 `FORBIDDEN` `role_forbidden`; 401 `UNAUTHORIZED` `suspended` or `session_epoch_mismatch`

**Invariants:**
- Loads identity by `sub`; missing row is 401
- Suspended status → 401 `suspended` (including reads)
- JWT `session_epoch` must equal row `session_epoch`

### 3.3 `require_programme_scope`

**Method / entry point:** `require_programme_scope(path_tenant_id: UUID)`
**Arguments:**
- `path_tenant_id`: tenant named by the route (existing path convention)

**Return:**
- `AuthContext` on success
- Error: 403 `FORBIDDEN` `not_granted` when no membership links `auth.user_id` to the programme that owns `path_tenant_id`; `wrong_actor` when `platform_admin` hits tenant-only delivery

**Invariants:**
- Does **not** compare `AuthContext.tenant_id` to the path
- Membership SSOT is `programme_memberships`, not `user_identities.tenant_id`
- After success, handlers still pass `path_tenant_id` into ADR-016 run writes

### 3.4 `IdentityDirectoryService` (platform_admin)

**Method / entry point:** `enter_identity(body) -> IdentityRead`
**Arguments:**
- `display_name`: non-empty string
- `email`: unique login identifier; must contain `@` and a domain part
- `password`: non-empty; stored hashed only

**Return:** identity id, name, email, status=`active`, role=`TENANT_ADMIN`, grants=[]
**Error:** 409 `duplicate email`; 422 `not an email` / `missing name` / `missing password`; 403 `wrong actor`

**Method / entry point:** `list_identities(query: Optional[str]) -> list[IdentityRead]`
**Arguments:** `query` optional — case-insensitive name contains **or** case-insensitive exact email
**Return:** matching rows; empty list on no match (not an error); **no** password/hash/PAT
**Error:** 403 `wrong actor`

**Method / entry point:** `suspend_identity` / `unsuspend_identity` / `set_password`
**Return:** updated `IdentityRead` (password never present)
**Invariants:** suspend/password-set increment `session_epoch`; unsuspend does not; grants unchanged on suspend (REQ-24)

**Method / entry point:** `grant(programme_id, identity_id) -> MembershipRead` / `detach(...)` / `list_members(programme_id)` / `list_grants(identity_id)`
**Arguments:** existing identity + onboarded programme
**Return:** membership pair; grant is idempotent
**Error:** 422 `unknown identity` / `unknown programme`; 403 `wrong actor`; grant of seeded `platform_admin` identity → 422 (REQ-05)
**Invariants:** grant does not collect or set password; does not mint JWT (REQ-06, REQ-12)

### 3.5 `AuthIdentityService.login` / session

**Method / entry point:** `login(LoginRequest) -> LoginResponse`
**Arguments:** `credential_identifier` (email) + `password`
**Return:** `access_token`, `token_type`, snapshot `{identity fields, grants[]}` — password/PAT absent
**Error:** 401 invalid credentials; 401 `suspended`; 422 `not an email`

**Method / entry point:** `current_snapshot(user_id) -> SessionSnapshot` (`GET /api/auth/me`)
**Return:** same snapshot shape as login; only the caller’s identity

**Method / entry point:** `assert_programme_grant(user_id, programme_id) -> SessionSnapshot` (`POST /api/auth/session/programme`)
**Arguments:** JSON body `{programme_id}`
**Return:** snapshot confirming that grant
**Error:** 403 `not_granted`
**Invariants:** **does not remint** JWT; **does not** write `tenant_id` onto the token (ADR-019 Option B)

### 3.6 `ProgrammeWipeService.wipe_programme`

**Method / entry point:** `wipe_programme(programme_id) -> ProgrammeWipeResult`
**Change vs 014:** delete `programme_memberships` for that programme; **do not** delete `user_identities` rows; keep existing ACTIVE-run 409
**Invariants:** identity rows remain (zero grants if that was their last membership)

### 3.7 Deleted doors

- `ProgrammeService.attach_tenant_admin` and `POST /api/v1/programmes/{id}/tenant-admins` — gone (REQ-21)
- `POST /api/v1/tenants/{tenant_id}/users` — gone (REQ-20)

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-01 | ADR_REQUIRED | `docs/specification/adr/adr-019-identity-jwt-programme-scope-and-session-epoch.md` | `[REQ-12, REQ-14, REQ-16]` | See those REQ ids | Option B — membership lookup + `session_epoch`; no remint; no Redis denylist | Accepted | `sha256:2fbe1ecdb1a73335982e365dd57bcbff12d4b51e328c95be124cc2efa9e86d25` |
| FF-02 | TDD_ONLY | §9 FF-02 | `[REQ-10, REQ-21]` + wipe non-goal | Delete-identity remains out of product | Wipe deletes memberships only | Resolved | N/A |
| FF-03 | TDD_ONLY | §9 FF-03 | `[REQ-20, REQ-21]` | — | Rewrite `provision_programme_tenant_admin` to enter → grant → login | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: 1
- TDD_ONLY: 2
- DEFERRED_WITH_DEFAULT: 0
- Draft ADR files created: 1
- Missing/broken ADR files: 0

**Constraint table (Accepted ADRs vs this design):**

| ADR | Relation |
|-----|----------|
| ADR-001 | **constrains** — membership + `session_epoch` live in PostgreSQL; Redis denylist rejected |
| ADR-014 | **constrains / partially superseded** — JWT-only edge kept; `TENANT_ADMIN`+`tenant_id` claim clause superseded by ADR-019 |
| ADR-016 | **constrains** — `runs.tenant_id` still set from the authorized path tenant after membership check |
| ADR-003, 004, 006–013, 015, 017, 018 | **independent** |

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| Middleware / `require_role` epoch | Decode + dependency with repo doubles; invert `test_tenant_admin_missing_tenant_id_401` | none | `verify_jwt_login` successor | exact status + `details.reason` |
| Membership scope | `require_programme_scope` with fake membership repo — granted / not_granted / cross-programme | none | `verify_cross_programme_isolation` | exact |
| Directory enter/grant/detach | `IdentityDirectoryService` with repo doubles; duplicate email; unknown ids; platform_admin not grantable | none | new `verify_identity_directory` (or extend onboarding) | exact |
| Wipe | `ProgrammeWipeService` — memberships gone, identity row remains, ACTIVE 409 unchanged | none | `verify_wipe_cutover` | exact |
| Deleted doors | Route 404/405 for attach + tenant users | none | `verify_dead_doors_deleted` / old-door script | exact |
| Provision helper | n/a | n/a | `verify_jwt_auth.provision_*` uses enter→grant→login only | exact |

**AI-output determinism policy (when applicable):**
- N/A — no LLM output on this INIT.

**Integration layer (T4 vocabulary):** no new “whole stack” pytest. The only real-I/O boundary planned is Alembic-applied schema in live verify. Unit tests use doubles for every collaborator.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Duplicate email | `IdentityDirectoryService.enter_identity` | `ConflictError` → API 409 `duplicate email` | terminal |
| Not an email / missing name / missing password | directory service / login | `UnprocessableEntityError` 422 | terminal |
| Unknown identity / unknown programme | grant/detach | `UnprocessableEntityError` 422 | terminal |
| Not granted | `require_programme_scope` / `assert_programme_grant` | `ForbiddenError` 403 `not_granted` | terminal |
| Suspended / epoch mismatch | `require_role` | `UnauthorizedError` 401 | terminal — caller must login after unsuspend / password-set |
| Wrong actor | `require_role` | `ForbiddenError` 403 `wrong actor` | terminal |
| Invalid login credentials | `AuthIdentityService.login` | `UnauthorizedError` 401 | terminal |
| Wipe while ACTIVE run | `ProgrammeWipeService` | `ConflictError` 409 `active_run` (unchanged) | terminal |
| Grant of `platform_admin` identity | directory service | `UnprocessableEntityError` 422 | terminal |

No silent fallbacks. Partial enter/grant is forbidden (single transaction).

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| `IdentityDirectoryService` | INFO on enter/grant/detach/suspend/password-set; WARNING on refuse | `identity_id`, `programme_id`, `reason` | never log password, hash, or PAT |
| `AuthIdentityService` | INFO login success; WARNING login refuse | `identity_id`, `reason` | no credential material |
| `require_role` / `require_programme_scope` | WARNING on 401/403 | `user_id`, `role`, `requested_tenant_id`, `reason` | existing pattern |
| `ProgrammeWipeService` | INFO wipe; WARNING ACTIVE refuse | `programme_id`, `deleted_memberships` (not `deleted_identities`) | |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| `IdentityEnterRequest` / `IdentityRead` / membership DTOs | `src/models/identity_models.py` | API edge `model_validate`; extra=forbid | amend-by-PE |
| `LoginRequest` / `LoginResponse` + snapshot | `src/models/auth_models.py` | API edge | breaking vs 014 token-only body — lab accepted |
| `UserIdentitySchema` | repository maps ↔ Pydantic; JSONB N/A | repository | Alembic via `create_postgres_migration.sh` |
| `ProgrammeMembershipSchema` | repository | repository | Alembic create script |
| `session_epoch` JWT claim | `AuthIdentityService.mint_user_jwt` | middleware decode (int) + `require_role` compare | integer, monotonic |
| Closed vocab `IdentityStatusType` (`active` / `suspended`) | `src/models/` enum `str, Enum` | edge + repo | add members only by spec |

`UserIdentityReadModel.password_hash` stays **internal** (repo/login verify). Directory and snapshot DTOs must not include it (REQ-30).

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-01 | PE | resolved | Where is programme scope authorized, and how is a live JWT invalidated? | ADR-019 Option B: membership lookup + `session_epoch`; no remint; no Redis denylist | plan | none | ADR-019 |
| FF-02 | PE | resolved | Wipe vs identity rows | `wipe_programme` deletes memberships for that programme only; identity rows remain | plan | none | §3.6 |
| FF-03 | PE | resolved | Verify still uses attach JWT | Rewrite `provision_programme_tenant_admin` to enter → grant → login; negate attach unit tests in the same wave that deletes the door | plan | none | `tests/_helpers/verify_jwt_auth.py` |
| Q-5 | PE | resolved | HTTP paths | §3 + §2 route modules: `/api/v1/identities`, `/api/v1/programmes/{id}/grants`, `/api/auth/me`, `/api/auth/session/programme`; login path unchanged | plan | — | this TDD |
| Q-1 | PE | resolved | Session vs 1:1 JWT bind | Same as FF-01 / ADR-019 | plan | — | spec Q-1 |
| Q-2 | PE | deferred | Wave split vs ops | Sequential: gateflow enter+grant live before ops screens (IM-03) | spec-implementation-plan | sequential provider then consumer | spec Q-2 |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| PM-1 | PM | deferred | 016 invite PRD document update | no | later | 017 wins (REQ-20) | spec Q-3 / OQ-02 | prayog-meta `/update-documents` |
| PM-2 | PM | deferred | 014 create+bind PRD document update | no | later | 017 wins (REQ-21) | spec Q-4 / OQ-04 | prayog-meta `/update-documents` |
| PM-3 | PM | deferred | ops must not ship invite | no | ops W0 | 017 wins | spec Q-6 / IM-02 | gateflow-ops spec |

---

## 11. Routed out — domain clarifications (SME)

None.

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | Name 014 attach door in REQ-21 | spec REQ-21 optional cite of `POST /programmes/{id}/tenant-admins` | N/A |
| AF-2 | executed-auto-fix | Feasibility Finding cell substring `the user` inside `the user JWT` tripped `validate_finding_marker` | Same alternative; noun only: `the identity JWT`. Three cells in `Initiative-Feasibility-Report-INIT-GATEFLOW-017.md` | N/A |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | PASS |
| Engineering decisions resolved | 5 resolved, 1 deferred with default (Q-2) |
| Draft ADR files written | 1 / 1 required |
| Product-boundary integrity (T12) | PASS — mechanical lint + context-reset re-read |
| PM questions outstanding | 3 deferred non-blocking |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` |
| Ready for PE review | YES — accepted 2026-08-14 by @nikd10x |
| **Ready for /spec-implementation-plan** | **YES — after `/commit-workspace` publishes Accepted files to PR #243** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | Existing vs new named; grounding cites files |
| T2 Interface contracts | PASS | §3.1–3.7 shapes, errors, invariants |
| T3 NEW-ADR dispositions | PASS | FF-01 → ADR-019; FF-02/FF-03 TDD_ONLY |
| T4 Test policy | PASS | unit vs live verify; integration = none extra |
| T5 Error handling | PASS | named reasons aligned to spec vocabulary |
| T6 Observability | PASS | structured fields; no secrets |
| T7 Data contract ownership | PASS | models + Alembic create script |
| T8 Dependency graph | PASS | api → business → repo → schema; middleware stays decode-only |
| T9 Engineering questions zero | PASS | FF-01–03 and Q-1/Q-5 resolved; Q-2 deferred with default |
| T10 PE review readiness | PASS | ADR-019 + TDD Accepted by @nikd10x 2026-08-14; `ready_for_plan: true` after `/commit-workspace` |
| T11 ADR artifact integrity | PASS | ADR-019 Accepted; lint `adr_boundary_lint.py 4/4, PASS, sha256:2fbe1ecdb1a73335982e365dd57bcbff12d4b51e328c95be124cc2efa9e86d25` |
| T12 Product-boundary integrity | PASS | ADR `--strict` 6/6 PASS; TDD `--tdd` 2 sources PASS; independent re-read (context-reset after subagent abort): REQ ids only, one Option B, flags false |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet. CODEOWNERS may request PE review on `Technical-Review-*`.

```
Branch:   chore/INIT-GATEFLOW-017-spec-gateflow
PR title: "[INIT-GATEFLOW-017] Spec — One human, many programmes, one login (gateflow)"
PR body:  link meta PRD PR #42; paste §13 Implementation readiness verdict when TDD is ready

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @drivestream-lab/prayog-pe-team  ← must give explicit Approve, not just silence

Review deadline: 2026-08-20
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — required Draft files exist; TDD-only/deferred rationales are valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — every required file/link/digest is valid
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*
  [ ] T12 mechanical: `scripts/adr_boundary_lint.py` run on every ADR (with
      --require-sources and --approved-req-id) AND on the TDD (--tdd) —
      confirm `Lint evidence` on each Accepted ADR, don't just take PASS on faith
  [ ] T12 manual (lint cannot see these — see checks.md "three gaps"):
      loose paraphrase in unfamiliar vocabulary; invented behavior under a
      real REQ with flags left false; multiple decisions narrated in one
      un-duplicated Recommendation section

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates ADR metadata Draft → Accepted and TDD Status → Accepted
    (only when changes_user_visible_behavior and spec_amendment_required are false,
    Approval evidence / Approved head are populated, and Lint evidence is recorded —
    not a placeholder)
  Publish acceptance package via Forge to spec branch (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → `/create-board-tickets` from merged plan §9
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-017.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_pr_head: "3a7d4d0e98f720bf41eba8991ece6cabd7cb9576"
    source_freshness: current
    new_adr: true
    adr_required_count: 1
    tdd_only_count: 2
    deferred_with_default_count: 0
    accepted_adr_files:
      - docs/specification/adr/adr-019-identity-jwt-programme-scope-and-session-epoch.md
    accepted_adr_lint_evidence:
      - "adr_boundary_lint.py 4/4, PASS, sha256:2fbe1ecdb1a73335982e365dd57bcbff12d4b51e328c95be124cc2efa9e86d25"
    pe_acceptance:
      accepted_by: "@nikd10x"
      accepted_at: "2026-08-14"
      evidence: "Explicit PE acceptance via Cursor chat, Draft spec PR #243"
      adrs_accepted:
        - adr-019-identity-jwt-programme-scope-and-session-epoch.md
    ready_for_pe_review: true
    ready_for_plan: true
    pm_open_items:
      - PM-1
      - PM-2
      - PM-3
    domain_open_items: []
    codegraph_provider: degraded-none
    grounding_depth: deep
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```
