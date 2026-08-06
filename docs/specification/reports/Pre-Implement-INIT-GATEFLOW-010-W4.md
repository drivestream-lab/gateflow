## Pre-implement — gateflow / W4 — Initiative closure Enter-at + freeze

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W4.md` |
| Initiative | INIT-GATEFLOW-010 |
| Wave | W4 |
| Date | 2026-08-06 |
| Outcome | `blocked` |
| Outcome reason | Prior wave W3 as-built row is **ground pass — pending human_approved** (not `human_approved`); Draft PR [#150](https://github.com/drivestream-lab/gateflow/pull/150) awaits `wave-signoff` merge before W4 coding may start. |
| Wave head context | Bound by Forge/human context: `develop` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` (integration branch) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#135](https://github.com/drivestream-lab/gateflow/pull/135) merged 2026-08-05; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — PR #135 labels include `spec-lgtm`; head `8cc76540…`; merge commit `1901dbe5…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#137](https://github.com/drivestream-lab/gateflow/issues/137); W4 [#142](https://github.com/drivestream-lab/gateflow/issues/142) sub-issue of EPIC; body lists TASK-W4-01…07 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W4 TASK-W4-01…07 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — W4 `verification.live.applicable: true`; planned script `tests/verify/verify_closure.py` (create in `/loop-spec`; absent on `develop` today) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness rows CURRENT (walk-time; plan digest not long-term SSOT) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:457f1961…`, H2 `sha256:09c89c14…`, H3 revision `1`, G1 `df0f5a5…`; narrative updates on product spec did not change H1–H3 citation rows |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_closure` — co-ship target under `tests/verify/` (P15; file to be created TASK-W4-05) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] planned — `tests/verify/verify_closure.py` (create); not present on tip yet |
| Prior wave as-built row | `human_approved` | [ ] **BLOCKED** — INIT-GATEFLOW-010 W3 = **ground pass — pending human_approved** (PR [#150](https://github.com/drivestream-lab/gateflow/pull/150) @ `c4d4cdc` open; merge at `wave-signoff` only) |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W3.md` (outcome pass; §Contracts produced complete) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W4 |

**Gate verdict:** BLOCKED — prior wave W3 not `human_approved` in `docs/specification/as-built/implementation-status.md`. Do not invoke `/loop-spec` until human completes `wave-signoff` on PR #150 and marks W3 `human_approved`.

**Human action required:** Complete W3 Pass-2 closeout at checkpoint `wave-signoff`:
- Review exact head `c4d4cdc2a42ab443a16897a9dcb92e3ba0c05d8d` on PR #150
- Optional GF-01: run `.venv/bin/python -m tests.verify.verify_wave_closeout` with `dogfood: true`
- Mark as-built INIT-GATEFLOW-010 W3 = **human_approved**
- Merge PR #150 manually; record merge commit SHA
- Re-run `/pre-implement` for W4 after W3 merge lands on `develop`

**Board process note (read-only):** W4 ticket [#142](https://github.com/drivestream-lab/gateflow/issues/142) is **In Progress** while W3 sign-off is pending — orch moved card early; coding must wait on gate above. W3 ticket [#141](https://github.com/drivestream-lab/gateflow/issues/141) awaits Done at sign-off.

**Forge readiness (when seed / wave head absent):** not required — seed complete; W4 branch not opened (remote `feature/INIT-GATEFLOW-010-w4-implement-lane` exists from prior attempt but W4 coding blocked on W3 gate). Planned branch per plan: `feature/INIT-GATEFLOW-010-w4-closure` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-010-W3.md §Contracts produced`.
> For each contract this slice depends on, confirm the actual built interface
> matches what this wave's spec assumes.
> Scan `source_roots` to confirm — not against spec alone.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Closeout Done hop after ground-spec pass | `RunOrchestrator.process_job` (Enter-at `ground-spec`) | job with `ticket_id`, closeout `head_ref`, ground-spec pass handoff | STOP at `wave-signoff`; `forge_executed` at `wave-done-action` | Ground-Report-W3 | [x] yes — `test_closeout_walk_applies_done_then_stops_at_wave_signoff`; source on W3 tip (not yet on `develop` until PR #150 merge) |
| Forge merge prohibition | `ForgeActionService.apply_external_action`, `ForgeClient.enable_auto_merge` | pin/handoff forge action | reject/raise on merge | Ground-Report-W3 | [x] yes — `_FORBIDDEN_MERGE_ACTIONS`; unit guards green on W3 tip |
| LGTM label prohibition | `parse_node_forge`, `merge_pin_and_handoff_forge`, `apply_external_action` | pin `apply_labels` / handoff forge | stripped or ValidationError | Ground-Report-W3 | [x] yes — `test_apply_external_action_rejects_lgtm_apply_labels` |
| No auto-chain after wave-signoff | `PolicyEngine.evaluate_dispatch` | handoff `stage=wave-signoff` or `wave-complete`, `outcome=pass` | `PolicyDecisionType.STOP` | Ground-Report-W3 | [x] yes — `test_policy_wave_signoff_pass_stops_no_auto_chain`; W4 closure Enter-at is separate API (REQ-19) |
| Live verify W3 closeout slice | `tests/verify/verify_wave_closeout.py` | programme knobs | exit 0 under prereqs | Ground-Report-W3 | [x] yes — co-shipped; W4 extends with `verify_closure` per plan |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- W3 contracts verified on W3 branch tip; **`develop` lacks W3 merge** until PR #150 sign-off — W4 `/loop-spec` must cut from post-W3-merge `develop`.
- **`POST /api/v1/initiatives/closure/start`** — not present on `develop` (grep: no route module); W4 creates new HTTP surface (REQ-12).

---

### Must read

- [x] `AGENTS.md` — constitution pin `v0.5.0-rc.2`; forge skills; Pass-1/Pass-2 lane naming
- [x] MDC rules (domain-filtered — W4 touches HTTP API, pydantic, architecture, fail-fast, testing, logging):
  - [x] `http-api-conventions.mdc` — closure route shape, status codes (400/422/202)
  - [x] `pydantic-schemas.mdc` — closure request/response models (TASK-W4-01)
  - [x] `architecture.mdc` — business/infra layering for closure service + orchestrator enqueue
  - [x] `fail-fast.mdc` — Done-gate fail closed; partial failure hygiene (REQ-20)
  - [x] `testing-verify-flows.mdc` — co-ship `verify_closure`; unit vs live separation
  - [x] `logging-loguru.mdc` — partial failure recording (TASK-W4-04)
  - [x] `dependency-injection.mdc` — DI wiring for new routes/services
  - Skipped: `database-migrations.mdc` — no schema change planned for W4 closure route
- [x] ADRs (keyword-matched):
  - [x] ADR-010 — §7 initiative-closure intake authority (Accepted)
  - [x] ADR-009 — forge publish/mutate; no merge; purge-app walk (Accepted)
  - [x] ADR-005 — programme-token mutations for closure start (Accepted)
  - [x] ADR-001 — Postgres SSOT for run records (Accepted)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — REQ-12…15, REQ-17, REQ-18, REQ-20
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` W4
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/142 — TASK list (projected from WorkManifest):
  - [ ] TASK-W4-01 — implements REQ-12 — depends_on: [] — files: `src/api/v1`, `src/models`, `src/app.py` — exit proof: `make check && make test`
  - [ ] TASK-W4-02 — implements REQ-13 — depends_on: [TASK-W4-01] — files: closure validator/service — exit proof: `make test`
  - [ ] TASK-W4-03 — implements REQ-14, REQ-15 — depends_on: [TASK-W4-02] — files: board_service + orchestrator — exit proof: `make test`
  - [ ] TASK-W4-04 — implements REQ-20 — depends_on: [TASK-W4-03] — files: `run_orchestrator.py` — exit proof: `make test`
  - [ ] TASK-W4-05 — implements REQ-12, REQ-13, REQ-17 — depends_on: [TASK-W4-04] — files: `tests/verify/verify_closure.py` (create) — exit proof: live command
  - [ ] TASK-W4-06 — implements REQ-18 — depends_on: [TASK-W4-05] — files: `Feature-Readiness-INIT-GATEFLOW-010.md` (create) — exit proof: review
  - [ ] TASK-W4-07 — implements REQ-12–15,17,18,20 — depends_on: [TASK-W4-06] — files: as-built — exit proof: review

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR — closure Enter-at authority in ADR-010 §7; product REQs SSOT in spec
- [x] Plan TASK MDC notes and ADR notes for W4 reviewed — http-api, pydantic, architecture, fail-fast, testing-verify-flows cited on TASK rows
- [x] Every initiative ADR cited for W4 is **Accepted** in `docs/specification/adr/` (ADR-009, ADR-010, ADR-005, ADR-001)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` — W4 human_approved narrative (post-sign-off)
- [ ] `docs/specification/as-built/implementation-status.md` — W4 verification row (TASK-W4-07)
- [ ] `tests/README.md` — feature map row for `verify_closure` (TASK-W4-05)
- [ ] Unit verification — closure route 400/202, Done-gate 422, EPIC Done ordering, partial failure (TASK-W4-01…04)
- [ ] Live verification — co-ship `tests/verify/verify_closure.py` (human-run at `live-verify`)
- [ ] `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md` — proven vs deferred (TASK-W4-06)
- [ ] ADR — no supersede expected; ADR-010 §7 already Accepted

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live-verify scripts
- [ ] Assume W3 contracts on `develop` before PR #150 merge — cut W4 branch from post-W3-merge tip
- [ ] Dispatch `purge-initiative-artifacts-meta` during eng closure walk (REQ-15)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layering | `make check` |
| Unit | Closure route, Done-gate, EPIC Done ordering, partial failure, no meta purge | `make test` |
| Live verify | Closure Enter-at HTTP + Done-gate + purge walk smoke (human-run at `live-verify`) | `.venv/bin/python -m tests.verify.verify_closure` — co-ship in `/loop-spec` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 skill |

> P15 applies: unit-only for live verify **blocks** the gate at implementation time; contract resolved in plan §9.

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_closure` in local-compose sandbox
- [ ] Confirm 202 + `run_id` on valid binds; 400/422 per PRD table; Done-gate negatives; no meta purge
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-010-W4.md`
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-010
- Issue: [#142](https://github.com/drivestream-lab/gateflow/issues/142) (W4 — In Progress on board; gate blocked pending W3 sign-off)
- Spec path: `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_closure`
- ADRs in scope: ADR-010 §7, ADR-009, ADR-005, ADR-001
- Wave head: bound to `develop` — W4 feature branch opens in `/loop-spec` after W3 merge

---

### Checklist publish readiness (on `pass` — deferred)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — W3 prior wave not `human_approved` |
| Next | `wave-signoff` (`human-checkpoint`) — complete W3 PR #150 merge first |
| Forge (this hop) | **deferred** — `commit_workspace` applies on `pass` only; re-run after W3 gate clears |
| Later | After W3 sign-off + `/pre-implement` pass → `/loop-spec` → `wave-pr-action` |

Do not invoke `/loop-spec` or `/commit-workspace` for W4 coding until W3 `human_approved`.

---

### Merge order (if cross-module / cross-service)

1. **W3 sign-off** — merge PR #150 to `develop` (human only at `wave-signoff`)
2. **W4 branch** — cut `feature/INIT-GATEFLOW-010-w4-closure` from post-W3-merge `develop`
3. **W4 depends on W3 contracts** — Done hop, no-auto-chain policy, merge/lgtm guards consumed unchanged
4. **Closure walk** — EPIC Done before `purge-initiative-artifacts-app`; never `purge-initiative-artifacts-meta`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-010-W4.md
    digest: sha256:24db7da217515aa010afa86c7d132bcd4b2111d1222c702917d9a50cdb5110f8
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W4
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/142"
    ticket_id: "142"
    epic_issue: "https://github.com/drivestream-lab/gateflow/issues/137"
    prior_wave: W3
    prior_wave_status: pending_human_approved
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W3.md
    prior_wave_pr: "https://github.com/drivestream-lab/gateflow/pull/150"
    prior_wave_head_sha: "c4d4cdc2a42ab443a16897a9dcb92e3ba0c05d8d"
    workmanifest_contract: pass
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_closure"
    live_verify_script_planned: tests/verify/verify_closure.py
    p15_applicable: true
    tasks:
      - TASK-W4-01
      - TASK-W4-02
      - TASK-W4-03
      - TASK-W4-04
      - TASK-W4-05
      - TASK-W4-06
      - TASK-W4-07
    h1_prd_digest: "sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206"
    h2_scope_digest: "sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532"
    h3_map_revision: 1
    g1_meta_pr_head: "df0f5a5c09b6c4f951463bb42f277305310aaa80"
    branch_context: develop
    planned_coding_branch: feature/INIT-GATEFLOW-010-w4-closure
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```
