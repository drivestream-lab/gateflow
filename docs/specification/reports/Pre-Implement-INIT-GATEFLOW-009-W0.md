## Pre-implement — gateflow / W0 — Pin consume + prove-out checklist

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-009-W0.md` |
| Initiative | INIT-GATEFLOW-009 |
| Wave | W0 |
| Date | 2026-08-03 |
| Outcome | `pass` |
| Outcome reason | Spec merged + board seeded + WorkManifest pass + plan PE sign-off; P15 N/A; no prior-wave gate (W0) |
| Wave head context | Recommended bind: `feature/INIT-GATEFLOW-009-w0-pin-checklist` from `develop` @ `bf5d3c6` — **not** opened by this skill; current checkout is `develop` |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `bf5d3c6` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#119](https://github.com/drivestream-lab/gateflow/pull/119) MERGED to `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — labels include `spec-lgtm`; merge `b3fdd14118f1c078654ba0e8452cb83ebd2ba2f4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#120](https://github.com/drivestream-lab/gateflow/issues/120); W0 [#121](https://github.com/drivestream-lab/gateflow/issues/121) parent=120; W1 [#122](https://github.com/drivestream-lab/gateflow/issues/122); W2 [#123](https://github.com/drivestream-lab/gateflow/issues/123); W3 [#124](https://github.com/drivestream-lab/gateflow/issues/124) |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `{"ok": true, "errors": []}` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/command\|review/expected/evidence_expected) | [x] complete — TASK-W0-01, TASK-W0-02 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` | [x] N/A — docs-only wave (`verification.live.applicable: false`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — digests backfilled on `develop` via PR [#125](https://github.com/drivestream-lab/gateflow/pull/125) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — revision `1`, scope digest `sha256:d0a2b626…` per plan header |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] N/A — P15 N/A (docs-only; no co-shipped live script) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` Pass-2 pin skill |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] N/A (no surface) |
| Prior wave as-built row | `human_approved` | [x] N/A — first wave of INIT-GATEFLOW-009 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-03 |

**Gate verdict:** **PASS**

**Forge readiness:** `commit_workspace` **required** — publish this checklist onto bound wave `head_ref` (cut `feature/INIT-GATEFLOW-009-w0-pin-checklist` from `develop` outside this skill if unbound). Do **not** open Draft PR here.

---

### Contracts consumed (from prior Ground Report)

> W0 of INIT-GATEFLOW-009 — no prior Ground Report for this initiative.
> Cross-init contracts below are verified against as-built + `src/` (not spec alone).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Harness pin consume | `.harness-pin.yaml` `agent_skills.ref` | tag ref `v0.5.0-rc.2` | submodule at tag tip | inspect + `git -C prayog-skills describe` | [x] yes — submodule `72ad383` == tag `v0.5.0-rc.2` |
| Pin workflow load | `WorkflowEngine.load_pin` / `get_node` | pin YAML path from harness | resolved node map incl. `dispatch`, `forge` | as-built INIT-008 + `src/business_services/workflow_engine.py` | [x] yes |
| `spec-draft` orchestrated | `prayog-skills/workflow.yaml` node `spec-draft` | pin node id | `dispatch: orchestrated`; `forge.commit_workspace: required` | pin submodule @ `v0.5.0-rc.2` | [x] yes |
| Dual authorization on EA nodes | pin `authorization` field | node type external-action | `explicit` \| `automated` enum on resolved node | Ground-Report-INIT-GATEFLOW-008-W0 + ADR-009 | [x] yes — Accepted |
| Meta intake + dual workspace (W1 prereq) | `POST /api/v1/waves/spec/start` | programme token + meta PR URL + dual bind | 202 + run_id or 4xx fail closed | Ground-Report-INIT-GATEFLOW-002-W0 + ADR-010 | [x] yes — unit + as-built; W1 live deferred to prove-out |

**Unconfirmed contracts:** none blocking W0. W1 will live-prove spec lane; W2 closeout; W3 authorize — all documented in plan but not yet grounded under INIT-009.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered — docs + pin inspect slice):
  - [x] `spec-driven-development.mdc` — truth hierarchy; same-PR discipline for artifacts
  - [x] `testing-verify-flows.mdc` — unit vs live layers (W0 unit-only + inspection)
  - [x] `code-guidelines-index.mdc` — rule index (no code changes expected beyond checklist doc)
- [x] ADRs (keyword-matched):
  - [x] ADR-009 — pin forge publish/mutate authority (**Accepted**; consume-only this wave)
  - [x] ADR-010 — lane intake + dual workspace (**Accepted**; checklist must document for W1)
  - [x] ADR-005 — programme token mutations (referenced by spec lane start)
  - [x] ADR-003 — ForgeClient infra boundary (unchanged)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` (REQ-1…REQ-2)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/121 — TASK list (projection from WorkManifest):
  - [x] **TASK-W0-01** — implements REQ-1 — depends_on: [] — files: `.harness-pin.yaml` inspect — exit: pin resolves `spec-draft` orchestrated; pin == submodule — proof: command `make check` → exit 0 — evidence: `Wave-Execution-INIT-GATEFLOW-009-W0.md § TASK-W0-01`
  - [x] **TASK-W0-02** — implements REQ-2 — depends_on: TASK-W0-01 — files: `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` create — exit: checklist exists; PE can execute — proof: review/inspection — evidence: `Wave-Execution-INIT-GATEFLOW-009-W0.md § TASK-W0-02`

---

### Governance alignment

- [x] Slice spec does not contradict any listed Accepted ADR (prove-out only; consume pin)
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed (P15 N/A; docs-only)
- [x] ADR-009, ADR-010, ADR-003, ADR-005 cited in plan §0 are **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if checklist wording requires spec amendment (prefer leave Draft)
- [ ] `docs/specification/as-built/implementation-status.md` — optional W0 row after checklist lands (not required for W0 exit proof)
- [ ] `tests/README.md` — **not required for W0** (no verification coverage change)
- [ ] Unit verification — REQ-1 regression via existing `make test` (pin load paths)
- [ ] Live verification — N/A this wave
- [ ] Create `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` (TASK-W0-02 deliverable)
- [ ] ADR — no supersede in W0

---

### Must not

- [ ] Run W1 live prove-out (`verify_spec_lane`) in W0
- [ ] Open spec Pass-1 run or Draft Spec PR from this wave
- [ ] Redesign prayog-skills pin or cut a new RC (REQ-1 consume-only)
- [ ] Assume W1 meta/fixture preconditions without documenting them in the checklist
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Treat board issue #121 body as SSOT over plan §9 WorkManifest

---

### Implementation sketch (for `/loop-spec` — not executed here)

1. **TASK-W0-01:** Confirm `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` resolves to submodule HEAD at tag tip (`72ad383`). Confirm pin node `spec-draft` has `dispatch: orchestrated`. Run `make check` → exit 0 as harness sanity.
2. **TASK-W0-02:** Create `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` covering: meta PR #23 accept preconditions (`meta_pr_url`, approved head `6660aa4…`, digest match), dual workspace paths (`workspace`, `meta_workspace`), programme token, reviewer tip-inspection steps, and live-verify config knobs for W1 (`tests/config.yaml` / `verify_spec_lane`).

**Current gap evidence:** W0 prove-out checklist artifact does not yet exist; pin consume preconditions otherwise satisfied on `develop`.

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | Pin/harness regression; no new product surface | `make test` |
| Live verify | N/A — P15 N/A | N/A — docs-only wave |
| Ground check | `/ground-spec` after Pass-2 (not this wave) | N/A |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate.
> Agent implements live scripts in later waves via `/loop-spec`; does **not** run them as W0 success.

### Human live-verify (after loop-spec)

- [ ] N/A for W0 — no co-shipped live script; human checkpoint follows pin after W1+ `wave-pr-action` → `live-verify`

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-009
- Issue: [#121](https://github.com/drivestream-lab/gateflow/issues/121) (W0)
- EPIC: [#120](https://github.com/drivestream-lab/gateflow/issues/120)
- Spec path: `docs/specification/product/INIT-GATEFLOW-009-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md`
- Verify command (human): N/A — P15 N/A
- ADRs in scope: ADR-009, ADR-010, ADR-005, ADR-003 (Accepted)
- Wave head: bind `feature/INIT-GATEFLOW-009-w0-pin-checklist` (plan §2 Branch column) before `/commit-workspace` / `/loop-spec`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W0 gate satisfied |
| Next | `loop-spec` (`skill`) — `human_checkpoint: false`, `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this file to bound `head_ref` |
| Later | After `/loop-spec` code publish → `wave-pr-action` (automated `open_draft_pr`) |

Recommend: bind wave branch → `/commit-workspace` (this checklist) → `/loop-spec`.

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only docs wave; W0 before W1 (checklist is W1 prerequisite per REQ-2 / DEP-1).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-009-W0.md
    digest: sha256:790687fb3c770f1b95fba355d8dd73b218b452c111e9be0e54614b0a21a2cc96
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-009
    wave: W0
    board_issue: "121"
    epic: "120"
    tasks: "TASK-W0-01,TASK-W0-02"
    check_command: make check
    test_command: make test
    verify_command: "N/A — P15 N/A"
    recommended_head_ref: feature/INIT-GATEFLOW-009-w0-pin-checklist
    base_ref: develop
    integration_sha: bf5d3c6abfd5afa4b50e0a2157afb2d578ecb52c
    spec_merge_pr: "119"
    spec_lgtm_merge_sha: b3fdd14118f1c078654ba0e8452cb83ebd2ba2f4
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: pre-implement commit_workspace = required.
    # Publish Pre-Implement artifact onto bound wave head_ref before loop-spec.
```
