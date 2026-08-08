# Technical Design Document — INIT-GATEFLOW-012

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-012 |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Spec digest | `sha256:b8a490e7e7c7ceb02f18097d9164611086d2c7aecd1d9c2e0a6b0a7495a13190` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-012.md` |
| PRD digest | `sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-012.md` / `1` |
| Repo scope digest | `sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678` |
| Approved meta PR head | `74402540efd98527014b4706d0d29bda1242b6cf` |
| Source freshness | **CURRENT** — H1/H2/H3 match live meta @ `7440254…`; label `impact-map-lgtm` unchanged since feasibility |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-08 |
| Branch | `chore/INIT-GATEFLOW-012-spec-gateflow` (spec PR [#183](https://github.com/drivestream-lab/gateflow/pull/183) — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-012` |
| Status | Accepted |
| Review deadline | 2026-08-15 (5 business days) |
| Deciders | PE: @nikd10x — explicit acceptance recorded 2026-08-08 via Cursor chat, Draft spec PR [#183](https://github.com/drivestream-lab/gateflow/pull/183) |

---

## 1. Problem statement

Today's implement-lane job path resolves exactly one workspace-source decider
(caller-or-nothing), one branch-creation primitive invoked unconditionally at
every run start, one harness check that only probes filesystem existence, and
one repository-conflict predicate keyed narrower than the physical resource
(a shared per-repo directory) it protects (REQ-10, REQ-12, REQ-15, REQ-16–19,
REQ-20–22, REQ-23–25). This initiative also introduces a data aggregate and
an authentication mechanism that do not exist in any form today (REQ-01–09,
REQ-32; REQ-03/REQ-04). The sections below fix module boundaries, interface
contracts, and test/error/observability/data policy for each.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/models/tenant_models.py` | new | create | models |
| `src/database/postgres/schema/tenant_schema.py` | new | create | schema (agent updates `schema/` + `postgres_migrations/env.py` imports only — human owns the `versions/` revision per `database-migrations.mdc`) |
| `src/database/postgres/repository/tenant_repository.py` | new | create | repository |
| `src/business_services/tenant_service.py` | new | create | business |
| `src/api/v1/tenant_routes.py` | new | create | api |
| `src/api/v1/tenant_token.py` | new | create | api (dependency; mirrors `programme_token.py`'s existing shape) |
| `src/infra_services/github_pat_probe.py` (illustrative name) | new | create | infra — ad-hoc, per-call PAT read-access probe; structurally distinct from `ForgeClient`'s singleton fixed-credential transport |
| `src/infra_services/tenant_git_workspace_client.py` (illustrative name) | new | create | infra — clone/fetch via tenant PAT; subprocess `git` transport (see §9 FF-04) |
| `src/business_services/run_orchestrator.py` | exists | extend | business — replace the `Path.cwd()` fallback (line 237) with CAP-02/03/04 composition |
| `src/infra_services/launchpad_client.py` | exists (stub) | extend | infra — `sync_harness` real artifact check + verified-cache flag |
| `src/infra_services/forge_client.py` | exists | extend | infra — new `delete_branch` method |
| `src/database/postgres/repository/run_store_repository.py` | exists | extend | repository — `find_active_run` query broadening |

**Boundary diagram (text):**

```
Caller → [tenant_routes.py] → [TenantService] → [TenantRepository] → [tenants / tenant_repos / tenant_users]
                                    │
                                    └→ [github_pat_probe] (per-call, caller-submitted PAT — not ForgeClient's credential)

Caller → [tenant_token.py dependency] → [TenantRepository] (token → tenant lookup)

Job worker → [run_orchestrator] → [tenant_git_workspace_client] → local disk workspace
                  │
                  ├→ [launchpad_client]        (harness-readiness)
                  ├→ [ForgeClient.ensure_branch_from_base / pr_branch_naming helpers] (branch resolve)
                  └→ [run_store_repository.find_active_run]  (pre-enqueue, inside WaveStartService)
```

---

## 3. Public interface contracts

### 3.1 `tenant_routes` → `TenantService`

**Method / entry point:** `register_tenant`
**Arguments:**
- `request`: validated model — name, submitted credential, repo list, absolute
  root path, optional board default — invariant: root path must be absolute

**Return:**
- `tenant_id`, one-time bearer token
- Error: itemized per-repo probe failure list; never includes the submitted
  credential in the error body or the success body

**Invariants:**
- All-or-nothing: zero rows persist on any probe failure

### 3.2 `TenantService` → `github_pat_probe`

**Method / entry point:** `verify_read_access`
**Arguments:**
- `credential`, `org`, `repo` — `credential` is caller-submitted per call,
  never the infra singleton's own fixed transport credential

**Return:**
- `ok` / `reason` pair; an expected auth-or-not-found failure populates
  `reason` rather than raising, so the caller can build one itemized report
  across every submitted repo

**Invariants:**
- This component never persists the submitted credential

### 3.3 `tenant_token` dependency → `TenantRepository`

**Method / entry point:** `resolve_tenant_by_token`
**Arguments:**
- bearer token string from the request header

**Return:**
- tenant identity, or none

**Invariants:**
- Does not populate the existing JWT auth-context object (ADR-012)

### 3.4 `run_orchestrator` → `tenant_git_workspace_client`

**Method / entry point:** `resolve_workspace`
**Arguments:**
- resolved tenant row, `org`, `repo`

**Return:**
- absolute path + which of two modes was used
- Error: raised on transport/not-found failure, and separately on an
  existing-but-invalid checkout at the target path

**Invariants:**
- Never invoked when the caller supplied an explicit path — the orchestrator
  branches before reaching this contract
- Resolves serially per `org`+`repo` (an advisory lock or lock file scoped to
  the resolved path, held for the duration of the call) — this holds
  **independent of** the pre-enqueue repository-conflict check in §3.6. Wave
  delivery order (clone/refresh lands before the conflict check is broadened
  to repo scope — see the approved dependency graph) means two different
  waves on the same registered repo can both pass today's narrower check and
  reach this call concurrently; the invariant must not depend on that
  upstream gate being broadened first, or on it staying broadened later (see
  §9 TF-01)

### 3.5 `run_orchestrator` → branch resolve (composing existing `ForgeClient` +
`pr_branch_naming` primitives)

**Method / entry point:** `resolve_branch`
**Arguments:**
- existing-run lookup result, `org`, `repo`, identity fields, base branch

**Return:**
- resolved head ref string — the already-existing base-fork primitive on one
  path, the already-existing head-ref-derivation primitive on the other; no
  third primitive is introduced

**Invariants:**
- Zero new refs created on the second (existing-run) path

### 3.6 `WaveStartService` → `run_store_repository.find_active_run` (broadened)

**Method / entry point:** `find_active_run` — signature drops the narrowing
parameters as filtering inputs (kept, if at all, as audit-only, non-filtering
call-site context; exact parameter list is TDD_ONLY, see §9 FF-04-adjacent row)

**Return:**
- any ACTIVE row for the `org`+`repo` pair, full stop

**Invariants:**
- Query change only; no schema change

### 3.7 `ForgeClient.delete_branch`

**Method / entry point:** `delete_branch`
**Arguments:**
- `owner`, `repo`, `branch`

**Return:**
- none on success; raises on a missing or protected branch

**Invariants:**
- Reuses the existing DELETE-shaped ref-update transport; zero callers wired
  into any orchestrated flow this initiative ships

---

## 4. ADR resolutions

> **Revised from the first review pass.** FF-01 and FF-03 were initially
> drafted as standalone `ADR_REQUIRED` files. Re-reading both against the
> qualification rubric found neither held up: each had exactly one viable
> option once the Lifecycle immutability rule ruled out an in-place edit and
> disproportion ruled out a wholesale rewrite — no genuine competing
> engineering alternatives, which the rubric's "a real trade-off exists"
> prong requires. Separately, re-reading ADR-010's own Recommendation text
> found it states what implement intake **must not** require (meta fields);
> it does not state that a caller must always supply the workspace. FF-01 is
> therefore a **gap** ADR-010 never addressed, not a **reversal** of
> something it actually said — the earlier framing overstated the conflict.
> Both are reclassified `TDD_ONLY` below; their standalone Draft files are
> retired (never Accepted, safe to remove). `docs/specification/adr/adr-012-…`
> is renumbered to `adr-011-…` so the surviving ADR fills the first available
> slot rather than leaving a numbering gap.

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-01 | TDD_ONLY | §9 row FF-01 | `[REQ-10, REQ-12, REQ-15]` | none | Gap-fill, not reversal — no new ADR; documented as an additive case in this TDD | Resolved | N/A |
| FF-02 | ADR_REQUIRED | `docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md` | `[REQ-03, REQ-04]` | none | Fourth trust zone, same Bearer/dependency mechanics as the existing programme-token zone | **Accepted** (@nikd10x, 2026-08-08) | `sha256:6d4578b99287b664a3a0e324196ed3f0fbcdb6f2a7b3a5d555c5be11d793b56e` |
| FF-03 | TDD_ONLY | §9 row FF-03 | `[REQ-11]` | none | Scope clarification only — no new ADR; ADR-003 Q-1 read as scoped to the credential it names | Resolved | N/A |
| FF-04 | TDD_ONLY | §9 row FF-04 | `[REQ-11]` | none | Subprocess `git` CLI transport, no new Python package dependency | Resolved | N/A |
| FF-05 | TDD_ONLY | §9 row FF-05 | `[REQ-20, REQ-21, REQ-22]` | none | First-ever unit coverage for the harness-check infra client, scheduled as plan §9 scope | Resolved | N/A |
| FF-06 | TDD_ONLY | §9 row FF-06 | `[REQ-23, REQ-24]` | none | Historical-pattern regression fixture before the query change ships, scheduled as plan §9 scope | Resolved | N/A |
| PE-1 | TDD_ONLY | §9 row PE-1 | `[REQ-16, REQ-17, REQ-18, REQ-19]` | none | Cross-repo contract PR treated as a hard build-order gate, per the approved dependency graph | Resolved | N/A |
| TF-01 | TDD_ONLY | §9 row TF-01 | `[REQ-10, REQ-13, REQ-14, REQ-23]` | none | Technical-review-native finding (not from feasibility) — workspace resolution must self-serialize per repo; see §3.4 invariant | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: 1
- TDD_ONLY: 7
- DEFERRED_WITH_DEFAULT: 0
- Draft ADR files created: 1
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| `tenant_service` / `tenant_repository` | request validation, all-or-nothing persistence, probe-failure itemization — test doubles for the probe and repository | exactly one boundary: repository against a real Postgres session | new tenant-registration script under `live_verify_dir` | exact match on response shape and rejection reason strings |
| `github_pat_probe` | ok/reason mapping for each transport outcome, doubled transport | exactly one boundary: outbound call against a fixture GitHub endpoint | folded into the tenant-registration live script | exact match |
| `tenant_token` dependency | token→tenant resolution, unattached/mismatched rejection — doubled repository | exactly one boundary: repository lookup against a real session | folded into the tenant-registration live script | exact match |
| `tenant_git_workspace_client` | clone-vs-fetch branching, invalid-checkout detection — doubled subprocess transport | exactly one boundary: a real fixture repository on disk | new workspace-lifecycle script under `live_verify_dir` | exact match on mode + path; no fuzzy matching needed (deterministic outcomes) |
| `launchpad_client` (extended) | present/absent artifact branching, cache-flag behavior — first unit file for this component (see §9 FF-05) | exactly one boundary: filesystem fixture with/without harness artifacts | extend `verify_implement_lane`-style script | exact match |
| `run_store_repository.find_active_run` (broadened) | new fixture asserting cross-repo non-blocking and same-repo blocking against representative historical row shapes (see §9 FF-06) | exactly one boundary: repository against a real session | extend `verify_wave_start` | exact match |
| `forge_client.delete_branch` | success + missing/protected-branch failure — doubled transport | exactly one boundary: outbound call against a fixture branch | none this initiative (dormant; zero live callers) | exact match |

**AI-output determinism policy:** not applicable — no AI/LLM-generated output
is produced by any module in this initiative's scope.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Malformed registration body | `tenant_routes` (edge validation) | raised at the API boundary | terminal — 400, no persistence attempted |
| PAT probe failure (one or more repos) | `github_pat_probe` → `tenant_service` | itemized result returned up to the route | terminal for this call — 422, no persistence; caller may retry after fixing credentials |
| Unattached/mismatched tenant token | `tenant_token` dependency | raised before any route handler body runs | terminal — 401 |
| Workspace transport failure (auth/network/not-found) | `tenant_git_workspace_client` | raised to `run_orchestrator` | terminal for this job attempt — surfaces as a named async-phase failure; caller-visible reason names the transport class |
| Existing path is not a valid checkout of the expected remote | `tenant_git_workspace_client` | raised to `run_orchestrator` | terminal — path left untouched, never overwritten |
| Harness artifacts absent | `launchpad_client` | raised to `run_orchestrator` | terminal for this job attempt — named missing artifact |
| Second start on an already-ACTIVE repo | `run_store_repository` → `WaveStartService` | existing precondition-failure path, unchanged shape | terminal for the second request only; first request unaffected |
| `delete_branch` on a missing/protected branch | `forge_client` | raised to direct caller (unit/verify only this initiative) | terminal — no partial ref state |

No failure mode in this table is silently swallowed; every one either raises
to its existing caller boundary or returns an itemized, named result — never
a bare boolean.

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| `tenant_service` | INFO (success) / WARNING (probe failure) | `tenant_id`, `repo_count`, `failed_repos` (names only) | never logs the submitted credential value |
| `tenant_git_workspace_client` | INFO | `org`, `repo`, `mode` (`cloned`/`fetched`), `tenant_id` | never logs the credential; path logged as relative to the tenant root, not absolute, to avoid host-path leakage in shared logs |
| `launchpad_client` (extended) | INFO (verified) / WARNING (not ready) | `org`, `repo`, `cache_hit` | |
| `run_store_repository` (broadened query) | INFO on rejection | `org`, `repo`, `existing_run_id` | no change to existing field names |
| `forge_client.delete_branch` | INFO (success) / ERROR (failure) | `owner`, `repo`, `branch` | matches the existing method-logging convention already used across `forge_client.py` |

No module in this table swallows an error without a corresponding log line
at WARNING or above.

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| `TenantRegisterRequest` / response models | `src/models/tenant_models.py` | edge (Pydantic) + repository (on read-back) | amend-by-PE; additive fields only without a spec amendment |
| `tenants` / `tenant_repos` / `tenant_users` ORM rows | `src/database/postgres/schema/tenant_schema.py`; repository validates on read/write | repository | human-owned Alembic revision per `database-migrations.mdc` — agent does not touch `versions/` |
| Workspace resolution result (path + mode) | `tenant_git_workspace_client` | internal to infra, not persisted | immutable shape — mode is a closed two-value set |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-01 | PE | resolved | Does ADR-010 need amending, or a new ADR, for a Gateflow-resolved workspace on Tenant-registered repos | Neither. ADR-010's Recommendation states what implement intake must not require; it is silent on whether the caller must always be the workspace source. This is an unaddressed case, not a reversal, so no ADR is needed — the second decider is recorded here and in §2/§3 only, and takes effect strictly when the caller supplies nothing | plan | N/A — resolved now | re-read of ADR-010 Recommendation item 2 (states an exclusion on required fields, not an exhaustive source-of-workspace rule) |
| FF-02 | PE | resolved (Draft ADR) | Fourth trust zone vs. extending an existing one | See `docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md` — genuine identity-model trade-off, recorded as its own file | technical review acceptance | N/A | §4 |
| FF-03 | PE | resolved | Does ADR-003 Q-1 govern the new per-tenant credential domain | Read as scoped to the single credential `GithubSettings` names; the per-tenant credential is a separate, application-data-held domain with its own posture already fixed by the approved requirement. No amendment needed — ADR-003 never claimed to be exhaustive over every future credential class, so this is a scope clarification, not a reversal | plan | N/A — resolved now | re-read of ADR-003 Recommendation "Forge credentials (Q-1)" (names one credential, does not claim exhaustivity) |
| FF-04 | PE | resolved | Which local transport for clone/fetch — subprocess vs. a client library | Invoke the `git` executable directly via an async subprocess call from the new infra client; add no new Python package dependency, since the executable must already be present in the deploy image regardless of library choice | plan | N/A — resolved now | pyproject.toml dependency inventory; no existing precedent for a git library in this codebase |
| FF-05 | PE | resolved | Missing first-ever unit coverage for the harness-check infra client | Add the first unit test file for this component as part of the wave that extends it, not as a separate cleanup task | plan §9 (harness-readiness wave) | N/A — resolved now | feasibility FF-05 |
| FF-06 | PE | resolved | Missing regression fixture for the broadened repository-conflict query | Add a fixture asserting both the widened same-repo block and the unaffected cross-repo case, built from representative historical row shapes, before the query change ships | plan §9 (concurrency wave) | N/A — resolved now | feasibility FF-06 |
| PE-1 | PE | resolved | Whether the cross-repo contract PR is a hard gate before this repo's branch-lifecycle waves | Treat it as a hard build-order gate for the waves that consume the new node shapes; the Tenant-aggregate and repository-conflict waves have no such dependency and may proceed independently | plan §9 (build order) | N/A — resolved now | approved dependency graph |
| TF-01 | PE | resolved | Two different waves on one Tenant-registered repo can both pass today's narrower pre-enqueue conflict check (broadened only in a later wave) and reach workspace resolution at the same time — is that race real, and if so what closes it | Real, for the window between the clone/refresh wave shipping and the conflict-check-broadening wave shipping (and defensively, forever after — correctness should not depend on that upstream gate's continued scope). Workspace resolution serializes per `org`+`repo` on its own, independent of the pre-enqueue check — see §3.4 invariant | plan (clone/refresh wave TASK) | N/A — resolved now | this review, comparing the approved delivery-wave order against the pre-enqueue check's narrower pre-broadening scope; technical-review-native finding, not carried from feasibility |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| PM-1 | programme PM | open | Whether the recorded Gate-1 review satisfies the plaintext-credential risk acknowledgment, or a separate explicit sentence is still wanted for the audit trail | no | before implementation begins | Treat the matching approval as sufficient; a follow-up comment is a nice-to-have, not a gate | feasibility Q-7 / spec Q-7 | pending PM comment on meta PR [#32](https://github.com/drivestream-lab/prayog-meta/pull/32) |

---

## 11. Routed out — domain clarifications (SME)

_None._

---

## 12. Fix disposition

_None — no auto-fixable items were identified in feasibility._

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | PASS (see Check summary) |
| Engineering decisions resolved | 8 resolved (1 via ADR, 7 via §9), 0 deferred |
| Draft ADR files written | 1 file / 1 required — **Accepted** by @nikd10x on 2026-08-08 (commit `ff1320e5254510a448d1dedd5ec21dfd5b5a05e2`) |
| Product-boundary integrity (T12) | PASS — mechanical lint clean on the ADR (both `--strict` and `--verify-lint-evidence`) + this TDD; manual re-read confirms no product-register leakage |
| PM questions outstanding | 1 — PM-1 (non-blocking, default recorded) |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` — zero unresolved engineering blockers; ready for PE review |
| Ready for PE review | YES — completed 2026-08-08 |
| **Ready for /spec-implementation-plan** | **YES — the sole required ADR is Accepted with real Approval evidence, Approved head, and verified Lint evidence; TDD Status updated to Accepted** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 names every affected module, current state, and layer |
| T2 Interface contracts | PASS | §3 specifies 7 boundary crossings with shapes/invariants |
| T3 NEW-ADR dispositions | PASS | 1 `ADR_REQUIRED` (FF-02), 7 `TDD_ONLY` (FF-01, FF-03…06, PE-1, TF-01), 0 `DEFERRED_WITH_DEFAULT` — every FF/PE/TF item dispositioned. FF-01 and FF-03 were reclassified from an initial `ADR_REQUIRED` pass after re-reading found neither had a genuine competing alternative (see §4 note) |
| T4 Test policy | PASS | §5 names unit/integration boundary + live script per module; no AI-determinism concern this initiative |
| T5 Error handling | PASS | §6 covers every failure mode named in the spec's Negative and failure paths section |
| T6 Observability | PASS | §7 states level + fields per module; PAT/credential values excluded by name |
| T7 Data contract ownership | PASS | §8 names owner/validation/versioning for every new schema and DTO |
| T8 Dependency graph | PASS | No circular imports introduced; new infra clients sit under `infra_services/`, new repository/service/routes follow the existing layer order; import-linter contract unaffected |
| T9 Engineering questions zero | PASS | Every PE-lane item from feasibility (FF-01…06, PE-1) plus the technical-review-native TF-01 has a disposition in §4/§9 |
| T10 PE review readiness | PASS | §13 states `ready_for_pe_review: true`, lists exact TDD + 1 ADR file, does not claim plan readiness |
| T11 ADR artifact integrity | PASS | The 1 `ADR_REQUIRED` file exists under `docs/specification/adr/`, Status `Draft`, linked with its Lint evidence digest in §4; the two retired Draft files (never Accepted) are removed, not left as broken links |
| T12 Product-boundary integrity | PASS | Mechanical lint (`adr_boundary_lint.py --strict`) clean on the ADR and on this TDD (`--tdd`); independent re-read confirms no restated REQ prose, one decision per ADR, no product consequence narrated as decision |

**Check PASS** = zero unresolved blocking findings.

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR**. Do **not** commit, push, open PRs, or
> apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-012-spec-gateflow
PR title: "[INIT-GATEFLOW-012] Spec — Tenant registry and workspace/branch lifecycle (gateflow)"
PR body:  link meta PRD PR #32; paste §13 Implementation readiness verdict when TDD is ready

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @drivestream-lab/prayog-pe-team  ← must give explicit Approve, not just silence

Review deadline: 2026-08-15
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — required Draft files exist; TDD-only rationales are valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — every required file/link/digest is valid
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*
  [ ] T12 mechanical: adr_boundary_lint.py run on every ADR AND on the TDD —
      confirm Lint evidence on each Accepted ADR, don't just take PASS on faith
  [ ] T12 manual: loose paraphrase check; invented-behavior check; one-decision-
      per-ADR check — all three already performed once by this skill, PE re-reads independently

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
  → Ready for review → merge → /create-board-tickets from merged plan §9
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-012.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-012
    source_freshness: CURRENT
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/32"
    meta_pr_head: "74402540efd98527014b4706d0d29bda1242b6cf"
    map_revision: 1
    prd_digest: "sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b"
    scope_digest: "sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678"
    adr_required_count: 1
    adr_files:
      - path: docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md
        status: Accepted
        lint_digest: "sha256:6d4578b99287b664a3a0e324196ed3f0fbcdb6f2a7b3a5d555c5be11d793b56e"
        approved_head: "ff1320e5254510a448d1dedd5ec21dfd5b5a05e2"
        approved_by: "@nikd10x"
        approved_at: "2026-08-08"
    reclassified_from_first_pass: "FF-01,FF-03"
    retired_adr_files: "adr-011-tenant-registered-workspace-authority.md,adr-013-per-tenant-github-credential-scope.md"
    native_findings: "TF-01"
    ready_for_pe_review: true
    ready_for_plan: true
    nonblocking_questions: "PM-1"
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: spec-technical-review forge.commit_workspace = required.
    # technical-review-approval (human-checkpoint) satisfied 2026-08-08 —
    # PE accepted the sole required ADR with real evidence (see adr_files
    # above). Acceptance package still needs /commit-workspace to publish
    # this follow-up edit onto the Draft spec PR head.
```
