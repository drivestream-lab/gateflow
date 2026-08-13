# Feasibility report — INIT-GATEFLOW-017

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| Spec | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` |
| PRD digest | `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-017.md` / `1` |
| Repo scope digest | `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` |
| Approved meta PR head | `601b00e0a74510a6af1c33bc80ca27260995c094` |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/42#pullrequestreview-4927360675), 2026-08-13T13:04:05Z, `impact-map-lgtm` |
| Source freshness | **CURRENT** — spec PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) head `fae37b40f342f56b598ab271465f20fc4775f08e` (this report is local until Forge publish); meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42) merged, head `601b00e0a74510a6af1c33bc80ca27260995c094` unchanged, `impact-map-lgtm` still active; H1/H2/H3/G1 re-verified this pass via live `gh pr view` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-13 |
| Branch | `chore/INIT-GATEFLOW-017-spec-gateflow` — spec PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) (single review surface) |
| Initiative segment | `INIT-GATEFLOW-017` |
| Status | Draft |
| Review deadline | 2026-08-18 |
| Deciders | PM: prayog PM · Domain SME: n/a (no domain-lane items this initiative) |

## Summary

**Buildable in this repo, but not a field-additive change to 014 attach.** Identity
entry, N:N grant, suspend, and “sign in then enter a programme” are new
capabilities on top of live 014 JWT + Programme. Two engineering decisions are
unresolved and block a clean implementation plan: (1) ADR-014’s Accepted claim
shape requires `tenant_admin` JWTs to carry `tenant_id`, which middleware
enforces with 401 — that invariant cannot satisfy zero-programme sign-in
(REQ-18) or many grants (REQ-09/REQ-16) without a successor ADR; (2) 014 wipe
deletes identity rows by `tenant_id`, which would delete a person when one of
several programmes is wiped. Teaching/verify still provision via create+bind
JWT. No blocking PM or domain questions remain (OQ-01/OQ-03 are already in
REQ-21/REQ-05).

**Findings:** 3 total (1 Critical, 1 Should fix, 1 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 0 | 2 (OQ-01 → REQ-21, OQ-03 → REQ-05 — resolved in spec) |
| PE / ADR | 2 | 1 | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 0 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 1 |
| Should fix | 1 |
| Verify / Gap (informational) | 1 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `findings` |
| Rationale | Unresolved blocking PE/ADR items: FF-01 (Critical, NEW-ADR vs ADR-014 claim shape) and FF-02 (Should-fix, wipe deletes identities). Informational FF-03 does not select the outcome. |
| Next (from workflow) | `spec-technical-review` |

Both `pass` and `findings` enter `/spec-technical-review` before plan. Do not
skip technical review. Gate 2 stays `spec-pending`.

### ADR pass (before T2)

| ADR | Domain matched | Status | Action |
|-----|----------------|--------|--------|
| ADR-014 | JWT product edge, claim shape `sub`/`role`/`tenant_id` | Accepted | **read** — revisit trigger fires; claim-shape conflict (FF-01) |
| ADR-016 | Programme-scoped delivery authorization via `runs.tenant_id` | Accepted | **read** — still valid once a session is bound to one programme |
| ADR-001 | Durable Postgres store / migrations | Accepted | **read** — N:N grant persistence is a schema change |
| ADR-015 | Per-programme ForgeClient credentials | Accepted | skipped — outbound git/forge unchanged |
| ADR-012 | Catalogue discovery | Accepted | skipped — CAP-06 keeps onboard |
| ADR-002 / 005 / 011 | Old trust zones | Superseded by ADR-014 | skipped |
| ADR-003, 004, 006–013, 017–018 | Slots, pin, metrics, board | Accepted | skipped — domain not in this spec |

### MDC pass (before T2)

| MDC file | Domain | Read / skipped |
|----------|--------|----------------|
| `architecture.mdc` | JWT verify, `*_service` naming, layered `src/` | read |
| `fail-fast.mdc` | Named refuse, no silent fallback | read |
| `pydantic-schemas.mdc` | Models in `src/models/`, enums | read |
| `http-api-conventions.mdc` | Body-only writes, path ids | read |
| `repository-pattern.mdc` | Business → repo → ORM | read |
| `dependency-injection.mdc` | `@inject`, lifecycle, settings `get_instance()` | read |
| `database-migrations.mdc` | Alembic create-script only | read |
| `testing-verify-flows.mdc` | verify vs unit, no dual journeys | read |
| `logging-loguru.mdc` | Structured kwargs, no secrets in logs | read |
| `strong-typing.mdc` | Pydantic at service boundary | read |
| `python-imports.mdc` | Top-of-file imports | read |
| `infra-services.mdc` | Outbound HTTP / pools | skipped — no new outbound client |
| `python-tooling.mdc` | Black/ruff/pyright | skipped — no toolchain change |
| `spec-driven-development.mdc` | Process | skipped — not an implementation domain |
| `code-guidelines-index.mdc` | Index | skipped |

No F14 wording conflict: the spec stays implementation-neutral on routes,
modules, and JWT encoding (Q-1 / Q-5).

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | 72 files under `tests/unit/` (`testpaths = ["tests/unit"]`). Identity/login covered: `test_auth_identity_service.py`, `test_auth_middleware.py` (including `test_tenant_admin_missing_tenant_id_401`), `test_auth_dependencies.py`, `test_user_identity_repository.py`, `test_programme_service.py` (attach+JWT), `test_programme_wipe_service.py` (`delete_for_tenant`), `test_tenant_routes.py` (`POST …/users`) | `pyproject.toml`; `Makefile` `test` target; file listing this pass |
| Live verify | 42 scripts under `tests/verify/`. Identity path today: `verify_jwt_login`, `verify_programme_onboarding` (attach JWT), `verify_jwt_cutover`, `verify_cross_programme_isolation`, `verify_wipe_cutover`. Helper `tests/_helpers/verify_jwt_auth.py` `provision_programme_tenant_admin` **requires attach `access_token`** | `tests/verify/*.py`; `verify_jwt_auth.py` |
| As-built | 014 W0–W4 human_approved at wave-acceptance (merge pending `wave-signoff`). Spec as-built table matches live code: 1:1 `user_identities.tenant_id`, attach mints JWT, login returns token only, `POST /tenants/{id}/users` still mounted | `docs/specification/as-built/implementation-status.md` 014 matrices; source reads this pass |
| Toolchain | `make check` (black, ruff, pyright, import-linter); `make test` unit only; CI placeholder | `Makefile`; as-built Testing harness |
| Codegraph | `mcp-user-prayog-fleet-cbm` project `data-repos-prayog-gateflow` used for route/symbol discovery; absences not treated as proof — confirmed by direct `src/` reads (graph SHA not bound to this checkout) | `signals.codegraph_provider` |

## Traceability matrix

| Spec REQ | Spec claim | Code evidence | Unit | Verify | Status |
|----------|------------|---------------|------|--------|--------|
| REQ-01, REQ-25, REQ-29 | Enter identity with name, email, password; no programme | No enter-identity API. Only `ProgrammeService.attach_tenant_admin` creates `tenant_admin` (identifier + password + `tenant_id`) | `test_programme_service` attach | `verify_programme_onboarding` | **gap** (new) |
| REQ-02, REQ-03 | Unique email login; refuse non-email | `credential_identifier` is unconstrained `String(512)`; `LoginRequest` documents “e.g. email” but does not validate shape | `test_auth_identity_service` (any identifier) | `verify_jwt_login` | **gap** (changed) |
| REQ-04 | Factory list / find by name or email | No list/search identity route. `GET /api/v1/programmes` is programme list, `platform_admin` only | none | none | **gap** (new) |
| REQ-05 | Enter creates `tenant_admin` only; seeded `platform_admin` not grantable | `ensure_platform_admin` seed path exists; attach of that email would hit `credential_conflict` if role/tenant mismatch — not an explicit “not grantable” refuse | `test_auth_identity_service` seed idempotent | seed script + login | **partial** — seed kept; grant-refuse is new |
| REQ-06–11, REQ-24, REQ-28 | Grant/detach N:N; who-can-enter; idempotent; unknown identity/programme | Attach is create+bind 1:1; `credential_conflict` on second programme; no detach; no membership list | `test_programme_service` | onboarding verify | **gap** + **drift** vs REQ-09 |
| REQ-12–14 | Suspend / unsuspend / set password; kill prior sign-in | No status column; no set-password API; JWT is stateless — middleware does not re-read identity | none | none | **gap** (new) — session invalidation → FF-01 |
| REQ-15 | Detach/suspend do not cancel in-flight waves | Wipe already refuses ACTIVE run (`ProgrammeWipeService`); detach/suspend have no code | `test_programme_wipe_service` mid-run 409 | `verify_wipe_cutover` | **partial** — wipe pattern reusable; detach/suspend new |
| REQ-16–19, REQ-26 | Sign-in once; see grants; enter one; zero-programme signed in; no roster | `LoginResponse` is token only; `mint_user_jwt` always sets `tenant_id` for `tenant_admin`; middleware 401 if `tenant_admin` lacks `tenant_id` | `test_tenant_admin_missing_tenant_id_401` | `verify_jwt_login` | **conflict** — FF-01 |
| REQ-20 | Purge invite / `POST /tenants/{id}/users` | Route still mounted: `tenant_routes.py` `attach_tenant_user` | `test_tenant_routes` mocks attach | none dedicated | **gap** (delete) |
| REQ-21 | Delete 014 create+bind; wipe leftover bind rows | `POST …/programmes/{id}/tenant-admins` live; response includes `access_token` | attach tests assert JWT | `provision_programme_tenant_admin` | **drift** — FF-03 |
| REQ-22–23 | Wrong-actor refuse | `require_role` already splits platform vs tenant on existing routes | `test_auth_dependencies` | `verify_jwt_cutover` | **exists** — extend to new identity/grant routes |
| REQ-27 | Programme onboard/catalogue unchanged | `ProgrammeService.validate_then_create`; catalogue refresh | programme unit tests | `verify_programme_onboarding`, `verify_catalogue_refresh` | **exists** — regression |
| REQ-30 | Password never returned | `UserIdentityReadModel` still includes `password_hash` (internal); attach/login responses omit password today | identity repo tests | inspection | **partial** — keep omit; drop hash from any new list DTO |
| CAP-06 / A-1 | Onboard APIs stay | As REQ-27 | as above | as above | **exists** |
| Wipe vs identity (A-8) | Wiped programme unknown; person remains | `delete_for_tenant` on wipe | `test_wipe_clears_rows_when_idle` | `verify_wipe_cutover` | **drift** — FF-02 |

## ADR traceability (F13)

| Spec REQ | Relevant ADR(s) | Status | Code evidence | Finding |
|----------|-----------------|--------|----------------|---------|
| REQ-09, REQ-16, REQ-18 | ADR-014 (claim shape); NEW-ADR | **conflict** | `src/common/auth/middleware.py` (`tenant_admin token missing tenant_id`); `src/common/auth/dependencies.py` `require_programme_scope`; `src/business_services/auth_identity_service.py` `mint_user_jwt`; `tests/unit/test_auth_middleware.py` `test_tenant_admin_missing_tenant_id_401` | `ALTERNATIVE: remint a tenant_id claim onto the user JWT at programme-select vs authorize programme scope by server-side lookup without a tenant_id claim; revoke live JWTs on suspend or password-set via identity token-version stamp vs denylist vs per-request identity status lookup` |
| REQ-23, REQ-24 (014) kept | ADR-016 | **aligned** once a session is bound to one programme | `require_programme_scope`; `RunSchema.tenant_id` | N/A — delivery scoping unchanged after enter |
| REQ-01, REQ-06, REQ-10 | ADR-001 | **aligned** (new tables/columns via Alembic create script) | `user_identity_schema.py` 1:1 `tenant_id`; no membership table | N/A — schema shape is TDD, not a second ADR, once session model is chosen |
| REQ-15 / wipe | none (014 wipe was 1:1) | missing decision in wipe collaborator only | `programme_wipe_service.py` `delete_for_tenant` | ordinary PE (FF-02) — not NEW-ADR |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F13 | "Programme is authorization, not a second login" | ADR-014 (Accepted) — Option A claim shape `sub`/`tenant_id`/`role`; revisit trigger “finer-grained than role + programme binding” | `ALTERNATIVE: remint a tenant_id claim onto the user JWT at programme-select vs authorize programme scope by server-side lookup without a tenant_id claim; revoke live JWTs on suspend or password-set via identity token-version stamp vs denylist vs per-request identity status lookup` |

F14: no spec wording contradicts MDC. Identity APIs will need Pydantic models in
`src/models/`, `*_service` naming, body-only writes, and Alembic via
`create_postgres_migration.sh` — all implementation-plan notes, not spec defects.

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F13 | Successor ADR required for identity-scoped sign-in + programme authorization + live-JWT revocation. ADR-014 Accepted Option A and current middleware make `tenant_admin` without `tenant_id` a 401, which cannot implement REQ-18 (zero-programme sign-in) or REQ-09/REQ-16 (one identity, many programmes, enter one). Independent implementers would otherwise pick incompatible claim/session designs. | Spec REQ-16/REQ-18/Q-1; ADR-014 revisit + Option A; `middleware.py` lines 105–106; `test_tenant_admin_missing_tenant_id_401`; `mint_user_jwt` optional `tenant_id` only omitted for `platform_admin` |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-02 | F2 / F5 / F10 | `ProgrammeWipeService` deletes all `user_identities` for the programme’s `tenant_id`. Under N:N, that is a delete-identity side effect (PRD non-goal) and would remove a person from other programmes. TDD must change wipe to remove grants for that programme only and leave the person row (spec A-8 default: programme becomes unknown; person remains). | `programme_wipe_service.py` `delete_for_tenant`; `test_programme_wipe_service.py` `test_wipe_clears_rows_when_idle`; spec A-8; PRD Lock 13 vs “delete identity” non-goal |

### Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F3 / F4 / F7 | Live verify and unit tests still treat `POST …/tenant-admins` + `access_token` as the `tenant_admin` provision path. Expected negation when REQ-21 deletes the door; rewrite `provision_programme_tenant_admin` to enter → grant → login (→ enter-programme). Do not duplicate the new HTTP journey in both unit and verify. | `tests/_helpers/verify_jwt_auth.py` `provision_programme_tenant_admin`; `test_programme_service.py` attach; spec REQ-21 / REQ-20 |

## Impact surface

| Area | Likely files/modules | Test touch |
|------|----------------------|------------|
| Identity enter/list/search/suspend/password | New business service + repo methods on `UserIdentityRepository`; models in `src/models/`; routes under `api/` (paths → TDD); DI `BusinessServicesModule` / `_BUSINESS_SERVICE_TYPES` | new unit module; `verify_jwt_login` successor |
| Grant/detach/who-can-enter | New membership persistence (schema + Alembic create script); replace `attach_tenant_admin` | negate attach tests; new grant tests |
| Sign-in / enter-programme | `AuthIdentityService.login` / `mint_user_jwt`; `AuthMiddleware`; `require_programme_scope` (FF-01 ADR) | flip `test_tenant_admin_missing_tenant_id_401`; new enter tests |
| Purge handle-attach | `tenant_routes.py` `attach_tenant_user` | negate `test_tenant_routes` attach |
| Wipe collaborator | `ProgrammeWipeService` stop `delete_for_tenant` (FF-02) | `test_programme_wipe_service` |
| Teaching | `tests/_helpers/verify_jwt_auth.py`, `tests/README.md` | verify rewrite (FF-03) |
| Unchanged | Programme onboard/catalogue, ADR-016 run `tenant_id`, forge PAT path | existing programme/catalogue verify as regression |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | FF-01 ADR choice changes every identity and delivery route’s auth dependency | Resolve in `/spec-technical-review` before plan; do not start waves on 1:1 JWT bind (kill line A-5) |
| R-2 | Lab DB leftover 014 bind rows (OQ-01) | Spec REQ-21: wipe leftover bind rows; no dual model |
| R-3 | `UserIdentityReadModel.password_hash` leaking onto a new list DTO | REQ-30; dedicated list/read models without hash (pydantic-schemas) |
| A-1…A-6 | Spec assumptions from PRD | Confirmed or unchanged this pass |
| A-7 | Historic `POST /tenants/{id}/users` is the invite door | Confirmed (`tenant_routes.py`) |
| A-8 | Wipe stays 014 wipe of the programme | Confirmed for programme/tenant/run delete; **identity collaborator must change** (FF-02) |

## Recommended spec edits

- None required for FF-01 / FF-02 — both are engineering (successor ADR + wipe collaborator). Spec Q-1 already routes session encoding to technical review.
- Optional (non-blocking): cite `POST /api/v1/programmes/{programme_id}/tenant-admins` explicitly in REQ-21 as the 014 door being deleted (as-built name), parallel to REQ-20’s handle-attach path. Auto-fix later; do not mutate the spec in this skill.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| FF-01 | PE | Successor ADR for identity-scoped JWT vs programme bind + live revocation | yes | PE | open | technical review | none — do not implement on 1:1 `tenant_id` claim | ADR-014; middleware 401; REQ-16/18 | pending TDD/ADR |
| FF-02 | PE | Wipe must not delete identity rows under N:N | yes | PE | open | technical review | Remove grants for wiped programme only; person remains | `delete_for_tenant`; A-8 | pending TDD |
| FF-03 | PE | Rewrite provision/verify off attach JWT | no | PE | open | plan / implement waves | Enter → grant → login in the wave that deletes the door | `verify_jwt_auth.py` | pending plan |
| Q-1 | PE | Same as FF-01 (spec already deferred) | no | PE | open | technical review | Product default already in REQ-16 | spec Q-1 | FF-01 |
| Q-2 | PE | Wave split gateflow vs ops | no | PE | open | spec-implementation-plan | Sequential: gateflow enter+grant live, then ops screens | spec Q-2; IM-03 | pending plan |
| Q-5 | PE | Exact HTTP paths / JSON keys | no | PE | open | technical review | CTR-01–04 semantics stay normative | spec Q-5 | pending TDD |
| Q-3 / Q-4 / Q-6 | PM | 016/014 document follow-ons; ops must not ship invite | no | PM | open | later / ops W0 | 017 wins; meta `/update-documents` | spec Q-3, Q-4, Q-6 | prayog-meta |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None.

#### Defer — can proceed with documented assumption

1. OQ-02 / OQ-04 — 016 invite and 014 create+bind PRD document updates after promotion (spec Q-3, Q-4).
2. IM-02 / spec Q-6 — ops must not ship invite; 017 wins.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

1. **FF-01** — `ALTERNATIVE:` remint a `tenant_id` claim onto the user JWT at programme-select vs authorize programme scope by server-side lookup without a `tenant_id` claim; revoke live JWTs on suspend or password-set via identity token-version stamp vs denylist vs per-request identity status lookup.
2. **FF-02** — Wipe collaborator: stop `delete_for_tenant`; remove grants for that programme only.

#### Defer with default

1. **FF-03** — Rewrite `provision_programme_tenant_admin` in the wave that deletes create+bind.
2. **Q-2** — Sequential provider then consumer waves.
3. **Q-5** — Paths/keys in TDD OpenAPI, not the spec.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | none | — | — |

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| AF-1 | REQ-21 as-built door name | Optionally name `POST /api/v1/programmes/{programme_id}/tenant-admins` in REQ-21 on a later spec edit |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Unit/verify/as-built/toolchain inventoried |
| F2 Spec → code map | PASS | Every REQ mapped; gaps and drifts named; FF-02 wipe collaborator |
| F3 Spec → verify map | PASS | No false claim of existing coverage; planned verify + FF-03 helper rewrite |
| F4 Spec → unit map | PASS | Existing auth/attach/wipe tests identified; new modules needed |
| F5 As-built drift | PASS | Spec as-built table matches code; 014 attach still live (expected) |
| F6 Docs drift | PASS | `tests/README.md` is a pointer; AGENTS/ADR index do not contradict; ADR-014 needs successor not a doc lie |
| F7 Overlap risk | PASS | FF-03 notes do not duplicate new journeys in unit and verify |
| F8 CI vs live | PASS | `make test` = unit; live verify human; CI placeholder — unchanged |
| F9 Cross-service | PASS | CTR-01–04 provider in this repo; consumer is gateflow-ops (out of scope) |
| F10 Assumptions | PASS | A-7 confirmed; A-8 identity collaborator flagged as FF-02 |
| F11 Effort drivers | PASS | N:N schema, successor ADR, wipe collaborator, verify rewrite, email/suspend — no waves in spec (Q-2) |
| F12 PM questions | PASS | Zero blocking PM |
| F13 ADR conformance | FAIL (blocking finding) | FF-01 Critical NEW-ADR vs ADR-014 claim shape |
| F14 MDC conformance | PASS | Spec does not prescribe forbidden layering |

**Draft verdict:** FAIL on F13 only — **Check PASS semantics** = zero unresolved *blocking* findings. FF-01 and FF-02 remain blocking PE → stage outcome `findings`, not `pass`.

| Check | Status | Findings |
|-------|--------|----------|
| F1–F14 | FAIL (F13) | FF-01 Critical; FF-02 Should-fix; FF-03 Gap |

**Check PASS** = zero unresolved blocking findings (informational OK).
This run: **not a check-PASS**; workflow outcome `findings` is still a legal
happy-path edge into technical review.

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → none blocking. Deferrals Q-3/Q-4/Q-6 stay on
[prayog-meta#42](https://github.com/drivestream-lab/prayog-meta/pull/42) (merged).

**PE questions** → discuss on Draft spec PR
[#243](https://github.com/drivestream-lab/gateflow/pull/243); run
`/spec-technical-review` next. Do **not** set `spec-lgtm` until the full
package includes the implementation plan.

**Domain clarifications** → none.

**Auto-fixable items** → AF-1 left in report.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-017.md` |
| Target branch | `chore/INIT-GATEFLOW-017-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-017-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered on meta PRD PR (none)
  [x] All blocking Domain clarifications answered (none)
  [ ] Spec updated to reflect answers (N/A — no spec edit required)
  [x] Incremental re-run of /initiative-feasibility on updated spec is clean
      (this is the first pass; outcome findings, not a dirty H1–H3)
  [ ] Proceed: /spec-technical-review (always — pin routes pass and findings here)
  [ ] After spec + feasibility + TDD (if any) + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: `/create-board-tickets` from plan §9 — then /pre-implement → /loop-spec
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-017.md
  blockers:
    - FF-01
    - FF-02
  signals:
    pr_ready: false
    initiative: INIT-GATEFLOW-017
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_pr_head: "fae37b40f342f56b598ab271465f20fc4775f08e"
    source_freshness: current
    findings_total: 3
    pe_blocking: 2
    pm_blocking: 0
    domain_blocking: 0
    new_adr: true
    d_checks: fail-f13
    nonblocking_questions: "FF-03,Q-2,Q-3,Q-4,Q-5,Q-6"
    codegraph_provider: mcp-user-prayog-fleet-cbm
    grounding_depth: deep
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```
