## Pre-implement — gateflow / W7 — Closeout readout + drift safeguard

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W7.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W7 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W7 gate checks pass: prior W6 `human_approved` (tip `0b0f144` `wave-accepted`; PR #178 merged `275c167`) with Ground-Report-W6 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W7 #168 with TASK-W7-01…03, Status In Progress); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `275c167` (after W6 merge) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w7-closeout-drift` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `275c167` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels include `spec-lgtm`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W7 [#168](https://github.com/drivestream-lab/gateflow/issues/168) (OPEN, title `[INIT-GATEFLOW-011 W7] Closeout readout + drift safeguard`, programme Status **In Progress**); TASK-W7-01…03 in body; `Board-Seed-INIT-GATEFLOW-011.md` lists W7 #168 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W7 TASK-W7-01…03 in plan §9 (lines 1544–1595); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` (FILE co-shipped in TASK-W7-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT (plan is walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop`; product file digest `sha256:0edf9b72…` matches plan `source_spec_digest` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_closeout_readout.py` (create in TASK-W7-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W6 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W6 row); tip `0b0f144` `wave-accepted`; PR #178 merged `275c167` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W6.md` (2026-08-07; outcome `pass`; §Contracts produced complete for W7+) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W7 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W7 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Manifest note:** WorkManifest W7 `depends_on: [W1, W2]` (data dependency on CAP-01/02 `checkpoint_check` baseline for REQ-19 + Gateflow-owned initiative/run identity). Programme prior-wave gate is still W6 `human_approved` (sequential delivery). Ground-Report-W6 supplies nesting path (`…/waves/{wave_id}/implementation` sibling → add `…/closeout`). Ground-Report-W1 supplies persistence/history contracts for drift baseline.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch: `feature/INIT-GATEFLOW-011-w7-closeout-drift` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Reports)

> Nesting / implement-lane from Ground-Report-W6.
> Checkpoint baseline from Ground-Report-W1.
> Initiative / run identity from Ground-Report-W2.
> Confirm against `src/`.

W7 delivers CAP-07 closeout readout + drift safeguard:  
`GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/closeout`  
lists what closeout added after `learning-extract` / `ground-spec` (REQ-18);
compares wave-acceptance-time head SHA (persisted REQ-06 `checkpoint_check`) vs
closeout-time PR head — drift flag or explicit `unknown — no baseline recorded`
(REQ-19); drift is **advisory only** — never blocks/fails closeout mechanics
(REQ-20); GET-only (REQ-28).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Wave path nesting + programme token | `GET …/waves/{wave_id}/implementation` | path + org/repo | readout JSON | Ground-Report-W6 | [x] yes — W7 nests sibling `…/closeout` under same router |
| Implement-lane run selection | `ImplementationReadoutService._select_implement_run` | runs + wave_id | run or none | Ground-Report-W6 | [x] yes — reuse pattern (prefer no `meta_pr_url`); **do not redefine** as CAP-06 status |
| Draft wave PR number | `ImplementationReadoutService._draft_pr_number` / run.`pr_number` | run + events | int or null | Ground-Report-W6 | [x] yes — closeout-time PR head needs resolvable PR |
| Checkpoint persistence (REQ-06) | `CheckpointEvidenceService._persist_check` | evaluate result | `checkpoint_check` event with `checked_sha` / `checked_at` / wave_id | Ground-Report-W1 | [x] yes — drift baseline source |
| Checkpoint history (REQ-07) | `CheckpointEvidenceService.list_history` | PR ref + filters | historical records | Ground-Report-W1 | [x] yes — may load wave-acceptance baseline without live verdict substitution |
| Composed checkpoint evaluate | `evaluate_composed(initiative_id, wave_id, checkpoint_id)` | initiative + wave + checkpoint | live verdict or 404 | Ground-Report-W1 | [x] yes present — W7 drift must **not** treat live CAP-01 as the acceptance baseline; use persisted historical `checkpoint_check` for `wave-acceptance` |
| Initiative identity + 404 | GET `/initiatives/{id}` | initiative id | readout or 404 | Ground-Report-W2 | [x] yes — unknown initiative → 404 |
| Learning store (INIT-007) | `LearningIngestService` / learning repos | initiative/wave filters | learning records | as-built INIT-007 | [x] yes present — prefer Gateflow-owned learning rows for REQ-18 itemization; fail closed / empty list when none |
| Wave map / CAP-05 | `WaveMapService` | — | — | Ground-Report-W4 | [x] yes present — **W7 does not consume** for CAP-07 fields; must not regress |
| Spec readout / CAP-04 | `SpecReadoutService` | — | — | Ground-Report-W5 | [x] yes present — **W7 does not consume**; must not regress |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W7 on missing Ground Reports (W1 + W6 grounded; W2 identity live).
- **Field-source design risk for `/loop-spec`:**
  - **REQ-18** “lessons captured / learning-store records / ground additions” — compose from Gateflow-owned evidence (learning table rows; run stages/events for `learning-extract` / `ground-spec`; handoff artifact paths). Do **not** scrape ambient workspace report files as SSOT.
  - **REQ-19** baseline = persisted `checkpoint_check` correlated to this wave at/near `wave-acceptance` (historical), compared to current PR head SHA via Forge **read** APIs only. If no baseline → explicit `unknown — no baseline recorded` (never silent clean). If SHAs differ → flag product-code-changed-after-acceptance wording per product failure mode.
  - **REQ-20** — expose drift as advisory fields only; no Forge writes; do not fail the GET when drifted; do not call `update_board_status` / merge / labels.
- **File-scope risk:** WorkManifest TASK-W7-01 does **not** list `src/di/modules/business_services_module.py`, but a new `@inject` service needs `binder.bind(CloseoutReadoutService, scope=singleton)`. Same glue pattern as W4–W6 — include DI bind in the TASK-W7-01 change set and record under observed files in Wave-Execution (do not invent TASK ids).

---

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board, verify pointers
- [x] MDC rules (domain-filtered):
  - [x] `.cursor/rules/architecture.mdc` — `api` → `business_services` → repo; new service + route + models
  - [x] `.cursor/rules/dependency-injection.mdc` — `@inject` + singleton bind + `get_*_service`
  - [x] `.cursor/rules/repository-pattern.mdc` — runs/events/learning via repositories (Pydantic); no ORM in service
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `closeout_readout_models.py` in `src/models/` only; enums with `Type` suffix; `extra="forbid"`
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET path `/initiatives/{initiative_id}/waves/{wave_id}/closeout`; query for org/repo; no write body
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative → 404; no baseline → explicit unknown string (REQ-19), not silent omit
  - [x] `.cursor/rules/strong-typing.mdc` — drift status enum typed; no bare magic strings for closed vocabularies
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `verify_wave_closeout_readout`; unit owns derivation; live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built W7 row
  - [x] `.cursor/rules/logging-loguru.mdc` — kwargs (`initiative_id`, `wave_id`, drift status, baseline sha)
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A (no new table expected; compose from existing checkpoint/learning/run data)
- [x] ADRs (keyword-matched — closeout readout, checkpoint baseline, programme token, no mutate):
  - [x] ADR-001 — durable store (**Accepted**; read existing runs/events/learning only)
  - [x] ADR-003 — slot/layer ownership (**Accepted**; Forge **reads** for PR head if needed)
  - [x] ADR-005 — programme-token reads (**Accepted**)
  - [x] ADR-009 — no mutate from CAP-07 (**Accepted**; REQ-28 / REQ-20)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-18, REQ-19, REQ-20 (+ REQ-28); route `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/closeout`
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W7 (lines 496–550, 1535–1626)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/168 — TASK list (projection only):
  - [ ] TASK-W7-01 — implements REQ-18, REQ-19, REQ-20 — depends_on: [] — files: `src/business_services/closeout_readout_service.py` (create), `src/models/closeout_readout_models.py` (create), `tests/unit/test_closeout_readout_service.py` (create) — exit proof: `make test` exit 0 — itemized additions; drift or unknown baseline; advisory only
  - [ ] TASK-W7-02 — implements REQ-18, REQ-19, REQ-20, REQ-28 — depends_on: [TASK-W7-01] — files: `src/api/v1/initiatives_routes.py` (modify), `tests/unit/test_initiatives_read_api.py` (modify) — exit proof: `make test` exit 0 — GET `.../closeout` GET-only
  - [ ] TASK-W7-03 — implements REQ-18, REQ-19, REQ-28 — depends_on: [TASK-W7-02] — files: `tests/verify/verify_wave_closeout_readout.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs — GET-only CAP-07; advisory drift (REQ-20); zero Forge writes (ADR-009 / REQ-28)
- [x] Plan TASK MDC notes and ADR notes for W7 reviewed
- [x] Every cited ADR is **Accepted** in `docs/specification/adr/` (zero NEW-ADR)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — as-built baseline after W7 (closeout readout live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W7 verification row (REQ-18 / REQ-19 / REQ-20 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_wave_closeout_readout`
- [ ] Unit — `test_closeout_readout_service`: itemized learning/ground additions; drift when SHAs differ; `unknown — no baseline recorded` when missing; advisory fields do not imply mutate; `test_initiatives_read_api`: GET `.../closeout` 200 shape, 401, 404 unknown initiative, 405 on non-GET
- [ ] Live — co-shipped `tests/verify/verify_wave_closeout_readout.py` (human at `wave-acceptance`)
- [ ] ADR — no supersede required

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without superseding it
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume prior contracts without Ground Report confirmation
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Introduce a new store / ORM table / Alembic revision unless product explicitly requires it
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from CAP-07 (REQ-28 / REQ-20)
- [ ] Add non-GET product routes for the closeout readout
- [ ] Treat missing baseline as clean / no-drift (REQ-19 failure mode)
- [ ] Block or fail closeout pin mechanics based on drift flag (REQ-20) — readout is advisory
- [ ] Substitute live CAP-01 evaluate for the historical wave-acceptance baseline
- [ ] Regress W1 checkpoints, W4 waves, W5 spec, or W6 implementation routes
- [ ] Mutate approved WorkManifest intent (exit criteria / deps / live contract)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Closeout additions + drift/unknown baseline + advisory-only; GET-only / 401 / 404 | `make test` |
| Live verify | Product behaviour on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` |
| Ground check | Assigned REQs + boundaries | N/A — `/ground-spec` Pass-2 pin skill |

> P15 applicable — new GET surface: `/api/v1/initiatives/{initiative_id}/waves/{wave_id}/closeout`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` (API+worker up; programme token; `tests/config.yaml`)
- [ ] Inspect closeout readout — additions list + drift/unknown baseline; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: [#168](https://github.com/drivestream-lab/gateflow/issues/168)
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_closeout_readout`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `275c167`; planned `feature/INIT-GATEFLOW-011-w7-closeout-drift`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W7 gates satisfied; ready for coding after checklist publish |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W7.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo gateflow CAP-07 slice; depends on prior waves already on `develop` (W1 checkpoint baseline; W2 identity; W6 nesting sibling).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W7.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W7
    ticket_id: "168"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/168
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 275c167e414f5e040cda9654fe10004e8fa8c5bd
    wave_branch_planned: feature/INIT-GATEFLOW-011-w7-closeout-drift
    prior_wave: W6
    prior_wave_approved: true
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W6.md
    manifest_depends_on: [W1, W2]
    tasks:
      - TASK-W7-01
      - TASK-W7-02
      - TASK-W7-03
    implements:
      - REQ-18
      - REQ-19
      - REQ-20
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout_readout
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    p15_applicable: true
    live_script_planned: tests/verify/verify_wave_closeout_readout.py
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    # Prefer publishing checklist onto develop tip or cut feature branch first in /commit-workspace /
    # /loop-spec per programme practice (W6 published checklist with code on feature branch).
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W7.md
```
