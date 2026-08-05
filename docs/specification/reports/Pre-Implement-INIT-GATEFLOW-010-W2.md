## Pre-implement — gateflow / W2 — Ticket gates + create predicates

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W2.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W2 |
| Date | 2026-08-05 |
| Outcome | `pass` |
| Outcome reason | W2 gate checks pass: W1 `human_approved` + Ground Report present; spec merged with `spec-lgtm`; board seeded; WorkManifest contract clean; P15 live script resolved; commands resolved. |
| Wave head context | Bound by Forge/human context: `develop` @ `ea1ea17` — not opened by this skill |

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
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W0–W4 [#138–#142](https://github.com/drivestream-lab/gateflow/issues/138); W2 body lists TASK-W2-01…05; waves are sub-issues of EPIC |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py …` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W2 TASK-W2-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W2 `verification.live.applicable: true`; script `tests/verify/verify_wave_start.py` (extend in TASK-W2-04; `verify_board.py` for create predicates) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; product spec file updated post-W1 (as-built baseline) — H1–H3 unchanged |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_start` — co-shipped under `tests/verify/` (+ `verify_board` for REQ-06/07 create path) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_start.py` — extend for 400/422 ticket gate + create predicate asserts (TASK-W2-04); `tests/verify/verify_board.py` for create success fields |
| Prior wave as-built row | `human_approved` | [x] INIT-GATEFLOW-010 W1 = **human_approved** — PR [#146](https://github.com/drivestream-lab/gateflow/pull/146) merge `34e5813`; live verify pass 2026-08-05 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W1.md` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2 |

**Gate verdict:** PASS — W2 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#140](https://github.com/drivestream-lab/gateflow/issues/140) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above. W1 ticket [#139](https://github.com/drivestream-lab/gateflow/issues/139) is **Closed**.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-010-w2-ticket-gates` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-010-W1.md §Contracts produced`.
> Scan `src/` confirms W1 as-built matches what W2 assumes.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Board-status APPLY_FORGE apply | `ForgeActionService.execute_update_board_status` / `apply_external_action` | pin `update_board_status` + merged handoff/run ticket + pin status | `BoardTicketResource` with updated column | Ground-Report W1 §Contracts produced | [x] yes — `src/business_services/forge_action_service.py`; missing ticket → ValidationError fail-closed |
| Pin status → board column | `board_column_for_pin_status` | pin status enum (`in_progress` \| `done`) | board column string (`In Progress` \| `Done`) | Ground-Report W1 | [x] yes — `src/models/forge_models.py` |
| Implement-start In Progress pre-hop | `WaveStartService._apply_implement_in_progress` | org, repo, ticket_id (numeric or issue-resolved) | board column `In Progress` before enqueue | Ground-Report W1 | [x] yes — `src/business_services/wave_start_service.py`; idempotent when already In Progress |
| REQ-11 same-run resume guard | `PolicyEngine.evaluate_dispatch` after `board-tickets-action` pass | handoff stage/outcome | STOP (no `resolve_next` into pre-implement) | Ground-Report W1 | [x] yes — `src/business_services/policy_engine.py` line 64; unit `test_policy_create_tickets_pass_stops_same_run_resume` |
| Live implement_lane board asserts | `tests/verify/verify_implement_lane` | API+worker; `features.implement_lane` knobs | exit 0; board In Progress; optional `update_board_status` timeline | Ground-Report W1 | [x] yes — script present; W1 live pass documented |
| WorkManifest contract at create (partial) | `ForgeActionService.execute_create_board_tickets` | workspace + plan_path + initiative | runs `run_workmanifest_contract` before seed | INIT-008 W2 + W1 baseline | [x] yes — contract script invoked; W2 TASK-W2-01 adds full triple predicate gate at authorize/apply |
| Create response epic/wave ids (partial) | `ForgeActionService` apply payload | successful create | `epic_ticket_id`, `wave_ticket_ids[]` in payload | forge_models + apply path | [x] partial — fields exist on models/payload; W2 TASK-W2-02 hardens success response contract |
| Implement ticket identity resolve (partial) | `WaveStartService._resolve_ticket_identity` | ticket_id + initiative_id + wave_id | parsed initiative/wave or numeric issue | existing wave-start | [x] partial — dual-identity + unresolvable checks present; W2 TASK-W2-03 extends 400/422 matrix + Done-column reject |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W2 — REQ-06 triple predicate gate, REQ-07 response fields, and REQ-08 ticket 400/422 matrix are **in-scope W2 deliverables**, building on W1 apply + partial create/ticket paths (not external drift).
- W3+ will consume W2 Ground Report §Contracts produced after Pass-2 closeout.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/fail-fast.mdc` — create predicate fail-closed; 422 + 0 creates (TASK-W2-01)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — epic/wave id response shapes (TASK-W2-02)
  - [x] `.cursor/rules/http-api-conventions.mdc` — implement-start 400 vs 422 error table (TASK-W2-03)
  - [x] `.cursor/rules/testing-verify-flows.mdc` — live verify co-ship; unit vs live separation (TASK-W2-04)
  - [x] `.cursor/rules/architecture.mdc` — ForgeActionService / BoardService / WaveStartService layer boundaries
  - [ ] `.cursor/rules/spec-driven-development.mdc` — cited at as-built TASK-W2-05 only (review row)
- [x] ADRs (keyword-matched — create predicates, ticket gate, lane intake, forge authority):
  - [x] ADR-009 — pin `forge:` publish/mutate authority; create-tickets authorize/apply SSOT (**Accepted**)
  - [x] ADR-010 — implement-start lane intake; ticket identity agreement (**Accepted**)
  - [x] ADR-003 — ForgeClient in infra; BoardService orchestration boundary (**Accepted**)
  - [x] ADR-005 — programme token for control-plane mutations (**Accepted**; wave-start + authorize auth)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W2 REQs REQ-06, REQ-07, REQ-08, REQ-17 (partial)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W2
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/140 — TASK list (projected from WorkManifest):
  - [ ] TASK-W2-01 — implements REQ-06 — depends_on: [] — files: forge authorize/apply, policy, unit tests — exit proof: `make test`
  - [ ] TASK-W2-02 — implements REQ-07 — depends_on: [TASK-W2-01] — files: forge response models — exit proof: `make test`
  - [ ] TASK-W2-03 — implements REQ-08 — depends_on: [] — files: wave start validators/routes — exit proof: `make test`
  - [ ] TASK-W2-04 — implements REQ-06, REQ-08, REQ-17 — depends_on: [TASK-W2-03] — files: `verify_wave_start.py`, `verify_board.py`, `tests/README.md` — exit proof: `.venv/bin/python -m tests.verify.verify_wave_start`
  - [ ] TASK-W2-05 — implements REQ-06–08, REQ-17 — depends_on: [TASK-W2-04] — files: `implementation-status.md` — exit proof: review as-built row

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR
- [x] Plan TASK MDC notes and ADR notes for W2 reviewed (fail-fast, pydantic-schemas, http-api, testing-verify; ADR-009, ADR-010)
- [x] Every initiative ADR cited for W2 is **Accepted** in `docs/specification/adr/` (ADR-009, ADR-010, ADR-003, ADR-005)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` § as-built baseline after W2 exit (create predicates + ticket gate)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-010 W2 row (TASK-W2-05)
- [ ] `tests/README.md` — feature map rows for create predicate negatives + implement ticket 400/422 asserts (TASK-W2-04)
- [ ] Unit verification scope — `test_forge_action_service.py`, `test_wave_start.py` for REQ-06–08 matrix
- [ ] Live verification — extend `tests/verify/verify_wave_start.py` (+ `verify_board.py` as needed) for negative ticket / create predicate cases (human-run at `live-verify`)
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
| Unit | Create triple predicate gate; epic/wave ids; implement ticket 400/422 matrix | `make test` |
| Live verify | Product behaviour on running stack (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_wave_start` — path `tests/verify/verify_wave_start.py` (+ `verify_board` for create predicates) |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after live-verify + learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W2 P15 **applicable** — live script resolved (extend in `/loop-spec`).

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_start` (co-shipped under `tests/verify/`) with API + programme token + board knobs per `tests/README.md`
- [ ] Run `.venv/bin/python -m tests.verify.verify_board` when exercising create predicate positive path (authorize or documented path)
- [ ] Experience / inspect the feature to the depth env access allows — 400/422 side-effect table for bad tickets; create success fields when positive path run
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

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W2 gates satisfied; WorkManifest clean; P15 live script resolved; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-010-W2.md` to bound `head_ref` (`develop`) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

W2 depends on W1 apply contract (DEP from plan): create-tickets authorize/apply and implement-start ticket gate must use W1-verified `execute_update_board_status`, `_apply_implement_in_progress`, and REQ-11 STOP. Single-repo; no cross-service ordering beyond W1 → W2.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W2.md
    digest: sha256:0c78a80cc2d7f815e12fbc92c72baa5c380644d5811de362b4309021b6ebba7c
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W2
    ticket_id: 140
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/140
    epic_ticket_id: 137
    wave_head: develop
    wave_branch_planned: feature/INIT-GATEFLOW-010-w2-ticket-gates
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
    board_wave_status: Todo
    prior_wave_approved: W1
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
