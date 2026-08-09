## Pre-implement — gateflow / W0 — Connect programme + catalogue discovery

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W0.md` |
| Initiative | INIT-GATEFLOW-013 |
| Wave | W0 |
| Date | 2026-08-09 |
| Outcome | `pass` |
| Outcome reason | Spec merged with `spec-lgtm`; board seeded; WorkManifest pass; PE sign-off complete; P15 live verify contracted; H1–H3 CURRENT |
| Wave head context | Bound by Forge/human context: `develop` @ `a3fa3677e57bda725a478d1fb31e1e2386491183` — recommended coding branch `feature/INIT-GATEFLOW-013-w0-programme-connect` (not opened by this skill) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` (not `chore/*-spec-*`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR #198 → `develop` @ `a3fa367…` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` on #198 |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC #199; W0 #200 (parent #199); TASK-W0-01…06 in body |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete |
| Live-verification contract | When P15 applies: `verification.live` + script under `live_verify_dir` | [x] contract — `tests/verify/verify_programme_connect.py` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — H1/H2/H3 match product-spec header (G1 meta `59301dce…`) |
| Impact-map repo scope | revision and scope digest match | [x] match — revision `1`; scope `sha256:17921af2…` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 | [x] `.venv/bin/python -m tests.verify.verify_programme_connect` |
| `ground_command` | resolved or N/A with reason | [x] N/A — Pass-2 `/ground-spec` after wave-acceptance; no Makefile ground target |
| Co-shipped live verify (P15) | FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_programme_connect.py` (TASK-W0-06) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] N/A — W0 first wave of INIT-013 |
| Prior Ground Report exists | `reports/Ground-Report-*-W{N-1}.md` | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-09 (@nikd10x) |

**Gate verdict:** PASS

**Forge readiness:** `handoff.forge` → `/commit-workspace` to publish this checklist onto bound head (recommend cut/bind `feature/INIT-GATEFLOW-013-w0-programme-connect` before `/loop-spec` coding commits).

---

### Contracts consumed (from prior Ground Report)

> W0 has no INIT-013 prior Ground Report. Cross-initiative contracts from
> INIT-GATEFLOW-012 as-built / live code (scan `src/`) — treat as **confirmed
> at source**, not as Ground-Report-W−1.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Tenant git clone/fetch | `TenantGitWorkspaceClient.resolve_workspace` | `TenantWorkspaceCredential` (tenant_id, org, repo, pat, absolute workspace_root) | `WorkspaceResolveResult` (path + clone\|fetch mode) | INIT-012 W1 as-built + `src/infra_services/tenant_git_workspace_client.py` | [x] yes — **no `ref` yet** (TASK-W0-02 adds optional ref) |
| Tenant registry persistence | `TenantRepository` / `TenantService` | tenant DTOs; session_factory | Pydantic tenant/repo rows | INIT-012 W0 | [x] yes — extend with programme connection (TASK-W0-01); do not fake as `tenant_repos` row |
| Tenant bearer trust zone | Auth middleware → `request.state.auth` → tenant-scoped routes | bearer JWT; path `tenant_id` must match | 401/403 on mismatch | ADR-011 Accepted | [x] yes — new programme routes stay tenant-scoped |
| Workspace layout authority | `{workspace_root}/{org}/{repo}` + per-org+repo lock | absolute root only | local checkout path | ADR-010 Accepted | [x] yes — programme meta uses same layout |
| Catalogue YAML existence (CTR-01) | meta `config/programme.yaml` + `config/service-catalog-<org>.yaml` | filesystem tree under synced checkout | candidate list | prayog-meta / ADR-012 | [x] yes — discovery-input class (not GATEFLOW_* knobs) |

**Unconfirmed contracts:**
- Exact OpenAPI path strings for connect/catalogue — deferred to OpenAPI in `/loop-spec` (spec Q-1); keep tenant-scoped, body models in `src/models/`.
- Human Alembic for `tenant_programme_connections` — DEP-01; agent writes schema + DDL note only (`database-migrations.mdc`).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `architecture.mdc` — layered `src/`; api → business → repo
  - [x] `repository-pattern.mdc` — ORM only in schema/repo; Pydantic at boundary
  - [x] `database-migrations.mdc` — no agent writes under `postgres_migrations/versions/`
  - [x] `dependency-injection.mdc` / `infra-services.mdc` — `@inject`; settings via `get_instance()`
  - [x] `pydantic-schemas.mdc` / `http-api-conventions.mdc` — models in `src/models/`; body for writes
  - [x] `fail-fast.mdc` / `logging-loguru.mdc` — named failures; structured kwargs
  - [x] `testing-verify-flows.mdc` / `python-tooling.mdc` — co-ship live verify; `make check`/`test`
  - skipped: messaging/telemetry-only MDCs not touched by W0 connect/catalogue
- [x] ADRs (keyword-matched):
  - [x] ADR-012 — catalogue discovery-input authority (Accepted) — **primary for TASK-W0-03**
  - [x] ADR-004 — programme config knobs stay process settings; do not load GATEFLOW_* from meta YAML
  - [x] ADR-011 — tenant bearer trust zone for new routes
  - [x] ADR-010 — workspace path authority (reuse clone/fetch layout)
  - skipped for W0 coding: ADR-013 (status dual evaluators — W3)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` (REQ-01–07, REQ-28)
- [x] Plan wave / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-013.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/200 — TASK list:
  - [x] TASK-W0-01 — implements REQ-01, REQ-28 — depends_on: [] — `tenant_programme_connections` schema/repo + DDL note — proof: review
  - [x] TASK-W0-02 — implements REQ-01 — depends_on: [TASK-W0-01] — optional `ref` on `resolve_workspace` — proof: `make test`
  - [x] TASK-W0-03 — implements REQ-05, REQ-06, REQ-07 — depends_on: [TASK-W0-01] — CatalogueParser + models — proof: `make test`
  - [x] TASK-W0-04 — implements REQ-01–07, REQ-28 — depends_on: [TASK-W0-02, TASK-W0-03] — onboarding service + routes + DI — proof: `make check`
  - [x] TASK-W0-05 — implements REQ-02, REQ-03, REQ-04, REQ-28 — depends_on: [TASK-W0-04] — unit tests — proof: `make test`
  - [x] TASK-W0-06 — implements REQ-01, REQ-04, REQ-05, REQ-06, REQ-28 — depends_on: [TASK-W0-04] — live `verify_programme_connect` + as-built/README — proof: live script

---

### Governance alignment

- [x] Slice does not contradict ADR-012 / ADR-004 / ADR-011 / ADR-010
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed
- [x] ADR-012 is **Accepted** in `docs/specification/adr/`

**Placement note:** plan FILE path `src/engine/catalogue_parser.py` — `src/engine/` package does not exist yet. `/loop-spec` may create `src/engine/` **or** place parser under `src/business_services/` per TDD §2; keep parse pure (no network) and models in `src/models/`.

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract wording changes (prefer no change for W0)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-013 W0 verification row
- [ ] `tests/README.md` — feature-map row for `verify_programme_connect`
- [ ] Unit — catalogue parser fixtures; connect upsert/fail-closed; optional ref
- [ ] Live — co-ship `tests/verify/verify_programme_connect.py` (human at `wave-acceptance`)
- [ ] ADR — none to supersede in W0
- [ ] `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-programme-connection.md` — human Alembic input

---

### Must not

- [ ] Implement against wording that treats catalogue YAML as ADR-004 GATEFLOW_* knobs
- [ ] Write files under `postgres_migrations/versions/`
- [ ] Put Pydantic models under `src/api/`
- [ ] Log or return PAT
- [ ] Create a second programme connection row per tenant (REQ-28)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Ship connect/catalogue HTTP without co-shipped live verify (P15)

---

### Engineering contracts to produce (W0)

| Contract | Entry point | Input | Output / invariants |
|----------|-------------|-------|---------------------|
| Persist programme connection | repository upsert/get on `tenant_programme_connections` | tenant_id, org, repo, optional ref, last_synced_at | Exactly one active row per tenant; DTO not ORM upward |
| Sync programme meta | `resolve_workspace` (+ optional ref) | tenant credential + programme org/repo/ref | Checkout under tenant workspace; fail-closed cleanup on error (REQ-04) |
| Parse catalogue | CatalogueParser from synced tree | absolute meta root + org | Full candidate list or named shape error — never partial (REQ-06); ADR-012 discovery-input |
| Connect API | tenant-scoped HTTP (body: org, repo, optional ref) | bearer + tenant_id path | Connection record; no PAT; upsert not insert-second (REQ-28) |
| Catalogue API | tenant-scoped HTTP GET (or equivalent read) after connect | tenant_id | Candidates from latest sync (REQ-05/07) |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | parser, git ref, connect fail-closed, single connection | `make test` |
| Live verify | connect + catalogue on running API (human @ wave-acceptance) | `.venv/bin/python -m tests.verify.verify_programme_connect` |
| Ground check | Pass-2 after accept | N/A — `/ground-spec` |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_programme_connect`
- [ ] Confirm connect + catalogue behaviour
- [ ] Label tip `wave-accepted` (human only)
- [ ] Tip hygiene before Pass-2

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-013
- Issue: [#200](https://github.com/drivestream-lab/gateflow/issues/200) (EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199))
- Spec path: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_programme_connect`
- ADRs in scope: ADR-012 (primary), ADR-004, ADR-010, ADR-011
- Wave head: `develop` @ `a3fa367…` (cut `feature/INIT-GATEFLOW-013-w0-programme-connect` before coding)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied; checklist ready for Forge publish |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-013-W0.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo W0. Human applies Alembic from DDL note before live verify against a real DB.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W0
    board_issue: https://github.com/drivestream-lab/gateflow/issues/200
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
      - TASK-W0-06
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_programme_connect
    ground_command: null
    workmanifest_contract: pass
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
    include_paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W0.md
```
