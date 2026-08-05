## Pre-implement — gateflow / W1 — Board-status apply + implement In Progress

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W1.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W1 |
| Date | 2026-08-05 |
| Outcome | `pass` |
| Outcome reason | W1 gate checks pass: W0 `human_approved` + Ground Report present; spec merged with `spec-lgtm`; board seeded; WorkManifest contract clean; P15 live script resolved; commands resolved. |
| Wave head context | Bound by Forge/human context: `develop` @ `eab2304` — not opened by this skill |

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
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/139); W1 body lists TASK-W1-01…05; waves are sub-issues of EPIC |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py …` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W1 TASK-W1-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W1 `verification.live.applicable: true`; script `tests/verify/verify_implement_lane.py` (extend in TASK-W1-04) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; spec file digest `f98e101a…` matches plan §Source freshness |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_implement_lane` — co-shipped under `tests/verify/` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_implement_lane.py` — extend for In Progress / board-status hop asserts (TASK-W1-04) |
| Prior wave as-built row | `human_approved` | [x] INIT-GATEFLOW-010 W0 = **human_approved** — PR [#144](https://github.com/drivestream-lab/gateflow/pull/144) merge `0ca2376`; Pass-2 backfill [#145](https://github.com/drivestream-lab/gateflow/pull/145) on `develop` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W0.md` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W1 |

**Gate verdict:** PASS — W1 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#139](https://github.com/drivestream-lab/gateflow/issues/139) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above. W0 ticket [#138](https://github.com/drivestream-lab/gateflow/issues/138) is **Closed**.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w1-board-status` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-010-W0.md §Contracts produced`.
> Scan `src/` confirms W0 as-built matches what W1 assumes.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Optional pin purpose/owner on resolved node | `ResolvedWorkflowNode.purpose` / `.owner` | pin node optional string fields | optional strings or null | Ground-Report W0 §Contracts produced | [x] yes — `src/models/handoff_models.py`; absent → None |
| Purpose/owner parse | `WorkflowEngine._to_resolved` / `get_node` | pin node mapping | `ResolvedWorkflowNode` with optional purpose/owner | Ground-Report W0 | [x] yes — `src/business_services/workflow_engine.py` |
| `run_stopped` payload enrichment | `RunOrchestrator._finalize_run` | resolved stop node | timeline payload includes purpose/owner when non-null | Ground-Report W0 | [x] yes — `src/business_services/run_orchestrator.py` lines 1165–1168 |
| Board-status forge **parse** (not apply) | `parse_node_forge` / `get_node` | pin EA with `update_board_status` | action/status/requires ticket | Ground-Report W0 | [x] yes — `test_forge_policy` board-status matrix; 0 BROKEN remounted |
| Harness pin ≡ tip | `.harness-pin.yaml` + submodule | pin ref `v0.5.0-rc.2` | tip SHA `6561c7c` | Ground-Report W0 | [x] yes — `describe --exact-match --tags HEAD` green |
| APPLY_FORGE board-status **apply** | `ForgeActionService.apply_external_action` | `update_board_status` hop + ticket in handoff/run context | board column update via BoardService | product spec § gaps; W1 REQ-03 | [ ] NO — apply branch absent (W1 TASK-W1-01 deliverable; not an external drift) |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W1 — board-status **apply** and implement-start In Progress are **in-scope W1 deliverables**, not missing external contracts.
- W2+ will consume W1 Ground Report §Contracts produced after Pass-2 closeout.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/architecture.mdc` — ForgeActionService / BoardService layer boundaries (TASK-W1-01)
  - [x] `.cursor/rules/fail-fast.mdc` — missing ticket fail-closed at apply (REQ-03)
  - [x] `.cursor/rules/http-api-conventions.mdc` — implement-start route shape (TASK-W1-02)
  - [x] `.cursor/rules/testing-verify-flows.mdc` — live verify co-ship; unit vs live separation (TASK-W1-04)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — forge/handoff merge shapes when extending apply path
  - [x] `.cursor/rules/logging-loguru.mdc` — structured forge apply logging
  - [ ] `.cursor/rules/spec-driven-development.mdc` — cited at as-built TASK-W1-05 only (review row)
- [x] ADRs (keyword-matched — board-status apply, lane intake, forge authority):
  - [x] ADR-009 — pin `forge:` publish/mutate authority; `update_board_status` apply SSOT (**Accepted**)
  - [x] ADR-010 — implement-start lane intake; no same-run resume after create-tickets (**Accepted**)
  - [x] ADR-003 — ForgeClient in infra; BoardService orchestration boundary (**Accepted**)
  - [x] ADR-005 — programme token for control-plane mutations (**Accepted**; wave-start auth)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W1 REQs REQ-03, REQ-04, REQ-11, REQ-17 (partial)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W1
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/139 — TASK list (projected from WorkManifest):
  - [ ] TASK-W1-01 — implements REQ-03 — depends_on: [] — files: `forge_action_service.py`, unit tests — exit proof: `make test`
  - [ ] TASK-W1-02 — implements REQ-04 — depends_on: [TASK-W1-01] — files: wave start routes/service, `test_wave_start.py` — exit proof: `make test`
  - [ ] TASK-W1-03 — implements REQ-11 — depends_on: [] — files: policy/orchestrator tests — exit proof: `make test`
  - [ ] TASK-W1-04 — implements REQ-03, REQ-04, REQ-17 — depends_on: [TASK-W1-02] — files: `verify_implement_lane.py`, `tests/README.md` — exit proof: `.venv/bin/python -m tests.verify.verify_implement_lane`
  - [ ] TASK-W1-05 — implements REQ-03, REQ-04, REQ-11 — depends_on: [TASK-W1-04] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed (architecture, fail-fast, http-api, testing-verify; ADR-009, ADR-010, ADR-003)
- [x] Every initiative ADR cited for W1 is **Accepted** in `docs/specification/adr/` (ADR-009, ADR-010, ADR-003, ADR-005)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built baseline after W1 exit (board-status apply + implement In Progress)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W1 row (TASK-W1-05)
- [ ] `tests/README.md` — feature map row for board-status / implement In Progress asserts (TASK-W1-04)
- [ ] Unit verification scope — `test_forge_action_service.py`, `test_wave_start.py`, policy/orchestrator tests for REQ-03/04/11
- [ ] Live verification — extend `tests/verify/verify_implement_lane.py` for In Progress + board-status hop evidence (human-run at `live-verify`)
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
| Unit | Board-status apply; implement-start In Progress; no same-run resume | `make test` |
| Live verify | Product behaviour on running stack (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_implement_lane` — path `tests/verify/verify_implement_lane.py` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after live-verify + learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W1 P15 **applicable** — live script resolved (extend in `/loop-spec`).

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_implement_lane` (co-shipped under `tests/verify/`) with API + worker + forge/board creds per `tests/README.md`
- [ ] Experience / inspect the feature to the depth env access allows — bound ticket reaches In Progress before coding; board-status hop when exercised
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-010-W1.md` / Forge publication
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: #139 — https://github.com/drivestream-lab/gateflow/issues/139
- EPIC: #137 — https://github.com/drivestream-lab/gateflow/issues/137
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_implement_lane`
- ADRs in scope: ADR-009, ADR-010, ADR-003, ADR-005
- Wave head: bound by Forge/human context — `develop` (planned coding branch: `feature/INIT-GATEFLOW-010-w1-board-status`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W1 gates satisfied; WorkManifest clean; P15 live script resolved; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-010-W1.md` to bound `head_ref` (`develop`) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

W1 depends on W0 parse contract (DEP-1 in plan): `ForgeActionService` apply must use W0-verified `parse_node_forge` / pin nodes. Single-repo; no cross-service ordering beyond W0 → W1.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W1.md
    digest: sha256:9e85bc26e7938787e63757afee254d6101f48277b89b350d2d9e498601823291
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W1
    ticket_id: 139
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/139
    epic_ticket_id: 137
    wave_head: develop
    wave_branch_planned: feature/INIT-GATEFLOW-010-w1-board-status
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    implements_reqs:
      - REQ-03
      - REQ-04
      - REQ-11
      - REQ-17
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    verify_script_path: tests/verify/verify_implement_lane.py
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: Todo
    prior_wave_approved: W0
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
