## Pre-implement — gateflow / W4 — Initiative closure Enter-at + freeze

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W4.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W4 |
| Date | 2026-08-06 |
| Outcome | `pass` |
| Outcome reason | W4 gate checks pass: W3 `human_approved` + Ground Report present; spec merged with `spec-lgtm`; board seeded; WorkManifest contract clean; P15 live script contract resolved; commands resolved. |
| Wave head context | Bound by Forge/human context: `develop` @ `7fdef084227657c1d97b95d3d552fc67b7100905` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` (remote `feature/INIT-GATEFLOW-010-w4-implement-lane` exists; not checked out here) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#135](https://github.com/drivestream-lab/gateflow/pull/135) merged 2026-08-05; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — PR #135 labels include `spec-lgtm`; head `8cc76540…`; merge commit `1901dbe5…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/138); W4 body lists TASK-W4-01…07; waves are sub-issues of EPIC |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W4 TASK-W4-01…07 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W4 `verification.live.applicable: true`; script `.venv/bin/python -m tests.verify.verify_closure` (co-ship path `tests/verify/verify_closure.py` per TASK-W4-05) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; post-W3 as-built updates did not change H1–H3 citation rows |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_closure` — co-ship under `tests/verify/` (create in `/loop-spec` TASK-W4-05) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_closure.py` — **to create** in TASK-W4-05 (not on tip yet; contract declared in §9) |
| Prior wave as-built row | `human_approved` | [x] INIT-GATEFLOW-010 W3 = **human_approved** — PR [#150](https://github.com/drivestream-lab/gateflow/pull/150) merge `85c2ec5`; Pass-2 closeout dogfood run `75dd6b42-…` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W3.md` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W4 |

**Gate verdict:** PASS — W4 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#142](https://github.com/drivestream-lab/gateflow/issues/142) programme-board Status is **In Progress** (`gateflow/column:In Progress`). W0–W3 tickets [#138–#141](https://github.com/drivestream-lab/gateflow/issues/138) are **Closed** with Done column labels where applicable. EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137) remains **Open** (expected until closure walk).

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w4-closure` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-010-W3.md §Contracts produced`.
> Scan `src/` confirms W3 as-built matches what W4 assumes.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Closeout Done hop after ground-spec pass | `RunOrchestrator.process_job` (Enter-at `ground-spec` on closeout lane) | job payload with `ticket_id`, closeout `head_ref`, ground-spec pass handoff | STOP at `wave-signoff`; `forge_executed` at `wave-done-action` | Ground-Report W3 §Contracts produced | [x] yes — `src/business_services/run_orchestrator.py`; unit `test_closeout_walk_applies_done_then_stops_at_wave_signoff` |
| Forge merge prohibition | `ForgeActionService.apply_external_action`, `ForgeClient.enable_auto_merge` | pin/handoff forge action | reject or raise on merge/auto-merge | Ground-Report W3 | [x] yes — `_FORBIDDEN_FORGE_ACTION_VALUES` in `forge_action_service.py`; client guard present |
| LGTM label prohibition | `parse_node_forge`, `merge_pin_and_handoff_forge`, `apply_external_action` | pin `apply_labels` / handoff forge | stripped or ValidationError/PermissionError | Ground-Report W3 | [x] yes — `*-lgtm` rejected at merge/apply |
| No auto-chain after wave-signoff | `PolicyEngine.evaluate_dispatch` | handoff with `stage=wave-signoff` or `wave-complete`, `outcome=pass` | `PolicyDecisionType.STOP` | Ground-Report W3 | [x] yes — `src/business_services/policy_engine.py`; W4 closure Enter-at is separate deliberate API (REQ-19) |
| Live verify W3 closeout slice | `tests/verify/verify_wave_closeout.py` | programme knobs (`wave_closeout.dogfood`, PR bind, worker) | exit 0 under prereqs | Ground-Report W3 | [x] yes — script on tip; W4 adds closure slice via new `verify_closure.py` |
| Create triple predicate gate | `create_board_tickets_gate.evaluate_*` | workspace path, plan_path, initiative_id | void or 422 | Ground-Report W2 (unchanged) | [x] yes — W4 closure reuses epic/wave ticket ids from create success |
| Implement ticket gate + Done reject | `implement_ticket_gate.*` | ticket_id, initiative_id, wave_id, column | 400/422 or cleaned ticket_id | Ground-Report W2 | [x] yes — W4 Done-gate is closure-specific validator (REQ-13), not implement gate |
| Board label + Project Status dual-write | `ForgeClient.update_issue_status` | org, repo, issue_number, column/state | updated issue resource | Ground-Report W2 | [x] yes — W4 REQ-14 EPIC Done before purge uses same dual-write path |
| Board-status APPLY_FORGE apply | `ForgeActionService.execute_update_board_status` | pin `update_board_status` + ticket + pin status | `BoardTicketResource` | Ground-Report W1/W2 | [x] yes — W3 Done hop proven; W4 EPIC Done is board hygiene before purge |
| Wave closeout intake (Pass-2 baseline) | `WaveStartService.start_closeout_wave` | `CloseoutWaveStartRequest` + PR bind | 202 + run_id | INIT-007 on tip | [x] yes — `src/business_services/wave_start_service.py`, `POST /api/v1/waves/closeout/start`; W4 adds distinct closure Enter-at per ADR-010 §7 |
| Pin closure graph | `workflow.yaml` `initiative-closure` → `purge-initiative-artifacts-app` → `initiative-closure-pr-action-app` → `initiative-closure-signoff-app` | closure pass handoff | STOP at signoff-app; never `purge-initiative-artifacts-meta` on eng walk | pin SSOT | [x] yes — `prayog-skills/workflow.yaml` lines 394–440; W4 wires Enter-at dispatch only |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- `POST /api/v1/initiatives/closure/start` — **in-scope W4 deliverable** (REQ-12); no route on tip yet (`grep` shows policy message only).
- Closure Done-gate validator (REQ-13) — **in-scope W4 deliverable** (TASK-W4-02).
- EPIC Done before purge-app dispatch (REQ-14) — **in-scope W4 deliverable** (TASK-W4-03); board apply family confirmed from W3.
- Partial failure hygiene after EPIC Done (REQ-20) — **in-scope W4 deliverable** (TASK-W4-04).
- `tests/verify/verify_closure.py` — **in-scope W4 co-ship** (TASK-W4-05); contract declared in §9, file not on tip.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/http-api-conventions.mdc` — closure route JSON body; programme token mutation (TASK-W4-01)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — closure request/response models in `src/models/` (TASK-W4-01)
  - [x] `.cursor/rules/fail-fast.mdc` — Done-gate 422; no silent EPIC mutation; partial failure (TASK-W4-02…04)
  - [x] `.cursor/rules/architecture.mdc` — WaveStartService / closure service / orchestrator layer boundaries (TASK-W4-03)
  - [x] `.cursor/rules/testing-verify-flows.mdc` — live verify co-ship; unit vs live separation (TASK-W4-05)
  - [x] `.cursor/rules/logging-loguru.mdc` — partial failure recording (TASK-W4-04)
  - [x] `.cursor/rules/dependency-injection.mdc` — DI wiring for new routes/services (TASK-W4-01)
  - [ ] `.cursor/rules/spec-driven-development.mdc` — cited at as-built TASK-W4-07 only (review row)
- [x] ADRs (keyword-matched — closure, intake, forge, board hygiene):
  - [x] ADR-010 — closeout §6 vs **closure §7** intake authority; distinct Enter-at; no overload closeout body (**Accepted**)
  - [x] ADR-009 — pin forge publish/mutate; no merge; refuse `*-lgtm`; purge-app forge hops (**Accepted**)
  - [x] ADR-005 — programme token for control-plane mutations (**Accepted**)
  - [x] ADR-001 — runtime/durable store for failure recording (**Accepted**; REQ-20)
  - [x] ADR-003 — ForgeClient in infra; BoardService orchestration boundary (**Accepted**)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W4 REQs REQ-12, REQ-13, REQ-14, REQ-15, REQ-17, REQ-18, REQ-20
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W4
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/142 — TASK list (projected from WorkManifest):
  - [ ] TASK-W4-01 — implements REQ-12 — depends_on: [] — files: `src/api/v1/`, `src/models/`, `src/app.py` — exit proof: `make check && make test`
  - [ ] TASK-W4-02 — implements REQ-13 — depends_on: [TASK-W4-01] — files: closure validator, unit tests — exit proof: `make test`
  - [ ] TASK-W4-03 — implements REQ-14, REQ-15 — depends_on: [TASK-W4-02] — files: board_service + orchestrator — exit proof: `make test`
  - [ ] TASK-W4-04 — implements REQ-20 — depends_on: [TASK-W4-03] — files: `run_orchestrator.py`, unit tests — exit proof: `make test`
  - [ ] TASK-W4-05 — implements REQ-12, REQ-13, REQ-17 — depends_on: [TASK-W4-04] — files: `verify_closure.py`, `tests/README.md` — exit proof: `.venv/bin/python -m tests.verify.verify_closure`
  - [ ] TASK-W4-06 — implements REQ-18 — depends_on: [TASK-W4-05] — files: `Feature-Readiness-INIT-GATEFLOW-010.md` — exit proof: review freeze doc
  - [ ] TASK-W4-07 — implements REQ-12–15, REQ-17–20 — depends_on: [TASK-W4-06] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR
- [x] Plan TASK MDC notes and ADR notes for W4 reviewed (http-api, pydantic, fail-fast, architecture, testing-verify; ADR-010 §7, ADR-009, ADR-001)
- [x] Every initiative ADR cited for W4 is **Accepted** in `docs/specification/adr/` (ADR-010, ADR-009, ADR-005, ADR-001, ADR-003)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built baseline after W4 exit (closure Enter-at + freeze)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W4 + initiative freeze row (TASK-W4-07)
- [ ] `tests/README.md` — feature map row for closure Enter-at, Done-gate, EPIC hygiene, purge walk (TASK-W4-05)
- [ ] Unit verification scope — closure route 400/202, Done-gate 422, EPIC Done ordering, partial failure, purge walk timeline (TASK-W4-01…04)
- [ ] Live verification — create `tests/verify/verify_closure.py` for 400/422/202 + Done-gate negatives (human-run at `live-verify`)
- [ ] Feature-readiness freeze — `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md` (TASK-W4-06)
- [ ] ADR — no supersede required (ADR_REQUIRED=0; closure folded in ADR-010 §7)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live-verify scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Dispatch `purge-initiative-artifacts-meta` from eng closure walk (REQ-15; meta purge is PM lane)
- [ ] Auto-chain from wave-signoff into closure (REQ-19 — PE must call closure-start deliberately)

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | Closure route validation; Done-gate; EPIC Done ordering; partial failure; purge walk stops at signoff-app | `make test` |
| Live verify | Product behaviour on running stack (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_closure` — path `tests/verify/verify_closure.py` (create in TASK-W4-05) |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after live-verify + learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W4 P15 **applicable** — live script contract resolved (co-ship in `/loop-spec`).

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_closure` (co-shipped under `tests/verify/`) with API + programme token + board tickets for Done-gate positives/negatives per `tests/README.md`
- [ ] Experience / inspect the feature to the depth env access allows — closure 400/422 matrix; EPIC Done before purge; timeline stops at `initiative-closure-signoff-app`; confirm no meta purge dispatch
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-010-W4.md` / Forge publication
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout / initiative closure signoff

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: #142 — https://github.com/drivestream-lab/gateflow/issues/142
- EPIC: #137 — https://github.com/drivestream-lab/gateflow/issues/137
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_closure`
- ADRs in scope: ADR-010, ADR-009, ADR-005, ADR-001, ADR-003
- Wave head: bound by Forge/human context — `develop` @ `7fdef08` (planned coding branch: `feature/INIT-GATEFLOW-010-w4-closure`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W4 gates satisfied; WorkManifest clean; P15 live script contract resolved; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-010-W4.md` to bound `head_ref` (`develop`) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

W4 depends on W3 closeout Done + no-auto-chain contracts (DEP-4 from plan): closure Done-gate assumes wave tickets can be board Done; EPIC Done hygiene uses W2-verified board dual-write; purge walk consumes pin `initiative-closure` → `purge-initiative-artifacts-app` graph. Single-repo; no cross-service ordering beyond W3 → W4. INIT-007 closeout route remains separate from closure Enter-at (ADR-010 §6 vs §7).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W4.md
    digest: sha256:f9dace678adbcf4ef34ef87bb6fc03e70208d38fbf44fd9a9705e02b522bc12b
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W4
    ticket_id: 142
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/142
    epic_ticket_id: 137
    wave_head: develop
    wave_head_sha: 7fdef084227657c1d97b95d3d552fc67b7100905
    wave_branch_planned: feature/INIT-GATEFLOW-010-w4-closure
    tasks:
      - TASK-W4-01
      - TASK-W4-02
      - TASK-W4-03
      - TASK-W4-04
      - TASK-W4-05
      - TASK-W4-06
      - TASK-W4-07
    implements_reqs:
      - REQ-12
      - REQ-13
      - REQ-14
      - REQ-15
      - REQ-17
      - REQ-18
      - REQ-20
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_closure
    verify_script_path: tests/verify/verify_closure.py
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: In Progress
    prior_wave_approved: W3
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
