## Pre-implement — drivestream-lab/gateflow / W1 — Repo clone/refresh workspace prep

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W1.md` |
| Initiative | INIT-GATEFLOW-012 |
| Wave | W1 |
| Date | 2026-08-08 |
| Outcome | `pass` |
| Outcome reason | W0 `human_approved` + Ground-Report; WorkManifest contract pass; board [#186] seeded; P15 live contracted; **PE-1 W1 waiver** clears TASK-W1-01 remount stop (current pin 0 BROKEN for existing nodes; new shapes hard-gated at W2) |
| Wave head context | Bound: `feature/INIT-GATEFLOW-012-w1-workspace-prep` @ `a4db4179e746b1bc38708b052f24bd16c3d2be92` (cut from `develop` @ `ad8c857…` / W0 merge [#191](https://github.com/drivestream-lab/gateflow/pull/191)). This skill does **not** open or re-cut the branch |

---

### Gate check (prior wave)

> Complete this before reading anything else. Board / branch / PR checks are **read-only**.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `feature/INIT-GATEFLOW-012-w1-workspace-prep` @ `a4db417…` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#183](https://github.com/drivestream-lab/gateflow/pull/183) MERGED (`b83006c…`); plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — [#186](https://github.com/drivestream-lab/gateflow/issues/186) under EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184); body has TASK-W1-01…06 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `WorkManifest contract passed.` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W1-01…06 |
| Live-verification contract | P15: live script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` |
| Plan source freshness | H1–H3 / G2 durable roots | [x] current — product H1–H3 on tree; G2 via [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Impact-map repo scope | match | [x] match — H2 `sha256:85e75d8b…` unchanged |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` (P15) | [x] `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_workspace_lifecycle.py` (create in TASK-W1-05) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W0 = **human_approved** (`wave-accepted` on [#191](https://github.com/drivestream-lab/gateflow/pull/191); merge `ad8c857…`) |
| Prior Ground Report exists | `Ground-Report-…-W0.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W0.md` |
| Plan PE sign-off (W0 only) | N/A for W1 | [x] N/A |
| PE-1 / TASK-W1-01 waiver | Active for W1 | [x] yes — [`PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md`](PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md) + [#186 comment](https://github.com/drivestream-lab/gateflow/issues/186#issuecomment-5225650041) |

**Gate verdict:** **PASS**

**PE-1 / TASK-W1-01 (waiver — clears prior RISK-05 stop):** Plan text still lists remounted tip with new Tenant workspace-prep shapes. **PE waiver** aligns W1 with TDD PE-1: TASK-W1-01 exit for **this wave** = current pin tip **0 BROKEN for existing nodes** (`v0.5.0-rc.2` ≡ `75b207ce…`; `test_all_remounted_pin_nodes_parse` **pass**). Net-new pin shapes (CTR-01 / REQ-28–31) remain a **hard gate for W2**, not W1. `/loop-spec` must record that evidence for TASK-W1-01, then proceed to TASK-W1-02+.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W0.md` §Contracts produced. Confirmed against `src/` on wave head @ `a4db417…` (W0 merge base `ad8c857…`).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Tenant register / aggregate | `TenantService.register_tenant` / `POST /api/v1/tenants` | name, pat, repos[], absolute workspace_root, optional board | tenant_id + bearer + repos/workspace/board (no pat) | Ground-Report W0 | [x] yes — `tenant_service.py`, `tenant_routes.py` |
| Tenant read model (no pat) | `get_tenant` / `list_tenants` / `TenantRepository` | tenant token (+ optional identity) | repos, workspace_root, board | Ground-Report W0 | [x] yes — PAT absent from DTOs |
| Tenant ORM + PAT column | `TenantSchema.pat` + `tenant_repos` | human DDL applied | durable rows | Ground-Report W0 / DDL-NOTE | [x] yes — schema present; **live DB still needs human Alembic** |
| Tenant token zone | `verify_tenant_bearer_token` | Bearer | TenantResolvedContext or 401 | Ground-Report W0 / ADR-011 | [x] yes — fourth zone; JWT auth context not populated |
| PAT probe (register-time only) | `GithubPatProbe.verify_read_access` | caller-submitted credential | ok/reason | Ground-Report W0 | [x] yes — W1 uses **stored** PAT for git, not re-probe at register |
| Board default resolve | `BoardService.resolve_board_default` | optional tenant_id / project fields | owner + number | Ground-Report W0 | [x] yes — not primary W1 path |
| Explicit `workspace_path` today | `RunOrchestrator` job path | `context.workspace_path` or `Path.cwd()` | string path | source scan | [x] yes — **gap to fill:** `run_orchestrator.py:237` still `Path.cwd()` fallback (REQ-10 target) |
| Pin parse (existing nodes) | `WorkflowEngine.load_pin` / `get_node` | remounted `workflow.yaml` | 0 BROKEN existing nodes | PE waiver + unit | [x] yes — `test_all_remounted_pin_nodes_parse` pass @ `v0.5.0-rc.2` |

**Unconfirmed / must extend in W1 (not on W0 Ground Report as callables):**
- **Lookup tenant (+ stored PAT) by `org`/`repo`** — repository path for fail-closed git auth (REQ-11) without leaking PAT into read DTOs or logs
- **`tenant_git_workspace_client.resolve_workspace`** — net-new infra (TDD §3.4); subprocess `git` only (FF-04); per-repo lock (TF-01); **file absent today**
- **Orchestrator composition** — registered omitted-path → client; explicit path unchanged (REQ-12); unregistered omitted → 422 / 0 enqueue (REQ-15)
- **Human DDL** — if local/dev DB never applied W0 migration, live W1 verify fails closed before clone

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `infra-services.mdc` — git client as infra; lifecycle initialize/close/health
  - [x] `architecture.mdc` — orchestrator in business; no ORM in business
  - [x] `fail-fast.mdc` — mismatch / unregistered → named 422; no silent Path.cwd() for registered
  - [x] `dependency-injection.mdc` — bind client in InfraModule + `_INFRA_SERVICE_TYPES`
  - [x] `logging-loguru.mdc` — never log PAT; mode/path as kwargs
  - [x] `strong-typing.mdc` / `python-imports.mdc` — typed boundaries
  - [x] `testing-verify-flows.mdc` — co-ship `verify_workspace_lifecycle`
  - [x] `repository-pattern.mdc` — any new lookup stays in repository
- [x] ADRs (keyword-matched):
  - [x] ADR-011 — tenant token zone (consume; do not repurpose for git)
  - [x] ADR-003 — forge outbound auth modes; W1 tenant PAT is **per-tenant stored credential** (FF-03 TDD_ONLY)
  - [x] ADR-009 / ADR-010 — workspace authority; FF-01 gap-fill for omitted path + registered repo (no Path.cwd())
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` — REQ-10…15
- [x] Plan / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` W1
- [x] PE waiver: `docs/specification/reports/PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md`
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/186 — TASK list (projection):
  - [x] TASK-W1-01 — REQ-10 — depends_on: [] — files: `.harness-pin.yaml` inspect — exit (**waiver**): current pin 0 BROKEN existing nodes (PE-1 → W2 for new shapes)
  - [x] TASK-W1-02 — REQ-10,11,13,14 — depends_on: TASK-W1-01 — `tenant_git_workspace_client.py` + DI
  - [x] TASK-W1-03 — REQ-10,12,15 — depends_on: TASK-W1-02 — `run_orchestrator.py` (+ wave-start as needed)
  - [x] TASK-W1-04 — REQ-10–15 — depends_on: TASK-W1-03 — unit tests
  - [x] TASK-W1-05 — REQ-10,13–15 — depends_on: TASK-W1-04 — `verify_workspace_lifecycle.py` + README
  - [x] TASK-W1-06 — REQ-10–15 — depends_on: TASK-W1-05 — as-built

---

### Governance alignment

- [x] Slice spec does not contradict Accepted ADR-011 (git uses stored PAT; token zone unchanged)
- [x] Plan TASK MDC / ADR notes reviewed (FF-01, FF-04, TF-01); PE-1 sequencing waived for W1 only
- [x] No new ADR required for W1 (TDD_ONLY dispositions)
- [x] Programme meta/Launchpad onboard is **out of 012** (separate INIT) — do not implement in this wave

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drift (prefer no drift)
- [ ] `as-built/implementation-status.md` — W1 verification row (TASK-W1-06)
- [ ] `tests/README.md` — feature-map row for `verify_workspace_lifecycle`
- [ ] Unit — `test_tenant_git_workspace_client`, orchestrator + wave-start regression
- [ ] Live — co-ship `tests/verify/verify_workspace_lifecycle.py` (human at `wave-acceptance`)
- [ ] ADR — none expected
- [ ] Keep PE waiver on tree (or cite board comment) for Wave-Execution TASK-W1-01 evidence

---

### Must not

- [ ] Re-impose RISK-05 stop for missing *new* pin shapes on W1 (waiver active; remount stays W2)
- [ ] Invent “0 BROKEN” for absent CTR-01 node shapes
- [ ] Add a Python git library (FF-04 — subprocess `git` only)
- [ ] Echo or log tenant PAT
- [ ] Override caller-supplied `workspace_path` (REQ-12)
- [ ] Guess workspace for unregistered org/repo when path omitted (REQ-15)
- [ ] Rely on W4 concurrency broaden for TF-01 — client must self-serialize per org+repo
- [ ] Implement meta-first / Launchpad CLI programme onboard in this wave
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | clone/fetch/mismatch/lock; orchestrator registered/explicit/unregistered; pin parse | `make test` |
| Live verify | clone then fetch; mismatch 422; unregistered omitted 422 (human at wave-acceptance) | `.venv/bin/python -m tests.verify.verify_workspace_lifecycle` |
| Ground check | Pass-2 `/ground-spec` after accept | N/A as Makefile — skill |

> P15 applies: agent co-ships the live script in `/loop-spec`; does **not** claim live success.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Apply W0 DDL if not already (tenants tables required for registered-repo path)
- [ ] Run `.venv/bin/python -m tests.verify.verify_workspace_lifecycle`
- [ ] Label tip `wave-accepted` (skills never apply it)
- [ ] Tip hygiene before Pass-2 Enter-at

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-012
- Issue: [#186](https://github.com/drivestream-lab/gateflow/issues/186)
- Spec path: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_workspace_lifecycle`
- ADRs in scope: ADR-011 (consume); FF-01/FF-04/TF-01 TDD_ONLY
- PE waiver: [`PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md`](PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md) / [issue comment](https://github.com/drivestream-lab/gateflow/issues/186#issuecomment-5225650041)
- Wave head: `feature/INIT-GATEFLOW-012-w1-workspace-prep` @ `a4db417…`
- Prior merge: [#191](https://github.com/drivestream-lab/gateflow/pull/191) → `ad8c857…`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — prior wave approved; WM clean; P15 live contracted; PE-1 W1 waiver active |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this checklist + PE waiver onto bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend: `/commit-workspace` (checklist + waiver), then `/loop-spec`. Do not open the Draft PR here.

---

### Merge order (if cross-module / cross-service)

1. Human: ensure W0 Alembic applied on target Postgres  
2. TASK-W1-01 — current pin 0 BROKEN evidence (waiver)  
3. Infra git client → orchestrator composition → units → live script → as-built  
4. External: `prayog-skills` new-shape remount remains **W2** hard gate (not W1)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W1.md
  blockers: []
  signals:
    wave: W1
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/186"
    prior_wave: W0
    prior_merge_sha: ad8c8573d5cf0fefac74b7ec4d97970bb60bfcb9
    pe1_waiver: docs/specification/reports/PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md
    pe1_waiver_board: "https://github.com/drivestream-lab/gateflow/issues/186#issuecomment-5225650041"
    task_w1_01_exit: "current pin 0 BROKEN existing nodes; new shapes deferred to W2"
    pin_ref: v0.5.0-rc.2
    pin_sha: 75b207ce0885ddaa28056cd624b4588efa3d960d
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
      - TASK-W1-06
    implements: [REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15]
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_workspace_lifecycle"
    head_ref: feature/INIT-GATEFLOW-012-w1-workspace-prep
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w1-workspace-prep
    base_ref: develop
```
