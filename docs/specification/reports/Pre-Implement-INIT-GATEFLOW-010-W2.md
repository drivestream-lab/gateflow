## Pre-implement — gateflow / W2 — Ticket gates + create predicates

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W2.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W2 |
| Date | 2026-08-05 |
| Outcome | `blocked` |
| Outcome reason | Prior wave W1 gate unsatisfied: no `Ground-Report-INIT-GATEFLOW-010-W1.md`, as-built W1 not `human_approved`, W1 product code not on `develop` (open PR #146). |
| Wave head context | Bound by Forge/human context: `develop` @ `eab2304` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `eab2304` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#135](https://github.com/drivestream-lab/gateflow/pull/135) merged; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — PR #135 labels include `spec-lgtm`; merge commit `1901dbe5…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/138); W2 [#140](https://github.com/drivestream-lab/gateflow/issues/140) body lists TASK-W2-01…05 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `WorkManifest contract passed.` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W2 TASK-W2-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W2 `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_wave_start`; scripts exist at `tests/verify/verify_wave_start.py`, `tests/verify/verify_board.py` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; live spec digest `sha256:f98e101a…` matches plan `source_spec_digest` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_start` (+ `verify_board` for REQ-06/07 create predicates per plan §9 W2) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_start.py`, `tests/verify/verify_board.py` (extend in TASK-W2-04) |
| Prior wave as-built row | `human_approved` | [ ] **W1 = not human_approved** — as-built still lists APPLY_FORGE board-status apply as **deferred W1** |
| Prior Ground Report exists | `reports/Ground-Report-INIT-GATEFLOW-010-W{N-1}.md` | [ ] **missing** — `Ground-Report-INIT-GATEFLOW-010-W1.md` absent |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2 |

**Gate verdict:** BLOCKED — prior wave W1 human gate unsatisfied. Do not invoke `/loop-spec` for W2 until W1 Pass-2 closeout: merge W1 wave PR, complete `live-verify`, `/learning-extract`, `/ground-spec`, human `wave-signoff`, and as-built W1 → `human_approved`.

**Read-only process notes (do not fail other rows):**
- Board W1 ticket [#139](https://github.com/drivestream-lab/gateflow/issues/139) is **CLOSED** / column Done, but W1 product PR [#146](https://github.com/drivestream-lab/gateflow/pull/146) is still **OPEN** on `feature/INIT-GATEFLOW-010-w1-implement-lane` — board Done ahead of grounded closeout (same class as W0 GF-01 backfill).
- `develop` tip has W0 merged ([#144](https://github.com/drivestream-lab/gateflow/pull/144) + Pass-2 backfill [#145](https://github.com/drivestream-lab/gateflow/pull/145)); `src/business_services/forge_action_service.py` on `develop` has **no** `update_board_status` apply branch (W1 REQ-03 still open).

**Forge readiness (when seed / wave head absent):** not required — board seeded; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w2-ticket-gates` (opened in `/loop-spec` after W1 gate clears — not here).

---

### Contracts consumed (from prior Ground Report)

> Required source: `Ground-Report-INIT-GATEFLOW-010-W1.md §Contracts produced`.
> **That report does not exist.** W2 depends on W1 deliverables per plan DEP-2
> (`W1 before W2 — In Progress path exists before ticket-gate live`).
> Below: W0 grounded contracts confirmed on `develop`; W1 assumed contracts flagged.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Board-status forge **parse** (not apply) | `parse_node_forge` / `WorkflowEngine.get_node` | pin EA with `update_board_status` | action/status/requires ticket | Ground-Report-W0 §Contracts produced | [x] yes — on `develop` |
| Optional pin purpose/owner on resolved node | `ResolvedWorkflowNode.purpose` / `.owner` | pin optional string fields | optional strings or null | Ground-Report-W0 | [x] yes — merged W0 #144 |
| `run_stopped` payload enrichment | `RunOrchestrator._finalize_run` | resolved stop node | timeline may include `purpose`/`owner` | Ground-Report-W0 | [x] yes — merged W0 #144 |
| APPLY_FORGE `update_board_status` **apply** | `ForgeActionService` apply branch | forge hop + ticket binding | board column/state update | **Ground-Report-W1 (missing)**; plan REQ-03 / TASK-W1-01 | [ ] **NO** — not on `develop`; open PR #146 |
| Implement-start In Progress before pre-implement (idempotent) | wave implement-start route / service | `ticket_id` + programme token | board In Progress; then enqueue | **Ground-Report-W1 (missing)**; plan REQ-04 / TASK-W1-02 | [ ] **NO** — not grounded |
| Create-tickets does not resume implement same run | orchestrator / policy guard | create-tickets success path | no `pre-implement` on same run | **Ground-Report-W1 (missing)**; plan REQ-11 / TASK-W1-03 | [ ] **NO** — not grounded |
| Live implement-lane path (In Progress evidence) | `tests.verify.verify_implement_lane` | API+worker+board knobs | exit 0 / documented skip | **Ground-Report-W1 (missing)**; plan TEST-W1-L | [ ] **NO** — W1 live not proven on integration tip |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- All W1 §Contracts produced rows — **blocking for W2** per DEP-2 and REQ-08 live matrix (ticket gate assumes In Progress path from W1).
- W2 must not assume `ForgeActionService` board-status apply or implement-start In Progress behaviour until W1 Ground Report confirms entry points, shapes, and invariants.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify pointers
- [x] MDC rules (domain-filtered — files for W2 domains: API gates, forge predicates, verify):
  - [x] `.cursor/rules/fail-fast.mdc` — fail-closed create predicates + ticket gate (TASK-W2-01, W2-03)
  - [x] `.cursor/rules/http-api-conventions.mdc` — 400/422 implement-start errors (TASK-W2-03)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — create response `epic_ticket_id` / `wave_ticket_ids[]` (TASK-W2-02)
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship live scripts; no unit duplication (TASK-W2-04)
  - [x] `.cursor/rules/architecture.mdc` — forge/orchestrator layering (TASK-W2-01)
  - [ ] `.cursor/rules/logging-loguru.mdc` — skipped (no new logging surface called out)
  - [ ] `.cursor/rules/database-migrations.mdc` — skipped (W2: no schema change)
- [x] ADRs (keyword-matched — ticket gates, forge create, lane intake):
  - [x] ADR-009 — forge mutate authority; create-tickets / board-status policy (**Accepted**)
  - [x] ADR-010 — implement-start intake; ticket binding; closure §7 out of W2 scope (**Accepted**)
  - [x] ADR-005 — programme-token mutations (cross-cutting **Accepted**)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W2 REQs REQ-06, REQ-07, REQ-08, REQ-17 (partial)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W2
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/140 — TASK list (projected from WorkManifest):
  - [ ] TASK-W2-01 — implements REQ-06 — depends_on: [] — files: `forge_action_service.py`, `test_forge_action_service.py` — exit proof: `make test`
  - [ ] TASK-W2-02 — implements REQ-07 — depends_on: [TASK-W2-01] — files: forge action / response models — exit proof: `make test`
  - [ ] TASK-W2-03 — implements REQ-08 — depends_on: [] — files: wave start validators/routes, `test_wave_start.py` — exit proof: `make test`
  - [ ] TASK-W2-04 — implements REQ-06, REQ-08, REQ-17 — depends_on: [TASK-W2-03] — files: `verify_wave_start.py`, `verify_board.py`, `tests/README.md` — exit proof: `.venv/bin/python -m tests.verify.verify_wave_start`
  - [ ] TASK-W2-05 — implements REQ-06–08, REQ-17 — depends_on: [TASK-W2-04] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR (pending W1 grounded contracts)
- [x] Plan TASK MDC notes and ADR notes for W2 reviewed (fail-fast, http-api, pydantic, testing-verify; ADR-009, ADR-010)
- [x] Every initiative ADR cited for W2 is **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`)

> **Deferred** until W1 gate clears and outcome becomes `pass`.

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built after W2 exit
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W2 row (TASK-W2-05)
- [ ] `tests/README.md` — feature map rows for W2 create/ticket gates (TASK-W2-04)
- [ ] Unit verification scope — create predicate negatives; ticket 400/422 matrix (TASK-W2-01…03)
- [ ] Live verification — extend `tests/verify/verify_wave_start.py` and `verify_board.py` (human-run at `live-verify`)
- [ ] ADR — no supersede required (ADR_REQUIRED=0)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live-verify scripts
- [ ] Assume W1 contracts (board-status apply, In Progress path) without W1 Ground Report §Contracts produced
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Start W2 coding while W1 PR #146 is unmerged and W1 Ground Report absent

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | Create triple-predicate gate; epic/wave id response; implement-start 400/422 matrix | `make test` |
| Live verify | Ticket/create gate side-effect table on running stack (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_wave_start` (+ `verify_board` for create predicates) — paths under `tests/verify/` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 after W2 live-verify + learning-extract |

> P15 applies to W2 — live command resolved and scripts exist; gate blocked on **prior wave**, not on W2 live contract.

### Human live-verify (after loop-spec)

When W1 gate clears, W2 checklist re-run passes, and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_start` (and `verify_board` as documented)
- [ ] Experience / inspect ticket gate and create predicate behaviour under programme knobs
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-010-W2.md`
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: #140 — W2 board ticket
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_start`
- ADRs in scope: ADR-009, ADR-010, ADR-005
- Wave head: bound by Forge/human context — `develop` @ `eab2304`
- Blocking W1 PR: https://github.com/drivestream-lab/gateflow/pull/146 (OPEN)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — prior wave W1 not `human_approved`; Ground Report W1 missing |
| Next | `wave-signoff` (`human-checkpoint`) — resolve W1 programme closeout first |
| Forge (this hop) | **not required** — `commit_workspace` applies on `pass` only |
| Later | After W1 merge + Pass-2: re-run `/pre-implement` W2 → `pass` → `/loop-spec` → `wave-pr-action` |

Do not publish this checklist to a wave feature branch until W1 gate clears and a subsequent pre-implement run outcomes `pass`.

---

### Merge order (if cross-module / cross-service)

1. **W1 first (blocking):** merge PR #146 → human `live-verify` W1 → `/learning-extract` → `/ground-spec` → human `wave-signoff` → as-built W1 `human_approved`.
2. **W2 second:** re-run `/pre-implement` W2 (expect `pass`) → `/loop-spec` on `feature/INIT-GATEFLOW-010-w2-ticket-gates`.
3. Plan DEP-2: W1 In Progress path must exist before W2 ticket-gate live (`verify_wave_start`).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W2.md
    digest: sha256:6f00ba233c0fe2030f1f04466ea0c572b70c3dc1a49aecec5e4b08f4b2e5bef1
  blockers:
    - TASK-W1-05
  signals:
    initiative: INIT-GATEFLOW-010
    wave: W2
    board_ticket: "140"
    board_ticket_url: https://github.com/drivestream-lab/gateflow/issues/140
    prior_wave: W1
    prior_ground_report: missing
    prior_wave_human_approved: false
    blocking_w1_pr: "146"
    blocking_w1_pr_url: https://github.com/drivestream-lab/gateflow/pull/146
    workmanifest_contract: pass
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_start
    live_verify_scripts:
      - tests/verify/verify_wave_start.py
      - tests/verify/verify_board.py
    task_ids:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
      - TASK-W2-05
    wave_head_ref: develop
    wave_head_sha: eab23042c6982d54452eba922128ad2b51a60676
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```
