## Pre-implement — gateflow / W0 — Pin consume + prove-out checklist

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-009-W0.md` |
| Initiative | INIT-GATEFLOW-009 |
| Wave | W0 |
| Date | 2026-08-03 |
| Outcome | `stale` |
| Outcome reason | Plan § source-freshness digests and `repo_scope_digest` do not match merged upstream files / canonical spec handoff — refresh via `/spec-implementation-plan` before `/loop-spec` |
| Wave head context | Bound by Forge/run context: `feature/INIT-GATEFLOW-009-w0-implement-lane` @ `f47042d` (remote); current checkout `develop` @ `b3fdd14` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `b3fdd14`; remote wave head `feature/INIT-GATEFLOW-009-w0-implement-lane` exists |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#119](https://github.com/drivestream-lab/gateflow/pull/119) MERGED @ `b3fdd14` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; merge head `f4d1bb7…`; merge commit `b3fdd14` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#120](https://github.com/drivestream-lab/gateflow/issues/120); W0 [#121](https://github.com/drivestream-lab/gateflow/issues/121) sub-issue of 120; W1–W3 [#122–124](https://github.com/drivestream-lab/gateflow/issues/122) |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `{"ok": true, "errors": []}` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — W0 `TASK-W0-01`, `TASK-W0-02` |
| Live-verification contract | When P15 applies: `verification.live` + script under `live_verify_dir` | [x] N/A — W0 docs-only; `verification.live.applicable: false` |
| Plan source freshness | all upstream rows `CURRENT` **and digests match files** | [ ] **stale** — table marks CURRENT but recorded digests ≠ merged file SHA-256 (see below) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [ ] **stale** — plan `repo_scope_digest` typo vs spec/feasibility canonical (`7092` vs `7022` in digest) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15; else N/A | [x] N/A — P15 N/A for W0 |
| `ground_command` | resolved or N/A | [x] N/A — Pass-2 pin skill `/ground-spec` |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` when surface changes | [x] N/A (no new product surface) |
| Prior wave as-built row | `human_approved` | [x] N/A — first wave of INIT-009 |
| Prior Ground Report exists | `Ground-Report-W{N-1}.md` | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-03 |

**Digest evidence (stale):**

| Source | Plan records | Actual on `develop` @ `b3fdd14` |
|--------|--------------|----------------------------------|
| Feasibility report | `sha256:99dec941…` | `sha256:36d16d9c31d43ebbed356f36efc415f30978c29821755cc328aa7b41f12ce0ca` |
| Technical review | `sha256:7ec5a04c…` | `sha256:b314173e7e35104bbb62730816c9d94947057b6ae56eb3b45be82046af079562` |
| Spec | `sha256:f4c93f4a…` | [x] match |
| `repo_scope_digest` (plan) | `…8217022dda…` | Canonical in spec + feasibility: `…8217092dda…` |

**Gate verdict:** **BLOCKED (stale inputs)** — do not invoke `/loop-spec` until plan digests are refreshed on `develop`.

**Forge readiness:** N/A on `stale` — route to `/spec-implementation-plan` first. On a future `pass`, fill `handoff.forge` for `commit_workspace` to publish this checklist onto bound `head_ref`.

---

### Contracts consumed (from prior Ground Report)

> W0 of INIT-009 — no prior Ground Report. Baseline contracts from as-built + pin consume (REQ-1).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Harness pin load | `.harness-pin.yaml` → submodule `prayog-skills` | pin ref `v0.5.0-rc.2` | tag tip `72ad383` ≡ describe output | `.harness-pin.yaml`, `git -C prayog-skills describe` | [x] yes — TASK-W0-01 inspect target |
| Pin workflow graph | `prayog-skills/workflow.yaml` | node id + outcome | next node, forge policy | submodule @ `v0.5.0-rc.2` | [x] yes — `spec-draft` orchestrated; implement lane chain documented |
| Forge publish authority | pin `forge.commit_workspace` on `pre-implement` | stage outcome `pass` | required publish before `loop-spec` | ADR-009 Accepted + pin | [x] yes |
| Dual workspace (later W1) | lane intake per ADR-010 | `workspace` + optional `meta_workspace` | bound run context | ADR-010 Accepted | [x] yes — W0 checklist must document knobs (TASK-W0-02) |

**Unconfirmed contracts:** none blocking W0. W1+ live paths depend on W0 checklist + prior wave completion (not assumed grounded yet).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered — W0 is pin/docs-only; no new API surface):
  - [x] `spec-driven-development.mdc` — same-PR discipline; as-built updates in later waves
  - [x] `testing-verify-flows.mdc` — unit vs live separation; W0 unit-only (`make test`)
  - [x] `code-guidelines-index.mdc` — rule index (skipped deep infra/http rules — out of W0 scope)
- [x] ADRs (keyword-matched — pin, forge, lane intake, handoff):
  - [x] ADR-009 — pin forge publish/mutate authority (Accepted)
  - [x] ADR-010 — lane intake + dual-workspace (Accepted)
  - [x] ADR-003 — slot/layer ownership (Accepted; context for forge client boundary)
  - [x] ADR-005 — programme-token mutations (Accepted; W1+ live)
  - [x] ADR-008 — packaged handoff ingest (Accepted; orchestrator baton)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` (REQ-1, REQ-2)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/121 — TASK list (projection from §9):
  - [x] **TASK-W0-01** — implements REQ-1 — depends_on: [] — files: `.harness-pin.yaml` (inspect) — exit: pin resolves `spec-draft` orchestrated; pin == submodule — proof: command `make check` → exit 0
  - [x] **TASK-W0-02** — implements REQ-2 — depends_on: [TASK-W0-01] — files: `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` (create) — exit: checklist exists; PE can execute — proof: review / inspection

---

### Governance alignment

- [x] Slice spec does not contradict listed Accepted ADRs (factory prove-out only)
- [x] Plan P11/P12 MDC + ADR notes reviewed for W0
- [x] ADR-009, ADR-010, ADR-003, ADR-005, ADR-008 are **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`, after stale cleared)

- [ ] `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` — create (TASK-W0-02): meta preconditions, dual workspace, programme token, reviewer tip inspection, verify config knobs per REQ-2
- [ ] `.harness-pin.yaml` — inspect only (TASK-W0-01); confirm `agent_skills.ref: v0.5.0-rc.2` matches submodule HEAD
- [ ] `docs/specification/as-built/implementation-status.md` — W0 row when wave lands (§6 plan; not required at pre-implement)
- [ ] `tests/README.md` — no W0 feature-map change (docs-only wave)
- [ ] Live verification — N/A (P15 N/A)
- [ ] ADR — no supersede in W0

---

### Must not

- [ ] Implement product code or open/create a branch from this skill
- [ ] Proceed to `/loop-spec` while plan digests are stale
- [ ] Treat board issue #121 body as SSOT over plan §9 WorkManifest
- [ ] Run live verify scripts as W0 exit proof (P15 N/A)
- [ ] Apply `*-lgtm` labels or merge

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Formatting, linting, types, layer checks | `make check` |
| Unit | Pin load / regression (REQ-1) | `make test` |
| Live verify | Product behaviour on running stack | N/A — P15 N/A (docs-only W0) |
| Ground check | Wave REQs satisfied post Pass-2 | N/A — `/ground-spec` after later waves |

> Human runs co-shipped live scripts only at checkpoint `live-verify` on W1+ waves.

### Human live-verify (after loop-spec)

- [ ] N/A for W0 — no co-shipped live script; implement-lane Draft PR + live-verify follow W0 code wave via pin

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-009
- EPIC: [#120](https://github.com/drivestream-lab/gateflow/issues/120)
- Wave issue: [#121](https://github.com/drivestream-lab/gateflow/issues/121)
- Spec path: `docs/specification/product/INIT-GATEFLOW-009-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md`
- Verify command (human): N/A — P15 N/A
- ADRs in scope: ADR-009, ADR-010, ADR-003, ADR-005, ADR-008
- Wave head (bound): `feature/INIT-GATEFLOW-009-w0-implement-lane` @ `f47042d` (implement-lane dogfood); plan §2 branch column also names `feature/INIT-GATEFLOW-009-w0-pin-checklist`

---

### Checklist publish readiness (on `stale`)

| Field | Value |
|-------|-------|
| Workflow outcome | `stale` — plan digest / scope digest mismatch |
| Next | `spec-implementation-plan` (`skill`) — refresh § source-freshness + digests on `develop` |
| Forge (this hop) | **disabled** — no `commit_workspace` until `pass` after plan refresh |
| After refresh | Re-run `/pre-implement`; on `pass` → `loop-spec` with `forge.commit_workspace` required |

Recommend: `/spec-implementation-plan` to reconcile feasibility/TDD/scope digests → re-run `/pre-implement` → `/commit-workspace` (checklist) → `/loop-spec`.

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only W0; W0 checklist before W1 spec-lane live prove-out.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: stale
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-009-W0.md
    digest: sha256:9640b7e90b9b647f2d1592d6681054e46fb0a45b5612def89d6378a95e99636d
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-009
    wave: W0
    board_issue: "121"
    epic: "120"
    ticket_id: "121"
    tasks: "TASK-W0-01,TASK-W0-02"
    check_command: make check
    test_command: make test
    verify_command: "N/A — P15 N/A"
    integration_sha: b3fdd14118f1c078654ba0e8452cb83ebd2ba2f4
    spec_pr: "119"
    spec_lgtm: true
    workmanifest_contract: pass
    stale_reason: plan_digest_mismatch
    feasibility_digest_plan: "sha256:99dec941857a7e8112d9ec6d4b3821feca2b34f9019495a20a6a6ae0020caa31"
    feasibility_digest_actual: "sha256:36d16d9c31d43ebbed356f36efc415f30978c29821755cc328aa7b41f12ce0ca"
    tdd_digest_plan: "sha256:7ec5a04c91ef9e6dfd68dbafc8c58619bf2a109eb32700a537b9d3dba64cd911"
    tdd_digest_actual: "sha256:b314173e7e35104bbb62730816c9d94947057b6ae56eb3b45be82046af079562"
    scope_digest_canonical: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b"
    scope_digest_plan: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217022dda242a99b3392978e9b"
    recommended_head_ref: feature/INIT-GATEFLOW-009-w0-implement-lane
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
