## Pre-implement — drivestream-lab/gateflow / W2 — Branch create-or-reuse

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W2.md` |
| Initiative | INIT-GATEFLOW-012 |
| Wave | W2 |
| Date | 2026-08-08 |
| Outcome | `pass` |
| Outcome reason | W1 `human_approved` + Ground-Report; WorkManifest contract pass; board [#187] seeded; P15 live contracted; **PE-1 W2 waiver** clears pin-remount start-block (current pin 0 BROKEN for existing nodes; CTR-01 consume remains later DEP-02) |
| Wave head context | Integration tip: `develop` @ `42c5b60…` (W1 merge [#192](https://github.com/drivestream-lab/gateflow/pull/192)). Intended coding head: `feature/INIT-GATEFLOW-012-w2-branch-resolve` — **cut from develop before `/commit-workspace` / `/loop-spec`** (this skill does not open the branch) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Board / branch / PR checks are **read-only**.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `42c5b60…` (feature head not yet cut) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#183](https://github.com/drivestream-lab/gateflow/pull/183) MERGED (`b83006c…`); plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — [#187](https://github.com/drivestream-lab/gateflow/issues/187) under EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184); body has TASK-W2-01…04 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `WorkManifest contract passed.` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W2-01…04 |
| Live-verification contract | P15: live script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_branch_lifecycle` |
| Plan source freshness | H1–H3 / G2 durable roots | [x] current — product + plan on `develop` via [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Impact-map repo scope | match | [x] match |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` (P15) | [x] `.venv/bin/python -m tests.verify.verify_branch_lifecycle` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_branch_lifecycle.py` (create in TASK-W2-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W1 = **human_approved** (`wave-accepted` on [#192](https://github.com/drivestream-lab/gateflow/pull/192); merge `42c5b60…`) |
| Prior Ground Report exists | `Ground-Report-…-W1.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W1.md` |
| Plan PE sign-off (W0 only) | N/A for W2 | [x] N/A |
| PE-1 / CTR-01 remount | Active W2 coding-start waiver | [x] yes — [`PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md`](PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md) + [#187 comment](https://github.com/drivestream-lab/gateflow/issues/187#issuecomment-5225722435) |

**Gate verdict:** **PASS**

**PE-1 / CTR-01 (waiver — clears prior W2 start-block):** W1 waiver and DEP-02 still require remount before **consuming** new pin shapes. **W2 PE waiver** allows coding start for REQ-16–19 via TDD §3.5 composition of existing branch primitives. `/loop-spec` records current-pin **0 BROKEN existing nodes** evidence, then implements TASK-W2-01…04. Do not invent shapes for absent CTR-01 node ids.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W1.md` §Contracts produced. Confirmed against `src/` on `develop` @ `42c5b60…`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Workspace resolve (clone/fetch) | `TenantGitWorkspaceClient.resolve_workspace` | tenant credential | absolute path + mode | Ground-Report W1 | [x] yes — file present; DI bound |
| Tenant git credential lookup | `get_workspace_credential_for_repo` | org, repo | credential or none | Ground-Report W1 | [x] yes — repository join path |
| Implement omit-path resolve | `WaveStartService._resolve_implement_workspace_path` | ImplementWaveStartRequest | path or 422 before enqueue | Ground-Report W1 | [x] yes |
| Orchestrator workspace bind | `RunOrchestrator._resolve_job_workspace_path` | org, repo, optional path | absolute path or fail | Ground-Report W1 | [x] yes — no `Path.cwd()` fallback |
| Existing branch primitives | `ForgeClient.ensure_branch_from_base` + `build_wave_head_branch` / naming helpers | org, repo, base, slug/ids | head ref created or existing | Ground-Report W1 + source | [x] yes — already called at run start; W2 tightens new-vs-continuation (TDD §3.5) |
| PE-1 pin sequencing | pin tip `v0.5.0-rc.2` | remounted nodes | 0 BROKEN existing | W2 PE waiver | [x] yes — waiver amends start-block; consume gate remains DEP-02 |

**Unconfirmed / must extend in W2:**
- **`resolve_branch` composition** — new-wave always fork from **live** `develop` tip; continuation reuses existing head with **zero** new refs (REQ-16/18); fail closed if continuation head missing on remote (named 422)
- **Naming** — stay on `feature/{INIT}-{wn}-{slug}` only (REQ-17); no second scheme
- **REQ-19** — continuation + never-cloned local workspace composes with W1 `resolve_workspace` then checkout existing head (live-primary)
- **Human wave head** — cut `feature/INIT-GATEFLOW-012-w2-branch-resolve` before publishing checklist / coding

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `architecture.mdc` — orchestrator in business; compose ForgeClient
  - [x] `fail-fast.mdc` — missing continuation head → named 422
  - [x] `infra-services.mdc` — ForgeClient remains infra; no new transport
  - [x] `logging-loguru.mdc` — branch/mode as kwargs
  - [x] `testing-verify-flows.mdc` — co-ship `verify_branch_lifecycle`
  - [x] `strong-typing.mdc` / `python-imports.mdc`
- [x] ADRs (keyword-matched):
  - [x] ADR-010 — lane intake; D2 branch create-or-reuse aligned
  - [x] ADR-009 — forge mutate/publish; ensure_branch already in force
  - [x] ADR-011 — tenant token zone unchanged (W2 uses ForgeClient + workspace client)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` — REQ-16…19
- [x] Plan / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` W2
- [x] TDD §3.5: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-012.md`
- [x] PE waiver: `docs/specification/reports/PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md`
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/187 — TASK list (projection):
  - [x] TASK-W2-01 — REQ-16,17,18 — depends_on: [] — `run_orchestrator.py` (and/or small helper) — fork vs reuse
  - [x] TASK-W2-02 — REQ-16,17,18 — depends_on: TASK-W2-01 — unit matrix (+ missing remote → 422)
  - [x] TASK-W2-03 — REQ-16,18,19 — depends_on: TASK-W2-02 — `verify_branch_lifecycle.py` + README
  - [x] TASK-W2-04 — REQ-16–19 — depends_on: TASK-W2-03 — as-built

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-010 / ADR-009 (compose existing primitives)
- [x] Plan TASK MDC / ADR notes reviewed; PE-1 remount start-block waived for W2 coding
- [x] No new ADR required for W2 (TDD §3.5 TDD_ONLY composition)
- [x] CTR-01 / REQ-28–31 remain out of gateflow product REQ set — do not claim pin shapes shipped

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drift (prefer no drift)
- [ ] `as-built/implementation-status.md` — W2 verification row (TASK-W2-04)
- [ ] `tests/README.md` — feature-map row for `verify_branch_lifecycle`
- [ ] Unit — orchestrator new-vs-continuation + `test_pr_branch_naming` regression
- [ ] Live — co-ship `tests/verify/verify_branch_lifecycle.py` (human at `wave-acceptance`)
- [ ] ADR — none expected
- [ ] Keep PE waiver on tree (or cite board comment) for Wave-Execution evidence

---

### Must not

- [ ] Re-impose W1 “hard gate for W2” start-block for missing *new* pin shapes (W2 waiver active)
- [ ] Invent “0 BROKEN” for absent CTR-01 node shapes
- [ ] Introduce a third branch-create primitive or second naming scheme
- [ ] Create new refs on the continuation path (REQ-18)
- [ ] Guess workspace for unregistered omit (W1 contract still binds)
- [ ] Implement pin-shape remount inside gateflow `loop-spec` as if it were a local FILE TASK
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | new-wave fork from live develop; continuation zero new refs; naming; missing remote 422 | `make test` |
| Live verify | new fork + continuation reuse + never-cloned continuation (REQ-19) | `.venv/bin/python -m tests.verify.verify_branch_lifecycle` |
| Ground check | Pass-2 `/ground-spec` after accept | N/A as Makefile — skill |

> P15 applies: agent co-ships the live script in `/loop-spec`; does **not** claim live success.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Ensure W0 DDL + W1 workspace contracts available for registered-repo paths
- [ ] Run `.venv/bin/python -m tests.verify.verify_branch_lifecycle`
- [ ] Label tip `wave-accepted` (skills never apply it)
- [ ] Tip hygiene before Pass-2 Enter-at

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-012
- Issue: [#187](https://github.com/drivestream-lab/gateflow/issues/187)
- Spec path: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_branch_lifecycle`
- ADRs in scope: ADR-010 (consume); ADR-009 (consume)
- PE waiver: [`PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md`](PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md) / [issue comment](https://github.com/drivestream-lab/gateflow/issues/187#issuecomment-5225722435)
- Wave head: cut `feature/INIT-GATEFLOW-012-w2-branch-resolve` from `develop` @ `42c5b60…` before Forge publish
- Prior merge: [#192](https://github.com/drivestream-lab/gateflow/pull/192) → `42c5b60…`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — prior wave approved; WM clean; P15 live contracted; PE-1 W2 coding-start waiver active |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this checklist + PE waiver onto bound `head_ref` **after** feature head is cut |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend: human/Forge cut `feature/INIT-GATEFLOW-012-w2-branch-resolve` from `develop`, then `/commit-workspace` (checklist + waiver), then `/loop-spec`. Do not open the Draft PR here.

---

### Merge order (if cross-module / cross-service)

1. Human: cut wave feature head from `develop` @ `42c5b60…`  
2. Publish Pre-Implement + PE waiver onto that head  
3. TASK-W2-01 branch resolve → units → live script → as-built  
4. External: `prayog-skills` CTR-01 remount remains **DEP-02** for pin-shape consume (not W2 coding start)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W2.md
  blockers: []
  signals:
    wave: W2
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/187"
    prior_wave: W1
    prior_merge_sha: 42c5b600cc94f85595e355482dd2618aa31110bd
    pe1_waiver: docs/specification/reports/PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md
    pe1_waiver_board: "https://github.com/drivestream-lab/gateflow/issues/187#issuecomment-5225722435"
    pe1_w2_exit: "current pin 0 BROKEN existing nodes; CTR-01 consume deferred (DEP-02)"
    pin_ref: v0.5.0-rc.2
    pin_sha: 75b207ce0885ddaa28056cd624b4588efa3d960d
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
    implements: [REQ-16, REQ-17, REQ-18, REQ-19]
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_branch_lifecycle"
    head_ref: feature/INIT-GATEFLOW-012-w2-branch-resolve
    head_bound: false
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w2-branch-resolve
    base_ref: develop
```
