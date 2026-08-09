# INIT-GATEFLOW-013 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-013.md` |
| PRD digest (H1) | `sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/33 |
| Meta PR approved head (G1) | `59301dce846043b8a4e70057a81dfa67a4868ece` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-013.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e` |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/33#pullrequestreview-4889131742) 2026-08-08T15:58:21Z on `59301dce846043b8a4e70057a81dfa67a4868ece` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-013.md`; label `impact-map-lgtm` |
| Architecture constraints (existing) | [`adr-011`](../adr/adr-011-tenant-scoped-bearer-token-trust-zone.md) (**Accepted** — tenant bearer trust zone; new programme-connect / select / refresh routes remain tenant-scoped). [`adr-010`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted** — workspace authority; this INIT reuses the Tenant workspace / clone-or-fetch path from INIT-GATEFLOW-012; does not reopen caller-supplied `workspace_path` rules). [`adr-009`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted** — forge mutate/publish; unaffected). How Launchpad `status` is provisioned and invoked (IM-02 / OQ-2) is **not decided here** — routed to technical review (Q-2). |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-08 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure — see
> `prayog-skills/references/artifact-write-contract.md`.

## Overview

Gateflow delivers **programme-first tenant onboarding**: a tenant connects once to
its programme's shared meta repo, reads a catalogue derived from that synced
copy, chooses (and later deselects) repos from that catalogue only, gets each
chosen repo set up via the existing clone-or-fetch path, and receives a **real**
Launchpad `status` readiness verdict (inspect-only) that becomes the stored
readiness answer for repos added through this flow. Hand-typed `repos[]` at
tenant registration is **retired** for new and existing tenants. Repos that
predate this initiative keep their existing stored readiness answer untouched.

**Scope boundary (this repo only):** CAP-01…CAP-07 / PRD REQ-01…REQ-28 per the
approved impact-map H2 payload. Out of this repo: `gateflow-ops` UI (deferred),
any Launchpad mutate/apply, `prayog-skills` contract/pin changes (not affected),
and provider-side changes in `prayog-meta` / `launchpad` (read-only consume via
CTR-01 / CTR-02).

**Ownership:** this spec defines observable behavior, acceptance, field meaning,
invariants, errors, and compatibility. Module/schema/route shape, Launchpad
binary provisioning, and transport realization are **deferred to feasibility /
technical review** — not decided here.

**As-built baseline (2026-08-08, verified against local checkout):**

| Existing behavior | Evidence |
|---|---|
| `TenantRegisterRequest.repos` is required, non-empty (`Field(min_length=1)`) | `src/models/tenant_models.py` |
| `TenantService.register_tenant` rejects an empty `repos` list before persist | `src/business_services/tenant_service.py` |
| `TenantGitWorkspaceClient.resolve_workspace` is generic `(org, repo)` clone-or-fetch with per-repo lock | `src/infra_services/tenant_git_workspace_client.py` |
| `GithubPatProbe.verify_read_access` is a per-call, caller-credential probe used at registration | `src/infra_services/github_pat_probe.py` |
| `tenant_repos.harness_verified` exists; `TenantService.mark_harness_verified` / `is_harness_verified` keyed by `(org, repo)` | `src/business_services/tenant_service.py`, `src/database/postgres/schema/tenant_schema.py` |
| Harness-readiness today is file-presence via `LaunchpadClient.sync_harness` (INIT-GATEFLOW-012 W3 — live) | as-built W3 matrix; `src/infra_services/launchpad_client.py` |
| No programme-connection or catalogue API exists yet | route/model inventory under `src/api/v1/`, `src/models/` |
| `prayog-meta` already publishes `config/programme.yaml` + `config/service-catalog-<org>.yaml` | meta checkout `config/` (CTR-01 source) |

**Delivery waves (product-normative; PRD §5, gateflow-scoped):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Connect to the programme + read the shared catalogue | REQ-01–REQ-07, REQ-28 |
| **W1** | Choose / deselect repos — retires hand-typed tenant setup | REQ-08–REQ-13, REQ-26–REQ-27 |
| **W2** | Set up chosen repos | REQ-14–REQ-16 |
| **W3** | Real readiness check + one trustworthy answer | REQ-17–REQ-23 |
| **W4** | Stay current (catalogue refresh) | REQ-24–REQ-25 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | A tenant can connect to its programme's shared repo (identified by org/repo/ref); connecting clones/syncs it using the same clone-or-fetch mechanism already used for any other tenant repo — no second git mechanism | PRD REQ-01; CAP-01; US-1; D2 | Connect call with programme org/repo/ref | Shared repo present in Gateflow's own synced copy for that tenant | unit + verify | W0 |
| REQ-02 | Connecting authenticates with the tenant's existing access credential; no new credential type is introduced | PRD REQ-02; CAP-01; D6 | Connect call | Same auth check as every other tenant-scoped call | unit | W0 |
| REQ-03 | The tenant's existing credential (already used for its other repos) is reused to read the shared repo; no separate, narrower credential is created | PRD REQ-03; CAP-01; D7 | Connect call | Same credential used; no new credential field/table appears in any API contract | unit + inspection | W0 |
| REQ-04 | Connect failure (credential, network, not found) is rejected with a specific, named reason; nothing partial is left behind | PRD REQ-04; CAP-01; fail-closed | Bad credential / unreachable / missing programme repo | Named reason; no partial local programme copy retained | unit + verify | W0 |
| REQ-05 | After connecting, Gateflow reads the programme's shared records from its synced copy and produces a list of candidate repos | PRD REQ-05; CAP-02; US-2; D1 | Any catalogue-read call after connect | Candidate list matches the shared records in the synced copy | unit + verify | W0 |
| REQ-06 | If the shared records don't match the expected shape, the read is rejected with a specific reason — not guessed at or partially returned | PRD REQ-06; CAP-02; fail-closed | Malformed/missing programme records | Named reason; no partial candidate list | unit + verify | W0 |
| REQ-07 | The candidate list reflects the most recently synced copy — not a value frozen at first connect | PRD REQ-07; CAP-02; D4 | After a catalogue refresh (CAP-07) | List includes anything added since the prior sync | unit + verify | W0 |
| REQ-08 | An operator can select and save a subset of the current candidate list as the tenant's active repos | PRD REQ-08; CAP-03; US-3; D4 | Selection call | Selected subset persisted as the tenant's active repos | unit + verify | W1 |
| REQ-09 | Any repo not on the current candidate list is rejected from selection outright | PRD REQ-09; CAP-03; D1 | Selection includes an out-of-catalogue repo | Rejected; 0 change to active list | unit + verify | W1 |
| REQ-10 | A selection can be changed later; every change is checked against the *current* candidate list | PRD REQ-10; CAP-03; D4 | Re-selection after catalogue changes | New selection validated against the current catalogue, not a stale snapshot | unit + verify | W1 |
| REQ-11 | Selecting a repo the tenant doesn't already have runs the same read-access probe already used at tenant setup, before the repo is added | PRD REQ-11; CAP-03; A3 | New repo selected | Probe runs; failure rejects the selection with a named reason; 0 change to active list | unit + verify | W1 |
| REQ-12 | Setting up a brand-new tenant no longer requires or accepts a starting repo list; a repo list provided at setup is rejected | PRD REQ-12; CAP-03; D1; D11 | New tenant setup with a repo list provided | Rejected; tenant not created with repos via this path; 0 rows written for that attempt | unit + verify (regression vs today's required-non-empty `repos`) | W1 |
| REQ-13 | Selection (CAP-03) is the only way any tenant, new or already existing, gains a repo from this point forward | PRD REQ-13; CAP-03; D1; D11 | Any attempt to add a repo by any other API path | No such path remains on the API surface | inspection + code guard | W1 |
| REQ-14 | Every newly selected repo is cloned (and sub-projects initialized where present) using the exact same mechanism already used for repo setup | PRD REQ-14; CAP-04; US-4; D2 | New repo selected | Repo present and usable under the tenant workspace rules already established by INIT-GATEFLOW-012 | unit + verify | W2 |
| REQ-15 | Setting up each selected repo happens independently; one repo's failure never blocks or delays any other repo in the same selection | PRD REQ-15; CAP-04; D5 | Mixed success/failure batch | Failing repo isolated; others proceed | unit + verify | W2 |
| REQ-16 | Each repo's setup result is reported individually, with a specific reason on failure | PRD REQ-16; CAP-04; D5 | Any selection/setup batch | Per-repo result; never a single bundled all-or-nothing outcome | unit + verify | W2 |
| REQ-17 | For every selected, set-up repo, Gateflow asks the programme's setup tool to run its full readiness check, pointed at Gateflow's own synced copy of the programme's records (depends on A-2 / OQ-2) | PRD REQ-17; CAP-05; US-5; D3 | Repo set up after selection | Real check runs; file-presence-only is not the readiness answer for this repo | unit + verify | W3 |
| REQ-18 | The setup tool is only ever asked questions — never asked to fix, install, or change anything, for any repo or the shared repo itself | PRD REQ-18; CAP-05; D3 | Any readiness-check call | No mutating setup-tool call is made | code guard + verify | W3 |
| REQ-19 | Each repo's check runs and reports independently, matching CAP-04's partial-success pattern | PRD REQ-19; CAP-05; D5 | Mixed pass/fail check batch | Failing repo isolated; others proceed | unit + verify | W3 |
| REQ-20 | If the setup tool itself can't run, that failure is reported distinctly from any individual repo's check result (depends on A-2 / OQ-2) | PRD REQ-20; CAP-05; fail-closed | Tool unavailable/misconfigured | Distinct named reason; no repo wrongly marked ready or not-ready by this failure | unit + verify | W3 |
| REQ-21 | The real check's result becomes the stored readiness answer for every repo added through this initiative, replacing today's simpler check for those repos | PRD REQ-21; CAP-06; US-6; D9 | New repo, check completes | Stored answer reflects the real check | unit + verify | W3 |
| REQ-22 | A repo a tenant already had before this initiative shipped keeps its existing stored readiness answer untouched | PRD REQ-22; CAP-06; D9 | Any repo predating this initiative | No write from this INIT's readiness path touches that repo's existing record | unit + code guard | W3 |
| REQ-23 | For a repo whose readiness is answered by the real check (REQ-21), a stored readiness answer can be refreshed on demand without removing and re-selecting the repo | PRD REQ-23; CAP-06; efficiency; OQ-9 narrows legacy | On-demand refresh-check call for an in-scope repo | New check result replaces the stored answer in place | unit + verify | W3 |
| REQ-24 | A connected tenant can refresh its copy of the programme's shared records at any time | PRD REQ-24; CAP-07; US-7; D4 | Refresh call | Synced copy updated | unit + verify | W4 |
| REQ-25 | Refreshing never changes an already-selected repo on its own — it only changes what's newly available to select | PRD REQ-25; CAP-07; D4 | Refresh after catalogue growth | Existing selections untouched; new candidates appear | unit + verify | W4 |
| REQ-26 | A repo can be deselected from the tenant's active list; deselecting does not delete its local clone or alter its stored readiness answer — only active-list membership changes | PRD REQ-26; CAP-03; D9 | Deselect call | Clone and readiness record untouched; only list membership changes | unit + verify | W1 |
| REQ-27 | Deselecting a repo with a wave currently running on it is rejected | PRD REQ-27; CAP-03; fail-closed | Deselect attempted while a wave is in flight for that repo | Rejected; repo remains selected; 0 change to active list | unit + verify | W1 |
| REQ-28 | A tenant has exactly one active programme connection at a time; connecting again refreshes/re-syncs that same connection rather than creating a second one | PRD REQ-28; CAP-01; D1 | Connect call while already connected | Same connection record updated; no second connection record created | unit + verify | W0 |

> **Id convention:** `REQ-*` is canonical, numbered to match the PRD 1:1 for
> traceability. This spec's scope is **REQ-01–REQ-28** only — matches impact-map
> H2 capabilities CAP-01…07 / REQ-01…28.
>
> **Behavioral acceptance vs evidence:** condition/event + observable result
> are the product acceptance statement (implementation-neutral). Evidence
> layer names how it will be proved later — module/schema/library choices are
> deferred to feasibility / technical review.

### Target capability surface (illustrative — engineering owns exact routes)

| Capability | Notes |
|------------|-------|
| Connect a tenant to its programme | New; CAP-01 / REQ-01–04, REQ-28 |
| Read the current catalogue | New; CAP-02 / REQ-05–07 |
| Choose / update / deselect the active repo list | New; CAP-03 / REQ-08–13, REQ-26–27 |
| Set up chosen repos | May be automatic on selection or a distinct call; CAP-04 / REQ-14–16 |
| Run / refresh the real readiness check | New; CAP-05/CAP-06 / REQ-17–23 |
| Refresh the catalogue | New; CAP-07 / REQ-24–25 |
| *(changed)* Tenant registration | Existing `POST /api/v1/tenants`; repo-list input removed or rejected when non-empty per REQ-12 |

Exact routes, request/response shapes, and error body fields → **Q-1**
(deferred to OpenAPI / implement waves; same deferral pattern as prior INITs).

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|----------------|----------|
| REQ-12 | New tenant registration includes a repo list | Rejected; 0 rows written | Prevents reintroducing hand-typed repos after D1/D11 retirement | unit + verify |
| REQ-04 | Programme connect fails (credential, network, not found) | Named reason; no partial programme checkout left | A half-connected tenant would produce empty/stale catalogues and opaque later failures | unit + verify |
| REQ-06 | Shared records missing or wrong shape | Named reason; no partial candidate list | Silent empty/partial catalogues would look like “programme owns nothing” | unit + verify |
| REQ-09 | Selection includes an out-of-catalogue repo | Rejected; 0 change to active list | Catalogue is the only discovery source (D1) — no bypass | unit + verify |
| REQ-11 | Newly selected repo fails read-access probe | Rejected with named reason; 0 change to active list | Catch inaccessible/mistyped catalogue entries before they become active | unit + verify |
| REQ-15 / REQ-16 | One repo fails setup in a multi-repo selection | That repo reported with its own reason; others proceed | Partial-success is the product contract (D5) — one bad repo must not strand the batch | unit + verify |
| REQ-20 | Setup tool unavailable/misconfigured | Distinct named reason; no repo marked ready or not-ready by this failure | Must not confuse “tool broken” with “repo not ready” | unit + verify |
| REQ-19 | One repo fails real check in a batch | That repo isolated; others proceed | Same partial-success contract as setup | unit + verify |
| REQ-24 | Catalogue refresh fails | Named reason; existing selections and readiness answers untouched | Refresh must never wipe a working tenant state | unit + verify |
| REQ-27 | Deselect while a wave is in flight on that repo | Rejected; repo remains selected | Avoid removing an active workspace under a running wave | unit + verify |
| Q-3 / OQ-1 | Wave start on a selected repo never checked, or last check failed | **Default if deferred:** fail closed (block start) — see Q-3 | Prevents waves on repos with unknown/failed readiness after CAP-05 takeover | unit + verify (when locked) |

## Out of scope for this repo

- `gateflow-ops` onboarding UI / dashboard — deferred (impact map §3; PRD D10)
- Any Launchpad mutate / apply / install / fix call — inspect-only (PRD D3; Non-Goals)
- Provider-side code or schema changes in `prayog-meta` or `launchpad` — consume-only (CTR-01, CTR-02)
- `prayog-skills` pin / workflow / contract shape changes — not affected (impact map §5)
- Selecting a repo that is not on the programme catalogue — deliberately closed (Non-Goals)
- Keeping any hand-typed repo-add path for any tenant — retired (D1/D11; Non-Goals)
- Retroactively re-checking or resetting repos that predate this initiative — untouched (REQ-22; D9)
- Per-repo ACL within a tenant — unchanged from INIT-GATEFLOW-012 (Non-Goals)
- Changing how a wave runs once it has started — out of scope (Non-Goals); wave-*start* gating when readiness is missing/failed is Q-3 only
- A separate, narrower credential just for reading programme records — same tenant credential (D6/D7)
- Relying on an individual operator's machine-local Launchpad client registry — checks point at Gateflow's synced meta copy (D3)
- Reconciling with `INIT-GATEFLOW-004` onboarding scorecard — open coordination (Q-8 / IM-09); not resolved here

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | `prayog-meta` / prayog-pe-team | gateflow | Read programme identity + service catalogue from the synced meta checkout (`config/programme.yaml` + `config/service-catalog-<org>.yaml`) to produce the candidate repo list (CAP-01/CAP-02, REQ-01–07) | Synced meta tree paths; programme org identity | Candidate repo list (org/repo and catalogue fields needed for selection) | Read-only; first Gateflow consumer — shape is load-bearing; no silent guess on unknown shape (REQ-06) | Missing/malformed → named reject; no partial list | Provider makes no code change this INIT; consumer must fail closed on unexpected shape | unit (fixture meta tree) + verify |
| CTR-02 | `launchpad` / prayog-pe-team | gateflow | Read-only readiness verdict via Launchpad `status` against a repo workspace, with programme records supplied from Gateflow's synced meta copy (`--config-dir` / `--repo` / `--meta` semantics) — CAP-05/CAP-06, REQ-17–23 | Repo workspace path + synced meta config dir | Pass/fail (or structured verdict) usable as the stored readiness answer | Inspect-only — never apply/mutate (REQ-18); never use operator-local client registry as the programme source | Tool unavailable → distinct named failure (REQ-20); per-repo check failure isolated (REQ-19) | First Gateflow consumer of CLI output shape; version-skew policy is Q-5 (OQ-5) | unit (fixture) + verify |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Tenant PAT blast radius widens to include the programme meta repo (same credential, larger read set) — same *kind* of risk already accepted under INIT-GATEFLOW-012 / ADR-011; named explicitly, not a new secrets model. Setup tool is inspect-only (REQ-18). No operator-machine dependency for programme records. PAT never logged or echoed. | unit + inspection |
| Reliability | Connect, catalogue parse, selection probe, per-repo setup, and per-repo readiness check fail closed with named reasons; batch operations are partial-success (D5). Tool-unavailable is distinct from repo-not-ready (REQ-20). | unit + verify |
| Performance / capacity | N/A as a product SLO this INIT — clone-or-fetch reuse and on-demand refresh (default for OQ-3 / Q-4) are the only latency-relevant behaviors; no new capacity claim. | inspection |
| Observability | Structured logs for connect outcome, catalogue parse/reject, selection accept/reject, per-repo setup result, per-repo readiness verdict, tool-unavailable, and refresh outcome — IDs/statuses as kwargs; never PAT or secret values (`logging-loguru.mdc`). | unit + inspection |
| Privacy / data handling | No new PII categories beyond existing tenant identity/PAT handling; programme catalogue is organisational repo metadata, not end-user personal data. | inspection |
| Migration / compatibility | Breaking cutover: registration no longer accepts `repos[]` (REQ-12/13). Existing tenants keep pre-existing repo rows and readiness answers (REQ-22). Dependents of hand-typed registration (scripts/runbooks/verify helpers) must be inventoried before W1 merge (Q-6 / IM-06) — residual Gate 1 blocker carried as a process gate, not a silent default. | unit regression + inventory before W1 |
| Rollback / recovery | New programme-connection / catalogue / selection APIs are additive; rollback is disable those routes. REQ-12/13 registration tightening is a deliberate breaking change — rollback restores accepting `repos[]` only via an explicit revert, not a dual path. Readiness write path must remain unable to rewrite pre-INIT rows (REQ-22) even under partial deploy. | inspection + code guard |
| Operations / support | Document connect, catalogue, selection, setup, readiness, and refresh verify commands per wave in `tests/README.md`. PE must dogfood one full connect→catalogue→select→setup→real-check path. Launchpad binary provisioning (Q-2) is an ops prerequisite for W3 live verify. | live verify + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | The programme's shared meta repo is reachable through the same git transport already used for tenant repos — no new network path or protocol | PRD A1; INIT-GATEFLOW-012 `TenantGitWorkspaceClient` live | PE | confirmed | Product requires a second host/protocol for meta |
| A-2 | Gateflow's execution environment can run the programme setup tool (Launchpad) as a new runtime dependency | PRD A2; OQ-2 / IM-02 | PE/Ops | assumed — provisioning undecided (Q-2) | Environment cannot provision Launchpad at all |
| A-3 | `GithubPatProbe.verify_read_access` can be reused unchanged at selection time | PRD A3; `src/infra_services/github_pat_probe.py` | PE | confirmed | Selection requires a different probe |
| A-4 | This INIT's readiness write path only ever updates repos added through CAP-03 selection going forward; it never iterates or rewrites pre-existing `tenant_repos` readiness rows | PRD A4; D9; REQ-22 | PE | confirmed by design intent | Product requires forced re-check of legacy rows |
| A-5 | INIT-GATEFLOW-012 tenant registry + workspace lifecycle remain the baseline (merged / human-approved); this INIT composes on top rather than replacing registry mechanics | as-built INIT-012 W0–W5; PRD D8 | PE | confirmed | 012 capabilities regress or are removed |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact routes, request/response field names, and problem+json error bodies for connect / catalogue / select / setup / readiness / refresh | PE | no | OpenAPI / implement waves | Capability surface + 4xx semantics above remain normative; field names deferred to OpenAPI pass | open | pending |
| Q-2 | PE/Ops | Where the Launchpad binary runs from inside Gateflow's execution environment — preinstalled image vs fetched on demand (PRD OQ-2 / IM-02) | PE/Ops | no | technical review / before W3 coding | **None** — must be explicitly provisioned before W3 implementation and live verify; Gate 1 approved with this residual | open | pending |
| Q-3 | PE | Wave-start behavior when a selected repo was never inspected, or its last inspect failed (PRD OQ-1 / IM-01) | PE | no | implementation plan | Fail closed (block start), consistent with programme fail-closed pattern | open | pending |
| Q-4 | PE | Catalogue refresh trigger — on-demand only, scheduled, or both (PRD OQ-3 / IM-03) | PE | no | implementation plan | On-demand only this INIT (REQ-24); scheduling is a follow-up | open | pending |
| Q-5 | PE | Version-skew policy when Gateflow's available Launchpad binary does not match a repo's pinned harness profile (PRD OQ-5 / IM-05) | PE | no | before W3 implementation | **None** — needs an explicit compatibility policy before coding the verdict mapping | open | pending |
| Q-6 | PM/PE | What currently depends on hand-typed tenant setup (scripts, runbooks, verify helpers, habits) that breaks once REQ-12/13 retire it (PRD OQ-8 / IM-06) | PM | no | before W1 merge / cutover lock | **None** — inventory must complete before W1 merge; Gate 1 approved with this residual | open | pending |
| Q-7 | PE | For a repo that predates this initiative (no programme-connection-backed real check yet), can an operator request a fresh readiness check — and if so via old file-presence or only after connect (PRD OQ-9 / IM-07)? REQ-23 in this spec is scoped to real-check-backed repos | PE | no | before W3 implementation | **None** — genuinely undecided in PRD; do not invent a legacy force-recheck path in plan until resolved | open | pending |
| Q-8 | PE | Coordination with `INIT-GATEFLOW-004` onboarding scorecard now that CAP-05/CAP-06 supersede 012's harness check (PRD Non-Goals / IM-09) | PE | no | whichever of 004/013 lands second | Ship independently; reconcile later if both exist live | open | pending |
| Q-9 | PE | Sub-project (submodule) credential handling during repo setup (PRD OQ-4 / IM-04) | PE | no | implementation plan | Assume tenant credential already covers same-org submodules until proven otherwise | open | pending |
| Q-10 | PM/PE | Direct notice to INIT-GATEFLOW-012 owners that this INIT takes over the live harness-readiness gate and retires hand-typed repo-add (IM-08) | PM | no | before gateflow Draft spec PR opens | Proceed — PRD D9 already frames the handover; record notice on spec PR description | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #33 head `59301dce…` = tech-lead APPROVED review `commit_id`; label `impact-map-lgtm`; H1 digest match; H3 rev 1; H2 gateflow affected `sha256:17921af2…`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | CAP-01…07 map to REQ-01…28; every REQ cites PRD CAP/REQ/D/US/A |
| D3 Repo-bounded scope | PASS | Matches H2 payload (CAP-01…07, REQ-01…28, CTR-01/02); gateflow-ops deferred; prayog-skills not affected; meta/launchpad consume-only |
| D4 Observable acceptance | PASS | Each REQ has condition/event, observable result, evidence layer; route/module/ADR choices deferred to Q-1/Q-2 |
| D5 Negative/failure paths | PASS | Covers PRD error table + why-it-matters; partial-success and tool-unavailable distinguished |
| D6 Assumptions/questions | PASS | A-1…A-5 evidenced; Q-1…Q-10 have lane/owner/blocking/required-by/default/status; no Blocking=yes rows |
| D7 Cross-repository contracts | PASS | CTR-01/CTR-02 semantic (logical operation, field meaning, invariants, errors); transport/module realization deferred |
| D8 NFR applicability | PASS | All 8 areas specified or N/A with reason |
| D9 As-built alignment | PASS | Existing vs changed vs new distinguished with direct evidence (required `repos[]`, harness_verified, git-workspace client, PAT probe, file-presence readiness) |
| D10 Dependency order | PASS | Matches impact map §7: 012 shipped → W0→W1→W2→W3→W4; no cross-repo build gate |
| D11 Zero unresolved blockers | PASS | No Blocking=yes Spec questions; IM-02/IM-06 carried as Q-2/Q-6 process gates before W3/W1 coding (Gate 1 already approved with those residuals) |
| D12 Output completeness | PASS | Header H4, all tables, check summary, outcome, PR readiness, dev review, handoff envelope present |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on the current meta PR head with matching digest/revision/scope; zero material acceptance/scope blockers after clarification classification (IM-02/IM-06/OQ-* routed as non-blocking Spec questions with required-by stages and explicit no-default process gates where the map provided none).

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full PRD traceability; no material acceptance blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-013-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-013] Spec — Programme-first onboarding and real readiness checks (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md`, `docs/specification/README.md` (active-initiative pointer update) |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` / `/open-draft-pr` — do not commit/push/open PR inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none for Draft publish; process gates Q-2 (before W3) and Q-6 (before W1 merge) remain open |

**No GitHub side effects have occurred.** Persist the draft locally, present
this section in chat, and ask whether to authorize Forge publish
(`/commit-workspace` / `/open-draft-pr` or Gateflow ForgeClient). Continue only
after explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-013 — Programme-first onboarding, catalogue-driven repo selection,
and real Launchpad readiness checks (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/33
- Approved meta head: `59301dce846043b8a4e70057a81dfa67a4868ece`
- Impact-map revision: 1
- PRD digest: `sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1`
- Repo scope digest: `sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e`

## Spec path

`docs/specification/product/INIT-GATEFLOW-013-gateflow.md`

## Summary

- Full gateflow scope: CAP-01…07 / REQ-01…28 — programme connect, catalogue,
  select/deselect (retires hand-typed `repos[]`), setup, real readiness,
  refresh
- Waves W0–W4 per PRD §5
- Cross-service consume-only contracts: CTR-01 (prayog-meta catalogue files),
  CTR-02 (launchpad `status` inspect-only)
- Open engineering questions: Q-1…Q-10 (non-blocking; Q-2/Q-6 are process
  gates before W3/W1 coding)

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

- PRD: `prayog-meta/prd/INIT-GATEFLOW-013.md` @ meta PR #33
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-013.md` revision 1
- Resolution: `prayog-meta/prd/reports/Resolution-INIT-GATEFLOW-013.md`
- Predecessor: [`INIT-GATEFLOW-012-gateflow.md`](INIT-GATEFLOW-012-gateflow.md) (tenant registry + workspace/branch lifecycle — this INIT takes over harness-readiness ownership for newly selected repos and retires hand-typed repo-add)
- Related, unreconciled (Q-8): `INIT-GATEFLOW-004` onboarding scorecard — not present in this repo's `product/` tree
- As-built: `docs/specification/as-built/implementation-status.md`
- Architecture: [`adr-011`](../adr/adr-011-tenant-scoped-bearer-token-trust-zone.md), [`adr-010`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md), [`adr-009`](../adr/adr-009-pin-forge-publish-mutate-authority.md)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-013
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/33"
    meta_pr_head: "59301dce846043b8a4e70057a81dfa67a4868ece"
    map_revision: 1
    source_prd_digest: sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1
    repo_scope_digest: sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e
    process_gates:
      - Q-2
      - Q-6
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-013] Spec — Programme-first onboarding and real readiness checks (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-013-gateflow.md
```
