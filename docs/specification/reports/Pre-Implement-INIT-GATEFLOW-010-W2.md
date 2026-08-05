## Pre-implement — gateflow / W2 — Ticket gates + create predicates

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W2.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W2 |
| Date | 2026-08-05 |
| Outcome | `blocked` |
| Outcome reason | Prior wave W1 as-built row is **pending human_approved** — Ground Report W1 exists and PR [#146](https://github.com/drivestream-lab/gateflow/pull/146) merged to `develop` (`34e5813`), but formal `human_approved` on the W1 capability row is not recorded; W2 pre-implement gate fails closed per skill rule 2. |
| Wave head context | Bound by Forge/human context: `develop` @ `34e5813` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `34e581337685198554b929d1c19c4412dfa113e3` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#135](https://github.com/drivestream-lab/gateflow/pull/135) merged; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — PR #135 labels include `spec-lgtm`; merge commit `1901dbe5…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/140); W2 body lists TASK-W2-01…05; waves sub-issues of EPIC |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W2 TASK-W2-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W2 `verification.live.applicable: true`; script `tests/verify/verify_wave_start.py` (+ `verify_board.py` per TASK-W2-04) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; spec digest `f98e101a…` matches plan §Source freshness |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_start` — co-shipped under `tests/verify/` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_start.py` — extend for ticket/create gate negatives (TASK-W2-04); `tests/verify/verify_board.py` for REQ-06/07 |
| Prior wave as-built row | `human_approved` | [ ] **BLOCKED** — INIT-GATEFLOW-010 W1 = **pending human_approved** in `docs/specification/as-built/implementation-status.md` (PR #146 merged `34e5813`; Live-Verify pass; Ground-Report W1 exists — formal `wave-signoff` / as-built update not recorded) |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W1.md` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2 |

**Gate verdict:** BLOCKED — prior wave W1 as-built row is not `human_approved`. Do not proceed to `/loop-spec` until human completes `wave-signoff` for W1 and updates the as-built row.

**Board process note (read-only):** W1 ticket [#139](https://github.com/drivestream-lab/gateflow/issues/139) is **Closed**; W2 ticket [#140](https://github.com/drivestream-lab/gateflow/issues/140) is **Open**. Board closure does not substitute for as-built `human_approved`.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w2-ticket-gates` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-010-W1.md §Contracts produced`.
> Scan `src/` on `develop` @ `34e5813` confirms W1 built interfaces match W2 assumptions.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Board-status APPLY_FORGE apply | `ForgeActionService.execute_update_board_status` / `apply_external_action` | pin `update_board_status` + merged handoff/run ticket + pin status | `BoardTicketResource` with updated column | Ground-Report W1 §Contracts produced | [x] yes — `src/business_services/forge_action_service.py` |
| Pin status → board column | `board_column_for_pin_status` | pin status enum (`in_progress` \| `done`) | board column string (`In Progress` \| `Done`) | Ground-Report W1 | [x] yes — same module; deterministic mapping |
| Implement-start In Progress pre-hop | `WaveStartService._apply_implement_in_progress` | org, repo, ticket_id (numeric or issue-resolved) | board column `In Progress` before enqueue | Ground-Report W1 | [x] yes — `src/business_services/wave_start_service.py` |
| REQ-11 same-run resume guard | `PolicyEngine.evaluate_dispatch` after `board-tickets-action` pass | handoff stage/outcome | STOP (no `resolve_next` into pre-implement) | Ground-Report W1 | [x] yes — `src/business_services/policy_engine.py` line 64 |
| Live implement_lane board asserts | `tests/verify/verify_implement_lane` | API+worker; `features.implement_lane` knobs | exit 0; board In Progress | Ground-Report W1 | [x] yes — script on tip; human Live-Verify W1 pass |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W2 contract consumption — W1 code and Ground Report §Contracts produced are on `develop`. W2 **create predicates** (REQ-06/07) and **implement ticket gate** (REQ-08) are in-scope W2 deliverables building on W1 apply/resume contracts.

---

### Must read (deferred until gate passes — documented for re-run)

- [ ] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [ ] MDC rules (domain-filtered — files for this slice's domains):
  - [ ] `.cursor/rules/fail-fast.mdc` — create/implement fail-closed (REQ-06, REQ-08)
  - [ ] `.cursor/rules/http-api-conventions.mdc` — 400/422 error table (TASK-W2-03)
  - [ ] `.cursor/rules/pydantic-schemas.mdc` — create response fields `epic_ticket_id` / `wave_ticket_ids[]` (TASK-W2-02)
  - [ ] `.cursor/rules/testing-verify-flows.mdc` — live verify co-ship; unit vs live separation (TASK-W2-04)
  - [ ] `.cursor/rules/architecture.mdc` — forge authorize/apply layer boundaries (TASK-W2-01)
  - [ ] `.cursor/rules/spec-driven-development.mdc` — cited at as-built TASK-W2-05 only (review row)
- [ ] ADRs (keyword-matched — forge authority, lane intake, ticket gates):
  - [ ] ADR-009 — create-tickets forge explicit authorize/apply; no merge (**Accepted**)
  - [ ] ADR-010 — implement-start ticket resolution; dual-workspace (**Accepted**)
  - [ ] ADR-003 — ForgeClient / BoardService boundary (**Accepted**)
  - [ ] ADR-005 — programme token for control-plane mutations (**Accepted**)
- [ ] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W2 REQs REQ-06, REQ-07, REQ-08, REQ-17 (partial)
- [ ] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W2
- [ ] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/140 — TASK list (projected from WorkManifest):
  - [ ] TASK-W2-01 — implements REQ-06 — depends_on: [] — files: `forge_action_service.py`, unit tests — exit proof: `make test`
  - [ ] TASK-W2-02 — implements REQ-07 — depends_on: [TASK-W2-01] — files: forge action / response models — exit proof: `make test`
  - [ ] TASK-W2-03 — implements REQ-08 — depends_on: [] — files: wave start validators — exit proof: `make test`
  - [ ] TASK-W2-04 — implements REQ-06, REQ-08, REQ-17 — depends_on: [TASK-W2-03] — files: `verify_wave_start.py`, `verify_board.py`, `tests/README.md` — exit proof: `.venv/bin/python -m tests.verify.verify_wave_start`
  - [ ] TASK-W2-05 — implements REQ-06–08, REQ-17 — depends_on: [TASK-W2-04] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [ ] Slice spec does not contradict any listed ADR — **deferred** (gate blocked; no contradiction spotted in spec scan)
- [ ] Plan TASK MDC notes and ADR notes for W2 reviewed — **deferred**
- [ ] Every initiative ADR cited for W2 is **Accepted** in `docs/specification/adr/` (ADR-009, ADR-010, ADR-003, ADR-005) — **confirmed on scan**

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built baseline after W2 exit (create predicates + ticket gate)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W2 row (TASK-W2-05)
- [ ] `tests/README.md` — feature map rows for create predicates + ticket gate live asserts (TASK-W2-04)
- [ ] Unit verification scope — `test_forge_action_service.py`, `test_wave_start.py` for REQ-06/07/08 matrix
- [ ] Live verification — extend `tests/verify/verify_wave_start.py` (+ `verify_board.py`) for 400/422 negatives (human-run at `live-verify`)
- [ ] ADR — no supersede required (ADR_REQUIRED=0)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live-verify scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | Create triple predicate gate; epic/wave ids on success; implement ticket 400/422 matrix | `make test` |
| Live verify | Product behaviour on running stack (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_wave_start` — path `tests/verify/verify_wave_start.py` (+ `verify_board.py` for REQ-06/07) |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after live-verify + learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W2 P15 **applicable** — live script resolved (extend in `/loop-spec`).

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_start` (and `verify_board` as needed) with API + worker + forge/board creds per `tests/README.md` / `tests/config.yaml` W2 knobs
- [ ] Experience / inspect create predicate failures (422 + 0 creates) and implement-start ticket gate (400/422; 0 enqueue)
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-010-W2.md` / Forge publication
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: #140 — https://github.com/drivestream-lab/gateflow/issues/140
- EPIC: #137 — https://github.com/drivestream-lab/gateflow/issues/137
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_start`
- ADRs in scope: ADR-009, ADR-010, ADR-003, ADR-005
- Wave head: bound by Forge/human context — `develop` (planned coding branch: `feature/INIT-GATEFLOW-010-w2-ticket-gates`)
- Prior wave: W1 PR [#146](https://github.com/drivestream-lab/gateflow/pull/146) merged `34e5813`; Ground-Report W1 present; as-built W1 **pending human_approved**

---

### Resolution path (blocked)

| Step | Owner | Action |
|------|-------|--------|
| 1 | Human | Complete **wave-signoff** for W1 — confirm reviewed head / merge commit `34e5813`; mark INIT-GATEFLOW-010 W1 = **human_approved** in `implementation-status.md` |
| 2 | Human / orch | Re-run `/pre-implement` for W2 — expect `pass` when W1 as-built gate satisfied |
| 3 | Forge (after pass) | `/commit-workspace` publishes Pre-Implement W2 checklist to `develop` |
| 4 | Skill | `/loop-spec` implements W2 on planned branch |

Do **not** open W2 coding branch or Draft PR from this blocked run.

---

### Checklist publish readiness (blocked — no commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — W1 as-built row not `human_approved` |
| Next | `wave-signoff` (`human-checkpoint`) — `external_action: false` |
| Forge (this hop) | **not required** — gate blocked; no checklist publish until W1 sign-off complete and re-run passes |

---

### Merge order (if cross-module / cross-service)

W2 depends on W1 In Progress path and board-status apply (DEP-2 in plan): ticket gate (REQ-08) builds on W1-resolved ticket + `_apply_implement_in_progress`. Single-repo; no cross-service ordering beyond W1 → W2.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W2.md
    digest: sha256:77b376c9f524a8e89cc47db983a3e73135930e030d90496079c40f747ca8ad20
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W2
    ticket_id: 140
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/140
    epic_ticket_id: 137
    wave_head: develop
    wave_head_sha: 34e581337685198554b929d1c19c4412dfa113e3
    wave_branch_planned: feature/INIT-GATEFLOW-010-w2-ticket-gates
    prior_wave: W1
    prior_wave_as_built: pending human_approved
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W1.md
    prior_wave_pr: https://github.com/drivestream-lab/gateflow/pull/146
    prior_wave_merge_commit: 34e581337685198554b929d1c19c4412dfa113e3
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
      - TASK-W2-05
    implements_reqs:
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-17
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_start
    verify_script_path: tests/verify/verify_wave_start.py
    ground_command: "N/A — /ground-spec pin skill"
    workmanifest_contract: pass
    p15_applicable: true
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/135
    spec_merge_commit: 1901dbe5b8ce10ff6e0426c0df1e1dd1906ed655
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```
