## Pre-implement — gateflow / W0 — Pin parse parity + purpose/owner on stops

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W0.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W0 |
| Date | 2026-08-05 |
| Outcome | `pass` |
| Outcome reason | W0 gate checks pass: spec merged with `spec-lgtm`, board seeded, WorkManifest contract clean, commands resolved, PE sign-off complete; no prior-wave Ground Report required. |
| Wave head context | Bound by Forge/human context: `develop` @ `18cf71b` — not opened by this skill |

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
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/138); W0 body lists TASK-W0-01…05; waves are sub-issues of EPIC |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W0 TASK-W0-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] N/A — W0 `verification.live.applicable: false` (parse + stop payload only; Q-3) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] N/A — P15 N/A; W0 unit + harness inspect only |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] N/A (no new callable product surface) |
| Prior wave as-built row | `human_approved` | [x] N/A — W0 first wave of INIT-GATEFLOW-010 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0; gate is plan §0 PE sign-off |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-05 PE package accept |

**Gate verdict:** PASS — W0 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#138](https://github.com/drivestream-lab/gateflow/issues/138) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w0-pin-parse` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> W0 is the first wave of INIT-GATEFLOW-010 — no `Ground-Report-INIT-GATEFLOW-010-W{-1}.md`.
> Dependencies are on **as-built** capabilities from prior INITs; scan confirms partial W0 baseline in product spec § as-built.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Pin remount + `get_node` for all workflow nodes incl. board-status hops | `WorkflowEngine.get_node` | pin node id string | `ResolvedWorkflowNode` with parsed `forge`, `authorization`, `outcomes` | as-built INIT-008/009; `tests/unit/test_forge_policy.py::test_all_remounted_pin_nodes_parse` | [x] yes — 0 BROKEN nodes; `update_board_status` parse tests green |
| `update_board_status` forge policy parse | `parse_node_forge` | pin `forge` dict with `action`, `status`, `requires` | `NodeForgePolicy` with action + status enum + requires list | `src/models/forge_models.py`; unit tests | [x] yes |
| Harness pin ≡ submodule tip | `.harness-pin.yaml` + `prayog-skills` submodule | tag `v0.5.0-rc.2` | SHA `6561c7c508539fbdb182159d3fdae5abef4b9b01` | product spec as-built baseline; `git -C prayog-skills rev-parse v0.5.0-rc.2^{commit}` | [x] yes — tag tip equals submodule HEAD |
| Optional `purpose` / `owner` on resolved stop node | `WorkflowEngine._to_resolved` → `ResolvedWorkflowNode` | pin node raw dict | model fields `purpose`, `owner` (optional) | product spec § gaps; `src/models/handoff_models.py` | [ ] NO — fields absent on `ResolvedWorkflowNode` (W0 TASK-W0-03) |
| `purpose` / `owner` on terminal `run_stopped` timeline payload | `RunOrchestrator` finalize / `_append_run_stopped` | resolved stop node + handoff envelope | timeline event payload includes pin purpose/owner when present | product spec § gaps; `src/business_services/run_orchestrator.py` | [ ] NO — payload has `stop_reason`, `handoff_context` only (W0 TASK-W0-04) |
| APPLY_FORGE board-status side effect | `ForgeActionService` apply | `update_board_status` hop | board ticket column update | as-built INIT-010 spec | [ ] N/A W0 — apply deferred to W1 (REQ-03); parse-only this wave |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W0 — gaps above are **in-scope W0 deliverables**, not missing external contracts.
- W1+ will consume W0 Ground Report §Contracts produced after Pass-2 closeout.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/fail-fast.mdc` — fail-closed parse/validation (TASK-W0-02, W0-03)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `ResolvedWorkflowNode` / handoff model shape (TASK-W0-03)
  - [x] `.cursor/rules/logging-loguru.mdc` — structured stop/timeline logging (TASK-W0-04)
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built discipline (TASK-W0-05)
  - [ ] `.cursor/rules/http-api-conventions.mdc` — skipped (W0: no new HTTP surface)
  - [ ] `.cursor/rules/testing-verify-flows.mdc` — skipped (P15 N/A; unit only)
  - [ ] `.cursor/rules/architecture.mdc` — skipped (no layer boundary change beyond model fields)
- [x] ADRs (keyword-matched — pin parse, forge policy, stop payload):
  - [x] ADR-009 — pin `forge:` publish/mutate authority; parse SSOT; hygiene strip INIT-010 (**Accepted**)
  - [x] ADR-010 — lane intake authority; W0 parse-only touches pin consume, not intake routes (**Accepted**; §7 closure out of W0 scope)
  - [x] ADR-001, ADR-003, ADR-005 — cross-cutting Accepted; cited in plan §0; no W0 contradiction
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W0 REQs REQ-01, REQ-02, REQ-10
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/138 — TASK list (projected from WorkManifest):
  - [ ] TASK-W0-01 — implements REQ-01 — depends_on: [] — files: `.harness-pin.yaml` (inspect), `implementation-status.md` — exit proof: `git -C prayog-skills describe --exact-match`
  - [ ] TASK-W0-02 — implements REQ-02 — depends_on: [TASK-W0-01] — files: `tests/unit/test_forge_policy.py` — exit proof: `make check && make test`
  - [ ] TASK-W0-03 — implements REQ-10 — depends_on: [TASK-W0-01] — files: `handoff_models.py`, `workflow_engine.py` — exit proof: `make check && make test`
  - [ ] TASK-W0-04 — implements REQ-10 — depends_on: [TASK-W0-03] — files: `run_orchestrator.py`, orchestrator unit tests — exit proof: `make test`
  - [ ] TASK-W0-05 — implements REQ-01, REQ-02, REQ-10 — depends_on: [TASK-W0-04] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed (fail-fast, pydantic-schemas, logging-loguru; ADR-009)
- [x] Every initiative ADR cited for W0 is **Accepted** in `docs/specification/adr/` (ADR-009, ADR-010; ADR-011 withdrawn)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built baseline after W0 exit
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W0 row (TASK-W0-05; closes FF-02)
- [ ] `tests/README.md` — no feature-map row required (P15 N/A)
- [ ] Unit verification scope — extend `test_forge_policy.py`, orchestrator tests for REQ-02/REQ-10
- [ ] Live verification — N/A (P15 N/A for W0)
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
| Unit | Board-status parse matrix; purpose/owner on node + stop payload; 0 BROKEN `get_node` | `make test` |
| Live verify | Product behaviour on running stack (human-run at `live-verify`) | N/A — P15 N/A (no new callable product surface; Q-3) |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after live-verify + learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W0 is explicitly N/A.

### Human live-verify (after loop-spec)

W0 does not add a live-verify checkpoint — Pass-1 stops at unit green + as-built row. Human live-verify applies from W1 onward.

When W1+ checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run the documented wave live script (co-shipped under `tests/verify/`)
- [ ] Experience / inspect the feature to the depth env access allows
- [ ] Capture exit evidence for `Live-Verify-{INIT}-W{N}.md` / Forge publication
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: #138 — https://github.com/drivestream-lab/gateflow/issues/138
- EPIC: #137 — https://github.com/drivestream-lab/gateflow/issues/137
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): N/A — P15 N/A (unit + inspect)
- ADRs in scope: ADR-009, ADR-010 (ADR-001/003/005 inherited Accepted)
- Wave head: bound by Forge/human context — `develop` (planned coding branch: `feature/INIT-GATEFLOW-010-w0-pin-parse`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W0 gates satisfied; WorkManifest clean; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-010-W0.md` to bound `head_ref` (`develop`) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W0 is single-repo pin-parse + model/orchestrator fields. W1 depends on W0 parse (DEP-1) before board-status apply.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W0.md
    digest: sha256:121d332a719339e3962313d445f6c25a35f1c325799709465cbfe08691ca1a21
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W0
    ticket_id: 138
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/138
    epic_ticket_id: 137
    wave_head: develop
    wave_branch_planned: feature/INIT-GATEFLOW-010-w0-pin-parse
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
    implements_reqs:
      - REQ-01
      - REQ-02
      - REQ-10
    check_command: make check
    test_command: make test
    verify_command: "N/A — P15 N/A"
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: Todo
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/135
    spec_merge_commit: 1901dbe5b8ce10ff6e0426c0df1e1dd1906ed655
    workmanifest_contract: pass
    p15_applicable: false
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```
