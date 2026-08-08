## Pre-implement — drivestream-lab/gateflow / W4 — Repo-scoped NO_CONCURRENT_RUN

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W4.md` |
| Initiative | INIT-GATEFLOW-012 |
| Wave | W4 |
| Date | 2026-08-08 |
| Outcome | `pass` |
| Outcome reason | W3 `human_approved` + Ground-Report; WorkManifest contract pass; board [#189] seeded under EPIC [#184]; P15 live contracted; develop @ `afeae2f…` (W3 merge [#194]) |
| Wave head context | Integration tip: `develop` @ `afeae2f…` (W3 merge [#194](https://github.com/drivestream-lab/gateflow/pull/194)). Intended coding head: `feature/INIT-GATEFLOW-012-w4-repo-concurrency` — **cut from develop before `/commit-workspace` / `/loop-spec`** (this skill does not open the branch) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Board / branch / PR checks are **read-only**.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `afeae2f…` (feature head not yet cut) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#183](https://github.com/drivestream-lab/gateflow/pull/183) MERGED (`b83006c…`); plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — [#189](https://github.com/drivestream-lab/gateflow/issues/189) parent EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184); body has TASK-W4-01…04 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `WorkManifest contract passed.` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W4-01…04 |
| Live-verification contract | P15: live script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_wave_start` |
| Plan source freshness | H1–H3 / G2 durable roots | [x] current — product + plan on `develop` via [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Impact-map repo scope | match | [x] match |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` (P15) | [x] `.venv/bin/python -m tests.verify.verify_wave_start` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_wave_start.py` (modify in TASK-W4-03 — extend concurrency asserts) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W3 = **human_approved** (`wave-accepted` on [#194](https://github.com/drivestream-lab/gateflow/pull/194); merge `afeae2f…`) |
| Prior Ground Report exists | `Ground-Report-…-W3.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W3.md` |
| Plan PE sign-off (W0 only) | N/A for W4 | [x] N/A |

**Gate verdict:** **PASS**

**Notes for loop-spec (not start-blocks):**
- **FF-06 order is mandatory:** land `tests/unit/test_run_store_concurrency.py` (TASK-W4-01) **before** changing `find_active_run` — document xfail → green flip in Wave-Execution when TASK-W4-02 lands.
- Today `find_active_run` scopes ACTIVE by `initiative_id`+`wave_id` **or** `pr_number` **or** `issue_number` (narrow). W4 must query **org+repo + ACTIVE only** (REQ-23) while different repos never collide (REQ-24).
- Keep **existing** concurrency failure surface — product says existing `NO_CONCURRENT_RUN` precondition / no new failure code. Wave-start currently raises `ConflictError` when `find_active_run` hits; trigger_router maps `NO_CONCURRENT_RUN` (`PC-06-…`). Prefer aligning message/details to the established precondition id without inventing a second concurrency mechanism.
- REQ-25: **inspection only** — no new worktree/lock/isolation types; query broaden + existing Conflict/precondition path only.
- W3 harness gate remains **before** shared-workspace mutation on start/job paths; concurrency check stays synchronous before persist/enqueue (product Reliability row).
- Intended head name from plan: `feature/INIT-GATEFLOW-012-w4-repo-concurrency`.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W3.md` §Contracts produced (+ W1/W2 workspace/branch still binding). Confirmed against `src/` on `develop` @ `afeae2f…`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Wave-start persist + concurrency probe | `WaveStartService` → `find_active_run` | org, repo, optional initiative/wave/PR/issue | Conflict when ACTIVE match; else create+enqueue | product baseline / source | [x] yes — narrower key match today |
| RunStore ACTIVE lookup | `RunRepository.find_active_run` | org, repo + optional identity filters | optional ACTIVE run | source | [x] yes — filters on initiative+wave / pr / issue |
| Harness gate before coding hop | `RunOrchestrator._ensure_harness_ready` / wave-start harness | workspace path + cache | 422 / run FAILED if miss | Ground-Report W3 | [x] yes — W4 does not change harness |
| Workspace / branch bind | W1/W2 contracts | omit-path resolve + checkout | absolute path on head | Ground-Report W1/W2 | [x] yes — concurrency protects shared dir (D10) |
| Trigger-router NO_CONCURRENT_RUN | `TriggerRouter` / `WavePreconditionIdType.NO_CONCURRENT_RUN` | authorize path | PreconditionFailure PC-06 | existing units | [x] yes — keep id; broaden query shared |

**Unconfirmed / must extend in W4:**
- **Org+repo ACTIVE scope** — drop initiative/wave/PR/issue filters from the ACTIVE collision query (REQ-23)
- **Cross-repo non-block** — two ACTIVE starts on different repos both succeed (REQ-24)
- **FF-06 fixture first** — historical-pattern unit file before query change
- **Live asserts** — extend `verify_wave_start` for same-repo reject + cross-repo allow under knobs
- **REQ-25 inspection** — as-built note: no new isolation infra
- **Human wave head** — cut `feature/INIT-GATEFLOW-012-w4-repo-concurrency` before publishing checklist / coding

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `repository-pattern.mdc` — query change lives in `run_store_repository`; business calls repo only
  - [x] `fail-fast.mdc` — second same-repo start fails closed; no silent allow
  - [x] `testing-verify-flows.mdc` — FF-06 unit first; extend live `verify_wave_start` (no duplicate full journeys in pytest)
  - [x] `strong-typing.mdc` / `python-imports.mdc` / `architecture.mdc`
  - [x] `pydantic-schemas.mdc` — keep existing error enums / precondition ids
- [x] ADRs (keyword-matched):
  - [x] ADR-001 — durable RunStore; query-only broaden (plan note: ADR-001 query-only)
  - [x] ADR-010 — lane intake / dual workspace; concurrent ACTIVE semantics for same scope
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` — REQ-23…25; D10
- [x] Plan / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` W4
- [x] TDD / FF-06 — historical-pattern fixture before query change
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/189 — TASK list (projection):
  - [x] TASK-W4-01 — REQ-23,24 — depends_on: [] — `tests/unit/test_run_store_concurrency.py` create — FF-06 fixture first
  - [x] TASK-W4-02 — REQ-23,24,25 — depends_on: TASK-W4-01 — `run_store_repository.py` + `wave_start_service.py` — broaden query; keep NO_CONCURRENT_RUN surface
  - [x] TASK-W4-03 — REQ-23,24 — depends_on: TASK-W4-02 — `verify_wave_start.py` + `tests/README.md` — live same-repo / cross-repo
  - [x] TASK-W4-04 — REQ-23–25 — depends_on: TASK-W4-03 — as-built + REQ-25 inspection note

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-001 / ADR-010
- [x] Plan TASK MDC / ADR notes reviewed (repository + fail-fast + FF-06)
- [x] No new ADR required (query-only broaden; REQ-25 forbids new isolation ADR scope)
- [x] Do not invent worktree/lock packages

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drift (prefer no drift)
- [ ] `as-built/implementation-status.md` — W4 verification row + REQ-25 inspection (TASK-W4-04)
- [ ] `tests/README.md` — feature-map concurrency row for `verify_wave_start` (TASK-W4-03)
- [ ] Unit — `test_run_store_concurrency` (FF-06) + wave-start/repo call-site updates
- [ ] Live — extend `tests/verify/verify_wave_start.py` concurrency probes (human at `wave-acceptance`)
- [ ] ADR — none expected

---

### Must not

- [ ] Change `find_active_run` before FF-06 fixture exists
- [ ] Introduce new worktree / file-lock / isolation mechanism (REQ-25)
- [ ] Invent a new failure code when existing `NO_CONCURRENT_RUN` / Conflict path can carry the reject
- [ ] Block cross-repo starts (REQ-24)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | FF-06 historical patterns; same-repo block; cross-repo allow; no new isolation types | `make test` |
| Live verify | same-repo second start rejected; cross-repo both OK under knobs | `.venv/bin/python -m tests.verify.verify_wave_start` |
| Ground check | Pass-2 `/ground-spec` after accept | N/A as Makefile — skill |

> P15 applies: agent extends the live script in `/loop-spec`; does **not** claim live success.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] API up; two wave-start capable repos/identities (or knobs) for cross-repo allow
- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_start`
- [ ] Confirm same-repo ACTIVE second start rejected; no orphan ACTIVE runs left
- [ ] Label tip `wave-accepted` (skills never apply it)
- [ ] Tip hygiene before Pass-2 Enter-at

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-012
- Issue: [#189](https://github.com/drivestream-lab/gateflow/issues/189)
- Spec path: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_start`
- ADRs in scope: ADR-001 (consume); ADR-010 (consume)
- Wave head: cut `feature/INIT-GATEFLOW-012-w4-repo-concurrency` from `develop` @ `afeae2f…` before Forge publish
- Prior merge: [#194](https://github.com/drivestream-lab/gateflow/pull/194) → `afeae2fb488ee9ab9bda989c68cb1a2fd3a972e8`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — prior wave approved; WM clean; P15 live contracted |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this checklist onto bound `head_ref` **after** feature head is cut |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend: human/Forge cut `feature/INIT-GATEFLOW-012-w4-repo-concurrency` from `develop`, then `/commit-workspace` (checklist), then `/loop-spec`. Do not open the Draft PR here.

---

### Merge order (if cross-module / cross-service)

1. Human: cut wave feature head from `develop` @ `afeae2f…`  
2. Publish Pre-Implement onto that head  
3. TASK-W4-01 FF-06 fixture → TASK-W4-02 query broaden → live verify extend → as-built  
4. No DDL / migrations expected

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W4.md
  blockers: []
  signals:
    wave: W4
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/189"
    prior_wave: W3
    prior_merge_sha: afeae2fb488ee9ab9bda989c68cb1a2fd3a972e8
    tasks:
      - TASK-W4-01
      - TASK-W4-02
      - TASK-W4-03
      - TASK-W4-04
    implements: [REQ-23, REQ-24, REQ-25]
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_wave_start"
    intended_head_ref: feature/INIT-GATEFLOW-012-w4-repo-concurrency
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w4-repo-concurrency
    base_ref: develop
```
