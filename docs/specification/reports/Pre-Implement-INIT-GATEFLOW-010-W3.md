## Pre-implement — gateflow / W3 — Closeout Done + no merge/lgtm/auto-chain

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W3.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W3 |
| Date | 2026-08-05 |
| Outcome | `pass` |
| Outcome reason | W3 gate checks pass: W2 `human_approved` + Ground Report present; spec merged with `spec-lgtm`; board seeded; WorkManifest contract clean; P15 live script resolved; commands resolved. |
| Wave head context | Bound by Forge/human context: `develop` @ `19eb9e8` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#135](https://github.com/drivestream-lab/gateflow/pull/135) merged 2026-08-05; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — PR #135 labels include `spec-lgtm`; head `8cc76540…`; merge commit `1901dbe5…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/138); W3 body lists TASK-W3-01…05; waves are sub-issues of EPIC |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py …` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W3 TASK-W3-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W3 `verification.live.applicable: true`; script `tests/verify/verify_wave_closeout.py` (+ `verify_spec_lane.py` as needed per plan) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; post-W2 as-built updates did not change H1–H3 citation rows |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_closeout` — co-shipped under `tests/verify/` (+ `verify_spec_lane` for spec Pass-1 green under knobs) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_closeout.py` — extend for Done hop / terminal purpose / no auto-chain (TASK-W3-04); `tests/verify/verify_spec_lane.py` as needed |
| Prior wave as-built row | `human_approved` | [x] INIT-GATEFLOW-010 W2 = **human_approved** — PR [#148](https://github.com/drivestream-lab/gateflow/pull/148) merge `ba6d804`; live verify pass 2026-08-05 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W2.md` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W3 |

**Gate verdict:** PASS — W3 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#141](https://github.com/drivestream-lab/gateflow/issues/141) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above. W2 ticket [#140](https://github.com/drivestream-lab/gateflow/issues/140) is **Closed**.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w3-closeout-done` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-010-W2.md §Contracts produced`.
> Scan `src/` confirms W2 as-built matches what W3 assumes.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Create triple predicate gate | `evaluate_create_board_tickets_predicates` | workspace path, plan_path, initiative_id, integration_branch | void or 422 `CreateBoardTicketsGateError` | Ground-Report W2 §Contracts produced | [x] yes — `src/business_services/create_board_tickets_gate.py`; fail-closed before any board creates |
| Create success seed contract | `ForgeActionService.execute_create_board_tickets` | org, repo, effective forge policy + workspace | `BoardTicketsSeedResult` with `epic_ticket_id` + non-empty `wave_ticket_ids[]` | Ground-Report W2 | [x] yes — `src/business_services/forge_action_service.py`; W3 Done hop uses resolved wave ticket ids |
| Implement ticket gate | `implement_ticket_gate.*` + `resolve_board_ticket_id` | ticket_id, initiative_id, wave_id, issue_number, board column | cleaned ticket_id or HTTP 400/422 | Ground-Report W2 | [x] yes — `src/business_services/implement_ticket_gate.py`; Done-column reject path present for wave-done bind |
| Board label + Project Status dual-write | `ForgeClient.update_issue_status` | org, repo, issue_number, column/state | updated issue resource | Ground-Report W2 | [x] yes — `src/infra_services/forge_client.py`; W3 `wave-done-action` Done apply must sync label + V2 Status |
| Board-status APPLY_FORGE apply | `ForgeActionService.execute_update_board_status` | pin `update_board_status` + ticket + pin status | `BoardTicketResource` with updated column | Ground-Report W1 (consumed via W2) | [x] yes — W1 apply path unchanged on tip; pin node `wave-done-action` declares `status: done` |
| Live verify W2 scripts baseline | `verify_wave_start`, `verify_board`, `verify_create_tickets`, `verify_implement_lane` | programme knobs + API/worker | exit 0 under prereqs | Ground-Report W2 | [x] yes — scripts present; W3 extends closeout slice (`verify_wave_closeout`) per REQ-17 |
| Closeout Enter-at intake (partial) | `WaveStartService.start_closeout_wave` | `CloseoutWaveStartRequest` + PR bind | 202 + run_id | INIT-007 baseline on tip | [x] partial — `src/business_services/wave_start_service.py`; W3 TASK-W3-01 wires Done hop after `ground-spec.pass` in orchestrator walk |
| No merge / `*-lgtm` guards (partial) | `ForgeClient` label projection + `forge_models` parse | pin `apply_labels` / forge action lists | rejected or stripped labels | Ground-Report W2 + ADR-009 | [x] partial — `src/infra_services/forge_client.py` refuses `*-lgtm` on apply; W3 TASK-W3-02 hardens merge absence + lgtm rejection at authorize/apply |
| Pin closeout → Done → signoff graph | `workflow.yaml` nodes `ground-spec` → `wave-done-action` → `wave-signoff` | ground-spec pass handoff | automated Done hop then human-checkpoint | pin SSOT | [x] yes — `prayog-skills/workflow.yaml` lines 353–384; W3 implements walker execution + purpose exposure |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- REQ-05 Done hop **after** `ground-spec.pass` in closeout walk timeline — **in-scope W3 deliverable** (INIT-007 closeout route exists; Done apply orchestration not yet proven for INIT-010 W3).
- REQ-19 no auto-chain after `wave-signoff` — pin `wave-complete.pass → pre-implement` exists; W3 TASK-W3-03 adds explicit terminal-stop guard — **in-scope W3 deliverable**, not external drift.
- W4 will consume W3 Ground Report §Contracts produced after Pass-2 closeout.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/fail-fast.mdc` — Done gate fail-closed; no merge/lgtm; terminal stop (TASK-W3-01…03)
  - [x] `.cursor/rules/testing-verify-flows.mdc` — live verify co-ship; unit vs live separation (TASK-W3-04)
  - [x] `.cursor/rules/architecture.mdc` — orchestrator / ForgeActionService / WaveStartService layer boundaries
  - [ ] `.cursor/rules/spec-driven-development.mdc` — cited at as-built TASK-W3-05 only (review row)
- [x] ADRs (keyword-matched — closeout, forge authority, terminal stop, no merge):
  - [x] ADR-009 — pin `forge:` publish/mutate authority; no merge; refuse `*-lgtm` (**Accepted**)
  - [x] ADR-010 — closeout §6 Pass-2 intake; wave-complete vs closure §7; no auto-chain intent (**Accepted**)
  - [x] ADR-003 — ForgeClient in infra; BoardService orchestration boundary (**Accepted**)
  - [x] ADR-005 — programme token for control-plane mutations (**Accepted**; closeout start auth)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W3 REQs REQ-05, REQ-09, REQ-16, REQ-17, REQ-19
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W3
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/141 — TASK list (projected from WorkManifest):
  - [ ] TASK-W3-01 — implements REQ-05 — depends_on: [] — files: orchestrator closeout path, unit tests — exit proof: `make test`
  - [ ] TASK-W3-02 — implements REQ-09, REQ-16 — depends_on: [] — files: forge guards — exit proof: `make test`
  - [ ] TASK-W3-03 — implements REQ-19 — depends_on: [TASK-W3-01] — files: orchestrator / policy — exit proof: `make test`
  - [ ] TASK-W3-04 — implements REQ-05, REQ-17, REQ-19 — depends_on: [TASK-W3-03] — files: `verify_wave_closeout.py`, `verify_spec_lane.py`, `tests/README.md` — exit proof: `.venv/bin/python -m tests.verify.verify_wave_closeout`
  - [ ] TASK-W3-05 — implements REQ-05, REQ-09, REQ-16, REQ-19 — depends_on: [TASK-W3-04] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR
- [x] Plan TASK MDC notes and ADR notes for W3 reviewed (fail-fast, testing-verify; ADR-009, ADR-010)
- [x] Every initiative ADR cited for W3 is **Accepted** in `docs/specification/adr/` (ADR-009, ADR-010, ADR-003, ADR-005)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built baseline after W3 exit (closeout Done + no merge/lgtm/auto-chain)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W3 row (TASK-W3-05)
- [ ] `tests/README.md` — feature map rows for closeout Done hop, terminal purpose, no auto-chain (TASK-W3-04)
- [ ] Unit verification scope — `test_wave_closeout.py`, orchestrator/policy tests for REQ-05, REQ-09, REQ-16, REQ-19
- [ ] Live verification — extend `tests/verify/verify_wave_closeout.py` (+ `verify_spec_lane.py` as needed) for Done hop / terminal purpose / no auto-chain (human-run at `live-verify`)
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
| Unit | Closeout Done hop; no merge/lgtm guards; no auto-chain after wave-signoff | `make test` |
| Live verify | Product behaviour on running stack (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_wave_closeout` — path `tests/verify/verify_wave_closeout.py` (+ `verify_spec_lane` for spec Pass-1 green) |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after live-verify + learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W3 P15 **applicable** — live script resolved (extend in `/loop-spec`).

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_closeout` (co-shipped under `tests/verify/`) with API + programme token + closeout dogfood knobs per `tests/README.md`
- [ ] Run `.venv/bin/python -m tests.verify.verify_spec_lane` when asserting spec Pass-1 green under documented knobs
- [ ] Experience / inspect the feature to the depth env access allows — Done hop on board; terminal `wave-signoff` purpose; confirm no auto-start of next wave or closure
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-010-W3.md` / Forge publication
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: #141 — https://github.com/drivestream-lab/gateflow/issues/141
- EPIC: #137 — https://github.com/drivestream-lab/gateflow/issues/137
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_closeout`
- ADRs in scope: ADR-009, ADR-010, ADR-003, ADR-005
- Wave head: bound by Forge/human context — `develop` (planned coding branch: `feature/INIT-GATEFLOW-010-w3-closeout-done`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W3 gates satisfied; WorkManifest clean; P15 live script resolved; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-010-W3.md` to bound `head_ref` (`develop`) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

W3 depends on W2 create/implement/ticket contracts (DEP from plan): closeout Done hop must use W2-verified `execute_update_board_status`, implement ticket resolution, and Project Status dual-write. Single-repo; no cross-service ordering beyond W2 → W3. INIT-007 closeout route baseline on tip is consumed but not replaced — W3 hardens INIT-010 REQ-05/09/16/19 on the eng pin.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W3.md
    digest: sha256:b7def91fa8891bdad1f6b077eab2cf812468636bfceadc5f96e914d9ff37d835
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W3
    ticket_id: 141
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/141
    epic_ticket_id: 137
    wave_head: develop
    wave_branch_planned: feature/INIT-GATEFLOW-010-w3-closeout-done
    tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
      - TASK-W3-04
      - TASK-W3-05
    implements_reqs:
      - REQ-05
      - REQ-09
      - REQ-16
      - REQ-17
      - REQ-19
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    verify_script_path: tests/verify/verify_wave_closeout.py
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: Todo
    prior_wave_approved: W2
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/135
    spec_merge_commit: 1901dbe5b8ce10ff6e0426c0df1e1dd1906ed655
    workmanifest_contract: pass
    p15_applicable: true
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```
