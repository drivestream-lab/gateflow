## Pre-implement — gateflow / W0 — Checkpoint status-check foundation

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W0.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W0 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W0 gate checks pass: PE sign-off complete, spec PR #159 merged with `spec-lgtm`, board seeded (#160/#161), WorkManifest contract clean, P15 live verify command resolved, H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `234f66a1b4d5e9d34522cb6bceb016c5672626a4` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED 2026-08-07; plan on `develop` @ `234f66a` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` on #159; Approve @ `c5047eaa…` (plan present); tip `ef6f8fd…` was format-only CI unblock (ancestor of merge); merge commit `234f66a…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W0 [#161](https://github.com/drivestream-lab/gateflow/issues/161) lists TASK-W0-01…05; W1–W9 [#162–#170](https://github.com/drivestream-lab/gateflow/issues/162); sub-issues of EPIC; `Board-Seed-INIT-GATEFLOW-011.md` B1–B8 PASS |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W0 TASK-W0-01…05 in plan §9 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_checkpoint_status` (FILE co-shipped in TASK-W0-05; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT; live digests match (spec `0edf9b72…`, feas `61cd10b2…`, TDD `aa68a3c6…`) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_checkpoint_status` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_checkpoint_status.py` (create in TASK-W0-05) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] N/A — W0 first wave of INIT-GATEFLOW-011 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0; gate is plan §0 PE sign-off |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-06 (TDD Accepted; PE package accept) |

**Gate verdict:** PASS — W0 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#161](https://github.com/drivestream-lab/gateflow/issues/161) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-011-w0-checkpoint-status` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> W0 is the first wave of INIT-GATEFLOW-011 — no `Ground-Report-INIT-GATEFLOW-011-W{-1}.md`.
> Dependencies are on **as-built** capabilities from prior INITs; scanned under `src/`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| ForgeClient PR fetch (labels + head SHA) | `ForgeClient.get_pull_request` | owner, repo, pr_number | `GithubPullRequestDocument` (title/body/state/labels/head/base) | as-built INIT-006/010; `src/infra_services/forge_client.py` | [x] yes — present; **no** reviews / check-runs / merged fields yet (W0 TASK-W0-01) |
| Meta PR intake shape precedent (not CAP-01) | `MetaPrIntakeService.accept` | meta_pr_url + expected_initiative_id | `MetaPrAcceptResult` (head SHA + labels only) | as-built ADR-010; `src/business_services/meta_pr_intake.py` | [x] yes — A-7 confirmed: does **not** evaluate `impact-map-lgtm`/reviews; CAP-01 sits beside it |
| Pin + delivery-contract load | `WorkflowEngine.load_pin` / `get_node` | pin path / node id | resolved workflow node + raw contract mapping | `src/business_services/workflow_engine.py`; `prayog-skills/delivery-contract.yaml` | [x] yes — `DEFAULT_CONTRACT_PATH` = `prayog-skills/delivery-contract.yaml`; `github.labels` + `review_roles` for all six checkpoint ids present |
| Programme-token control-plane auth | `verify_programme_service_token` + `public_paths` | Bearer programme token | void / 401 | ADR-005; `src/api/v1/programme_token.py`; `src/app.py` | [x] yes — pattern live for waves/runs/board/metrics; **`/api/v1/checkpoints` absent from `public_paths` today** (W0 TASK-W0-04) |
| Checkpoint status HTTP surface | `GET /api/v1/checkpoints/status` | checkpoint id + PR refs | verdict + itemized misses | product spec Appendix A | [ ] NO — route module missing (`checkpoints_routes.py`); W0 deliverable |
| ForgeClient list_reviews / list_check_runs / merge fields | CAP-01 evidence path | org/repo/PR | reviews, check-runs, merge state | product A-6 / Q-3 | [ ] NO — methods absent on `ForgeClient`; W0 TASK-W0-01 |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W0 — gaps above are **in-scope W0 deliverables**, not missing external contracts.
- W1+ will consume W0 Ground Report §Contracts produced after Pass-2 closeout (persistence + history compose on CAP-01 evaluate).

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify command pointers
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/architecture.mdc` — layered `api` → `business_services` → infra; JWT vs programme mounts
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET query params; no write bodies for CAP-01
  - [x] `.cursor/rules/pydantic-schemas.mdc` — checkpoint DTOs in `src/models/` only; enums for verdict vocabulary
  - [x] `.cursor/rules/fail-fast.mdc` — GitHub down → `could_not_verify`; no silent pass
  - [x] `.cursor/rules/infra-services.mdc` — ForgeClient as infra HTTP client; `@inject` + lifecycle
  - [x] `.cursor/rules/dependency-injection.mdc` — register `CheckpointEvidenceService` in BusinessServicesModule + `_BUSINESS_SERVICE_TYPES`
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `tests/verify/verify_checkpoint_status.py`; feature-map in `tests/README.md`
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built row (TASK-W0-05)
  - [ ] `.cursor/rules/repository-pattern.mdc` — skipped (W0: no persistence / no ORM)
  - [ ] `.cursor/rules/database-migrations.mdc` — skipped (W0: no schema)
  - [ ] `.cursor/rules/logging-loguru.mdc` — skipped beyond inherited service logger (no new observability surface)
- [x] ADRs (keyword-matched — checkpoint read, ForgeClient, programme token, pin SSOT):
  - [x] ADR-001 — runtime + durable store (**Accepted**; W0 does not persist — cite only)
  - [x] ADR-003 — ForgeClient in infra; evidence orchestration in business (**Accepted**)
  - [x] ADR-004 — programme config authority (**Accepted**; pin consume-only)
  - [x] ADR-005 — programme-token control-plane reads/writes zone; `public_paths` allowlist (**Accepted**)
  - [x] ADR-009 — pin `forge:` mutate authority; CAP-01 must not call write Forge actions (**Accepted**)
  - [x] ADR-010 — lane intake authority; MetaPrIntake is shape precedent only (**Accepted**)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — W0 REQs REQ-01, REQ-02, REQ-04, REQ-05 (+ REQ-28)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/161 — TASK list (projected from WorkManifest):
  - [ ] TASK-W0-01 — implements REQ-02 — depends_on: [] — files: `forge_client.py`, `meta_pr_models.py`, `test_forge_client.py` — exit proof: `make check && make test`
  - [ ] TASK-W0-02 — implements REQ-02 — depends_on: [TASK-W0-01] — files: `workflow_engine.py`, `checkpoint_models.py`, `test_checkpoint_vocab.py` — exit proof: `make test`
  - [ ] TASK-W0-03 — implements REQ-01, REQ-04, REQ-05 — depends_on: [TASK-W0-01, TASK-W0-02] — files: `checkpoint_evidence_service.py`, DI modules, `test_checkpoint_evidence.py` — exit proof: `make test`
  - [ ] TASK-W0-04 — implements REQ-01, REQ-05, REQ-28 — depends_on: [TASK-W0-03] — files: `checkpoints_routes.py`, `api/v1/__init__.py`, `app.py`, `test_checkpoints_api.py` — exit proof: `make test`
  - [ ] TASK-W0-05 — implements REQ-01, REQ-05, REQ-28 — depends_on: [TASK-W0-04] — files: `verify_checkpoint_status.py`, `tests/README.md`, `implementation-status.md` — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR — GET-only CAP-01; zero mutate from new path (ADR-009/005)
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed (architecture, http-api-conventions, pydantic-schemas, fail-fast; ADR-001/003/005/009)
- [x] Every initiative ADR cited for W0 is **Accepted** in `docs/specification/adr/` (zero NEW-ADR from TDD)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` as-built baseline after W0 exit (checkpoint status live; no persistence yet)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W0 verification row
- [ ] `tests/README.md` — feature-map row for `verify_checkpoint_status`
- [ ] Unit verification scope — `test_forge_client`, `test_checkpoint_vocab`, `test_checkpoint_evidence`, `test_checkpoints_api` (REQ-01/02/04/05/28)
- [ ] Live verification — co-shipped `tests/verify/verify_checkpoint_status.py` (human-run at `wave-acceptance`)
- [ ] ADR — no supersede required (ADR_REQUIRED=0)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from any CAP-01 path (REQ-05 / REQ-28)
- [ ] Persist check records in W0 (deferred to W1 / REQ-06)

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | ForgeClient read extension; pin vocabulary for six checkpoints; evaluate() itemized misses + no-mutate; GET status + non-GET rejected | `make test` |
| Live verify | Product behaviour on running stack (human-run at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_checkpoint_status` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate.
> Agent implements the script in `/loop-spec`; does **not** run it as success.
> Policy: live-smoke-policy (P15 applicable for new GET surface).

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_checkpoint_status` (API+worker up; programme token; `tests/config.yaml`; fixture PR)
- [ ] Experience / inspect CAP-01 GET responses (itemized misses; no writes)
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: #161 — https://github.com/drivestream-lab/gateflow/issues/161
- EPIC: #160 — https://github.com/drivestream-lab/gateflow/issues/160
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_checkpoint_status`
- ADRs in scope: ADR-001, ADR-003, ADR-004, ADR-005, ADR-009, ADR-010
- Wave head: bound by Forge/human context — `develop` (planned coding branch: `feature/INIT-GATEFLOW-011-w0-checkpoint-status`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W0 gates satisfied; WorkManifest clean; P15 live command resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W0.md` to bound `head_ref` (`develop` or wave branch once cut) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W0 is single-repo CAP-01 foundation (ForgeClient read + evidence service + GET). W1 depends on W0 evaluate() before persistence/history.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W0.md
    digest: sha256:2e3766b54ef63968d8d774727571a8e93633dd5c6c57adf2e0ec6a10fe5befa5
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W0
    ticket_id: 161
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/161
    epic_ticket_id: 160
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 234f66a1b4d5e9d34522cb6bceb016c5672626a4
    wave_branch_planned: feature/INIT-GATEFLOW-011-w0-checkpoint-status
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
    implements_reqs:
      - REQ-01
      - REQ-02
      - REQ-04
      - REQ-05
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_checkpoint_status
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: Todo
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/159
    spec_merge_commit: 234f66a1b4d5e9d34522cb6bceb016c5672626a4
    workmanifest_contract: pass
    p15_applicable: true
    h1_prd_digest: sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd
    h2_repo_scope_digest: sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d
    h3_impact_map_revision: "1"
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```
