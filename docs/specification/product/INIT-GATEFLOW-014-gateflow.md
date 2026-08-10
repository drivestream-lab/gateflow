# INIT-GATEFLOW-014 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-014 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-014.md` |
| PRD digest (H1) | `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/35 |
| Meta PR approved head (G1) | `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-014.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/35#pullrequestreview-4895934562) 2026-08-10T10:44:21Z on `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-014.md`; label `impact-map-lgtm` |
| Architecture constraints (existing) | [`adr-002`](../adr/adr-002-edge-trust-model.md) (**Accepted** — three trust zones: JWT default / forge-signature webhook / programme-token control-plane). [`adr-005`](../adr/adr-005-programme-token-control-plane-mutations.md) (**Accepted** — widens programme-token zone to reads+writes; supersedes ADR-002's read-only programme row). [`adr-011`](../adr/adr-011-tenant-scoped-bearer-token-trust-zone.md) (**Accepted** — fourth zone: per-tenant bearer, no populated `AuthContext`). This INIT's product intent (JWT-only edge; refuse then delete programme-token and tenant-bearer zones) **supersedes** ADR-002/005/011's zone model. Which new ADR(s) supersede which existing ADR(s), and the exact JWT claim/role/programme-binding shape, are **not decided here** — routed to technical review (Q-1, Q-2). [`adr-003`](../adr/adr-003-slot-layer-ownership.md) (**Accepted** — adapter registry fail-closed; unaffected by CAP-04's DB-catalogue addition, which is a new credential source for the existing `cursor` adapter, not a new adapter). |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-10 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure — see
> `prayog-skills/references/artifact-write-contract.md`.

## Overview

Gateflow's product APIs today authenticate through three shared-secret doors —
one global programme service token, one per-tenant bearer, and an
unauthenticated tenant register — while JWT middleware is wired but bypassed on
every product route. This initiative makes Gateflow-issued user JWTs
(`platform_admin` | `tenant_admin`) the **only** product-edge credential,
introduces a **Programme** entity that owns a per-programme GitHub PAT +
workspace root + per-lane runner/model defaults (with `Tenant` becoming a child
attach target for `tenant_admin`), moves code-agent credentials into a
**platform DB catalogue** that start calls resolve against, refuses the old
doors the moment the JWT edge is live (no dual-auth window), deletes the dead
code one wave later, wipes 012/013 lab tenant rows, and rewrites every
teaching/verify surface that still instructs callers to use the old doors.

**Scope boundary (this repo only):** CAP-01…CAP-08 / PRD REQ-01…REQ-38,
REQ-40…REQ-47 per the approved impact-map H2 payload. **REQ-39** (prayog-meta
vision/ADR-citation language) is **out of this repo** — it is content work in
`prayog-meta`, tracked there. Out of this repo: `gateflow-ops` UI (deferred —
inherits the JWT caller story once this INIT ships), any ops/login screen,
Claude Code / OpenCode runner implementation (catalogue reserves slots only),
GitHub App runtime activation (storage shape reserved, unused this INIT),
secrets encryption.

**Ownership:** this spec defines observable behavior, acceptance, field
meaning, invariants, errors, and compatibility for the JWT-only edge, the
Programme entity, the platform agent catalogue, and the old-door
refuse-then-delete sequence. Exact routes, JWT claim schema, ADR supersession
mapping, the `ForgeClient` per-programme credential resolution mechanism, and
the run/board/checkpoint tenant-scoping data model are **deferred to
feasibility / technical review** — not decided here (Q-1…Q-5).

**As-built baseline (2026-08-10, verified against local checkout):**

| Existing behavior | Evidence |
|---|---|
| `AuthMiddleware` validates Bearer JWT (HS256/RS256) and sets `request.state.auth`, but **every** product prefix (`/api/v1/waves`, `/initiatives`, `/runs`, `/metrics`, `/board`, `/checkpoints`, `/tenants`) is listed in `public_paths` — JWT gates nothing on product routes today | `src/app.py:76-87`, `src/common/auth/middleware.py` |
| Waves, runs, board, checkpoints, initiatives, metrics, and forge-authorize routes are gated by one static, process-global `verify_programme_service_token` compared against `PROGRAMME_SERVICE_TOKEN` | `src/api/v1/programme_token.py`; consumed by `waves_routes.py`, `runs_routes.py`, `board_routes.py`, `checkpoints_routes.py`, `initiatives_routes.py`, `metrics_routes.py`, `forge_routes.py` |
| Tenant CRUD and programme-connect/select/catalogue routes are gated by `verify_tenant_bearer_token`, a per-row lookup against `TenantSchema.bearer_token`; does **not** populate `AuthContext` (ADR-011 Option A) | `src/api/v1/tenant_token.py`, `tenant_routes.py`, `programme_routes.py` |
| `POST /api/v1/tenants` (tenant register) has **no** auth dependency at all | `src/api/v1/tenant_routes.py:23-29` |
| `TenantSchema` is the aggregate root holding `pat` (plaintext), `bearer_token`, and `workspace_root` — there is no `Programme` table | `src/database/postgres/schema/tenant_schema.py` |
| The name **"programme"** is already load-bearing product vocabulary for a *different* concept: `TenantProgrammeConnectionSchema` / `programme_routes.py` / `ProgrammeOnboardingService` model "the tenant's synced meta-repo catalogue connection" (INIT-GATEFLOW-013), not an owning entity with credentials | `programme_routes.py`, `programme_connection_models.py` |
| Cursor agent credential is process-global `CURSOR_API_KEY` (`CursorAgentSettings`); `CursorAgentRunner.run_skill` and `SlotValidator._check_adapter` both call `has_api_key()` / `require_api_key()` directly against env — no DB catalogue exists | `src/configs/cursor_agent_settings.py`, `src/infra_services/cursor_agent_runner.py:142-158`, `src/business_services/slot_validator.py:107-122` |
| Git clone/fetch for tenant workspaces already resolves credential **per-tenant** from `TenantSchema.pat` via `TenantGitWorkspaceClient` — this path already matches CAP-05's per-programme intent in shape, just keyed on the wrong table | `src/infra_services/tenant_git_workspace_client.py:80-105`, `tenant_repository.py:185,263` |
| Outbound GitHub API mutations (PR/issue/board comments, via `ForgeClient`) use a **separate**, **process-global singleton** credential (`GithubSettings`, env `GITHUB_AUTH_MODE=pat\|app`) minted **once** at DI `initialize()` and shared across every tenant/programme — this is a *different* credential path from the per-tenant git-clone path above | `src/infra_services/forge_client.py:55-79`, `github_token_provider.py`; injected directly into `BoardService.__init__` |
| `RunSchema`, `StageSchema`, `RunEventSchema`, `JobSchema`, board tickets, and checkpoint records carry **no tenant/programme identifier** — reads/lists (`GET /runs`, `/metrics`, `/board/tickets`, `/checkpoints/*`) filter only by `org`/`repo`/`initiative_id`, with nothing to authorize "this caller's programme" against | `src/database/postgres/schema/run_store_schema.py`; `runs_routes.py`, `board_routes.py`, `checkpoints_routes.py` |
| `WaveStartTargetingFields` (implement/spec/closeout start bodies) carries `org`/`repo` but no tenant/programme field | `src/models/wave_start_models.py:23-46` |
| `PatTokenProvider` (used by the singleton `ForgeClient`) already raises at construction if `GITHUB_AUTH_MODE=pat` and `APP_ENVIRONMENT=production` (ADR-003) | `src/infra_services/github_token_provider.py:40-47` |
| 12+ `tests/verify/*.py` scripts source `PROGRAMME_SERVICE_TOKEN` / tenant bearer from `.env` / `tests/config.yaml` today | `tests/README.md:38-71` |

**Delivery waves (product-normative; PRD §5, gateflow-scoped):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Seed `platform_admin` + user JWT mint/login edge | REQ-01–REQ-07, REQ-43 |
| **W1** | Validate-then-create Programme + `tenant_admin` attach + platform DB agent catalogue + lane defaults | REQ-08–REQ-22, REQ-40–REQ-42, REQ-44–REQ-45, REQ-47 |
| **W2** | Cut over repo lifecycle + twin/initiative under JWT; **refuse** old doors (no dual-auth window) | REQ-23–REQ-33 |
| **W3** | Dead-door **deletion** + wipe cutover | REQ-34–REQ-35, REQ-46 |
| **W4** | Prove absence + rewrite gateflow teaching/verify surfaces | REQ-36–REQ-38 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | A seed script creates at least one `platform_admin` and can mint a Gateflow-issued user JWT for that user | PRD REQ-01; CAP-01; D10, OQ-1 | Seed run | `platform_admin` exists; minted JWT accepted by the product edge | unit + verify | W0 |
| REQ-02 | A login API (no UI) authenticates an existing user and returns a Gateflow-issued user JWT | PRD REQ-02; CAP-01; OQ-1 | Login call with valid credentials | JWT returned; usable on product APIs | unit + verify | W0 |
| REQ-03 | Login with invalid credentials is refused; no JWT issued | PRD REQ-03; CAP-01; fail-closed | Bad login | Named unauthorized/invalid outcome; 0 token | unit + verify | W0 |
| REQ-04 | Product APIs listed in Appendix C accept only Gateflow-issued user JWTs as the caller Bearer | PRD REQ-04; CAP-01; D1 | Product call | Valid JWT authorized per role; non-JWT secrets not accepted as dual-auth | unit + verify | W0 |
| REQ-05 | Missing, malformed, expired, or wrong-issuer/audience JWTs are refused | PRD REQ-05; CAP-01; D12 | Bad JWT | Unauthorized; 0 state change | unit + verify | W0 |
| REQ-06 | JWT identifies user and role; `tenant_admin` is bound to its Programme | PRD REQ-06; CAP-01; D10, D17 | Authorized call | Role/programme binding enforced | unit + verify | W0 |
| REQ-07 | GitHub PAT and agent keys are never accepted as the caller's API Bearer | PRD REQ-07; CAP-01; D4 | Caller sends PAT/agent key as Bearer | Refused as product auth | unit + verify | W0 |
| REQ-43 | Invalid login is refused with a named outcome and issues no JWT (surfaces REQ-03) | PRD REQ-43; CAP-01; fail-closed | Bad login | 0 token | unit + verify | W0 |
| REQ-08 | `platform_admin` can validate-then-create a **Programme** with meta location, workspace root, and **required** GitHub PAT | PRD REQ-08; CAP-02; D13, D14, D15, D18 | Onboard call | On success: Programme exists with PAT + workspace + repo catalogue from validation | unit + verify | W1 |
| REQ-09 | Validation (PAT usability + meta clone/extract) runs before durable create | PRD REQ-09; CAP-02; D13 | Onboard call | Create happens only after validation succeeds | unit + verify | W1 |
| REQ-10 | Validation failure leaves no Programme row and no child Tenant behind | PRD REQ-10; CAP-02; fail-closed | Bad PAT / bad meta | Named reason; 0 durable Programme/Tenant | unit + verify | W1 |
| REQ-11 | Successful create stores **that programme's** PAT in plaintext on the Programme — not a factory-global GitHub credential | PRD REQ-11; CAP-02; D14, D18 | Successful onboard | PAT readable only as that programme's runtime secret; not returned on ordinary read APIs | unit + inspection | W1 |
| REQ-12 | Workspace root is set at programme onboard and used as the programme's workspace root thereafter | PRD REQ-12; CAP-02; D15 | Successful onboard | Workspace root persisted and used by subsequent lifecycle | unit + verify | W1 |
| REQ-13 | Agent keys supplied on programme onboard are rejected; no agent key is stored on the Programme | PRD REQ-13; CAP-02; D14, D19 | Onboard with agent key | Rejected; 0 create | unit + verify | W1 |
| REQ-14 | GitHub App fields may exist as reserved storage shape; unused at runtime this INIT; PAT remains the required runtime GitHub credential | PRD REQ-14; CAP-02; OQ-2 | Onboard / forge/git | PAT used; App materials not required and not runtime-active | unit + inspection | W1 |
| REQ-15 | `platform_admin` can create/attach a `tenant_admin` (Tenant child) for an onboarded Programme | PRD REQ-15; CAP-03; D10, D17 | Attach call | `tenant_admin` can log in and receive JWT for that programme | unit + verify | W1 |
| REQ-16 | The only programme role type is `tenant_admin` | PRD REQ-16; CAP-03; D17 | Role model | No additional programme role types ship | inspection | W1 |
| REQ-17 | `platform_admin` can list programmes | PRD REQ-17; CAP-03; D11 | List call | Onboarded programmes visible | unit + verify | W1 |
| REQ-18 | `platform_admin` cannot onboard/deboard repos or start twin/initiative runs | PRD REQ-18; CAP-03; D11 | `platform_admin` JWT on those calls | Refused | unit + verify | W1 |
| REQ-44 | Attach `tenant_admin` to an unknown programme is rejected; 0 attach | PRD REQ-44; CAP-03; fail-closed | Bad attach | Named reason | unit + verify | W1 |
| REQ-47 | Re-seed of the same `platform_admin` is idempotent; re-attach of the same `tenant_admin` identity to the same programme is idempotent; multiple distinct `tenant_admin` identities on one programme are allowed | PRD REQ-47; CAP-03; efficiency | Seed / attach | Named idempotent behavior | unit + verify | W1 |
| REQ-19 | `platform_admin` can provision Cursor into a platform-level **DB** agent catalogue | PRD REQ-19; CAP-04; D19 | Provision call | Cursor present as a choose-able / default-able platform agent | unit + verify | W1 |
| REQ-20 | Catalogue may include reserved slots for Claude Code / OpenCode without implementing those runners | PRD REQ-20; CAP-04; scope-out | Provision/list | Slots representable; runners not required to execute | unit + inspection | W1 |
| REQ-21 | Twin/initiative start resolves an **effective** runner (+ model): caller if supplied, else Programme per-lane default | PRD REQ-21; CAP-04; D19, OQ-4 | Start call | Effective runner/model recorded/used for that run | unit + verify | W1 |
| REQ-22 | If the effective runner is missing or not provisioned (or key missing) in the DB catalogue, start is rejected with a named reason | PRD REQ-22; CAP-04; OQ-4 | Start with bad/missing effective runner | Rejected; 0 run | unit + verify | W1 |
| REQ-40 | Platform agent catalogue is a durable **separate DB table**; provision persists runner identity + key there | PRD REQ-40; CAP-04; D19 | Provision | Catalogue row exists; not env-only | unit + inspection | W1 |
| REQ-41 | Before twin/initiative start, Gateflow checks the DB catalogue for the effective runner and uses only that row's credential; process-global `CURSOR_API_KEY` must not authorize a product run | PRD REQ-41; CAP-04; OQ-4 | Start | Catalogue used; env fallback does not succeed | unit + verify | W1 |
| REQ-42 | Each Programme may store default runner + model per lane (spec, implement, closeout, initiative); caller-supplied values win; omit → lane default; both omit and no default → reject; defaults must themselves be provisioned catalogue runners | PRD REQ-42; CAP-04; D19, OQ-4 | Start / set-defaults | Defaults applied correctly; reject when unresolved | unit + verify | W1 |
| REQ-45 | Provisioning a platform agent with blank or missing key is rejected | PRD REQ-45; CAP-04; fail-closed | Bad provision | 0 usable credential | unit + verify | W1 |
| REQ-23 | `tenant_admin` JWT authorizes repo lifecycle calls (connect/choose/onboard/deboard) for its programme | PRD REQ-23; CAP-05; D1, D9 | Repo lifecycle under JWT | Same 012/013 behaviors, new auth | unit + verify | W2 |
| REQ-24 | `tenant_admin` JWT authorizes twin/initiative start and Appendix C control-plane reads/actions for its programme | PRD REQ-24; CAP-05; D1, D9 | Control-plane under JWT | Authorized for matching programme | unit + verify | W2 |
| REQ-25 | Outbound forge/git for a programme uses that programme's stored GitHub credential — never the caller JWT | PRD REQ-25; CAP-05; D4, D18 | Forge/git operation | Per-programme PAT used | unit + verify | W2 |
| REQ-26 | Twin/initiative start loads agent credentials **only** from the platform DB catalogue for the effective runner — never a programme-stored agent key and never env Cursor as product auth | PRD REQ-26; CAP-05; D19 | Agent dispatch | Catalogue key used; env alone does not authorize | unit + verify | W2 |
| REQ-27 | Pin explicit vs automated forge authorize policy is unchanged | PRD REQ-27; CAP-05; scope-out | Authorize path | Behavior matches pre-INIT policy | inspection + unit | W2 |
| REQ-28 | Webhooks remain signature-checked and are not converted to user-JWT auth | PRD REQ-28; CAP-05; D5 | Webhook ingress | Signature verification unchanged | unit + verify | W2 |
| REQ-29 | Unauthenticated product API calls (Appendix C) fail closed | PRD REQ-29; CAP-06; D12 | No auth header | Refused | unit + verify | W2 |
| REQ-30 | Role mismatch fails closed (`tenant_admin` ↛ platform-only; `platform_admin` ↛ tenant-only) | PRD REQ-30; CAP-06; D10, D11, D17 | Cross-role call | Refused | unit + verify | W2 |
| REQ-31 | Cross-programme `tenant_admin` access fails closed | PRD REQ-31; CAP-06; D12 | JWT for A on B's resources | Refused | unit + verify | W2 |
| REQ-32 | When the JWT product edge is live, presenting the global programme service token is refused (no dual-auth window) | PRD REQ-32; CAP-06; D1, D2, D16 | Call with `PROGRAMME_SERVICE_TOKEN` | Refused | unit + verify | W2 |
| REQ-33 | When the JWT product edge is live, presenting a tenant bearer is refused | PRD REQ-33; CAP-06; D3, D16 | Call with tenant bearer | Refused | unit + verify | W2 |
| REQ-34 | Open (unauthenticated) tenant register is removed | PRD REQ-34; CAP-07; D3 | Unauthenticated register | Gone / refused; 0 create | unit + verify | W3 |
| REQ-35 | Existing 012/013 lab tenants/shared-secret rows are wiped at cutover; re-onboard uses CAP-02/CAP-03 | PRD REQ-35; CAP-07; OQ-3 | Cutover | Old lab tenants gone; new Programme path works | verify + runbook | W3 |
| REQ-46 | Wipe while any run is in flight for that programme is rejected; 0 wipe | PRD REQ-46; CAP-07; fail-closed | Wipe mid-run | Named reason; rows unchanged | unit + verify | W3 |
| REQ-36 | Verify / live-check scripts prove JWT happy path for `platform_admin` and `tenant_admin` | PRD REQ-36; CAP-08; exit | Verify run | Scripts pass on JWT path | verify | W4 |
| REQ-37 | Verify / live-check scripts prove refusal of programme service token, tenant bearer, and open register | PRD REQ-37; CAP-08; exit, D16 | Negative verify | Named refusal / absence | verify | W4 |
| REQ-38 | Teaching surfaces (verify scripts, caller examples, docs that instruct product callers) describe JWT + per-programme GitHub + DB catalogue only | PRD REQ-38; CAP-08; D6, D8 | Doc/script review | No instruction to use old product doors or env Cursor as product path | inspection | W4 |

> **Id convention:** `REQ-*` is canonical, numbered to match the PRD 1:1 for
> traceability. This spec's scope is **REQ-01–REQ-38, REQ-40–REQ-47** — matches
> impact-map H2 capabilities CAP-01…08. **REQ-39** is excluded — it is
> `prayog-meta` content scope only (Overview).
>
> **Behavioral acceptance vs evidence:** condition/event + observable result
> are the product acceptance statement (implementation-neutral). Evidence
> layer names how it will be proved later — module/schema/route/ADR choices
> are deferred to feasibility / technical review.

### Target capability surface (illustrative — engineering owns exact routes)

| Capability | Notes |
|------------|-------|
| Seed `platform_admin` | Script; CAP-01 |
| Login → JWT | API only, no UI; CAP-01 |
| Validate-then-create Programme | `platform_admin`; CAP-02 |
| Attach `tenant_admin` | `platform_admin`; CAP-03 |
| List programmes | `platform_admin`; CAP-03 |
| Provision platform agent (DB catalogue) | `platform_admin`; CAP-04 |
| Set/read programme per-lane runner+model defaults | `platform_admin`; CAP-04 |
| Repo lifecycle + twin/initiative under JWT | `tenant_admin`; CAP-05; effective agent at start |
| *(removed)* Programme service token product auth | CAP-06 refuse / CAP-07 delete |
| *(removed)* Tenant bearer product auth | CAP-06 refuse / CAP-07 delete |
| *(removed)* Open tenant register | CAP-07 |

Exact routes, request/response shapes, error body fields, JWT claim schema,
and ADR supersession mapping → **Q-1, Q-2** (deferred to technical review).

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|-----------------|----------|
| REQ-05, REQ-29 | Product call with missing/invalid/expired/malformed/wrong-issuer JWT | Refused (unauthorized); 0 state change | JWT is the sole edge credential post-cutover — any silent pass-through reopens an unauthenticated door | unit + verify |
| REQ-32 | Product call with programme service token after JWT edge live | Refused; 0 state change | Prevents "JWT + keep the old token for scripts" dual-auth regression (PRD hard exit rule) | unit + verify |
| REQ-33 | Product call with tenant bearer after JWT edge live | Refused; 0 state change | Same dual-auth regression risk on the onboarding surface | unit + verify |
| REQ-34 | Unauthenticated tenant register after cutover | Gone / refused; 0 create | Open register was the original uncontrolled-onboarding gap this INIT closes | unit + verify |
| REQ-03, REQ-43 | Login with invalid credentials | Refused; 0 JWT | Prevents credential-stuffing from minting a usable product token | unit + verify |
| REQ-10 | Validate-then-create with bad PAT or unreachable/malformed meta | Rejected, named reason; no Programme row; no child Tenant | Prevents a half-created Programme with an unusable credential from silently existing | unit + verify |
| REQ-13 | Programme onboard includes agent keys | Rejected; 0 Programme create | Agent keys are platform-level only (D19) — accepting one on Programme onboard would create a second, inconsistent credential surface | unit + verify |
| REQ-44 | Attach `tenant_admin` to unknown programme | Rejected, named reason; 0 attach | Prevents dangling user↔programme bindings that would silently fail at first product call | unit + verify |
| REQ-47 | Duplicate attach of same `tenant_admin` identity / re-seed same `platform_admin` | Idempotent success; no second conflicting row | Retried onboarding scripts must not create duplicate identities | unit + verify |
| REQ-45 | Provision agent with blank/missing key | Rejected, named reason; 0 usable catalogue credential | An unusable catalogue row would surface only at run-start time, far from the provisioning mistake | unit + verify |
| REQ-30 | `tenant_admin` attempts platform_admin-only action / `platform_admin` attempts twin start or repo onboard | Refused; 0 state change | Role-boundary escape would let either role assume the other's blast radius | unit + verify |
| REQ-22, REQ-41 | Twin/initiative start: effective runner unprovisioned, key missing, or resolved only from process-global `CURSOR_API_KEY` | Rejected, named reason; 0 run started | Env-key fallback would silently reopen the exact single-key blast-radius problem CAP-04 exists to close | unit + verify |
| REQ-42 | Twin/initiative start: caller omits runner/model and programme has no lane default | Rejected, named reason; 0 run started | Prevents an ambiguous or accidental default from choosing which agent key runs the job | unit + verify |
| REQ-31 | Cross-programme `tenant_admin` JWT used on another programme's resources | Refused; 0 state change | Multi-tenant isolation is the entire point of moving off one shared secret — a cross-programme leak is the worst-case regression | unit + verify |
| REQ-46 | Wipe while a run is in flight for that programme | Rejected, named reason; rows unchanged | Wiping mid-run would orphan a running job's credentials and workspace | unit + verify |

## Out of scope for this repo

- `gateflow-ops` UI / login screens — deferred (impact map §3; PRD Non-Goals); this INIT ships API-only login that a future BFF/UI would call
- Full IdP / SSO product line — seed + Gateflow-issued JWTs only (PRD Non-Goals)
- Implementing Claude Code / OpenCode runners — provision slots only (REQ-20)
- One shared factory-wide GitHub PAT for all programmes — rejected; PAT is per-Programme (PRD Non-Goals)
- Agent keys stored on the Programme row — rejected; agents are platform-level DB catalogue (D19)
- Changing the pin's explicit-vs-automated forge authorize policy — unchanged (REQ-27)
- Encrypting DB secrets — plaintext accepted, same class as INIT-GATEFLOW-012 G1 (PRD Non-Goals)
- Migrating existing lab tenants in place — wipe + re-onboard only (REQ-35, OQ-3)
- Runtime use of GitHub App credentials this INIT — storage shape reserved only (REQ-14, OQ-2)
- `prayog-meta` vision/ADR-citation content (REQ-39) — tracked in that repo, not here
- Provider-side changes in `prayog-meta` beyond consuming it as a read source for Programme meta validation (unchanged shape from INIT-GATEFLOW-013's CTR-01)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | gateflow / prayog-pe-team | Product callers: lab/verify scripts, future `gateflow-ops`, humans | Product API Bearer contract: caller presents a Gateflow-issued user JWT identifying user + role (+ Programme binding for `tenant_admin`) on every Appendix-C route | `Authorization: Bearer <jwt>` header; no request-body auth fields | 401/403 with a named unauthorized code on any non-JWT or invalid-JWT presentation; otherwise normal route response | JWT is the **only** accepted product-edge credential once W2 is live; programme service token and tenant bearer are refused (W2) then deleted (W3, CAP-07); breaking, no dual-auth window | Missing/invalid/expired/wrong-issuer JWT → 401 named `UNAUTHORIZED`; role/programme mismatch → 403 named reason | Breaking change — supersedes the current programme-token / tenant-bearer contract in-band; no versioned coexistence period | unit + verify (negative-path scripts prove refusal, REQ-37) |

> Entry point is a **semantic** boundary: exact route paths, header names, and
> JSON error-body field names are engineering's to design in feasibility /
> technical review (PRD Appendix C is the accept/refuse matrix, not fixed
> routes).

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | JWT is the sole product-edge credential post-cutover (CTR-01); GitHub PAT and agent keys are never accepted as the caller Bearer (REQ-07). Programme PAT and platform agent keys are plaintext by explicit accepted risk (same class as INIT-GATEFLOW-012 G1) — not a new secrets model. Platform agent blast radius is shared across programmes using that catalogue row; only `platform_admin` may provision (accepted, named). Programme PAT blast radius stays wide within one programme (accepted, named, same class as 012). Env `CURSOR_API_KEY` must not authorize a product run when catalogue resolution fails or as silent fallback (REQ-41). Webhooks remain signature-based, not user-JWT (REQ-28). | unit + verify + inspection |
| Reliability | Validate-then-create, agent provisioning, attach, and wipe all fail closed with named reasons and zero partial state (REQ-10, REQ-13, REQ-44, REQ-45, REQ-46). Old-door refusal (REQ-32/33) and unauthenticated/role-mismatch/cross-programme refusal (REQ-29/30/31) never partially authorize. | unit + verify |
| Performance / capacity | N/A as a product SLO this INIT — JWT verification, catalogue lookup, and Programme resolution are the only new per-request costs; no new capacity claim. | inspection |
| Observability | Structured logs for JWT accept/refuse (with named reason, never the token value), old-door refusal events (REQ-37 negative-path evidence), Programme validate/create outcomes, agent provision/resolve outcomes, and wipe outcomes — IDs/statuses as kwargs; never PAT, agent key, or JWT secret material logged (`logging-loguru.mdc`). | unit + inspection |
| Privacy / data handling | No new end-user PII category beyond existing tenant/user identity handling; Programme PAT and agent keys are organisational credentials, not personal data. JWT `sub`/`role`/programme-binding claims are the only new identity data. | inspection |
| Migration / compatibility | **Breaking, in-band cutover** (D1, D2): programme service token, tenant bearer, and open register are refused (W2) then deleted (W3) in the same delivery — no dual-auth window; shipping JWT while the old programme token still works is a **failed** exit (PRD Hard exit rule). 012/013 lab tenant rows are wiped, not migrated (REQ-35, OQ-3). Every caller of the old doors (lab scripts, `tests/verify/*`, docs) must be inventoried and rewritten before/at W2/W4 cutover — residual process gate (Q-3-equivalent risk from PRD "Lab automation still sends programme API token"). | unit regression + inventory before W2/W3 |
| Rollback / recovery | This is a deliberate breaking, non-reversible cutover by product design (Hard exit rule) — rollback is restoring the old doors via an explicit revert, not a dual path. Wipe (REQ-35) is destructive and has no application-level undo; runbook discipline is the only recovery path (REQ-46 prevents wipe mid-run, but does not make wipe reversible). | inspection + runbook |
| Operations / support | Document JWT mint/login, Programme onboard, agent provisioning, and old-door refusal verify commands per wave in `tests/README.md`. PE must dogfood one full seed→login→onboard-programme→attach-tenant-admin→provision-agent→repo-lifecycle→twin-start path under JWT only, plus the negative refusal suite (REQ-36/37). | live verify + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | INIT-GATEFLOW-012/013 callables (repos, readiness, waves, runs, board, checkpoints, initiatives, forge authorize) remain the behavior substrate; this INIT changes auth + secret placement + entity model, not those behaviors' core contracts | PRD A1; as-built capability matrices (012/013) | PE | confirmed by scope | REQ-23–REQ-28 |
| A-2 | Dormant `AuthMiddleware` / JWT settings can be activated and role-shaped for `platform_admin` / `tenant_admin` without introducing a second JWT stack | PRD A2; `src/app.py`, `src/common/auth/middleware.py`, `src/configs/jwt_settings.py` already exist | PE | assumed — exact claim/schema design owned by eng (Q-1) | REQ-01–REQ-07 |
| A-3 | Lab environments can wipe 012/013 tenant/secret rows and re-onboard without preserving old bearer tokens | PRD A3; OQ-3 locked | PE | confirmed (locked) | REQ-35, REQ-36 |
| A-4 | Cursor remains the only implemented runner this INIT; other catalogue slots are name/placeholder until a later INIT implements them | PRD A4 | PE | confirmed by scope | REQ-19–REQ-22, REQ-40–REQ-41 |
| A-5 | Webhooks stay outside the user-JWT product edge and continue signature verification unchanged | PRD A5; D5; `src/api/webhooks/github_routes.py` unaffected by this INIT's scope | PE | confirmed by D5 | REQ-28 |
| A-6 | The existing per-tenant git-clone credential path (`TenantGitWorkspaceClient` + `TenantSchema.pat`) is close enough in shape to the Programme-owned PAT model that it can be re-pointed rather than redesigned; the singleton `ForgeClient` GitHub-mutation path is the one requiring redesign (see Q-3) | Direct code evidence this session — see As-built baseline | PE | assumed — confirm at technical review | Technical review finds the git-clone path also needs structural change |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact JWT claim schema (issuer/audience/role/programme binding) and password/credential store for the login API (PRD OQ-5 / impact-map IM-01) | PE | no | technical review / W0 design | Gateflow-issued user JWT with role + `tenant_admin` programme binding only — eng owns exact schema | open | pending |
| Q-2 | PE | Whether health/internal/webhook paths remain on the JWT public allowlist exactly as today, and the exact `public_paths` shrink for Appendix C routes (PRD OQ-6 / impact-map IM-02) | PE | no | technical review / W0–W2 design | Webhooks stay signature-based (REQ-28); Appendix C product APIs become JWT-only | open | pending |
| Q-3 | PE | `ForgeClient` is currently a DI **singleton** minting one process-global GitHub Bearer token at startup (`GithubSettings`), shared across all tenants/programmes for PR/issue/board mutations — a separate credential path from the already-per-tenant git-clone client. REQ-25 requires per-**programme** forge/git credential. Does this mean redesigning `ForgeClient` into a per-programme-keyed client/factory, or is a different mechanism intended (e.g. per-call token injection, one GitHub App installation per programme)? | PE | no | technical review, before W2 design | **None** — must be resolved before W2 coding; this is the highest-risk architectural gap found in code review and is not addressed by an auth-dependency swap alone | open | pending |
| Q-4 | PE | `RunSchema`/`StageSchema`/`JobSchema`, board tickets, and checkpoint records carry no tenant/programme identifier today; reads/lists filter only by `org`/`repo`/`initiative_id`. REQ-24 ("reads/actions for its programme") and REQ-31 ("cross-programme access fails closed") require a way to know which programme a run/ticket/checkpoint belongs to. Is the intended mechanism (a) a new `programme_id` column added to these tables, (b) a join through `tenant_repos` (org+repo → tenant → programme) at query time, or (c) something else? | PE | no | technical review, before W2 design | **None** — needs an explicit data-model decision before W2 coding; verify scripts for REQ-31/REQ-37 cannot be written against current schema | open | pending |
| Q-5 | PE | Naming collision: PRD's new **Programme** entity (owns PAT/workspace/lane-defaults) and the existing product vocabulary **"programme"** (`programme_routes.py`, `ProgrammeOnboardingService`, `TenantProgrammeConnectionSchema` — "the tenant's synced meta-repo catalogue connection", INIT-GATEFLOW-013) name two different concepts. Does the new entity get a distinct name (e.g. `Factory`/`Account`/`Org`) to avoid collision, or does the existing "programme connection" concept get renamed/folded in? | PE/PM | no | technical review, before schema/route design | **None** — must be resolved before naming any table/route/model; picking wrong risks a confusing mid-design rename | open | pending |
| Q-6 | PE | `PatTokenProvider` (used by the singleton `ForgeClient`) already forbids `GITHUB_AUTH_MODE=pat` in production (ADR-003). Once forge/git moves to per-programme PAT (REQ-25), does this production guard still apply to the (redesigned) forge path, or does per-programme PAT storage supersede that guard for production use? | PE | no | technical review (same node as Q-3) | Assume ADR-003's production PAT prohibition is unaffected until explicitly revisited — Programme PAT is a distinct credential class from the singleton `ForgeClient` mode setting | open | pending |
| Q-7 | PM | Direct team notice that this INIT **supersedes INIT-GATEFLOW-012 G3** (JWT parked; tenant bearer as product auth) and wipes lab 012/013 tenant rows (impact-map IM-04) | PM | no | before W2/W3 cutover | Proceed — PRD already locks wipe + supersession; record notice on the spec PR description | open | pending |
| Q-8 | PE | Which new ADR(s) formally supersede ADR-002 / ADR-005 / ADR-011 (three-plus-one trust-zone model), and how the superseded/superseded_by chain is recorded, given `spec-driven-development.mdc` treats Accepted ADRs as immutable until superseded (impact-map IM-03, PRD "Eng follow-on: supersede ADR-005/ADR-011") | PE | no | technical review | **None** — ADR supersession must be drafted as part of technical review, not silently implied by shipping code | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #35 head `3120e4e…` = tech-lead APPROVED review (id `4895934562`) `commit_id`; label `impact-map-lgtm`; H1 PRD digest verified by direct `shasum -a 256` match; H3 rev 1; H2 gateflow affected `sha256:53bb4c4f…`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | CAP-01…08 map to REQ-01…38, REQ-40…47 (46 REQs); every REQ row cites PRD REQ-id + CAP + PRD decision refs (D*/OQ*) |
| D3 Repo-bounded scope | PASS | Matches H2 payload exactly (capabilities list REQ-01…38, REQ-40…47, CTR-01); REQ-39 explicitly excluded (prayog-meta only); `gateflow-ops` deferred; `prayog-skills` not affected |
| D4 Observable acceptance | PASS | Each REQ states condition/event, observable result, evidence layer, largely inherited verbatim from the PRD's own engineering-language Requirements table; route/schema/ADR choices deferred to Q-1…Q-5, Q-8 |
| D5 Negative/failure paths | PASS | 15 rows covering every PRD error-table entry relevant to gateflow, each with an explicit "why it matters" |
| D6 Assumptions/questions | PASS | A-1…A-6 evidenced with owner/status/invalidation; Q-1…Q-8 have lane/owner/blocking/required-by/default/status; zero Blocking=yes rows |
| D7 Cross-repository contracts | PASS | CTR-01 semantic (logical Bearer contract, invariants, errors, compatibility); transport/route realization deferred to technical review |
| D8 NFR applicability | PASS | All 8 areas specified with concrete, PRD-sourced content; none N/A |
| D9 As-built alignment | PASS | As-built baseline table distinguishes existing (JWT dormant, programme-token, tenant-bearer, open register, singleton ForgeClient, per-tenant git-clone PAT, env Cursor key, no tenant-scoping on run/board/checkpoint data) vs changed (REQ-04/23-24/32-33 auth cutover) vs new (Programme entity, DB agent catalogue) — with direct source citations for every claim |
| D10 Dependency order | PASS | Matches impact map §7: 012/013 shipped → gateflow W0→W1→W2→W3→W4; prayog-meta W4 (REQ-39) runs in parallel, not a gateflow build gate |
| D11 Zero unresolved blockers | PASS | No Blocking=yes Spec questions; Q-3/Q-4/Q-5/Q-8 are explicit **no-default process gates before W2 coding/design** (not blockers to publishing this Draft spec) — same pattern INIT-GATEFLOW-013's Q-2/Q-6 used |
| D12 Output completeness | PASS | Header H4, all required tables, check summary, selected workflow outcome, PR readiness handoff, developer review, handoff envelope all present; no placeholder text presented as fact |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on the current meta PR head with matching digest/revision/scope; zero blocking Spec questions after classification — the four architecturally material findings from code review (ForgeClient singleton redesign, missing tenant/programme data-model scoping, "programme" naming collision, ADR supersession mapping) are routed as explicit no-default process gates required **before W2 design/coding**, not blockers to Draft spec publication, mirroring the precedent set by INIT-GATEFLOW-013's Q-2/Q-6.

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full PRD traceability; no material acceptance blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-014-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-014] Spec — One identity to call Gateflow, retire shared-secret doors (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`, `docs/specification/README.md` (active-initiative pointer update) |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` / `/open-draft-pr` — do not commit/push/open PR inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none for Draft publish; process gates Q-3, Q-4, Q-5, Q-8 remain open and must resolve before W2 coding/design |

**No GitHub side effects have occurred.** Persist the draft locally, present
this section in chat, and ask whether to authorize Forge publish
(`/commit-workspace` / `/open-draft-pr` or Gateflow ForgeClient). Continue only
after explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-014 — One identity to call Gateflow, retire shared-secret doors
(gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/35
- Approved meta head: `3120e4eff4b4dfe86ed1a14f02439d62bc6151c7`
- Impact-map revision: 1
- PRD digest: `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e`
- Repo scope digest: `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef`

## Spec path

`docs/specification/product/INIT-GATEFLOW-014-gateflow.md`

## Summary

- Full gateflow scope: CAP-01…08 / REQ-01…38, REQ-40…47 (46 REQs) — JWT-only
  product edge, Programme validate-then-create with per-programme PAT,
  `tenant_admin` attach, platform DB agent catalogue with lane defaults,
  refuse-then-delete old shared-secret doors, wipe 012/013 lab tenants, prove
  absence + rewrite teaching surfaces
- Waves W0–W4 per PRD §5
- Cross-service contract: CTR-01 (Gateflow-issued JWT is the sole product-edge
  Bearer contract for all product callers)
- Open engineering questions: Q-1…Q-8 (non-blocking to Draft publish; Q-3/Q-4/
  Q-5/Q-8 are process gates before W2 coding/design — code review surfaced a
  singleton `ForgeClient` credential model and a total absence of
  tenant/programme scoping on run/board/checkpoint data that the PRD's auth
  swap alone does not resolve)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `/open-draft-pr`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADRs (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [ ] Scope matches the approved impact-map repo scope digest
- [ ] REQs have condition/event, observable result, and evidence layer
- [ ] Contracts are semantic (logical operation); no architecture decisions in REQs
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Never infer approval from labels
alone — `spec-lgtm` requires matching artifacts on the exact PR head.

Provision labels before PR creation when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-014.md` @ meta PR #35
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-014.md` revision 1
- Resolution: `prayog-meta/prd/reports/Resolution-INIT-GATEFLOW-014.md`
- Predecessors: [`INIT-GATEFLOW-012-gateflow.md`](INIT-GATEFLOW-012-gateflow.md) (tenant registry — `TenantSchema.pat`/`bearer_token` this INIT retires), [`INIT-GATEFLOW-013-gateflow.md`](INIT-GATEFLOW-013-gateflow.md) (programme-connect vocabulary this INIT's naming must disambiguate against, Q-5)
- As-built: `docs/specification/as-built/implementation-status.md`
- Architecture (existing, requires supersession — Q-8): [`adr-002`](../adr/adr-002-edge-trust-model.md), [`adr-005`](../adr/adr-005-programme-token-control-plane-mutations.md), [`adr-011`](../adr/adr-011-tenant-scoped-bearer-token-trust-zone.md); unaffected: [`adr-003`](../adr/adr-003-slot-layer-ownership.md), [`adr-012`](../adr/adr-012-programme-catalogue-discovery-authority.md)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-014
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/35"
    meta_pr_head: "3120e4eff4b4dfe86ed1a14f02439d62bc6151c7"
    map_revision: 1
    source_prd_digest: sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e
    repo_scope_digest: sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef
    process_gates:
      - Q-3
      - Q-4
      - Q-5
      - Q-8
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-014] Spec — One identity to call Gateflow, retire shared-secret doors (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-014-gateflow.md
```
