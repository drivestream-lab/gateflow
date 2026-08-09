# Feasibility report — INIT-GATEFLOW-013

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| PRD digest | `sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-013.md` / `1` |
| Repo scope digest | `sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e` |
| Approved meta PR head | `59301dce846043b8a4e70057a81dfa67a4868ece` |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/33#pullrequestreview-4889131742) 2026-08-08T15:58:21Z; label `impact-map-lgtm` |
| Source freshness | CURRENT — G1 head matches live meta PR #33; H1/H2/H3 match spec header |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-08 |
| Branch | `chore/INIT-GATEFLOW-013-spec-gateflow` — spec PR (single review surface) |
| Initiative segment | `INIT-GATEFLOW-013` |
| Status | Draft |
| Review deadline | 2026-08-12 |
| Deciders | PM: programme PM · Domain SME: @drivestream-lab/prayog-pe-team |

## Summary

Buildable on INIT-GATEFLOW-012 primitives (`TenantGitWorkspaceClient`,
`GithubPatProbe`, `tenant_repos.harness_verified`, `find_active_run`, tenant
bearer). Programme connect / catalogue / select-deselect / real Launchpad
`status` are **net-new**. Highest engineering risk is W3 readiness takeover
(today's `LaunchpadClient.sync_harness` is filesystem-only) plus an ADR-004
boundary question for consuming meta catalogue YAML. Spec is not blocked for
Draft publish; unresolved PE/ADR items select outcome **`findings`** and must
be resolved in `/spec-technical-review` before plan.

**Findings:** 9 total (0 Critical, 5 Should fix, 4 Verify / Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 1 | 0 |
| PE / ADR | 5 | 3 | 0 |
| Domain | 0 | 1 | 0 |
| Auto-fix | 0 | 2 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 5 |
| Verify / Gap (informational) | 4 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `findings` |
| Rationale | Unresolved blocking PE/ADR Should-fix items (NEW-ADR catalogue vs ADR-004; Launchpad status client shape; ref sync; dual readiness path; binary provisioning) — first matching lane-to-outcome rule |
| Next (from workflow) | `spec-technical-review` |

Informational observations alone do **not** select `findings`. Unresolved
blocking PE/ADR → `findings`; blocking PM/domain → `needs-input`.

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` green path for 012 tenant/workspace/harness; no 013 coverage | `test_tenant_service.py`, `test_tenant_git_workspace_client.py`, `test_launchpad_client.py`, `test_github_pat_probe.py`, `test_wave_start.py` |
| Live verify | Standalone 012 scripts; not in `verify_all` aggregator; no 013 scripts | `verify_tenant_registry.py`, `verify_workspace_lifecycle.py`, `verify_harness_readiness.py`; `tests/README.md` |
| As-built | INIT-012 W0–W5 human_approved; no INIT-013 rows | `docs/specification/as-built/implementation-status.md` |
| Toolchain | `make check` / `make test` wired | Makefile; `pyproject.toml` |

### ADR pass (pre-T2)

| ADR | Domain matched | Status | Action |
|-----|----------------|--------|--------|
| ADR-011 | Tenant bearer trust zone | Accepted | deep-read — aligned |
| ADR-010 | Workspace / lane intake | Accepted | deep-read — reuse path; no reopen |
| ADR-009 | Forge mutate | Accepted | cited — unaffected |
| ADR-004 | Programme config authority | Accepted | deep-read — **boundary tension with CTR-01** |
| ADR-001 | Runtime / durable store | Accepted | skim — Postgres + human Alembic still applies |
| ADR-002 / ADR-005 | Trust zones / programme token | Accepted | skim — new routes stay tenant-scoped per ADR-011 |
| ADR-003 / 006–008 | Slots / adapters / handoff | Accepted | skipped — not in 013 domain |

### MDC pass (pre-T2)

| MDC file | Domain | Read / skipped |
|----------|--------|----------------|
| `architecture.mdc` | layers, api layout | read |
| `infra-services.mdc` | Launchpad/git clients | read |
| `repository-pattern.mdc` | ORM isolation | read |
| `dependency-injection.mdc` | `@inject` / lifecycle | read |
| `pydantic-schemas.mdc` | models in `src/models/` | read |
| `http-api-conventions.mdc` | body/query | read |
| `database-migrations.mdc` | human Alembic | read |
| `fail-fast.mdc` | named rejects | read |
| `testing-verify-flows.mdc` | verify layout | read |
| `logging-loguru.mdc` | structured logs | skim |
| others | unrelated | skipped |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01–04,28 / W0 | Connect to programme meta (clone/sync, one connection) | `TenantGitWorkspaceClient.resolve_workspace` reusable; **no** programme-connection schema/API; **no** `ref` on resolve | none for connect | none | **gap** (partial reuse) |
| REQ-05–07 / W0 | Parse catalogue from synced meta | No `programme.yaml` / `service-catalog` parser in `src/` | none | none | **gap** |
| REQ-08–13,26–27 / W1 | Select/deselect; retire `repos[]` | `TenantRegisterRequest.repos` `Field(min_length=1)`; `TenantService.register_tenant` rejects empty; **no** select/deselect API; `find_active_run` reusable for REQ-27 | `test_tenant_*` assert non-empty repos today | `verify_tenant_registry` sends repos | **gap** + **drift** (existing tests) |
| REQ-14–16 / W2 | Setup chosen repos (partial success) | Same `resolve_workspace`; no batch selection setup orchestration | workspace unit only | workspace verify only | **partial** |
| REQ-17–23 / W3 | Real Launchpad `status`; legacy untouched | `LaunchpadClient.sync_harness` = pin+`.harness/` presence only; no CLI `status`/`--config-dir` | `test_launchpad_client` (filesystem) | `verify_harness_readiness` (filesystem) | **gap** (highest risk) |
| REQ-24–25 / W4 | Catalogue refresh | No refresh API; would reuse connect sync | none | none | **gap** |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-05–07 / W0 (CTR-01) | ADR-004; **NEW-ADR** | missing ADR | `ALTERNATIVE: treat prayog-meta catalogue YAML as a read-only discovery contract from a synced checkout vs revisit ADR-004 Option C (load programme config from meta)` |
| REQ-17–23 / W3 (CTR-02) | ADR-003 (infra vs business); **NEW-ADR** | missing ADR | `ALTERNATIVE: evolve LaunchpadClient.sync_harness into inspect-only launchpad status --config-dir vs add a separate LaunchpadStatusClient and keep filesystem sync_harness for legacy repos only` |
| REQ-01–04,28 / W0 | ADR-010; ADR-001 | aligned | N/A — reuse workspace client + durable tenant rows; connection table shape is TDD |
| REQ-08–13 / W1 | ADR-011 | aligned | N/A — tenant-scoped bearer remains the zone for new routes |
| REQ-14–16 / W2 | ADR-010 | aligned | N/A |
| REQ-21–22 / W3 | (readiness ownership) **NEW-ADR** candidate bundled with CTR-02 row | missing ADR | See FF-02 / FF-04 — dual evaluator vs single path |
| REQ-24–25 / W4 | ADR-010 | aligned | N/A |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F13 | "After connecting, Gateflow reads the programme's shared records from its synced copy and produces a list of candidate repos" | ADR-004 | `ALTERNATIVE: treat prayog-meta catalogue YAML as a read-only discovery contract from a synced checkout vs revisit ADR-004 Option C (load programme config from meta)` |
| FF-02 | F13 | "Gateflow asks the programme's setup tool to run its full readiness check, pointed at Gateflow's own synced copy of the programme's records" | ADR-003; infra-services.mdc | `ALTERNATIVE: evolve LaunchpadClient.sync_harness into inspect-only launchpad status --config-dir vs add a separate LaunchpadStatusClient and keep filesystem sync_harness for legacy repos only` |
| FF-03 | F14 | "connecting clones/syncs it using the same clone-or-fetch mechanism already used for any other tenant repo" | infra-services.mdc; `tenant_git_workspace_client.py` | REQ-01 names org/repo/**ref**, but `resolve_workspace` has no ref — TDD must choose extend-client vs default-branch-only (see FF-05) |

## Findings by severity

### Critical

_None._

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F13 | NEW-ADR required: catalogue consume vs ADR-004 ownership boundary | Spec REQ-05–07 / CTR-01; ADR-004 Option C rejected meta-loaded programme config; revisit trigger names meta overlays |
| FF-02 | F13 | NEW-ADR / TDD required: how real Launchpad `status` replaces filesystem readiness for new repos without touching legacy | Spec REQ-17–22; `LaunchpadClient.sync_harness` filesystem-only (`src/infra_services/launchpad_client.py`); wave-start/orchestrator always call it |
| FF-04 | F2 / F13 | Dual readiness evaluator at wave-start must be designed — provenance branch vs global replace | `WaveStartService._ensure_implement_harness_ready`; `RunOrchestrator._ensure_harness_ready`; REQ-22 write-path isolation alone does not stop legacy force-recheck via `force_harness_recheck` |
| FF-05 | F2 / F10 | Connect `ref` is product-normative but git client cannot pin a ref today | Spec REQ-01 "org/repo/ref"; `TenantGitWorkspaceClient.resolve_workspace` / `_git_clone` — default branch only |
| FF-06 | F10 / F11 | Launchpad binary provisioning undecided (spec Q-2 / IM-02) — blocks W3 live verify and coding | Spec A-2 / Q-2; no launchpad binary in Gateflow runtime today |

### Verify / Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-07 | F3 / F5 | Existing `verify_tenant_registry` / unit registration tests require non-empty `repos[]` — will drift when REQ-12 lands | `TenantRegisterRequest.repos` min_length=1; `verify_tenant_registry.py`; `test_tenant_service.py` |
| FF-08 | F3 / F4 | No verify/unit surface yet for connect, catalogue, select, real `status` | `tests/verify/` inventory; `tests/unit/` inventory |
| FF-09 | F1 / F6 | Programme-connection (+ possibly selection metadata) needs human-owned Alembic; agent updates schema/`env.py` only | `database-migrations.mdc`; existing `DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md` pattern |
| FF-10 | F7 / F8 | 012 harness verify remains file-presence; 013 must add distinct live scripts — avoid double-owning the same journey in unit+verify | `verify_harness_readiness.py`; testing-verify-flows.mdc |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 connect + catalogue | New models/routes/service; `TenantGitWorkspaceClient` call site; new repo/ORM for programme connection; catalogue parser | new unit + `verify_programme_connect` (planned) |
| W1 select/deselect + retire repos[] | `tenant_models.py`, `tenant_service.py`, `tenant_routes.py`, `tenant_repository.py`; `GithubPatProbe` at selection; `find_active_run` on deselect | rewrite registration tests; new select/deselect unit+verify |
| W2 setup batch | Business orchestration over `resolve_workspace`; per-repo result DTO | unit mixed fixture; verify batch |
| W3 real readiness | `LaunchpadClient` (or new client); wave-start + orchestrator gate branch; `mark_harness_verified` write path guard | replace/extend harness unit+verify; code guard for legacy no-touch |
| W4 refresh | Reuse connect sync + catalogue re-parse | unit + verify refresh growth fixture |
| DI / schema | `InfraModule`, `BusinessServicesModule`, `RepositoryModule`, `dependency_container.py`, `tenant_schema.py`, `postgres_migrations/env.py` | — |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | ADR-004 misread as forbidding all meta YAML reads | Resolve FF-01 in TDD/NEW-ADR before coding W0 catalogue |
| R-2 | Launchpad unavailable in API/worker images | Resolve FF-06 before W3; fail closed per REQ-20 |
| R-3 | Cutting over REQ-12 breaks verify scripts / runbooks (IM-06) | Spec Q-6 inventory before W1 merge |
| R-4 | Dual readiness paths confuse operators (OQ-9 / Q-7) | Lock legacy force-recheck policy in TDD; default: no real check until connect |
| A-2 (spec) | Environment can run Launchpad | Same as R-2 / FF-06 |
| A-4 (spec) | Write path never touches pre-INIT rows | Code guard + unit (REQ-22); design FF-04 so force-recheck cannot rewrite legacy via file-presence accidentally either |

## Recommended spec edits

- None required for Draft publish — Q-2/Q-6/Q-7 already recorded.
- Optional clarity (dev edit on same branch): explicitly state that REQ-23 refresh applies only to real-check-backed repos (already implied); add one sentence that ADR-004 covers Gateflow runtime knobs, not the programme service catalogue — **or** leave that to NEW-ADR in technical review (preferred; do not silently amend product ownership in feasibility).

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| FF-01 | PE | Catalogue vs ADR-004 NEW-ADR | yes | PE | open | technical review | none | REQ-05–07; ADR-004 | pending TDD |
| FF-02 | PE | Launchpad status client shape NEW-ADR | yes | PE | open | technical review | none | REQ-17–22; `launchpad_client.py` | pending TDD |
| FF-04 | PE | Dual readiness evaluator at wave-start | yes | PE | open | technical review | none | wave-start / orchestrator harness gates | pending TDD |
| FF-05 | PE | Connect `ref` vs default-branch-only client | yes | PE | open | technical review / plan | none — must choose before W0 coding | REQ-01; `TenantGitWorkspaceClient` | pending TDD |
| FF-06 | PE | Launchpad binary provisioning (spec Q-2) | yes | PE/Ops | open | before W3 coding | none | A-2 / IM-02 | pending |
| Q-6 | PM | Inventory hand-typed registration dependents | no | PM | open | before W1 merge | none | IM-06; Migration NFR | meta PR #33 |
| Q-7 | domain / PE | Legacy force-recheck without programme connect (OQ-9) | no | PE | open | before W3 | none | REQ-23 scope; IM-07 | pending |
| Q-3 | PE | Wave-start when never checked / last failed | no | PE | open | plan | fail closed | IM-01 | pending |
| Q-4 | PE | Refresh on-demand vs scheduled | no | PE | open | plan | on-demand only | IM-03 | pending |
| AF-1 | auto-fix | Update registration unit/verify when REQ-12 lands | no | eng | open | W1 | — | FF-07 | later wave |
| AF-2 | auto-fix | Add as-built INIT-013 rows after first wave | no | eng | open | after W0 land | — | as-built | later |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

_None._

#### Defer — can proceed with documented assumption

1. **Q-6 / IM-06** — What scripts, runbooks, or verify helpers still post `repos[]` at tenant registration? Inventory before W1 merge (comment on meta PRD PR #33).

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

1. **FF-01** — NEW-ADR: catalogue discovery contract vs ADR-004.
2. **FF-02 / FF-04** — NEW-ADR: Launchpad `status` client + dual readiness path for new vs legacy repos.
3. **FF-05** — How connect `ref` is honored given today's default-branch clone.
4. **FF-06** — Where Launchpad binary lives in API/worker runtime.

#### Defer with default

1. **Q-3** — Wave-start on unchecked/failed repo → default fail closed.
2. **Q-4** — Catalogue refresh → on-demand only this INIT.
3. **Q-9** — Submodule credentials → assume tenant PAT covers same-org.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| D-1 | OQ-9 / Q-7 — can a pre-INIT repo get a fresh readiness check without programme connect? | programme PE / PM | W3 policy only — not Draft merge |

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| AF-1 | Registration tests/verify still require `repos` | Retarget to zero-repo registration + selection path in W1 |
| AF-2 | As-built / tests README lack INIT-013 feature map | Add rows when waves land |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Toolchain + 012 verify/unit inventoried; 013 absent |
| F2 Spec → code map | FAIL (blocking PE) | W0–W4 mostly gap; FF-04, FF-05 |
| F3 Spec → verify map | PASS (informational) | FF-08 / FF-10 — planned scripts, no false claim of existing |
| F4 Spec → unit map | PASS (informational) | FF-08 |
| F5 As-built drift | PASS | Spec correctly treats 012 as baseline; no false "already live" for 013 |
| F6 Docs drift | PASS | README active pointer updated; as-built/tests README need later AF rows |
| F7 Overlap risk | PASS (informational) | FF-10 — keep 013 verify distinct from 012 file-presence |
| F8 CI vs live boundary | PASS | CI = `make check`/`test`; live verify human — unchanged |
| F9 Cross-service touch | PASS | CTR-01/02 consume-only; meta/launchpad files exist as sources |
| F10 Assumptions | FAIL (blocking PE) | FF-05, FF-06 — ref + Launchpad binary not evidenced |
| F11 Effort drivers | PASS | See Impact surface / Risks |
| F12 PM questions | PASS | No blocking PM; Q-6 deferred with required-by |
| F13 ADR conformance | FAIL (blocking PE) | FF-01, FF-02 NEW-ADR |
| F14 MDC conformance | PASS (informational) | FF-03 noted; spec stays implementation-neutral |

**Check PASS** = zero unresolved blocking findings (informational OK).

**Overall check verdict:** FAIL (blocking PE/ADR) → workflow outcome `findings`.

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → post as numbered comments on the **meta PRD PR** (plain English).
  Link from a spec PR comment if helpful. PM answers on meta PRD PR.
  Unresolved blocking PM items → outcome `needs-input`.

**PE questions** → discuss on the **Draft spec PR**; run `/spec-technical-review` next.
  PE accepts TDD/ADRs in **files** (`Draft` → `Accepted`); do **not** set
  `spec-lgtm` until the full package includes the implementation plan.
  Unresolved blocking PE/ADR items → outcome `findings`.

**Domain clarifications** → meta PRD PR comment or tracked issue; record answers in
  `open-questions.md` and publish via Forge to the spec branch.
  Unresolved blocking domain items → outcome `needs-input`.

**Auto-fixable items** → leave in report; resolve in a later authorized edit —
  not during this read-only feasibility run.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-013.md` |
| Target branch | `chore/INIT-GATEFLOW-013-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-013-spec-gateflow  (spec-pending)
When ready:
  [ ] Source freshness is CURRENT
  [ ] All blocking PM questions answered on meta PRD PR
  [ ] All blocking Domain clarifications answered and published via Forge
  [ ] Spec updated to reflect answers (same branch, via Forge)
  [ ] Incremental re-run of /initiative-feasibility on updated spec is clean
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
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-013.md
  blockers:
    - FF-01
    - FF-02
    - FF-04
    - FF-05
    - FF-06
  signals:
    new_adr: true
    pe_blocking: 5
    pm_blocking: 0
    domain_blocking: 0
    verify_gap: 4
    source_freshness: CURRENT
    initiative: INIT-GATEFLOW-013
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/33"
    meta_pr_head: "59301dce846043b8a4e70057a81dfa67a4868ece"
    map_revision: 1
    source_prd_digest: sha256:c3653bdc5ab7f7aa679962d034a74efe3ea11040ab9db5c79b1e207a3540dbb1
    repo_scope_digest: sha256:17921af2c90e9d375914cf7e649d8dc25ad8dba7a669cf74d3d1ffe3188d719e
    ripple_action: continue
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```
