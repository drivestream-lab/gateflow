# Technical Design Document — INIT-GATEFLOW-013

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Spec digest | `sha256:44e10fa850753325b8acf1a892723fe5d3293da94f10ed9a129d8651dca595b4` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-013.md` |
| PRD digest | `sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-013.md` / `1` |
| Repo scope digest | `sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e` |
| Approved meta PR head | `59301dce846043b8a4e70057a81dfa67a4868ece` |
| Source freshness | CURRENT — G1 head matches live meta PR #33; H1/H2/H3 match spec header |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-09 |
| Branch | `chore/INIT-GATEFLOW-013-spec-gateflow` (spec PR — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-013` |
| Status | Accepted |
| Review deadline | 2026-08-14 |
| Deciders | PE: @nikd10x — Accepted 2026-08-09 via Cursor chat |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-09 via Cursor chat (INIT-GATEFLOW-013 technical-review package) |
| Approved head | `3d9fa93b4b3f4519585898928a78b744d455c5f0` (Forge publish tip of Accepted package on chore/INIT-GATEFLOW-013-spec-gateflow) |

---

## 1. Problem statement

Gateflow must add a tenant-scoped onboarding data path that syncs a programme
meta checkout, parses catalogue documents from that tree, admits
`tenant_repos` rows only through the selection write path (REQ-12, REQ-13),
and evaluates harness readiness through an inspect-only Launchpad `status`
protocol for selection-admitted repos while preserving the existing filesystem
evaluator for pre-INIT rows (REQ-17–REQ-22) — without violating ADR-004
runtime-knob ownership or layering rules (REQ-01–REQ-28).

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/api/v1/tenant_routes.py` (+ new programme/onboarding routes module) | tenant register/list/attach | extend / create | HTTP edge; body models from `src/models/` |
| `src/business_services/tenant_service.py` (+ new orchestration service if split) | register / harness cache | extend | use-case orchestration; no ORM |
| `src/infra_services/tenant_git_workspace_client.py` | clone/fetch default branch | extend optional `ref` | git subprocess transport |
| `src/infra_services/github_pat_probe.py` | registration probe | unchanged; new call site | PAT read probe |
| `src/infra_services/launchpad_client.py` | filesystem `sync_harness` | retain for legacy | filesystem readiness |
| `src/infra_services/launchpad_status_client.py` (new) | — | create | inspect-only `status` CLI |
| `src/database/postgres/repository/tenant_repository.py` | tenants/repos/users | extend | persistence + DTO map |
| `src/database/postgres/schema/tenant_schema.py` | tenants/repos/users | extend (+ programme connection) | ORM only |
| Catalogue parser (new module under `business_services/` or `engine/`) | — | create | YAML → Pydantic candidates |
| `src/di/modules/*`, `dependency_container.py` | 012 wiring | bind new infra/business | composition root |
| `src/business_services/wave_start_service.py`, `run_orchestrator.py` | filesystem harness gate | provenance branch | readiness gate before enqueue / Enter-at |

**Boundary diagram (text):**

```
HTTP (tenant bearer) → [Onboarding / Tenant business] → [TenantRepository] → Postgres
                              ↓                ↓
                    [TenantGitWorkspaceClient] [GithubPatProbe]
                              ↓
                    synced meta checkout → [CatalogueParser] → candidate DTOs
                              ↓
         provenance? → [LaunchpadStatusClient]  (selection-admitted)
                     → [LaunchpadClient.sync_harness] (pre-INIT rows)
                              ↓
                    mark_harness_verified (selection-admitted writers only)
```

---

## 3. Public interface contracts

### 3.1 API → Onboarding / Tenant business

**Method / entry point:** connect programme; read catalogue; select/deselect;
refresh catalogue; on-demand readiness refresh (exact paths deferred to OpenAPI
— see spec Q-1).

**Arguments:**
- `tenant_id`: UUID — must match bearer zone (ADR-011)
- connect body: `org`, `repo`, optional `ref` — absolute workspace root already on tenant
- select body: list of `{org, repo}` — must be subset of current candidates
- deselect body: `{org, repo}`

**Return:**
- connect: connection record (org/repo/ref, last_synced_at) — no PAT
- catalogue: candidate list DTO
- select: per-repo result list (admitted / probe_failed / setup_failed /
  status_failed / ok) — partial success
- errors: 400 validation; 401 tenant bearer; 422 named domain failures

**Invariants:**
- Registration body rejects non-empty `repos` (REQ-12); empty/absent only
- No second programme connection row per tenant (REQ-28)
- PAT never in any response

### 3.2 Business → `TenantGitWorkspaceClient`

**Method / entry point:** `resolve_workspace(credential, *, ref: Optional[str])`

**Arguments:**
- `credential`: existing `TenantWorkspaceCredential` shape
- `ref`: optional git ref; when set, after clone/fetch ensure checkout of that ref

**Return:**
- `WorkspaceResolveResult` (path + mode clone|fetch)

**Invariants:**
- Same `{workspace_root}/{org}/{repo}` layout; per-org+repo lock retained
- No PAT logged

### 3.3 Business → CatalogueParser

**Method / entry point:** `parse_candidates(meta_checkout_root, *, org: str)`

**Arguments:**
- absolute path to synced meta tree
- programme `org` for `service-catalog-<org>.yaml` resolution

**Return:**
- list of candidate `{org, repo, …catalogue fields needed for selection}`

**Error:**
- named shape/missing-file failure — no partial list (REQ-06)

**Invariants:**
- Read-only filesystem; no network
- Authority per ADR-012 (discovery contract, not ADR-004 knobs)

### 3.4 Business → `GithubPatProbe`

**Method / entry point:** `verify_read_access(credential, org, repo)` — existing

**Invariants:**
- Called at selection for newly admitted repos only (REQ-11); not at connect
  for every catalogue row

### 3.5 Business → `LaunchpadStatusClient` (new)

**Method / entry point:** `inspect_status(*, repo_workspace: str, meta_config_dir: str)`

**Arguments:**
- repo workspace absolute path
- meta config dir = synced programme checkout (or its `config/` as required by CLI)

**Return:**
- structured pass/fail (+ reason codes for mapping to cache)

**Error:**
- `tool_unavailable` distinct from `repo_not_ready` (REQ-20)

**Invariants:**
- Question-only argv (status / --config-dir / --repo / --meta) — no apply
- Never uses operator-local `~/.config/launchpad/clients.yaml` as programme source

### 3.6 Business → `LaunchpadClient.sync_harness` (existing)

**Method / entry point:** unchanged filesystem check

**Invariants:**
- Invoked only for pre-INIT provenance when a re-check is requested (ADR-013)

### 3.7 Wave-start / orchestrator → readiness gate

**Method / entry point:** `_ensure_*_harness_ready` (existing hooks)

**Invariants:**
- Select evaluator by durable provenance (ADR-013)
- Cache skip via `is_harness_verified` retained; `force_harness_recheck` honored
  per evaluator rules above
- Unchecked / last-failed selected repo: fail closed at start (spec Q-3 default)

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-01 | ADR_REQUIRED | `docs/specification/adr/adr-012-programme-catalogue-discovery-authority.md` | `[REQ-05, REQ-06, REQ-07]` | catalogue field UX | Option A — discovery-input authority; ADR-004 unchanged | Accepted | file `sha256:2a70f9a173a111f39927824bdcef306e1650e864f01ee3be94cd518d1a985a00`; lint `adr_boundary_lint.py 4/4, PASS, sha256:101861275eb458826e04bd63803196b4c097236bb511db115fc572b1197dc6a9` |
| FF-02 | ADR_REQUIRED | `docs/specification/adr/adr-013-dual-harness-readiness-evaluators.md` | `[REQ-17, REQ-18, REQ-20, REQ-21, REQ-22]` | inspect-only product rule | Option B — dual evaluators + provenance switch | Accepted | file `sha256:1ec81820dbeeb3b455b3a460fc319a73f1153b4da3c902cc232c23ba6c46327e`; lint `adr_boundary_lint.py 6/6, PASS, sha256:b4d9ea508a8a8258a3337051a2886df9218f3b1017f24a8e38ccac5df0c1710d` |
| FF-04 | TDD_ONLY | §9 FF-04 | `[REQ-21, REQ-22]` | — | Provenance switch inside existing harness gates (satisfied by ADR-013 B) | Resolved | N/A |
| FF-05 | TDD_ONLY | §9 FF-05 | `[REQ-01]` | — | Extend `resolve_workspace` with optional `ref` + post-sync checkout | Resolved | N/A |
| FF-06 | TDD_ONLY | §9 FF-06 | `[REQ-17, REQ-20]` | — | Preinstall Launchpad CLI in API+worker images; path via settings; fail closed if missing | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: 2
- TDD_ONLY: 3
- DEFERRED_WITH_DEFAULT: 0
- Draft ADR files created: 2 (both now **Accepted**)
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| CatalogueParser | fixture meta trees (valid / missing / malformed) — no I/O beyond tmpfs fixtures | N/A (pure parse) | N/A | exact candidate list |
| Connect / refresh | mock git client; assert one connection row; fail-closed cleanup | optional real git against fixture remote | `verify_programme_connect` (new) | exact status codes + connection fields |
| Select / deselect / retire `repos[]` | probe mock; active-run mock for deselect; registration rejects `repos` | N/A | extend/replace `verify_tenant_registry` | exact |
| Setup batch | mock resolve per repo; assert isolation | N/A | batch fixture in connect verify or `verify_repo_selection` | exact per-repo results |
| LaunchpadStatusClient | subprocess double; argv guard (no apply); tool_unavailable mapping | contract test against real CLI when binary present | readiness verify for selection-admitted repo | exact reason codes |
| Dual gate | unit: provenance → which client called; legacy force-recheck never calls status | N/A | legacy path still passes filesystem verify | exact call assertions |
| Wave-start fail-closed | unit: never-checked selected repo → 422 / 0 enqueue | N/A | secondary | exact |

**AI-output determinism policy (when applicable):**
- N/A — no LLM/agent output in this INIT’s acceptance path.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Connect git auth/network/not-found | TenantGitWorkspaceClient | business → 422 named reason; no connection row | terminal |
| Catalogue shape invalid | CatalogueParser | business → 422; no candidates | terminal |
| Out-of-catalogue select | business | 422; 0 active-list change | terminal |
| PAT probe fail on new select | GithubPatProbe | business → 422 named; 0 change | terminal |
| One repo setup fail in batch | TenantGitWorkspaceClient | per-repo failure entry; others continue | partial |
| Status tool missing/misconfigured | LaunchpadStatusClient | distinct `tool_unavailable`; no cache write | terminal for that batch item / call |
| Status repo not ready | LaunchpadStatusClient | per-repo not-ready; others continue | partial |
| Deselect while ACTIVE run | RunRepository.find_active_run | 422; 0 deselect | terminal |
| Refresh git fail | TenantGitWorkspaceClient | 422; selections/readiness untouched | terminal |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| Connect / refresh | INFO/ERROR | `tenant_id`, `org`, `repo`, `ref`, `outcome` | never PAT |
| Catalogue parse | INFO/WARNING | `tenant_id`, `candidate_count`, `reject_reason` | |
| Select / deselect | INFO/WARNING | `tenant_id`, `org`, `repo`, `outcome` | |
| Setup / status per repo | INFO/WARNING | `tenant_id`, `org`, `repo`, `result`, `reason` | |
| Dual gate | INFO | `org`, `repo`, `evaluator` (`status`\|`filesystem`), `cache_hit` | |
| Tool unavailable | ERROR | `reason=tool_unavailable` | distinct from repo not ready |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Programme connection row | ORM schema + repository; business DTOs in `src/models/` | API body + repo map | amend-by-PE; human Alembic |
| Catalogue candidate DTO | Pydantic in `src/models/`; parser validates | parse edge | fail closed on unknown required shape |
| `tenant_repos` active list + `harness_verified` | existing schema; selection writers | repository | no new column required for legacy vs new if provenance = “admitted via selection after connect” **or** add `readiness_evaluator` enum — TDD recommends optional `readiness_source` column (`filesystem` \| `launchpad_status`) set at admission time for unambiguous gate branching |
| Launchpad status verdict DTO | `src/models/` | status client boundary | amend-by-PE when CLI shape drifts |
| Registration request (no `repos`) | `tenant_models.py` | API edge | breaking vs 012 |

**DDL note:** human owns `postgres_migrations/versions/` — agent updates
`schema/` + `env.py` only; produce `DDL-NOTE-INIT-GATEFLOW-013-*.md` like 012.

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-01 | PE | resolved | Catalogue vs ADR-004 | ADR-012 Option A | PE accept | — | adr-012 |
| FF-02 | PE | resolved | Status client vs evolve sync_harness | ADR-013 Option B | PE accept | — | adr-013 |
| FF-04 | PE | resolved | Dual evaluator at wave-start | Provenance switch in existing gates; optional `readiness_source` column | plan W3 | infer: selection-admitted after 013 ship → status | ADR-013 + §8 |
| FF-05 | PE | resolved | Connect `ref` | Extend `resolve_workspace` with optional `ref`; checkout after clone/fetch | plan W0 | — | §3.2 |
| FF-06 | PE | resolved | Launchpad binary location | Preinstall CLI in API + worker images; settings path; `health_check`/status call fail closed if missing | plan W3 / ops | — | §3.5 |
| Q-3 | PE | deferred | Wave-start when never checked / last failed | Fail closed (block start) | plan | fail closed | spec Q-3 |
| Q-4 | PE | deferred | Refresh schedule | On-demand only | plan | on-demand | spec Q-4 |
| Q-9 | PE | deferred | Submodule credentials | Assume tenant PAT covers same-org submodules | plan | assume PAT | spec Q-9 |
| Selection+setup coupling | PE | resolved | Auto vs distinct setup call | Selection admits repos then runs setup+status per newly admitted repo in the same request with per-repo results | plan W1/W2 | — | §3.1 |
| Programme connection storage | PE | resolved | Dedicated table vs reserved tenant_repos | Dedicated `tenant_programme_connections` (1:1 tenant) — not a fake app repo row | plan W0 | — | §8 |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| PM-1 | PM | open | Inventory dependents of hand-typed `repos[]` registration (scripts/runbooks/verify) | no | before W1 merge | none — process gate | spec Q-6 / IM-06 | meta PR #33 |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| D-1 | PE/PM | open | Pre-INIT repo fresh real check without programme connect (OQ-9) | no | before W3 | unavailable until connect; filesystem force-recheck only | spec Q-7 | pending |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | Retarget registration unit/verify off required `repos[]` | W1 tests | N/A |
| AF-2 | planned-auto-fix | As-built + tests README INIT-013 feature map | after W0 land | N/A |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | PASS (after lint evidence filled below) |
| Engineering decisions resolved | 8 resolved, 3 deferred with defaults |
| Draft ADR files written | 2 / 2 required — **Accepted** 2026-08-09 |
| Product-boundary integrity (T12) | PASS (lint + manual re-read; evidence re-verified after Accept) |
| PM questions outstanding | 1 non-blocking (PM-1) |
| Domain questions outstanding | 1 non-blocking (D-1) |
| Selected workflow outcome | `pass` — PE Accepted TDD + ADR-012 + ADR-013 via Cursor chat 2026-08-09 |
| Ready for PE review | YES (complete — artifacts Accepted) |
| **Ready for /spec-implementation-plan** | **YES — Accepted ADR/TDD files present; publish via Forge first; Gate 2 `spec-lgtm` still only after plan on tip** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 layers + diagram |
| T2 Interface contracts | PASS | §3.1–3.7 |
| T3 NEW-ADR dispositions | PASS | FF-01/02 → ADR_REQUIRED; FF-04/05/06 → TDD_ONLY |
| T4 Test policy | PASS | unit / integration-boundary / live named |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 + DDL note |
| T8 Dependency graph | PASS | api → business → repo/infra; no ORM upward |
| T9 Engineering questions zero | PASS | PE items resolved/deferred |
| T10 PE review readiness | PASS | Draft ADRs + this TDD; `ready_for_plan: false` |
| T11 ADR artifact integrity | PASS | adr-012, adr-013 Draft linked |
| T12 Product-boundary integrity | PASS | lint evidence on ADRs + TDD scan — see Acceptance blocks |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet. CODEOWNERS may request PE review on `Technical-Review-*`.

```
Branch:   chore/INIT-GATEFLOW-013-spec-gateflow
PR title: "[INIT-GATEFLOW-013] Spec — Programme-first onboarding and real readiness checks (gateflow)"
PR body:  link meta PRD PR #33; paste §13 Implementation readiness verdict when TDD is ready

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @drivestream-lab/prayog-pe-team  ← must give explicit Approve, not just silence

Review deadline: 2026-08-14
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — required Draft files exist; TDD-only/deferred rationales are valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — every required file/link/digest is valid
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*
  [ ] T12 mechanical: adr_boundary_lint.py on every ADR + TDD
  [ ] T12 manual gaps (lint cannot see): loose paraphrase; invented behavior; multi-decision ADR

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates ADR metadata Draft → Accepted and TDD Status → Accepted
  Publish acceptance package via Forge to spec branch (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-013.md
  blockers: []
  signals:
    ready_for_pe_review: true
    ready_for_plan: true
    new_adr: true
    adr_status: Accepted
    pe_acceptance: "Explicit PE acceptance by @nikd10x on 2026-08-09 via Cursor chat"
    draft_adr_paths:
      - docs/specification/adr/adr-012-programme-catalogue-discovery-authority.md
      - docs/specification/adr/adr-013-dual-harness-readiness-evaluators.md
    draft_adr_digests:
      - sha256:2a70f9a173a111f39927824bdcef306e1650e864f01ee3be94cd518d1a985a00
      - sha256:1ec81820dbeeb3b455b3a460fc319a73f1153b4da3c902cc232c23ba6c46327e
    source_freshness: CURRENT
    initiative: INIT-GATEFLOW-013
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/33"
    meta_pr_head: "59301dce846043b8a4e70057a81dfa67a4868ece"
    map_revision: 1
    source_prd_digest: sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1
    repo_scope_digest: sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```

