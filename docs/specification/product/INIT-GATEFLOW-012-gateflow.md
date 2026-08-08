# INIT-GATEFLOW-012 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-012 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-012.md` |
| PRD digest (H1) | `sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/32 |
| Meta PR approved head (G1) | `74402540efd98527014b4706d0d29bda1242b6cf` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-012.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678` |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/32#pullrequestreview-4885261904) 2026-08-07T17:45:36Z on `74402540efd98527014b4706d0d29bda1242b6cf` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-012.md`; label `impact-map-lgtm` |
| Architecture constraints (existing) | [`adr-010`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**) currently authorizes caller-supplied `workspace_path` on the implement-lane contract; PRD D1 **reverses** that assumption for Tenant-registered repos only (unregistered/legacy callers unaffected). Whether this is an ADR-010 amendment or a new ADR is **not decided here** — routed to technical review (Q-4). [`adr-009`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted** — forge mutate/publish authority) is unaffected. |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-07 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure.

## Overview

Gateflow gains a **Tenant registry** (PAT + repo list + workspace root + board
default, registered via one API call, no UI) and the **workspace/branch
lifecycle** that consumes it: repo clone-on-first-use / refresh-on-repeat-use,
branch create-or-reuse, a harness-readiness gate, repo-scoped run exclusivity,
and a **dormant** (built, unit/verify-proven, never wired live) branch-purge
capability. Today, when `ImplementWaveStartRequest.workspace_path` is omitted,
Gateflow silently falls back to its own process working directory
(`RunOrchestrator.process_job`) — this INIT replaces that fallback with a real,
Tenant-scoped workspace for registered repos, and fails closed (**422**) for
everything else.

**Scope boundary (this repo only):** this spec covers **CAP-01–CAP-06 / REQ-01
–REQ-27, REQ-32** — Tenant registry API, clone/refresh, branch create-or-reuse,
harness-readiness, repo-scoped `NO_CONCURRENT_RUN`, and the dormant
`ForgeClient.delete_branch` method. It does **not** cover `prayog-skills`'
new pin node/action shapes (**REQ-28–REQ-31**) — that is a distinct contract
change owned by `drivestream-lab/prayog-skills` per the approved impact map
(§6 CTR-01); gateflow only **consumes** the remounted pin (0 BROKEN nodes) once
that contract lands. No `gateflow-ops` UI this INIT (deferred, out of repo).

**Ownership:** this spec defines observable behavior, acceptance, field
meaning, invariants, errors, and compatibility. Module/schema/ADR choices
(e.g. exact Postgres table shape, whether ADR-010 is amended or superseded,
which GitHub call satisfies eager PAT verification) are **deferred to
feasibility / technical review** — not decided here (see Spec questions).

**As-built baseline (2026-08-07, verified against local checkout):**

| Existing behavior | Evidence |
|---|---|
| `ImplementWaveStartRequest.workspace_path` is already `Optional[str]` — the only wave-start request that skips `_require_existing_directory` | `src/models/wave_start_models.py` |
| Omitted `workspace_path` → `RunOrchestrator.process_job` falls back to `str(Path.cwd())` (active behavior today, not a passive gap) | `src/business_services/run_orchestrator.py:237` |
| `ForgeClient` has `ensure_branch_from_base`, `get_branch_tip_sha`, `commit_paths_to_branch`, board/PR/label methods — **no** `delete_branch` | `src/infra_services/forge_client.py` (method inventory) |
| `LaunchpadClient.sync_harness` is a real, DI-wired stub: verifies the path exists only ("W1: log + no-op"); already invoked inside `RunOrchestrator.process_job` | `src/infra_services/launchpad_client.py` |
| `RunRepository.find_active_run` already filters `org`+`repo` first, then narrows by `initiative_id`+`wave_id` **or** `pr_number` **or** `issue_number` — narrower key match, not repo-only | `src/database/postgres/repository/run_store_repository.py:198-227` |
| `WaveStartService._enqueue_wave` calls `find_active_run` directly (not `TriggerRouter`) before enqueue | `src/business_services/wave_start_service.py:365-380` |
| `AuthMiddleware` sets `request.state.auth` (`user_id`/`tenant_id`/`owner_id`) but **every** `/api/v1/*` route is listed in `public_paths` — gates nothing today | `src/app.py:76-86`, `src/common/auth/middleware.py` |
| `GithubSettings` is one global env-var GitHub credential for the whole service | `src/configs/github_settings.py` |
| `BoardTicketCreateRequest.project_number`/`project_owner` are already caller-supplied per call, no config-derived default | `src/models/board_models.py` |
| Deterministic branch naming (`build_wave_head_branch`, `branch_slug_from_head_ref`) already used by wave-start/closeout | `src/models/pr_branch_naming.py` |

**Delivery waves (product-normative; PRD §5, gateflow-scoped):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Tenant registry: data model + API (register, attach user, eager PAT verify, read/list) | REQ-01–REQ-09, REQ-32 |
| **W1** | Repo clone (first use) + refresh (subsequent use) | REQ-10–REQ-15 |
| **W2** | Branch create-or-reuse (new wave vs. continuation) | REQ-16–REQ-19 |
| **W3** | Harness-readiness check | REQ-20–REQ-22 |
| **W4** | Repo-level sequencing (`NO_CONCURRENT_RUN` broadening) | REQ-23–REQ-25 |
| **W5** | Branch purge capability — built, pin-declared, dormant (gateflow half only; `prayog-skills` half is REQ-28–REQ-31) | REQ-26, REQ-27 |

W1/W2 exit and W5's full dormancy proof (REQ-29) depend on the `prayog-skills`
contract PR landing first (impact map §7) — see Cross-service contracts (CTR-01)
and Spec questions (Q-6).

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | Tenant registration accepts `name`, `pat`, `repos[]` (org/repo pairs), `workspace_root` (absolute path), optional `board` default (`project_owner`/`project_number`) | PRD REQ-01; CAP-01; US-1 | `POST` tenant-registration call | Missing/malformed required field → **400**, 0 rows written; well-formed call proceeds to REQ-06 verification | unit | W0 |
| REQ-02 | The tenant's PAT is persisted in a dedicated column, in plaintext (**G1**, accepted risk — see NFR Security), and is never echoed in any response body | PRD REQ-02; D8; G1 | Registration success or any subsequent tenant read | Response body has no `pat`/PAT-shaped field, ever | unit + inspection | W0 |
| REQ-03 | Registration issues a tenant-scoped bearer token distinct from the existing global `PROGRAMME_SERVICE_TOKEN` | PRD REQ-03; D9; G3 | Registration success | Token returned once in the registration response; usable on subsequent tenant-scoped calls | unit | W0 |
| REQ-04 | A user-attach endpoint records an identity (email/handle) against a `tenant_id`; a caller with no attachment to that tenant, or an invalid/absent tenant token, is rejected before any lane logic runs | PRD REQ-04; D9 | Attach call, then a subsequent tenant-scoped call | **401** on an unattached/mismatched caller; success on an attached caller | unit + verify | W0 |
| REQ-05 | No per-repo ACL exists within a tenant — any attached user may act on any of that tenant's registered repos | PRD REQ-05; D9 | Any attached-user call | No repo-scoped permission check narrows access below tenant scope | inspection | W0 |
| REQ-06 | Registration eagerly verifies the submitted PAT has read access to every listed repo **before** the Tenant row is committed; any failing repo(s) reject the whole registration with an itemized, per-repo reason | PRD REQ-06; G4 (resolves PRD OQ-2) | Registration call, one or more repos fail PAT read-access check | **422**, 0 rows written; response names exactly which repo(s) failed and why (not a single boolean) | unit + verify | W0 |
| REQ-07 | `workspace_root` is validated as an absolute path | PRD REQ-07 | Registration call, `workspace_root` not absolute | **400** | unit | W0 |
| REQ-08 | A tenant's default board (`project_owner`/`project_number`) is applied when a board-touching call omits an explicit override; an explicit per-call value still wins — same override precedent as today's `BoardTicketCreateRequest` | PRD REQ-08; A-5 (resolves PRD OQ-3) | Board-touching call with no explicit `project_owner`/`project_number` | Tenant default applied; explicit override always takes precedence when present | unit | W0 |
| REQ-09 | Registering a second (or Nth) tenant requires zero edits to `GithubSettings` or any other global env-backed settings class | PRD REQ-09 | Second tenant registration | No deploy/env change required for the new tenant to operate | inspection + manual UAT | W0 |
| REQ-32 | Tenant read/list returns the tenant's registered repo list, `workspace_root`, and board default; the PAT is never present in any read/list response | PRD REQ-32 (Draft PRD gap closure) | `GET /api/v1/tenants` or `GET /api/v1/tenants/{tenant_id}` | **200** with tenant fields present; `pat` field absent from every response, including list | unit + verify | W0 |
| REQ-10 | When `ImplementWaveStartRequest.workspace_path` is omitted **and** the request's `org`/`repo` resolve to a Tenant-registered repo, Gateflow resolves a deterministic, discoverable workspace for that repo before dispatching the Enter-at skill — replacing today's `Path.cwd()` fallback | PRD REQ-10; D1 | Implement-lane start, `workspace_path` omitted, registered repo | A workspace exists at a deterministic, discoverable path before dispatch; the `Path.cwd()` fallback is never reached for this case | unit + verify | W1 |
| REQ-11 | Clone/refresh authenticates git operations with the Tenant's stored PAT — the same credential used for `ForgeClient` platform calls (**G2**, accepted risk — see NFR Security) | PRD REQ-11; D8; G2 | Any clone/refresh for a Tenant-registered repo | Git auth uses the Tenant PAT; no separate deploy-key credential path exists | unit + inspection | W1 |
| REQ-12 | Explicit `workspace_path` on any wave-start request is honored exactly as it is today — this capability is strictly additive and never overrides a caller-supplied path | PRD REQ-12 | Any wave-start request with `workspace_path` present | Behavior identical to pre-INIT-012 code path (regression) | unit (regression) | W1 |
| REQ-13 | If the deterministic workspace path already exists and is a valid checkout of the expected remote, Gateflow fetches in place rather than re-cloning | PRD REQ-13; D1; depends on A-2 | Repeat use, valid existing checkout | Fetch executed; no clone invoked | unit + verify | W1 |
| REQ-14 | If the deterministic workspace path exists but is **not** a valid checkout of the expected remote, refresh fails closed rather than silently operating on the wrong tree | PRD REQ-14; fail-closed | Corrupted/mismatched existing path | **422**; the mismatch is named; the existing tree is left untouched | unit + verify | W1 |
| REQ-15 | When `workspace_path` is omitted **and** the repo is not Tenant-registered, Gateflow does not guess a workspace | PRD REQ-15; fail-closed | Implement-lane start, `workspace_path` omitted, unregistered repo | **422**; 0 enqueue; no clone attempted | unit + verify | W1 |
| REQ-16 | "New wave" (no existing run/PR for this `initiative_id`+`wave_id`) forks the head branch from the target repo's **current** `develop` tip | PRD REQ-16; D2 | New wave start | Head branch is created from the live `develop` SHA at fork time, not a cached/stale SHA | unit + verify | W2 |
| REQ-17 | The head branch name uses the existing deterministic convention — no second naming scheme is introduced | PRD REQ-17; consistency | New wave start | Branch name matches `feature/{INIT}-{wn}-{slug}` | unit | W2 |
| REQ-18 | "Continuation" (an existing run/PR already found for this `initiative_id`+`wave_id`) resolves and reuses the existing head ref — zero new branches are created | PRD REQ-18; D2 | Continuation start | No branch-create path is invoked; the existing branch is checked out | unit + verify | W2 |
| REQ-19 | Continuation succeeds even when Gateflow has not previously cloned the repo locally (clone-then-checkout-existing-branch composes with continuation) | PRD REQ-19; composition | Continuation start on a fresh (never-cloned) workspace | Clone and checkout of the existing branch both succeed in one flow | verify | W2 |
| REQ-20 | The harness-readiness check runs after clone/refresh and before any coding-hop dispatch, for any repo not yet marked harness-verified for that Tenant | PRD REQ-20; D6 | Repo not yet verified for this Tenant | Check executes before the Enter-at skill is dispatched | unit + verify | W3 |
| REQ-21 | A repo lacking the expected harness artifacts fails the readiness check (extends the existing check beyond path-exists-only); a harness-enabled repo passes | PRD REQ-21; A-3; D6 | Any harness-readiness check | Non-ready repo (harness artifacts absent) fails; harness-enabled repo passes | unit + verify (positive + negative fixture) | W3 |
| REQ-22 | A harness-ready repo is cached as verified so repeat waves do not re-check on every call; an explicit re-check path exists | PRD REQ-22; efficiency | Repeat wave on an already-verified repo | No redundant check call is made; a re-check is available on demand | unit | W3 |
| REQ-23 | The concurrency check rejects a new run whenever an ACTIVE run already exists for the same `org`+`repo`, regardless of whether `initiative_id`/`wave_id`/`pr_number`/`issue_number` match — broadened from today's narrower key match | PRD REQ-23; D10 | Second start, same repo, different wave/PR/issue, prior run ACTIVE | Rejected with the existing `NO_CONCURRENT_RUN` precondition — no new failure code | unit + verify | W4 |
| REQ-24 | Two initiatives on two different repos are never blocked by each other under the broadened check | PRD REQ-24; D10 | Two starts, different repos, both otherwise eligible | Both authorized; no cross-repo blocking | unit + verify | W4 |
| REQ-25 | No new worktree/lock/isolation mechanism is introduced — one shared working directory per repo remains sufficient | PRD REQ-25; D10 | Any repo | No new isolation infrastructure is present | inspection | W4 |
| REQ-26 | `ForgeClient` gains a method to delete a named branch, using the same DELETE-ref transport shape as the existing branch-update path — no new transport is introduced | PRD REQ-26; D4 | Direct unit call (not exercised via any live route this INIT) | Branch deleted on success; correct API path/method used | unit | W5 |
| REQ-27 | The delete-branch method fails closed (raises, no partial state) on a missing or protected branch | PRD REQ-27; fail-closed | Missing/protected branch | Named error; no silent no-op | unit | W5 |

> **Id convention:** `REQ-*` is canonical, numbered to match the PRD 1:1 for
> traceability. This spec's scope is **REQ-01–REQ-27, REQ-32** only — PRD
> REQ-28–REQ-31 (pin/contract shapes) belong to the `prayog-skills` spec slice
> per the approved impact map scope digest (H2); see Out of scope.
>
> **Behavioral acceptance vs evidence:** condition/event + observable result
> are the product acceptance statement (implementation-neutral). Evidence
> layer names how it will be proved later — module/schema/library choices are
> deferred to feasibility / technical review.

### Target API surface (new routes, this repo)

| Route | Capability | Notes |
|-------|------------|-------|
| `POST /api/v1/tenants` | CAP-01 | Registration; body-only per `http-api-conventions.mdc` |
| `POST /api/v1/tenants/{tenant_id}/users` | CAP-01 | Attach a user (D9) |
| `GET /api/v1/tenants` | CAP-01 | List registered tenants (REQ-32) — never returns the PAT |
| `GET /api/v1/tenants/{tenant_id}` | CAP-01 | Tenant detail: repo list, `workspace_root`, board default (REQ-32) — never returns the PAT |
| *(no new route)* — `POST /api/v1/waves/implement/start` extended | CAP-02, CAP-03, CAP-04, CAP-05 | `workspace_path` becomes optional-and-self-sufficient for Tenant-registered repos; existing route, extended behavior only |

Exact response schema / problem+json field names → **Q-1** (deferred to
gateflow OpenAPI pass, same deferral pattern as prior INITs).

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|-----------------|----------|
| REQ-01 | Missing/malformed required registration field | **400**; 0 rows written | Prevents a half-registered Tenant that later fails opaquely at first use | unit |
| REQ-06 | PAT fails eager per-repo read-access check | **422**; 0 rows written; itemized per-repo reason | A typo'd PAT or missing scope must surface at registration, not mid-wave on a real run (US-3 intent) | unit + verify |
| REQ-04 | Caller not attached to the target tenant, or presents the wrong/absent tenant token | **401** before any lane logic runs | Prevents cross-tenant access via a stale or borrowed token | unit + verify |
| REQ-15 | `workspace_path` omitted, repo not Tenant-registered | **422**; 0 enqueue | Gateflow must never guess a workspace for an unregistered repo — silent guessing would risk operating on the wrong tree | unit + verify |
| — (clone) | Clone fails (auth, network, repo not found) on first use | **422**; 0 enqueue; reason names the repo and the underlying failure class | A bad credential or unreachable repo must fail the API call, not silently degrade the async worker | unit + verify |
| REQ-14 | Refresh finds an existing path that is not a valid checkout of the expected remote | **422**; 0 enqueue; workspace left untouched | Prevents Gateflow from committing/publishing into a stale or wrong-remote tree | unit + verify |
| — (branch fork) | Fork from `develop` fails (missing branch, API/network/permission error) | **422**; 0 enqueue; reason names the underlying failure; no partial branch left behind | Avoids orphaned half-created branches on transient GitHub failures | unit + verify |
| — (continuation) | Continuation's recorded head ref no longer exists on the remote (PR closed / branch deleted out-of-band) | **422**; reason "continuation branch not found on remote" | Prevents silently re-forking a wave whose branch was deleted out-of-band, which would orphan prior work | unit + verify |
| REQ-20/REQ-21 | Harness-readiness check fails for a newly registered/cloned repo | **422**; 0 enqueue; reason names the missing harness artifact | Stops Gateflow from producing work that does not match a repo's actual conventions | unit + verify |
| REQ-23 | Two starts target the same `org`+`repo` while one is ACTIVE | Existing `NO_CONCURRENT_RUN` `PreconditionFailure`; 0 enqueue for the second request | Prevents two waves colliding on one shared working directory (the reason D10 requires no new isolation mechanism) | unit + verify |
| REQ-27 | `delete_branch` called against a missing/protected branch | Fails closed; no partial state; error names the branch | The method is genuinely destructive — silent no-op or partial deletion would be worse than a clear error | unit |

## Out of scope for this repo

- `prayog-skills` pin/workflow/contract shapes (Tenant-aware workspace-prep node,
  branch create-or-reuse node, branch-delete forge action type) — **REQ-28–
  REQ-31**, a distinct contract-change spec owned by
  `drivestream-lab/prayog-skills` per the approved impact map scope digest
  (H2). Gateflow only consumes the remounted pin (0 BROKEN nodes).
- `gateflow-ops` onboarding UI ("Mission Control") — follow-on initiative,
  deferred repo (impact map §3)
- GitHub App installation per tenant — PAT only this INIT (D8); App mode
  deferred
- Per-repo ACL within a tenant — D9; User↔Tenant is the only boundary this
  INIT builds
- Activating branch purge live — capability ships dormant; activation is a
  separate, later decision (D5/G5)
- Any new concurrency/locking/worktree-isolation mechanism — D10; repo-level
  exclusivity is enough
- Changing merge behavior — merge stays human-only at `wave-signoff`,
  unchanged
- Encrypting/rotating the stored PAT, or any secrets-manager integration —
  explicit scope cut this INIT (G1), carried as a risk (see NFR Security), not
  solved here
- A separate git-workspace credential distinct from the tenant PAT — G2;
  single PAT serves both `ForgeClient` and local git this INIT
- Repurposing the dormant JWT `AuthMiddleware`/`tenant_id` scaffolding — G3;
  left exactly as-is (still gates nothing; still in `public_paths`)
- Breaking the existing caller-supplied `workspace_path` path for
  unregistered repos — CAP-02 is additive only (REQ-12)
- Reconciling with `INIT-GATEFLOW-004`'s onboarding "scorecard" categories —
  flagged for cross-initiative coordination (Q-5), not resolved here
- `launchpad` code changes — CAP-04 consumes launchpad's harness artifact
  scheme as a read-only contract (CTR-03); no launchpad repo change

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | `prayog-skills` / prayog-pe-team | gateflow | Parse the pinned `workflow.yaml` / `delivery-contract.yaml` for the new Tenant-aware workspace-prep node shape, branch create-or-reuse node shape, and branch-delete forge action type at the remounted tip | Pin tip (new node/action shapes) | 0 BROKEN nodes on remount; branch-delete action carries `authorization: explicit` | Gateflow does not invent node/action shapes — the pin is dispatch SSOT (ADR consistent with `architecture.mdc`) | Missing/unparseable new shape → fail closed at remount, not at runtime dispatch | This is the contract change itself (not consume-only) — genuine `prayog-skills` spec/PR, reviewed as such | unit (fixture pin) + inspection |
| CTR-02 | GitHub (git + REST API) | gateflow | Outbound: existing `ForgeClient.ensure_branch_from_base`; new `ForgeClient.delete_branch` (REQ-26/27); new local git clone/fetch transport authenticated with the tenant PAT (REQ-10–REQ-15) — first local git execution inside Gateflow | org/repo/branch + Tenant PAT | Branch created/deleted; workspace cloned/refreshed on disk | Local git and `ForgeClient` REST/GraphQL share one credential (G2) — no blast-radius separation | Auth/network/not-found failures fail closed (see Negative and failure paths) | New transport (local git) and new write method (`delete_branch`) — both new this INIT; design in technical review | unit (fixture repo) + verify |
| CTR-03 | `launchpad` | gateflow | Read-only contract: harness artifact scheme (`.harness-pin.yaml` / `.harness/` presence) consumed by the harness-readiness check | Workspace path | Present/absent harness artifacts | Read-only; no launchpad code or API call — filesystem contract only, same as today's stub | Missing artifacts → readiness check fails (REQ-21) | Format unchanged this INIT; newly **consumed** by gateflow (extends `LaunchpadClient.sync_harness` from path-exists-only to a real check) | unit + verify (fixture repo with/without artifacts) |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Per-tenant PAT stored in **plaintext** Postgres — explicit, PM-accepted risk for this INIT's pilot scope (G1), not a security recommendation; never echoed in any API response (REQ-02/32). Same PAT authenticates both `ForgeClient` writes and local git (G2) — no blast-radius separation, explicitly accepted. Tenant-scoped bearer token (G3) replaces the single global `PROGRAMME_SERVICE_TOKEN` pattern for tenant-scoped routes; the dormant JWT `AuthMiddleware`/`tenant_id` scaffolding is left untouched (not repurposed). `delete_branch` (REQ-26/27) ships with zero live outcome edges this INIT (structural dormancy, G5) so its blast radius is proven only in tests. | Unit (no `pat` field in any response); code guard (no `delete_branch` caller in any shipped flow); inspection of G1/G2 carried-risk documentation |
| Reliability | Every new async-phase step (clone/refresh, branch resolve, harness check) fails closed with a named reason rather than silently degrading — see Negative and failure paths. Concurrency check (REQ-23) runs synchronously before any shared-workspace mutation. | unit + verify |
| Performance / capacity | N/A as a product SLO this INIT — fetch-in-place (REQ-13) avoids repeated full clones, which is the only stated latency-relevant behavior; no new capacity claim beyond existing `ForgeClient`/git patterns. Depends on Assumption A-2 (persistent disk). | inspection / verify smoke |
| Observability | Structured logs for tenant registration outcome, clone/refresh mode (clone vs fetch), harness-readiness verdict, and concurrency rejection — no PAT or other secret value logged (per `logging-loguru.mdc`, IDs/statuses as kwargs, never message-interpolated). | unit + inspection |
| Privacy / data handling | Tenant PAT is the only new credential-shaped data; stored plaintext (carried risk, G1), never returned in any response body. User-attach records store an identity (email/handle) only — no other PII beyond what Gateflow already handles for GitHub identities. | inspection |
| Migration / compatibility | Strictly additive: explicit `workspace_path` behavior is unchanged (REQ-12, regression-tested); existing `GithubSettings` global credential path may remain for any non-Tenant-scoped caller. Broadening `NO_CONCURRENT_RUN` to repo scope (REQ-23) could surface latent double-starts that today's narrower key silently allowed — must be unit-tested against representative historical run patterns before the query changes. | unit regression on existing wave-start/orchestrator tests; new unit against the broadened `find_active_run` query |
| Rollback / recovery | Tenant registry rows are additive; disabling the new routes is sufficient rollback with no required data purge this INIT. `delete_branch` ships dormant (zero live outcome edges) — rollback is "do not wire it," not "undo a deletion." Clone/refresh operates on Gateflow-owned workspace directories only — no remote GitHub state is mutated by CAP-02/CAP-03/CAP-04 beyond the existing `ensure_branch_from_base` branch-create path. | inspection |
| Operations / support | Document tenant-onboarding, clone/refresh, and harness-readiness verify commands per wave in `tests/README.md`, consistent with the existing feature-map convention. PE must be able to dogfood one full Tenant-registered-repo implement-lane start end to end without hand-preparing a workspace. | live verify + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | A Tenant's registered repos are on the same GitHub host already reachable by `ForgeClient` (`api_base_url`) — no new GitHub Enterprise/self-hosted transport this INIT | PRD A1; `src/configs/github_settings.py` | PE | confirmed | Product requires a second GitHub host |
| A-2 | Deployment target has a **persistent disk** between runs, so fetch-in-place (REQ-13) is valid without a shared/remote cache | PRD A2 (resolves PRD OQ-5, "not blocking") | PE | assumed, not yet infra-confirmed | Deployment moves to ephemeral/stateless compute |
| A-3 | `LaunchpadClient.sync_harness`'s current no-op stub is the intended integration point for real harness verification (CAP-04), not a placeholder for a different mechanism | PRD A3; `src/infra_services/launchpad_client.py` (already DI-wired, already invoked in `RunOrchestrator.process_job`) | PE | confirmed | A different harness-verification mechanism is required |
| A-4 | `RunRepository.find_active_run`'s existing `org`+`repo` WHERE clause (already present before the narrower key filter) means broadening to repo-scope is a query change, not a new table/index | PRD A4; verified directly — `src/database/postgres/repository/run_store_repository.py:198-227` | PE | confirmed | Broadening requires a schema change |
| A-5 | The Tenant's default board (`project_owner`/`project_number`) follows the exact override precedent `BoardTicketCreateRequest` already establishes — no new board data model | PRD A5; verified directly — `src/models/board_models.py` | PE | confirmed | Board default requires a new data model |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact problem+json / OpenAPI error body field names for the new Tenant/workspace/branch routes (PRD OQ-01 / IM-01) | PE | no | OpenAPI / implement waves | Route paths + 400/401/422 semantics above remain normative; field names deferred to OpenAPI pass | open | pending |
| Q-2 | PE | Exact eager-verification GitHub call for REQ-06/US-3 — repo metadata read vs. a scoped permissions probe (PRD OQ-7 / IM-02) | PE | no | implementation plan | Repo metadata GET per registered repo (cheapest read-only probe) | open | pending |
| Q-3 | PE | Whether the deterministic clone path (`{workspace_root}/{org}/{repo}`, illustrative) needs per-wave subpaths to avoid collision with a *future* worktree-isolation initiative, given D10 explicitly rules out isolation this INIT (PRD OQ-8 / IM-03) | PE | no | whoever revisits D10 later | Single shared per-repo path this INIT; flagged for a future initiative | open | pending |
| Q-4 | PE / architecture | PRD D1 reverses ADR-010's caller-supplied-`workspace_path` assumption for Tenant-registered repos. Does this require a formal ADR-010 amendment (new clause) or a new ADR? Architecture choice is explicitly **not** decided in this spec. | PE | no | spec-technical-review | Technical review proposes the ADR path; do not implement CAP-02 without that decision recorded | open | pending |
| Q-5 | PE | Reconcile CAP-04 (harness-readiness)/REQ-06 (eager PAT verify) with `INIT-GATEFLOW-004`'s onboarding "scorecard" categories ("Harness posture," "GitHub/Forge access") — same PRD Non-Goal, carried for visibility (IM-06) | PE | no | whichever of 004/012 lands second | Ship independently for now; reconcile later if both exist live | open | pending |
| Q-6 | PE | PRD REQ-29 ("0 live outcome edges route to branch-delete in the default walker") describes gateflow's own orchestrator graph, but the approved impact map assigns REQ-28–REQ-31 fully to `prayog-skills`' scope digest. Does gateflow need its own mirrored code-guard/verify assertion (analogous to the existing `test_forge_action_type_excludes_merge` pattern) as part of CAP-06 exit, distinct from the `prayog-skills`-owned REQ-29? | PE | no | technical review / plan §9 for W5 | Yes — add a gateflow-owned code guard proving no shipped flow calls `delete_branch`, cited under REQ-27's evidence, without claiming PRD REQ-29 as this repo's product id | open | pending |
| Q-7 | PM/PE | Impact map IM-04 required PE/tech-lead's explicit, recorded acknowledgment of the G1 plaintext-PAT risk before Gate 1 sign-off. The recorded APPROVED review on the matching PR head uses the standard "Impact map approved" attestation only, with no separate G1 acknowledgment sentence. Gate 1's approval-evidence check (D1) already passed on matching SHA/digest/revision — is a separate, explicit G1 acknowledgment still needed for audit clarity? | PM | no | before implementation begins | Treat the matching APPROVED review as sufficient sign-off (it required reading the PRD's G1 framing); recommend a one-line explicit G1 acknowledgment on the meta or spec PR for audit trail, but do not block on it | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #32 head `7440254…` = tech-lead APPROVED review `commit_id`; label `impact-map-lgtm`; H1 digest match; H3 rev 1; H2 gateflow affected `sha256:85e75d8b…`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | CAP-01…06 map to REQ-01…27, REQ-32; every REQ cites PRD CAP/REQ/D/G/US |
| D3 Repo-bounded scope | PASS | Matches H2 payload exactly (`REQ-01…27,32`); REQ-28–31 explicitly out of scope (prayog-skills); gateflow-ops deferred; prayog-meta not eng delivery |
| D4 Observable acceptance | PASS | Each REQ has condition/event, observable result, evidence layer; module/ADR choices deferred to Q-4/Q-6 |
| D5 Negative/failure paths | PASS | Covers PRD error table (400/401/422/PreconditionFailure) + why-it-matters for each |
| D6 Assumptions/questions | PASS | A-1…A-5 confirmed with direct code evidence; Q-1…Q-7 all non-blocking with recorded defaults |
| D7 Cross-repository contracts | PASS | CTR-01…03 semantic (logical operation, invariants, errors); no architecture/transport decisions in the table |
| D8 NFR applicability | PASS | All 8 areas specified or N/A with reason |
| D9 As-built alignment | PASS | Existing vs changed vs new distinguished with direct file/line evidence (Path.cwd() fallback, ForgeClient method inventory, LaunchpadClient stub, find_active_run WHERE clause, dormant JWT middleware, global GithubSettings) |
| D10 Dependency order | PASS | Matches impact map §7: `prayog-skills` contract PR → gateflow W0→W1→W2→W3→W4→W5 |
| D11 Zero unresolved blockers | PASS | No blocking PM/PE/domain question remains; Q-1…Q-7 non-blocking with explicit defaults; IM-04 addressed via Q-7 |
| D12 Output completeness | PASS | Header H4, all tables, check summary, outcome, PR readiness, dev review present; no placeholders presented as fact |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on the current meta PR head with matching digest/revision/scope; zero material unresolved questions after the clarification loop (Q-1…Q-7 all non-blocking with recorded defaults, including the G1 acknowledgment residual in Q-7).

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full traceability; no material blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-012-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-012] Spec — Tenant registry and workspace/branch lifecycle (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`, `docs/specification/README.md` (active-initiative pointer update) |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` / `/open-draft-pr` — do not commit/push/open PR inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** Persist the draft locally, present
this section in chat, and ask whether to authorize Forge publish
(`/commit-workspace` / `/open-draft-pr` or Gateflow ForgeClient). Continue only
after explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-012 — Tenant registry and workspace/branch lifecycle (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/32
- Approved meta head: `74402540efd98527014b4706d0d29bda1242b6cf`
- Impact-map revision: 1
- PRD digest: `sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b`
- Repo scope digest: `sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678`

## Spec path

`docs/specification/product/INIT-GATEFLOW-012-gateflow.md`

## Summary

- Full gateflow scope: Tenant registry (CAP-01) + workspace/branch lifecycle
  (CAP-02–05) + dormant branch-purge method (CAP-06 gateflow half); REQ-01…27,
  REQ-32 — 28 requirements
- Waves W0–W5 per PRD §5 (gateflow-scoped)
- `prayog-skills` contract shapes (REQ-28–31) are a separate spec slice, not
  covered here
- Open engineering questions: Q-1…Q-7 (non-blocking; defaults documented)

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

- PRD: `prayog-meta/prd/INIT-GATEFLOW-012.md` @ meta PR #32
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-012.md` revision 1
- Predecessor: [`INIT-GATEFLOW-010-gateflow.md`](INIT-GATEFLOW-010-gateflow.md) (eng-lane pin tip executor parity — this INIT extends that executor's workspace assumptions)
- Related, independent: [`INIT-GATEFLOW-011-gateflow.md`](INIT-GATEFLOW-011-gateflow.md) (Day-1 visibility — no dependency either direction)
- Related, unreconciled overlap (Q-5): `INIT-GATEFLOW-004` onboarding scorecard — not present in this repo's `product/` tree (see PRD Non-Goals)
- As-built: `docs/specification/as-built/implementation-status.md`
- Architecture: [`adr-010`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted** — implement-intake authority; D1 reversal routed to technical review per Q-4), [`adr-009`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted** — forge mutate/publish authority, unaffected)
- Pin: `prayog-skills` @ `v0.5.0-rc.2` today; new node/action shapes land as a separate contract PR (CTR-01)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
    digest: sha256:697dc535971f1a25fa4843019a9266abc6437ee8706b2dc8b8a3c0498754f6a4
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-012
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/32"
    meta_pr_head: "74402540efd98527014b4706d0d29bda1242b6cf"
    map_revision: 1
    prd_digest: "sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b"
    scope_digest: "sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678"
    d_checks: pass
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4,Q-5,Q-6,Q-7"
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-012] Spec — Tenant registry and workspace/branch lifecycle (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-012-gateflow.md
```
