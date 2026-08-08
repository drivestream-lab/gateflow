# Feasibility report — INIT-GATEFLOW-012

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-012 |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Spec digest | `sha256:b8a490e7e7c7ceb02f18097d9164611086d2c7aecd1d9c2e0a6b0a7495a13190` |
| PRD digest | `sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-012.md` / `1` |
| Repo scope digest | `sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678` |
| Approved meta PR head | `74402540efd98527014b4706d0d29bda1242b6cf` |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/32#pullrequestreview-4885261904) 2026-08-07T17:45:36Z on `7440254…` — [prayog-meta#32](https://github.com/drivestream-lab/prayog-meta/pull/32) |
| Source freshness | **CURRENT** — H1/H2/H3 match live meta @ `7440254…`; G1 APPROVED review on same head; label `impact-map-lgtm`; pin `v0.5.0-rc.2` ≡ submodule `75b207c` |
| Prior stage | `/spec-draft` → `pass` (handoff baton) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-07 |
| Branch | `chore/INIT-GATEFLOW-012-spec-gateflow` — Draft spec PR [#183](https://github.com/drivestream-lab/gateflow/pull/183) (single review surface) |
| Initiative segment | `INIT-GATEFLOW-012` |
| Status | Draft |
| Review deadline | 2026-08-12 (3 business days) |
| Deciders | PM: programme PM · Domain SME: @drivestream-lab/prayog-pe-team |

## Summary

INIT-GATEFLOW-012's spec slice is **largely buildable** against the current
codebase — most seams already exist exactly where the PRD claims (the
`Path.cwd()` fallback point, `ForgeClient`'s method inventory, the
`LaunchpadClient.sync_harness` stub, `find_active_run`'s query shape, the
dormant JWT middleware) — but the spec's own scope is not the only thing
gating progress here. Three of this repo's **Accepted** ADRs constrain
territory this spec's requirements now enter, and the spec does not (and per
its own Ownership statement, correctly should not) resolve those conflicts
itself:

1. **ADR-010** (lane intake / dual-workspace authority) explicitly authorizes
   caller-supplied `workspace_path` as implement-intake authority. PRD D1 /
   spec REQ-10 reverses that assumption for Tenant-registered repos. The spec
   already flags this as Q-4 — feasibility elevates it to a **Critical** F13
   finding because it is a direct reversal of an Accepted ADR clause, not an
   ordinary implementation gap.
2. **ADR-002 / ADR-005** define exactly **three** Gateflow trust zones (JWT
   `AuthMiddleware`, forge-webhook signature, one shared global
   `PROGRAMME_SERVICE_TOKEN`). Spec REQ-03/G3 introduces a **fourth**
   mechanism — a per-tenant bearer token looked up by `tenant_id` — that
   none of the three documented zones describe. This was not flagged as its
   own spec question and is a new **Critical** F13 finding.
3. **ADR-003** answers "which GitHub credential in production?" as "App
   installation token in production; scoped PAT only when explicitly
   configured for non-prod." PRD D8 / spec REQ-11 chooses **PAT-only, in every
   environment**, for the new per-tenant credential. Whether this is a
   distinct credential domain ADR-003 never addressed, or a direct
   contradiction of its production policy, is unresolved — a third **Critical**
   F13 finding.

No PM or domain blocking items remain (spec Q-1…Q-7 are all non-blocking with
recorded defaults). No repo/gate closure. Given the outcome rubric's ordering
(`stale` → `failed` → `blocked` → `needs-input` → `findings` → `pass`), the
three unresolved Critical PE/ADR items select **`findings`** — which routes to
`/spec-technical-review` identically to `pass` (pin routes both there), so this
does not stall the programme; it means the next stage must produce Draft ADR
dispositions for all three before an implementation plan is safe to write.

**Findings:** 9 total (3 Critical, 1 Should fix, 2 Verify, 3 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 1 (Q-7 residual) | 0 |
| PE / ADR | 3 (FF-01…03) | 3 (FF-04, FF-06, PE-1) | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 0 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 3 |
| Should fix | 1 |
| Verify / Gap (informational) | 5 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `findings` |
| Rationale | Source freshness CURRENT; zero unresolved blocking PM/domain items; but three Critical, unresolved PE/ADR items (FF-01…03) directly contradict Accepted ADR-010, ADR-002/005, and ADR-003 clauses — first-matching rule in the lane-to-outcome rubric is `findings`, not `pass` |
| Next (from workflow) | `spec-technical-review` |

Informational Gap/Verify observations alone would not select `findings` — the
three Critical ADR-conformance findings are what select it here. Technical
review is required by the pin regardless of `pass` vs `findings`, so this
finding set changes **what** technical review must produce (three Draft ADR
dispositions), not **whether** it runs.

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Toolchain | `make check` (black, ruff, pyright, import-linter) | `Makefile`; `.harness/profile.yaml` |
| Unit tests | `make test` → `tests/unit/` — 46 test modules; **zero** for Tenant, workspace-prep, or `LaunchpadClient` today | directory listing 2026-08-07 |
| Live verify | 22 scripts under `tests/verify/`; none for tenant/workspace/branch lifecycle | `tests/README.md` feature map |
| Pin consume | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` ≡ submodule `75b207ce0885ddaa28056cd624b4588efa3d960d` | `git -C prayog-skills rev-parse HEAD` |
| As-built | INIT-001…011 matrices; **no INIT-012 section yet** (expected — pre-implementation) | `docs/specification/as-built/implementation-status.md` |
| Local git dependency | **None** — no `GitPython`/`pygit2`/subprocess-git usage anywhere in `src/`; `ForgeClient` is httpx REST/GraphQL only | `pyproject.toml` dependency list; `src/infra_services/forge_client.py` (no `subprocess`/`git` import) |
| CI | `.github/workflows/ci.yml` — `make check-ci` + unit | as-built INIT-009 row |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01–09, REQ-32 / W0 | Tenant registry data model + API | No `tenants`/`tenant_repos`/`tenant_users` schema, repository, business service, or routes exist | — | — | **gap** (net-new domain) |
| REQ-10 / W1 | Resolve deterministic workspace before dispatch, replacing `Path.cwd()` fallback | Fallback point confirmed live: `run_orchestrator.py:237` (`workspace_path = context.workspace_path or str(Path.cwd())`) | — | — | **partial** (seam exists; resolution logic does not) |
| REQ-11 / W1 | Clone/refresh authenticated with Tenant PAT | No local git transport exists; no git library dependency | — | — | **gap** (net-new infra) |
| REQ-12 / W1 | Explicit `workspace_path` unchanged (additive) | Already true today — no other lane touches this path | `test_wave_start.py` (existing) | `verify_wave_start` | **exists** (regression-only) |
| REQ-13/14 / W1 | Fetch-in-place; fail closed on mismatched remote | No workspace-validity check exists | — | — | **gap** |
| REQ-15 / W1 | Unregistered repo + omitted path → 422 | Today this case hits the `Path.cwd()` fallback, not 422 | — | — | **gap** (behavior must change, not just add) |
| REQ-16 / W2 | New wave forks from live `develop` tip | `ForgeClient.ensure_branch_from_base` + `_ensure_run_branch` already run this exact fork-from-base at every run start today | `test_forge_client.py`, `test_run_orchestrator.py` (`test_ensure_branch_before_stage_*`) | `verify_implement_lane` | **partial** (mechanism exists; new-vs-continuation branch decision does not) |
| REQ-17 / W2 | Deterministic naming, no second scheme | `build_wave_head_branch` already implements this | `test_pr_branch_naming.py` | — | **exists** |
| REQ-18 / W2 | Continuation reuses existing head ref | `branch_slug_from_head_ref` already exists and is used today by closeout (Pass-2) lane (`WaveStartService.start_closeout_wave`) | `test_pr_branch_naming.py` | `verify_wave_closeout` | **partial** (precedent code exists; wiring into implement-lane CAP-03 does not) |
| REQ-19 / W2 | Continuation composes with never-cloned workspace | Depends entirely on REQ-10/11 (CAP-02), which are gaps | — | — | **gap** |
| REQ-20–22 / W3 | Real harness-readiness check + cache | `LaunchpadClient.sync_harness` stub exists, DI-wired, already invoked pre-dispatch in `run_orchestrator.py:238`; it is path-exists-only, no cache | **none** — `LaunchpadClient` has zero unit test coverage today (baseline gap, not new) | — | **partial** |
| REQ-23/24 / W4 | Broaden `NO_CONCURRENT_RUN` to repo scope | `find_active_run` already filters `org`+`repo` first (`run_store_repository.py:198-227`); only the narrowing branches (`initiative_id`+`wave_id` / `pr_number` / `issue_number`) need removal | `test_wave_start.py` (existing narrower-key assertions will need updating) | `verify_wave_start` | **partial** (well-bounded query change) |
| REQ-25 / W4 | No new isolation mechanism | Trivially true today — nothing to prove wrong | — | — | **exists** |
| REQ-26/27 / W5 | `ForgeClient.delete_branch` + fail closed | Confirmed absent from `ForgeClient`'s method inventory | `test_forge_client.py` (existing file, no `delete_branch` tests) | — | **gap** |

## ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-010 | lane intake, dual workspace authority, caller-supplied `workspace_path` | **Accepted** — **conflict** (FF-01) |
| ADR-002 | edge trust model / three trust zones | **Accepted** — **conflict** (FF-02) |
| ADR-005 | programme-token control-plane mutations (supersedes ADR-002's read-only row only) | **Accepted** — **conflict** (FF-02) |
| ADR-003 | slot/layer ownership; forge credential policy (Q-1: App in prod, PAT non-prod) | **Accepted** — **conflict** (FF-03) |
| ADR-001 | runtime topology, Postgres SSOT, repository-only ORM, human-owned Alembic | **Accepted** — aligned (new Tenant tables are additive; spec correctly defers exact schema, §4 Appendix A explicitly "illustrative — engineering owns exact schema") |
| ADR-009 | pin `forge:` publish/mutate authority, dual `authorization` | **Accepted** — aligned (REQ-26/27 add a `ForgeClient` method only; no pin node/authorization wiring happens in this repo — that is `prayog-skills`' REQ-28, out of this spec's scope) |
| ADR-004 | programme config authority (non-secret carrier, secrets in env/secret store) | **Accepted** — aligned, distinct domain (governs this repo's own non-secret runtime config carrier; a per-tenant credential stored as a database row is a different concern the spec's NFR Security section already carries as an explicit risk, G1) |
| ADR-006, ADR-007, ADR-008 | adapter registry / AgentRunner message contract / packaged-skill handoff ingest | Accepted — domain not matched (no adapter, prompt-contract, or handoff-ingest change in this spec) — **skipped** |

## ADR traceability (F13)

> **Finding must start with the literal prefix `ALTERNATIVE:`** — see
> `governance.md`. Spec quotes below are verbatim, bounded excerpts from
> `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`, used only as
> lint evidence for `/spec-technical-review`.

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-10 / W1 | ADR-010 | **conflict** | `ALTERNATIVE: express PRD D1's reversal of ADR-010's caller-supplied-workspace_path authority as a new clause amending ADR-010 (parallel to its existing §6/§7 amendments) vs. a new superseding ADR — ADR-010 §2 Recommendation currently states implement intake authority "must not require meta PR / meta workspace fields" and makes no exception for a self-sufficient workspace path` |
| REQ-01–09, REQ-32 / W0 | ADR-002, ADR-005 | **conflict** | `ALTERNATIVE: whether the new per-tenant bearer-token mechanism (G3) is a fourth Gateflow trust zone requiring a new or amended ADR, vs. an extension of ADR-005's existing "programme control-plane" zone — ADR-005 Option C widened that zone to "reads + documented writes" under one shared static secret, not a per-identity-keyed set of secrets` |
| REQ-11 / W1 | ADR-003 | **conflict** | `ALTERNATIVE: whether a per-tenant GitHub PAT used in production (D8, no environment carve-out) is a distinct credential domain outside ADR-003's Q-1 scope, vs. a direct contradiction of ADR-003's stated recommendation "App installation token in production; scoped PAT only when explicitly configured for non-prod"` |
| REQ-16–19 / W2 | ADR-010 (D2) | aligned | — |
| REQ-20–22 / W3 | N/A (no architectural constraint touched) | aligned | — |
| REQ-23–25 / W4 | ADR-001 (query-shape change on existing table only, no new schema) | aligned | — |
| REQ-26/27 / W5 | ADR-009 (method addition only; no node/authorization wiring in this repo) | aligned | — |

## MDC pass (pre-T2)

| MDC file | Domain | Read / skipped |
|----------|--------|----------------|
| `architecture.mdc` | layer boundaries, service profiles, JWT verification | read — spec correctly leaves module placement to technical review; local-git transport belongs in `infra_services/` per `infra-services.mdc`'s own third-party-API criteria |
| `infra-services.mdc` | new outbound clients (local git transport, first inside Gateflow) | read — spec's CTR-02 attributes local git to infra correctly; no conflict |
| `dependency-injection.mdc` | new services (Tenant repo/service, git-workspace client) | read — spec is silent on DI wiring by design (Ownership statement); no conflict |
| `http-api-conventions.mdc` | new `POST /api/v1/tenants`, `POST .../users`, `GET` list/detail | read — spec's Target API surface uses JSON body for POST, no query-string payload fields; compliant |
| `pydantic-schemas.mdc` | new Tenant models, `board` default field, PAT field naming | read — spec correctly avoids inventing model shapes; flags PAT-never-in-response as a REQ (REQ-02/32), which is the right acceptance-level statement for this layer |
| `repository-pattern.mdc`, `database-migrations.mdc` | new `tenants`/`tenant_repos`/`tenant_users` tables | read — spec Appendix A is explicitly "illustrative — engineering owns exact schema"; no conflict in the spec text itself. **Reminder for plan stage** (not a spec defect): `postgres_migrations/versions/` stays human-owned — agents update `schema/` + `env.py` imports only |
| `fail-fast.mdc` | new 400/401/422 fail-closed paths | read — every REQ in Negative and failure paths fails closed with a named reason; no silent defaults; compliant |
| `logging-loguru.mdc` | structured logs for registration/clone/harness/concurrency | read — spec NFR Observability row explicitly states PAT/secret values must never be logged and IDs are kwargs; compliant |
| `strong-typing.mdc`, `python-imports.mdc` | general typing/import discipline | read — no spec wording implies `dict`-typed service signatures, `TYPE_CHECKING` imports, or `Any`; no conflict |
| `spec-driven-development.mdc` | truth hierarchy, same-PR discipline | read — spec correctly defers architecture decisions and cites this skill's own governance for that boundary |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F13 | "PRD D1 **reverses** that assumption for Tenant-registered repos only (unregistered/legacy callers unaffected)" | ADR-010 | `ALTERNATIVE: ADR-010 amendment (new clause) vs. a new superseding ADR for Tenant-registered workspace authority` |
| FF-02 | F13 | "Registration issues a tenant-scoped bearer token distinct from the existing global `PROGRAMME_SERVICE_TOKEN`" | ADR-002, ADR-005 | `ALTERNATIVE: fourth Gateflow trust zone (new/amended ADR) vs. extension of ADR-005's existing single-shared-secret programme control-plane zone` |
| FF-03 | F13 | "Clone/refresh authenticates git operations with the Tenant's stored PAT — the same credential used for `ForgeClient` platform calls (**G2**, accepted risk — see NFR Security)" | ADR-003 | `ALTERNATIVE: per-tenant production PAT as a distinct credential domain vs. contradiction of ADR-003's "App installation token in production" recommendation` |
| — | F14 | Target API surface — `POST /api/v1/tenants` (body-only) | `http-api-conventions.mdc` | aligned — no conflict |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F13 | Spec REQ-10/CAP-02 directly reverses ADR-010's implement-intake authority ("must not require meta PR / meta workspace fields," caller-supplied `workspace_path` unconditional) for Tenant-registered repos, with no Draft ADR yet disposing the change | `docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md` §2 Recommendation item 2; spec header "Architecture constraints" row |
| FF-02 | F13 | Spec REQ-03/G3 introduces a fourth auth mechanism (per-tenant bearer token) outside the three trust zones ADR-002 defines and the single-secret zone ADR-005 widens | `docs/specification/adr/adr-002-edge-trust-model.md` Recommendation (three zones); `docs/specification/adr/adr-005-programme-token-control-plane-mutations.md` Option C |
| FF-03 | F13 | Spec REQ-11/D8 chooses PAT-only for the new per-tenant credential in every environment, while ADR-003's Q-1 answer restricts production Gateflow-held GitHub credentials to App installation tokens | `docs/specification/adr/adr-003-slot-layer-ownership.md` Recommendation, "Forge credentials (Q-1)" |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-04 | F10 | Local git clone/fetch transport (REQ-10/11) has no existing library dependency or precedent in this codebase — subprocess `git` CLI vs. `GitPython` vs. `pygit2` is unresolved. Governance's own bar ("locally reversible implementation choice already bounded by rules is an ordinary finding, not a NEW-ADR") applies — this is a PE design question for `/spec-technical-review`, not an ADR-qualifying alternative | `pyproject.toml` dependency list (no git library); `src/infra_services/forge_client.py` (httpx-only transport, no `subprocess`) |

### Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-05 | F4 | `LaunchpadClient` has zero unit test coverage today — pre-existing baseline gap, not introduced by this INIT, but CAP-04 (REQ-20–22) will be the first work to actually exercise it beyond the path-exists stub, so it needs its first-ever test file, not just extension of one | `tests/unit/` directory listing — no `test_launchpad_client.py` |
| FF-06 | F2 | No unit test file exists yet asserting the broadened `find_active_run` query (REQ-23) against representative historical narrower-key run patterns, which the spec's own NFR Migration/compatibility row calls out as a required regression check before the query changes | Spec NFR row; `tests/unit/` — no fixture asserting cross-repo non-blocking today beyond `test_wave_start.py`'s narrower-key cases |
| PE-1 | F13 | Whether the `prayog-skills` contract PR (CTR-01, REQ-28–31) needs to land — and be remounted (0 BROKEN nodes) — **before** this repo's W1/W2 implementation work starts, or whether gateflow can implement CAP-02/CAP-03 against a stub/interface first and wire the pin dependency later, is an open sequencing question the spec's own Overview flags (line: "W1/W2 exit... depend on the `prayog-skills` contract PR landing first") but does not fully resolve as a build-order constraint | Spec Overview "Delivery waves" note; impact map §7 dependency order |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| **W0** Tenant registry | new `src/models/tenant_models.py`-style module; `src/database/postgres/schema/` (new tables) + `postgres_migrations/env.py` (import only — human owns `versions/`); new repository under `src/database/postgres/repository/`; new business service under `src/business_services/`; new `src/api/v1/tenant_routes.py`-style router | new `tests/unit/test_tenant_*.py`; new `tests/verify/verify_tenant_registry.py` |
| **W1** Clone/refresh | new infra client under `src/infra_services/` (local git transport); `src/business_services/run_orchestrator.py` (replace `Path.cwd()` fallback at line 237) | new `tests/unit/test_workspace_prep.py`-style file; extend `test_run_orchestrator.py`; new `tests/verify/verify_workspace_lifecycle.py` (fixture repo) |
| **W2** Branch create-or-reuse | new/extended business logic composing `ForgeClient.ensure_branch_from_base` + `pr_branch_naming.branch_slug_from_head_ref`; likely `run_orchestrator.py` or a new branch-resolver module | extend `test_run_orchestrator.py`, `test_pr_branch_naming.py` |
| **W3** Harness-readiness | `src/infra_services/launchpad_client.py` (extend `sync_harness` beyond path-exists); caching location (Tenant row column vs. separate table — technical review) | **new** `tests/unit/test_launchpad_client.py` (first-ever, see FF-05); fixture repos with/without `.harness-pin.yaml` |
| **W4** Repo-scoped concurrency | `src/database/postgres/repository/run_store_repository.py` (`find_active_run` query change, lines 198-227) | extend `tests/unit/` run-store/wave-start concurrency tests (see FF-06 regression fixture) |
| **W5** Branch purge (gateflow half) | `src/infra_services/forge_client.py` (new `delete_branch` method, reusing `_git_ref_update_path` DELETE shape) | extend `tests/unit/test_forge_client.py` |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Three Critical ADR-conformance findings (FF-01…03) could each independently require a new Draft ADR — technical review scope is larger than a typical "confirm alignment" pass | Budget `/spec-technical-review` for three ADR dispositions, not zero; do not treat this as a rubber-stamp pass |
| R-2 | Local git as new attack surface (first-ever local git execution inside Gateflow, PRD's own framing) compounds with the FF-03 production-credential question — a wrong disposition here has real security blast-radius, not just a style question | Resolve FF-03 before implementation plan names concrete git-library TASKs |
| R-3 | Broadening `find_active_run` to repo-scope (REQ-23) could surface latent double-starts in real historical usage that today's narrower key silently allowed (spec's own NFR row already names this) | Require the regression fixture (FF-06) before the query changes ship, not after |
| A-1…A-5 | Spec assumptions (GitHub host, persistent disk, `LaunchpadClient` extension point, `find_active_run` query-only change, `BoardTicketCreateRequest` override precedent) | All five **confirmed** directly against code this session (see spec's Assumptions table); A-2 (persistent disk) additionally corroborated by `GATEFLOW_HANDOFF_ROOT`'s existing requirement for a persistent, absolute, cross-run directory (`src/configs/orchestration_settings.py`) — stronger evidence than the spec cites alone |

## Recommended spec edits

- None blocking — the spec's own Ownership statement correctly declined to
  pre-decide ADR-10/ADR-002/ADR-003 disposition, which is exactly why these
  are feasibility findings rather than spec defects.
- Optional, non-blocking: promote Q-6 (REQ-29 verification boundary) into an
  explicit cross-reference to FF-06's regression-fixture requirement when the
  spec is next revised, so both sides of "what proves the concurrency change
  is safe" live next to each other.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| FF-01 | PE | ADR-010 amendment vs. new ADR for Tenant-registered workspace authority reversal (D1) | yes | prayog-pe-team | open | technical review | none — must be disposed before `/spec-implementation-plan` can name CAP-02 TASKs | ADR-010 §2; spec REQ-10 | pending `/spec-technical-review` |
| FF-02 | PE | Fourth trust zone (per-tenant bearer token, G3) vs. extension of ADR-005's shared-secret zone | yes | prayog-pe-team | open | technical review | none — must be disposed before CAP-01 auth TASKs are planned | ADR-002, ADR-005; spec REQ-03/G3 | pending `/spec-technical-review` |
| FF-03 | PE | Per-tenant production PAT (D8) vs. ADR-003's App-in-production credential policy | yes | prayog-pe-team | open | technical review | none — security-bearing; must be disposed before CAP-02 credential TASKs are planned | ADR-003 Q-1; spec REQ-11 | pending `/spec-technical-review` |
| FF-04 | PE | Local git transport library choice (subprocess vs. `GitPython` vs. `pygit2`) | no | prayog-pe-team | open | implementation plan | Ordinary PE design decision, not ADR-qualifying; technical review or plan may pick | pyproject.toml; spec CTR-02 | pending `/spec-technical-review` or plan |
| FF-05 | PE | `LaunchpadClient` needs its first-ever unit test file for CAP-04 | no | prayog-pe-team | open | plan §9 (W3 TASKs) | Add `test_launchpad_client.py` as part of W3 scope | `tests/unit/` inventory | pending plan |
| FF-06 | PE | Regression fixture for broadened `find_active_run` against historical narrower-key patterns | no | prayog-pe-team | open | plan §9 (W4 TASKs) | Add fixture-based regression test as part of W4 scope | spec NFR Migration row | pending plan |
| PE-1 | PE | `prayog-skills` contract PR (CTR-01) sequencing — hard gate before W1/W2, or gateflow can implement against a stub first | no | prayog-pe-team | open | technical review | Treat as a hard gate (matches impact map §7 dependency order) unless technical review finds a safe stub path | impact map §7; spec Overview | pending `/spec-technical-review` |
| Q-7 (carried from spec) | PM | G1 plaintext-PAT explicit acknowledgment residual — matching APPROVED review vs. a separate one-line sentence | no | programme PM | open (non-blocking, per spec) | before implementation begins | Treat matching APPROVED review as sufficient; recommend an explicit one-line follow-up comment for audit trail | spec Q-7; impact map IM-04 | pending PM comment on meta PR #32 |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

_None._

#### Defer — can proceed with documented assumption

1. **Q-7** (carried) — G1 acknowledgment residual; default: matching APPROVED review is sufficient, recommend an explicit follow-up comment for audit clarity.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

> These are **not** for PM. `/spec-technical-review` must produce Draft ADR
> files disposing FF-01, FF-02, and FF-03 before `/spec-implementation-plan`
> can safely name CAP-01/CAP-02 TASKs.

#### Blocking for implementation plan

1. **FF-01** — ADR-010 amendment vs. new ADR for the Tenant-registered workspace-authority reversal.
2. **FF-02** — New/amended ADR for the per-tenant bearer-token trust zone vs. extending ADR-005's shared-secret zone.
3. **FF-03** — Per-tenant production PAT policy vs. ADR-003's App-in-production credential recommendation.
4. **PE-1** — `prayog-skills` contract PR (CTR-01) sequencing relative to gateflow W1/W2.

#### Defer with default

1. **FF-04** — Local git transport library choice; ordinary design decision, not ADR-qualifying.
2. **FF-05 / FF-06** — Missing regression/first-time test coverage; carried into plan §9 as explicit W3/W4 TASKs, not blocking technical review.

### Domain clarifications (business source-of-truth)

_None._

### Auto-fixable (agent resolves later — not inside this skill)

_None recorded._

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | — |
| F2 Spec → code map | PASS | FF-06 (Gap) |
| F3 Spec → verify map | PASS | none — spec correctly names new verify scripts per wave |
| F4 Spec → unit map | PASS | FF-05 (Gap) |
| F5 As-built drift | PASS | expected — no INIT-012 as-built section yet (pre-implementation) |
| F6 Docs drift | PASS | README active-initiative pointer updated same PR |
| F7 Overlap risk | PASS / N/A | no duplicated unit+live journey beyond the expected positive/negative harness fixture pair |
| F8 CI vs live boundary | PASS | spec's evidence layers correctly split unit (CI) vs. verify (live-only) per wave |
| F9 Cross-service touch | PASS | CTR-01…03 files/contracts exist or are correctly deferred (prayog-skills pin, GitHub REST, launchpad format-only) |
| F10 Assumptions | PASS | A-1…A-5 confirmed with direct code evidence; FF-04 (Should fix) on git-library choice |
| F11 Effort drivers | PASS | W0/W5 well-bounded; W1 (new infra, no library precedent) and W3 (first-ever test coverage) are the real complexity drivers |
| F12 PM questions | PASS | Q-7 carried, non-blocking, numbered |
| F13 ADR conformance | **FAIL (blocking)** | FF-01, FF-02, FF-03 — three Critical, unresolved conflicts with Accepted ADRs |
| F14 MDC conformance | PASS | no conflicts found in spec wording |

**Check PASS** = zero unresolved blocking findings. F13 is the blocking
failure that selects `findings` — all other checks pass.

---

## Next steps

Persist this report locally. Fill `handoff.forge` for `/commit-workspace` onto
the Draft spec PR branch — **do not** commit, push, open PRs, or apply labels
inside this skill. Gate 2 stays **`spec-pending`**.

**PM questions** → meta PRD PR [#32](https://github.com/drivestream-lab/prayog-meta/pull/32) comment (Q-7, non-blocking).

**PE questions** → Draft spec PR [#183](https://github.com/drivestream-lab/gateflow/pull/183); proceed
**`/spec-technical-review`** (pin routes `pass` and `findings` identically) —
that stage must produce Draft ADR files disposing FF-01, FF-02, FF-03, and a
sequencing disposition for PE-1, before `/spec-implementation-plan` runs.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-012.md` |
| Target branch | `chore/INIT-GATEFLOW-012-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-012-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [ ] Feasibility report published via Forge (/commit-workspace)
  [ ] Proceed: /spec-technical-review — must dispose FF-01, FF-02, FF-03, PE-1
  [ ] After TDD + ADRs + plan on branch: PE sets spec-lgtm on exact head → merge
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-012.md
    digest: sha256:7d4beaedff2d11359678d0381f651dfd72a33d5975bedda2cabf99123858b8eb
  blockers:
    - FF-01
    - FF-02
    - FF-03
  signals:
    initiative: INIT-GATEFLOW-012
    source_freshness: CURRENT
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/32"
    meta_pr_head: "74402540efd98527014b4706d0d29bda1242b6cf"
    map_revision: 1
    prd_digest: "sha256:542a3680ac0a05917758c90a23c38681a20d47e0428bc30a41d539fd2f7bfb5b"
    scope_digest: "sha256:85e75d8b61e0002b4c60aecd257aa0f9fdc99428a275083f0861f461ae04c678"
    ripple_action: continue
    new_adr: true
    lane_counts:
      pm: 1
      pe: 4
      domain: 0
      auto_fix: 0
    findings_critical: 3
    findings_should_fix: 1
    findings_verify: 0
    findings_gap: 2
    pin_ref: v0.5.0-rc.2
    pin_sha: "75b207ce0885ddaa28056cd624b4588efa3d960d"
    nonblocking_questions: "Q-7"
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: initiative-feasibility forge.commit_workspace = required.
    # Publish this report onto the Draft spec PR head — invoke /commit-workspace
    # (or Gateflow ForgeClient). This skill does not mutate.
```
