## Pre-implement — drivestream-lab/gateflow / W3 — Harness-readiness check

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W3.md` |
| Initiative | INIT-GATEFLOW-012 |
| Wave | W3 |
| Date | 2026-08-08 |
| Outcome | `pass` |
| Outcome reason | W2 `human_approved` + Ground-Report; WorkManifest contract pass; board [#188] seeded under EPIC [#184]; P15 live contracted; develop @ `2aa2094…` |
| Wave head context | Integration tip: `develop` @ `2aa2094…` (W2 merge [#193](https://github.com/drivestream-lab/gateflow/pull/193)). Intended coding head: `feature/INIT-GATEFLOW-012-w3-harness-ready` — **cut from develop before `/commit-workspace` / `/loop-spec`** (this skill does not open the branch) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Board / branch / PR checks are **read-only**.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `2aa2094…` (feature head not yet cut) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#183](https://github.com/drivestream-lab/gateflow/pull/183) MERGED (`b83006c…`); plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — [#188](https://github.com/drivestream-lab/gateflow/issues/188) parent EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184); body has TASK-W3-01…05 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `WorkManifest contract passed.` (`prayog-skills/scripts/workmanifest_contract.py`) |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W3-01…05 |
| Live-verification contract | P15: live script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_harness_readiness` |
| Plan source freshness | H1–H3 / G2 durable roots | [x] current — product + plan on `develop` via [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Impact-map repo scope | match | [x] match |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` (P15) | [x] `.venv/bin/python -m tests.verify.verify_harness_readiness` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_harness_readiness.py` (create in TASK-W3-04) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W2 = **human_approved** (`wave-accepted` on [#193](https://github.com/drivestream-lab/gateflow/pull/193); merge `2aa2094…`) |
| Prior Ground Report exists | `Ground-Report-…-W2.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W2.md` |
| Plan PE sign-off (W0 only) | N/A for W3 | [x] N/A |

**Gate verdict:** **PASS**

**Notes for loop-spec (not start-blocks):**
- `tenant_repos.harness_verified` already exists on ORM + W0 DDL-NOTE — prefer **persist/read via repository** over inventing a second cache store; human Alembic already owns the column (agents do not write `postgres_migrations/versions/`).
- `LaunchpadClient.sync_harness` is still path-exists-only stub — W3 makes it a real harness-artifact check (CTR-03 / A-3).
- Orchestrator already calls `sync_harness` after workspace resolve — W3 must **skip probe when cached verified**, fail closed with named missing artifact when not ready, and set cache on success; wire order remains after workspace (+ W2 checkout) and before Enter-at skill.
- CTR-01 pin-shape remount remains DEP-02 (W2 PE waiver) — W3 consumes filesystem harness presence (CTR-03), not new pin node ids.
- Explicit **re-check** path (REQ-22): force-probe when cache true (API/path or internal flag) — do not leave “cache forever” with no escape hatch.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W2.md` §Contracts produced (+ W1 workspace contracts still binding). Confirmed against `src/` on `develop` @ `2aa2094…`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Workspace resolve (clone/fetch) | `TenantGitWorkspaceClient.resolve_workspace` | tenant credential | absolute path + mode | Ground-Report W1 | [x] yes |
| Orchestrator workspace bind | `RunOrchestrator._resolve_job_workspace_path` | org, repo, optional path | `(path, tenant_bound)` | Ground-Report W1/W2 | [x] yes — omit-path then checkout |
| Branch resolve | `RunOrchestrator.resolve_branch` | org, repo, run, payload | head + mode | Ground-Report W2 | [x] yes — runs before workspace sync |
| Local head checkout | `TenantGitWorkspaceClient.checkout_branch` | path, branch, org, repo | side-effect checkout | Ground-Report W2 | [x] yes — tenant-bound only |
| Launchpad stub slot | `LaunchpadClient.sync_harness` | workspace_path | void / raise | product baseline | [x] yes — DI-wired; path-exists only today (W3 extends) |
| Harness verified cache column | `TenantRepoSchema.harness_verified` | boolean default false | durable flag | Ground-Report W0 / DDL-NOTE | [x] yes — column present; repo write path still thin |

**Unconfirmed / must extend in W3:**
- **Real artifact check** — beyond `Path.is_dir()`: require expected harness files (at least `.harness-pin.yaml` / `.harness/` per CTR-03); named failure when absent
- **Cache skip + persist** — read `harness_verified` for tenant org/repo; skip redundant probe when true; set true after successful check
- **Re-check** — explicit force path that probes even when cached (REQ-22)
- **Wire timing** — after workspace resolve (+ checkout), before Enter-at / coding-hop dispatch (REQ-20); fail closed → named 422-class reason when check fails on start path that can surface it
- **First unit file** — `tests/unit/test_launchpad_client.py` (FF-05)
- **Human wave head** — cut `feature/INIT-GATEFLOW-012-w3-harness-ready` before publishing checklist / coding

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `infra-services.mdc` — LaunchpadClient stays infra; lifecycle + `@inject`
  - [x] `fail-fast.mdc` — missing harness → named fail; no silent skip
  - [x] `database-migrations.mdc` — no agent `versions/` writes; column already in ORM/DDL-NOTE
  - [x] `repository-pattern.mdc` — cache flag updates via tenant repository only
  - [x] `testing-verify-flows.mdc` — co-ship `verify_harness_readiness`
  - [x] `logging-loguru.mdc` — artifact names / verified flag as kwargs
  - [x] `architecture.mdc` / `python-imports.mdc` / `strong-typing.mdc`
- [x] ADRs (keyword-matched):
  - [x] ADR-010 — lane intake / walker composition (harness before coding hop)
  - [x] ADR-011 — tenant token zone unchanged (filesystem check only)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` — REQ-20…22; CTR-03; A-3
- [x] Plan / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` W3
- [x] TDD: FF-05 (first launchpad unit file); A-3 / CTR-03 filesystem contract
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/188 — TASK list (projection):
  - [x] TASK-W3-01 — REQ-20,21,22 — depends_on: [] — `launchpad_client.py` + tenant schema/repo (cache) — real check + cache + re-check
  - [x] TASK-W3-02 — REQ-20 — depends_on: TASK-W3-01 — `run_orchestrator.py` — after workspace, before Enter-at
  - [x] TASK-W3-03 — REQ-20,21,22 — depends_on: TASK-W3-02 — `test_launchpad_client.py` create + orchestrator cases
  - [x] TASK-W3-04 — REQ-20,21 — depends_on: TASK-W3-03 — `verify_harness_readiness.py` + README
  - [x] TASK-W3-05 — REQ-20–22 — depends_on: TASK-W3-04 — as-built

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-010 / ADR-011
- [x] Plan TASK MDC / ADR notes reviewed (infra + migrations + fail-fast)
- [x] No new ADR required (A-3 confirmed; FF-05 TDD_ONLY)
- [x] Do not claim CTR-01 pin shapes; CTR-03 is filesystem consume only

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drift (prefer no drift)
- [ ] `as-built/implementation-status.md` — W3 verification row (TASK-W3-05)
- [ ] `tests/README.md` — feature-map row for `verify_harness_readiness`
- [ ] Unit — `test_launchpad_client` + orchestrator cache/skip/fail matrix
- [ ] Live — co-ship `tests/verify/verify_harness_readiness.py` (human at `wave-acceptance`)
- [ ] DDL-NOTE — only if human migration still missing `harness_verified` on applied DBs (point to W0 note; do not invent agent revisions)
- [ ] ADR — none expected

---

### Must not

- [ ] Leave `sync_harness` as path-exists-only while claiming REQ-21
- [ ] Re-probe every hop when `harness_verified` is already true (unless re-check forced)
- [ ] Skip readiness for unverified repos (REQ-20)
- [ ] Author files under `postgres_migrations/versions/`
- [ ] Invent CTR-01 pin node shapes or claim pin remount
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | missing artifacts fail; ready passes; cache skip; re-check forces probe; wire before Enter-at | `make test` |
| Live verify | positive (harness present) + negative (absent → named 422) | `.venv/bin/python -m tests.verify.verify_harness_readiness` |
| Ground check | Pass-2 `/ground-spec` after accept | N/A as Makefile — skill |

> P15 applies: agent co-ships the live script in `/loop-spec`; does **not** claim live success.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] W0 DDL applied (includes `harness_verified`); W1/W2 workspace+branch contracts available as needed
- [ ] Run `.venv/bin/python -m tests.verify.verify_harness_readiness`
- [ ] Label tip `wave-accepted` (skills never apply it)
- [ ] Tip hygiene before Pass-2 Enter-at

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-012
- Issue: [#188](https://github.com/drivestream-lab/gateflow/issues/188)
- Spec path: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_harness_readiness`
- ADRs in scope: ADR-010 (consume); ADR-011 (consume)
- Wave head: cut `feature/INIT-GATEFLOW-012-w3-harness-ready` from `develop` @ `2aa2094…` before Forge publish
- Prior merge: [#193](https://github.com/drivestream-lab/gateflow/pull/193) → `2aa2094…`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — prior wave approved; WM clean; P15 live contracted |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this checklist onto bound `head_ref` **after** feature head is cut |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend: human/Forge cut `feature/INIT-GATEFLOW-012-w3-harness-ready` from `develop`, then `/commit-workspace` (checklist), then `/loop-spec`. Do not open the Draft PR here.

---

### Merge order (if cross-module / cross-service)

1. Human: cut wave feature head from `develop` @ `2aa2094…`  
2. Publish Pre-Implement onto that head  
3. TASK-W3-01 launchpad + cache → wire orchestrator → units → live script → as-built  
4. Human Alembic: confirm `harness_verified` applied where live verify runs (W0 DDL-NOTE)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W3.md
  blockers: []
  signals:
    wave: W3
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/188"
    prior_wave: W2
    prior_merge_sha: 2aa209439ec3ab1165bea0cce3463039a1935f31
    tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
      - TASK-W3-04
      - TASK-W3-05
    implements: [REQ-20, REQ-21, REQ-22]
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_harness_readiness"
    head_ref: feature/INIT-GATEFLOW-012-w3-harness-ready
    head_bound: false
    harness_verified_column: present_in_orm_and_ddl_note
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w3-harness-ready
    base_ref: develop
```
