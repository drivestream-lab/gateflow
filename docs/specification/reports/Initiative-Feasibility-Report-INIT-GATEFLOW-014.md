# Feasibility report — INIT-GATEFLOW-014

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| PRD digest | `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-014.md` / `1` |
| Repo scope digest | `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Approved meta PR head | `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7` |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/35#pullrequestreview-4895934562), 2026-08-10T10:44:21Z, `impact-map-lgtm` |
| Source freshness | **CURRENT** — spec PR #212 head `7f212feb3267628b7448c3e56460c0f727e5236c` unchanged since publish; meta PR #35 head `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7` unchanged, `impact-map-lgtm` still active; H1/H2/H3/G1 independently re-verified this incremental pass via live `gh pr view` on both PRs |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-10 (incremental re-run — revision 2) |
| Branch | `chore/INIT-GATEFLOW-014-spec-gateflow` — spec PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) (single review surface) |
| Initiative segment | `INIT-GATEFLOW-014` |
| Status | Draft |
| Review deadline | 2026-08-13 |
| Deciders | PM: prayog PM · Domain SME: n/a (no domain-lane items this initiative) |

> **Incremental re-run context:** this is a revision, not a fresh report.
> Impact-map revision handling = `continue` (H1–H3/G1 unchanged since
> revision 1). All `FF-*` ids are preserved from the original pass per the
> incremental-revalidation convention; statuses below reflect what has
> changed since, not a renumbering. Trigger: `/spec-technical-review`
> produced a `pass` after resolving all findings from revision 1 via three
> Draft ADRs, discovering and then resolving one new blocking PM item
> (PM-2) via an interactive human decision. Per the pin,
> `spec-human-decision`'s `pass` edge routes here before re-entering the
> technical-review lane — this run is that gate check, not a request to
> redo the analysis from zero.

## Summary

**Revision 1 finding: buildable, but not a pure auth-dependency swap** — two
Critical ADR conflicts (FF-01, FF-02) blocked clean implementation.

**Revision 2 (this pass): both Critical findings are now addressed, not
merely deferred.** `/spec-technical-review` produced three Draft ADRs:
`adr-014` (supersedes ADR-002/005/011, resolves FF-01), `adr-015`
(`ForgeClientFactory` per-programme credential resolution, resolves FF-02),
and `adr-016` (tenant-scoped run/board/checkpoint authorization, resolves the
Q-4 data-model gap this report's original traceability matrix flagged as
"critical drift"). All three passed mechanical `adr_boundary_lint.py`
re-verification independently in this pass (not taken on faith from the TDD).
The five Should-fix/Gap findings (FF-03…FF-07) are resolved as `TDD_ONLY`
engineering decisions in the same TDD's §9. One new blocking item (**PM-2**
— legacy-row read-access policy) was discovered *during* ADR-016 drafting
(a genuine product-boundary gap the original feasibility pass could not have
found, since it only surfaces once the data-model decision is made) and has
since been resolved by PM: this is a **greenfield, pre-production initiative
with a full database reset**, so no legacy row can exist — PM-2 is moot, not
answered a particular way. **Zero unresolved blocking findings remain.**

**Findings:** 7 total (0 Critical unresolved / 2 addressed via Draft ADR,
5 resolved) — see Check summary for current F13 status.

### Derived counts (lane × severity) — revision 2

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 0 | 2 (PM-1, PM-2 — resolved interactively this session) |
| PE / ADR | 0 | 0 | 7 (FF-01…FF-07 — 3 via Draft ADR pending PE Accept, 4 via TDD §9 `TDD_ONLY`) |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 0 | 1 (AF-1, planned — programme-connection naming rename, tracked for implementation plan) |

| Severity | Unresolved count | Addressed-pending-acceptance count |
|----------|------------------|--------------------------------------|
| Critical | **0** | 2 (FF-01 → Draft `adr-014`; FF-02 → Draft `adr-015`) |
| Should fix | **0** | 3 (FF-03, FF-04, FF-05 → TDD §9 `TDD_ONLY`) |
| Verify / Gap (informational) | 0 | 2 (FF-06, FF-07 → folded into TDD §9 / ADR-015 Options) |

### Selected workflow outcome — revision 2

| Field | Value |
|-------|-------|
| Outcome | `pass` |
| Rationale | Zero unresolved blocking findings. All 7 PE-lane findings from revision 1 have a disposition (3 `ADR_REQUIRED` Draft files, 4 `TDD_ONLY` resolutions) independently re-verified this pass (fresh `adr_boundary_lint.py` runs, not trusted from the TDD's own claim). The one new blocking item discovered mid-review (PM-2) is resolved. Draft (not yet Accepted) ADR status is *not* a feasibility-level blocker — PE acceptance is a distinct human-checkpoint gate (`technical-review-approval`) downstream of this stage, per the pin. |
| Next (from workflow) | `spec-technical-review` |

This re-enters `/spec-technical-review` per the pin's literal edge for
`initiative-feasibility: pass`. In practice the substantive engineering work
is already done (this incremental pass found no new gap requiring fresh TDD
content) — re-running `/spec-technical-review` should be a confirmation pass,
not a rewrite, unless it independently finds something this feasibility pass
missed.

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | 60 files under `tests/unit/`; **zero** dedicated `AuthMiddleware` / JWT-behavior test file exists — `conftest.py` only sets `JWT_SECRET_KEY`/`JWT_ALGORITHM` env vars to satisfy settings-singleton startup, not middleware behavior | `tests/unit/` listing; `tests/unit/conftest.py:19-30` |
| Live verify | 31 scripts under `tests/verify/`; 12+ source `PROGRAMME_SERVICE_TOKEN` / tenant bearer from `.env`/`tests/config.yaml` today (`verify_wave_start`, `verify_board`, `verify_tenant_registry`, `verify_repo_selection`, `verify_checkpoint_status`, etc.) | `tests/README.md:38-71` |
| As-built | `implementation-status.md` accurately reflects the current (pre-014) auth doors as live state — matches this spec's own As-built baseline table exactly; no drift between as-built doc and actual code found | `docs/specification/as-built/implementation-status.md`; direct source reads this session |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01–07 / W0 | JWT-only product edge; dormant middleware activated | `src/common/auth/middleware.py`, `src/app.py:76-87` (dormant), `src/models/auth_models.py` (`AuthContext`) | none dedicated | none | gap (expected — new capability) |
| REQ-06 / W0 | JWT identifies role; `tenant_admin` bound to Programme | `AuthContext.role: str` (untyped) | none | none | **partial** — field exists but not a closed-vocabulary enum (FF-03) |
| REQ-08–14 / W1 | Programme entity, validate-then-create | No `Programme` schema/repository/service exists; `TenantSchema` is the only aggregate today | none | none | gap (expected — new entity) |
| REQ-19–22, 40–42 / W1 | Platform DB agent catalogue + lane defaults | No catalogue table; `CursorAgentSettings` (env) is the only credential source; `SlotValidator._check_adapter` hardcodes `CursorAgentSettings.has_api_key()` for the `cursor` adapter id | `test_cursor_agent_settings.py`, `test_slot_validator.py` (env-based only) | none | gap + **should-fix** (FF-04) — existing tests assert env-based behavior that REQ-41 explicitly forbids as the *sole* authorization path |
| REQ-23–24 / W2 | `tenant_admin` JWT authorizes repo lifecycle + control-plane for its programme | `WaveStartTargetingFields` has no tenant/programme field (`src/models/wave_start_models.py:23-46`); `RunSchema`/board tickets/checkpoint records carry no programme identifier (`run_store_schema.py`) | `test_wave_start.py`, `test_run_orchestrator.py` (no tenant-scoping cases) | `verify_wave_start.py` (no tenant-scoping cases) | gap — confirms spec Q-4 |
| REQ-25 / W2 | Outbound forge/git uses that programme's stored GitHub credential | `ForgeClient` is a DI singleton (`src/infra_services/forge_client.py:55-79`); `AppInstallationTokenProvider._discover_installation_id` **raises if App installation count != 1** (`github_token_provider.py:101-126`) | `test_forge_client.py`, `test_github_token_provider.py` (single-installation assumption baked into fixtures) | `tests/debug/debug_forge_client.py` (single-credential probe) | **critical drift** — see FF-02 |
| REQ-26, REQ-41 / W2 | Agent dispatch loads credential only from DB catalogue; env `CURSOR_API_KEY` never authorizes | `CursorAgentRunner.run_skill` calls `self._settings.has_api_key()` directly (`cursor_agent_runner.py:142-158`) | `test_cursor_agent_runner.py` (env-based) | none | gap (expected) |
| REQ-32–33 / W2 | Refuse programme token / tenant bearer once JWT edge is live | `verify_programme_service_token` / `verify_tenant_bearer_token` are the **only** auth deps on 7 route files today | `test_programme_token_api.py`, `test_tenant_token.py` (assert current accept behavior — will need negation) | `verify_wave_start.py` et al. (assert current accept behavior) | **critical drift** — see FF-01; existing unit tests currently assert the exact behavior REQ-32/33 requires reversed |
| REQ-34 / W3 | Open tenant register removed | `register_tenant` route has no auth dependency (`tenant_routes.py:23-29`) | `test_tenant_routes.py` (asserts current open-register success) | `verify_tenant_registry.py` | gap — test will need negation, not just extension |
| REQ-35, REQ-46 / W3 | Wipe 012/013 lab tenants; reject wipe mid-run | No wipe script/endpoint exists | none | none | gap (expected — new capability) |
| REQ-36–38 / W4 | Verify/teaching surfaces prove JWT + refuse old doors | 12+ scripts teach old doors today (`tests/README.md`) | n/a | 31 existing scripts, 0 rewritten yet | gap (expected — last wave) |

## ADR traceability (F13) — revision 2 (current dispositions)

| Spec REQ / wave | Relevant ADR(s) | Status (rev. 1 → rev. 2) | Finding / disposition |
|-----------------|-----------------|---------------------------|------------------------|
| REQ-32, REQ-33, REQ-04 / W2 | ADR-002, ADR-005, ADR-011 | **conflict → addressed (Draft)** | `docs/specification/adr/adr-014-jwt-only-product-edge-trust-zone.md` — `ADR_REQUIRED`, `Status: Draft`, `supersedes: ADR-002, ADR-005, ADR-011`. Re-verified this pass: `adr_boundary_lint.py --strict` PASS (2/2 sources). Not yet `Accepted` — PE sign-off is the downstream `technical-review-approval` human-checkpoint, not a feasibility gate |
| REQ-25 / W2 | ADR-003 | **conflict → addressed (Draft)** | `docs/specification/adr/adr-015-programme-scoped-forge-credential-resolution.md` — `ADR_REQUIRED`, `Status: Draft`, `supersedes: ADR-003 (forge-credential clause only)`. Re-verified this pass: PASS (2/2 sources) |
| REQ-23, REQ-24, REQ-31 / W2 | none pre-existing (new decision) | **gap (spec Q-4) → addressed (Draft)** | `docs/specification/adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md` — `ADR_REQUIRED`, `Status: Draft`. Originally drafted with a nullable `tenant_id` for legacy-row compatibility; **corrected twice** during technical review's own self-critique (removed an invented, unapproved legacy-row read-access policy — see PM-2 below) and again after PM confirmed a full greenfield DB reset — `tenant_id` is now **non-nullable**. Re-verified this pass: PASS (1/1 source) |

## Governance findings (F13–F14) — revision 2 status

| ID | Check | Spec quote | Governing doc | Rev. 1 finding | Rev. 2 status |
|----|-------|------------|---------------|-----------------|----------------|
| FF-01 | F13 | "When the JWT product edge is live, presenting the global programme service token is refused (no dual-auth window)" | ADR-002, ADR-005, ADR-011 | `ALTERNATIVE: one new ADR superseding ADR-002/005/011 together, vs. three separate superseding ADRs, vs. in-place amendment` | **Resolved** — `adr-014` Draft, `ADR_REQUIRED`, chose the single-supersession option |
| FF-02 | F13 | "Outbound forge/git for a programme uses that programme's stored GitHub credential — never the caller JWT" | ADR-003 | `ALTERNATIVE: per-programme GitHub App installation vs. per-programme PAT vs. per-call token-injection layer` | **Resolved** — `adr-015` Draft, `ADR_REQUIRED`, chose `ForgeClientFactory` (structural resolver, Option C) |
| FF-03 | F14 | "JWT identifies user and role; `tenant_admin` is bound to its Programme" | `pydantic-schemas.mdc` Domain enums | `AuthContext.role` is `str`, not `RoleType(str, Enum)` | **Resolved** — TDD §9 row E1: `RoleType(str, Enum)`, field name stays `role` (MDC's own unambiguous-context carve-out) |
| FF-04 | F14 | "Twin/initiative start loads agent credentials only from the platform DB catalogue" | `dependency-injection.mdc` `is_configured()` anti-pattern / ADR-006 | `SlotValidator`'s env-based cursor check is the anti-pattern named | **Resolved** — TDD §9 row E2: rewritten (not additive) to query the catalogue |
| FF-05 | F14 (via F4) | "Missing, malformed, expired, or wrong-issuer/audience JWTs are refused" | `testing-verify-flows.mdc` | Zero dedicated `AuthMiddleware` unit coverage | **Resolved** — TDD §9 row E3: `test_auth_middleware.py` scheduled as explicit early W0 plan task |
| FF-06 | F13/F14 (naming) | "New **Programme** entity holds per-programme GitHub PAT..." | ADR-004 title collision | Three-way "programme" naming collision | **Resolved** — TDD §9 row E4: rename the *existing* catalogue-connection code; new entity keeps the PRD's own term |
| FF-07 | F14 (informational) | "Outbound forge/git for a programme uses that programme's stored GitHub credential" | `infra-services.mdc` `PostgresSessionFactory` Protocol precedent | Candidate pattern for FF-02 | **Folded in** — cited directly in `adr-015`'s Options considered (Option C) |

### New item discovered mid-review: PM-2 (not present in revision 1)

Technical review's own self-critique of `adr-016`'s first draft found the
ADR had invented a legacy-row read-access policy ("`tenant_id IS NULL` rows
visible only through `platform_admin`-scoped reads") with **no approved
`REQ-*` backing it** — a live product-boundary violation this feasibility
pass could not have found at revision 1, since the gap only exists once the
data-model decision itself is drafted. This was correctly routed as a new
blocking PM item (PM-2), not silently engineering-decided. PM has since
confirmed this is a greenfield, pre-production initiative with a full
database reset — no legacy row can ever exist, so PM-2 is resolved as
**moot**, not answered a specific way. `adr-016` was updated accordingly
(`tenant_id` non-nullable). This is recorded here as a demonstration that the
self-critique discipline caught something a lint-only check would have
missed — not as a new feasibility finding requiring its own `FF-*` id, since
it was discovered and resolved entirely within the technical-review stage.

## Findings by severity — revision 2 (all resolved or addressed)

### Critical (revision 1) → Addressed, pending PE acceptance

| ID | Check | Rev. 1 finding | Rev. 2 disposition | Evidence |
|----|-------|-----------------|----------------------|----------|
| FF-01 | F13 | REQ-32/33 directly contradicts the currently-Accepted ADR-002/005/011 zone table | `adr-014-jwt-only-product-edge-trust-zone.md` — Draft, `ADR_REQUIRED`, `supersedes: ADR-002, ADR-005, ADR-011` | Re-verified this pass: `adr_boundary_lint.py --strict` PASS |
| FF-02 | F13 | `AppInstallationTokenProvider` hard-fails on non-single App installation; structurally incompatible with per-programme credential requirement | `adr-015-programme-scoped-forge-credential-resolution.md` — Draft, `ADR_REQUIRED`, `ForgeClientFactory` per-programme resolver | Re-verified this pass: PASS |

### Should fix (revision 1) → Resolved

| ID | Check | Rev. 1 finding | Rev. 2 disposition | Evidence |
|----|-------|-----------------|----------------------|----------|
| FF-03 | F14 | `AuthContext.role` untyped `str` | TDD §9 row E1 — `RoleType(str, Enum)` | `Technical-Review-INIT-GATEFLOW-014.md` §9 |
| FF-04 | F14 | `SlotValidator` cursor check is env-based `is_configured()` anti-pattern | TDD §9 row E2 — rewritten to query catalogue, not extended | `Technical-Review-INIT-GATEFLOW-014.md` §9 |
| FF-05 | F4 | Zero `AuthMiddleware` unit coverage | TDD §9 row E3 — explicit early W0 plan task | `Technical-Review-INIT-GATEFLOW-014.md` §9 |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 — JWT edge | `src/common/auth/middleware.py`, `src/models/auth_models.py` (role enum, FF-03), `src/app.py` (`public_paths` shrink), new seed script, new login route + service | new `test_auth_middleware.py`, `test_jwt_settings.py`; new `verify_jwt_login.py`-class script |
| W1 — Programme entity + catalogue | New `src/database/postgres/schema/programme_schema.py` (or resolved name per Q-5), `programme_repository.py`, `programme_service.py`; new `platform_agent_catalogue_schema.py` + repo/service; `programme_routes.py` naming collision to resolve (Q-5) | new unit suites for onboarding validate-then-create, catalogue provision, lane-default resolution |
| W2 — Cutover + refuse | All 7 route files currently importing `verify_programme_service_token`/`verify_tenant_bearer_token` (`waves_routes.py`, `runs_routes.py`, `board_routes.py`, `checkpoints_routes.py`, `initiatives_routes.py`, `metrics_routes.py`, `forge_routes.py`, `tenant_routes.py`, `programme_routes.py`); `ForgeClient`/`github_token_provider.py` (FF-02); `run_store_schema.py`/board/checkpoint schema (Q-4 scoping); `SlotValidator` (FF-04) | rewrite of `test_programme_token_api.py`, `test_tenant_token.py`, `test_tenant_routes.py` (negate current-accept assertions, don't just extend); new cross-programme isolation test suite |
| W3 — Delete + wipe | Delete `programme_token.py`, `tenant_token.py`; new wipe script/endpoint with in-flight-run guard | new wipe unit tests (idempotency, in-flight rejection) |
| W4 — Prove + rewrite | 12+ files under `tests/verify/`; `tests/README.md` | new negative-path verify scripts per REQ-37 |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | FF-01/FF-02 NEW-ADR drafting could reveal a broader redesign than "swap the dependency" (e.g. `ForgeClient` architecture) — effort for W2 may be underestimated in the implementation plan if drafted before technical review resolves FF-02 | Sequence: resolve FF-01/FF-02 at `/spec-technical-review` before `/spec-implementation-plan` sizes W2 |
| R-2 | Existing unit tests (`test_programme_token_api.py`, `test_tenant_token.py`, `test_tenant_routes.py`) currently assert the *opposite* of REQ-32/33/34 — a plan that treats these as "add coverage" rather than "flip assertions" will silently leave contradictory green tests in the suite | Implementation plan should explicitly enumerate these three files as **rewrite**, not **extend** |
| R-3 | Q-4 (tenant/programme scoping schema gap) touches `RunSchema`/board/checkpoint — a live-data migration decision (backfill vs. forward-only) is not yet discussed anywhere | Raise as an explicit technical-review question alongside Q-4, not assumed away |

## Recommended spec edits

- Elevate the ADR-003 single-App-installation conflict (FF-02) into the spec's Q-3/Q-6 explicitly — the spec currently frames Q-3/Q-6 around the `ForgeClient` *singleton* pattern generally; the sharper, code-verified fact is that production forge auth **cannot presently support more than one GitHub App installation**, which is a stronger and more concrete blocker than "singleton" framing alone.
- Add FF-03 (role field typing) as an explicit acceptance note under REQ-06 so the implementation plan doesn't treat it as a drive-by refactor outside REQ scope.
- Consider folding FF-06's three-way "programme" naming collision (not just two) into Q-5's resolution scope.

---

## Open items by lane — revision 2 (all resolved)

| ID | Lane | Question / item | Blocking | Owner | Status | Resolution |
|----|------|-----------------|----------|-------|--------|------------|
| FF-01 | PE | Which new ADR(s) supersede ADR-002/005/011's trust-zone model | ~~yes~~ **no** | PE | **resolved** | `adr-014` Draft — single supersession record |
| FF-02 | PE | How per-programme forge/git credentials coexist with ADR-003's single-App-installation path | ~~yes~~ **no** | PE | **resolved** | `adr-015` Draft — `ForgeClientFactory` |
| FF-03 | PE | Type `AuthContext.role` as an enum | no | PE | **resolved** | TDD §9 row E1 |
| FF-04 | PE | Replace `SlotValidator`'s env-based check as a rewrite, not addition | no | PE | **resolved** | TDD §9 row E2 |
| FF-05 | PE | Schedule `test_auth_middleware.py` explicitly | no | PE | **resolved** | TDD §9 row E3 |
| FF-06 | PE/PM | Three-way "programme" naming collision | no | PE/PM | **resolved** | TDD §9 row E4 |
| FF-07 | PE | `Protocol`-based structural typing candidate for FF-02 | no | PE | **resolved** | Folded into `adr-015` Options |
| PM-2 (new, TR-discovered) | PM | Legacy-row read-access policy | was **yes**, now **no** | PM | **resolved (moot)** | Greenfield full DB reset confirmed — no legacy row can exist; `adr-016` updated to non-nullable `tenant_id` |

Zero open items remain in any lane.

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None. (PM-2 was blocking as of the technical-review pass; resolved
interactively — see Open items by lane.)

#### Resolved

1. Spec Q-7 — proceed as-is; PM additionally confirmed a full greenfield DB
   reset (broader than REQ-35's literal "012/013 lab tenants" wording, but a
   strict superset of that outcome — no spec amendment needed).
2. PM-2 — moot; no legacy row can exist under a full pre-INIT database reset.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

All resolved. See Governance findings and Open items by lane above — 3
`ADR_REQUIRED` Draft files (`adr-014`, `adr-015`, `adr-016`) and 4 `TDD_ONLY`
resolutions (TDD §9 rows E1–E4), independently re-verified this pass.

### Domain clarifications (business source-of-truth)

None this initiative.

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix | Status |
|---|------|-----|--------|
| AF-1 | Rename `programme_routes.py`/`ProgrammeOnboardingService`/`TenantProgrammeConnectionSchema` to disambiguate from the new Programme entity | `catalogue_connection_routes.py`/`CatalogueConnectionService`/`MetaCatalogueConnectionSchema` | `planned-auto-fix` (TDD §12) — not performed in this or the technical-review skill; scheduled for the implementation plan |

---

## Check summary — revision 2

| Check | Rev. 1 | Rev. 2 | Findings |
|-------|--------|--------|----------|
| F1 Baseline snapshot | PASS | PASS | FF-05 now resolved (TDD §9 E3) |
| F2 Spec → code map | PASS | PASS | Gaps still expected (no code written yet — spec/design phase) |
| F3 Spec → verify map | PASS | PASS | No named verify artifacts yet — expected, W4 scope |
| F4 Spec → unit map | PASS | PASS | R-2 risk (existing tests assert pre-cutover behavior) still stands as a plan-quality note, not a blocker |
| F5 As-built drift | PASS | PASS | No drift |
| F6 Docs drift | PASS | PASS | No drift |
| F7 Overlap risk | PASS | PASS | No change |
| F8 CI vs live boundary | PASS | PASS | No change |
| F9 Cross-service touch | PASS | PASS | No change |
| F10 Assumptions | PASS | PASS | A-6 now validated by `adr-015`'s actual Option C choice |
| F11 Effort drivers | PASS | PASS | W2 remains highest-complexity; now has concrete architectural direction (3 Draft ADRs) reducing estimation risk |
| F12 PM questions | PASS | PASS | PM-2 discovered and resolved this cycle; zero remain |
| F13 ADR conformance | **FAIL** (2 Critical) | **PASS** | FF-01/FF-02 addressed via Draft `adr-014`/`adr-015`, independently re-verified lint-clean this pass; Q-4 gap also addressed via Draft `adr-016` |
| F14 MDC conformance | PASS (informational) | PASS | FF-03/04/05/06/07 all resolved (TDD §9 / `adr-015` Options) |

**Check PASS** = zero unresolved blocking findings. F13 now PASSes because
the two Critical ADR conflicts have Draft dispositions (not because the
underlying architectural work was skipped) — `Accepted` status is a separate,
downstream PE gate at `technical-review-approval`.

---

## Next steps

Persist this report locally alongside the spec draft, TDD, and 3 Draft ADRs.
Fill `handoff.forge` for `/commit-workspace` (or Gateflow ForgeClient) onto
the Draft spec PR — **do not** commit, push, open PRs, or apply labels inside
this skill.

**PM questions** → none open (PM-1, PM-2 both resolved interactively this
session — no meta PRD PR comment required unless PM wants a durable written
record).

**PE questions** → none open. All 7 revision-1 findings have a disposition;
independently re-verified lint-clean this pass. Recommend `/spec-technical-review`
run once more as a **confirmation** pass (pin's literal edge for `pass`) —
not expected to surface new content, since this incremental feasibility pass
found nothing beyond what the existing TDD/ADRs already resolve.

**Domain clarifications** → none this initiative.

**Auto-fixable items** → AF-1 (naming rename) tracked, not yet performed —
scheduled for `/spec-implementation-plan`.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-014.md` |
| Target branch | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) — publish this report **together with** the TDD and 3 Draft ADRs, all currently local-only |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-014-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT (re-verified independently this pass)
  [x] All blocking PM questions answered (PM-1, PM-2 — resolved interactively)
  [x] All blocking Domain clarifications answered (none exist)
  [x] Spec-level Q-1...Q-8 and feasibility FF-01...FF-07 all have a resolution
      or Draft ADR disposition (TDD §4/§9)
  [x] Incremental re-run of /initiative-feasibility is clean (this report)
  [ ] Proceed: /spec-technical-review (confirmation pass per pin's pass edge)
  [ ] After spec + feasibility + TDD + 3 ADRs + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: /create-board-tickets from plan §9 — then /pre-implement → /loop-spec
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: pass
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-014.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-014
    revision: 2
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/212"
    spec_pr_head: "7f212feb3267628b7448c3e56460c0f727e5236c"
    source_freshness: current
    findings_total: 7
    findings_resolved: 7
    findings_addressed_pending_pe_accept: 2
    pm_blocking: 0
    pm_items_resolved: [PM-1, PM-2]
    pe_blocking: 0
    domain_blocking: 0
    draft_adr_files:
      - docs/specification/adr/adr-014-jwt-only-product-edge-trust-zone.md
      - docs/specification/adr/adr-015-programme-scoped-forge-credential-resolution.md
      - docs/specification/adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
```
