## Pre-implement — gateflow / W8 — Merge confirm + completion eligibility

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W8.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W8 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W8 gate checks pass: prior W7 `human_approved` (tip `6bd8336` `wave-accepted`; PR #179 merged `ee1fd89`) with Ground-Report-W7 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W8 #169 with TASK-W8-01…04); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `ee1fd89` (after W7 merge) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w8-merge-completion` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `ee1fd89` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels include `spec-lgtm`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W8 [#169](https://github.com/drivestream-lab/gateflow/issues/169) (OPEN, title `[INIT-GATEFLOW-011 W8] Merge confirm + completion eligibility`, programme Status **Todo**); TASK-W8-01…04 in body; `Board-Seed-INIT-GATEFLOW-011.md` lists W8 #169 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W8 TASK-W8-01…04 in plan §9 (lines 1637–1706); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_merge_and_completion` (FILE co-shipped in TASK-W8-04; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT (plan is walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop`; product file digest `sha256:0edf9b72…` matches plan `source_spec_digest` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_merge_and_completion` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_merge_and_completion.py` (create in TASK-W8-04) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W7 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W7 row); tip `6bd8336` `wave-accepted`; PR #179 merged `ee1fd89` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W7.md` (2026-08-07; outcome `pass`; §Contracts produced complete for W8+) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W8 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W8 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Manifest note:** WorkManifest W8 `depends_on: [W1, W4]` (data dependency on CAP-01 composed `wave-signoff` evidence for REQ-21 + CAP-05 wave-map rollup for REQ-23/24). Programme prior-wave gate is still W7 `human_approved` (sequential delivery). Ground-Report-W7 supplies nesting guidance (initiative tree; do not regress `…/closeout`); Ground-Report-W1 / W4 supply CAP-01 / CAP-05 contracts W8 reuses.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch: `feature/INIT-GATEFLOW-011-w8-merge-completion` (opened in `/loop-spec`, not here). Board #169 programme Status is **Todo** — Forge/human may move to In Progress before or with `/loop-spec` (read-only here).

---

### Contracts consumed (from prior Ground Reports)

> Nesting / no-regress from Ground-Report-W7.
> CAP-01 merge-confirm evidence from Ground-Report-W1.
> CAP-05 rollup from Ground-Report-W4.
> Confirm against `src/`.

W8 delivers CAP-08 merge confirm + CAP-09 completion eligibility:  
`GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/merge`  
reuses CAP-01 evidence rules against checkpoint `wave-signoff` (REQ-21) — merged
state + merge commit SHA, or itemized missing items; after confirmed merge, if
next wave is unblocked (predecessor Done), surfaces next-wave nudge (REQ-22).  
`GET /api/v1/initiatives/{initiative_id}/completion`  
reports ready-to-close **iff** every wave ticket is board Done (REQ-23); empty /
unresolvable → distinct "no waves found"; pure rollup of CAP-05 wave-map data —
no second board query with different logic (REQ-24); GET-only (REQ-28).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Composed CAP-01 evaluate | `CheckpointEvidenceService.evaluate_composed` | initiative + wave + checkpoint_id | live `CheckpointStatusResult` or 404 | Ground-Report-W1 | [x] yes — W8 merge confirm uses checkpoint `wave-signoff` (review/merge class); do **not** invent parallel evidence rules |
| Live CAP-01 evaluate + Forge reads | `CheckpointEvidenceService.evaluate` / `ForgeClient` PR reads | PR ref + checkpoint vocab | verdict + missing items + checked_sha | Ground-Report-W0/W1 | [x] yes — merge SHA / merged state via existing Forge PR document reads |
| Checkpoint persistence side-effect | `_persist_check` on evaluate | evaluate result | `checkpoint_check` event | Ground-Report-W1 | [x] yes — composed merge-confirm evaluate may persist; readout path remains GET-only to clients |
| Wave map compose | `WaveMapService.get_wave_map` | initiative + org/repo | `WaveMapResult` waves[] | Ground-Report-W4 | [x] yes — REQ-24: completion **must reuse** this derivation (status Done / ready / blocked / active); no parallel status store |
| Wave status derivation | `WaveMapService._derive_status` | board + runs + predecessor | `WaveMapStatusType` + reason | Ground-Report-W4 | [x] yes — nudge (REQ-22) and waiting-on-wave (REQ-23) must use same rules |
| Initiative identity + 404 | GET `/initiatives/{id}` | initiative id | readout or 404 | Ground-Report-W2 | [x] yes — unknown initiative → 404 |
| Initiative nesting + programme token | `initiatives_routes` | path + org/repo | JSON | Ground-Report-W6/W7 | [x] yes — add `…/waves/{wave_id}/merge` and `…/completion` under same router |
| Closeout GET (must not regress) | `GET …/waves/{wave_id}/closeout` | — | — | Ground-Report-W7 | [x] yes present — **W8 does not consume** for CAP-08/09 fields; must not regress |
| Implementation / spec / waves GETs | prior routes | — | — | Ground-Report-W4–W6 | [x] yes present — **must not regress** |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W8 on missing Ground Reports (W1 + W4 + W7 grounded).
- **Field-source design risk for `/loop-spec`:**
  - **REQ-21** — call CAP-01 against `wave-signoff` for the wave’s Draft/merged PR (composed initiative+wave or resolved PR). Report merged + merge commit SHA when satisfied, else itemized missing items (e.g. not yet merged). Prefer `evaluate` / `evaluate_composed` — **do not** fork evidence vocabulary.
  - **REQ-22** — after merge confirmed, if CAP-05 shows next wave `ready-to-start` (predecessor Done), include plain nudge string (e.g. wave W{n+1} unblocked). No board mutate.
  - **REQ-23 / REQ-24** — completion service must call / reuse `WaveMapService.get_wave_map` (or shared derivation helper extracted without changing status rules). Ready-to-close iff all waves `done`; else list waiting-on waves; empty Feature set → distinct no-waves-found (never ready-to-close).
  - **REQ-28** — GET-only; Forge/board **reads** only; no `apply_labels` / merge / `update_board_status`.
- **File-scope risk:** WorkManifest TASK-W8-01/02 do **not** list `src/di/modules/business_services_module.py`, but new `@inject` services need `binder.bind(MergeReadoutService)` and `binder.bind(CompletionReadoutService)`. Same glue as W4–W7 — include DI binds in the TASK-01/02 change sets and record under observed files in Wave-Execution (do not invent TASK ids).
- **Parallel TASK-W8-01 ∥ TASK-W8-02:** both `depends_on: []` — either order or parallel OK before TASK-W8-03.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify pointers
- [x] MDC rules (domain-filtered):
  - [x] `.cursor/rules/architecture.mdc` — new services + routes + models
  - [x] `.cursor/rules/dependency-injection.mdc` — `@inject` + singleton bind + `get_*_service`
  - [x] `.cursor/rules/repository-pattern.mdc` — no ORM in services; reuse repos via CAP-01 / CAP-05 services
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `merge_readout_models.py` / `completion_readout_models.py` in `src/models/` only; enums with `Type` suffix
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET `…/merge` and `…/completion`; query org/repo; no write body
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative → 404; empty waves → distinct no-waves-found (REQ-23)
  - [x] `.cursor/rules/strong-typing.mdc` — merged/ready-to-close enums typed
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `verify_merge_and_completion`; unit owns derivation
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built W8 row
  - [x] `.cursor/rules/logging-loguru.mdc` — kwargs (`initiative_id`, `wave_id`, merge verdict, completion state)
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A (compose from existing CAP-01 / CAP-05)
- [x] ADRs (keyword-matched — merge confirm, completion rollup, programme token, no mutate):
  - [x] ADR-001 — durable store (**Accepted**; read runs/board via existing services)
  - [x] ADR-003 — slot/layer ownership (**Accepted**; Forge **reads** for merge evidence)
  - [x] ADR-005 — programme-token reads (**Accepted**)
  - [x] ADR-009 — no mutate from CAP-08/09 (**Accepted**; REQ-28)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-21, REQ-22, REQ-23, REQ-24 (+ REQ-28); routes `GET …/waves/{wave_id}/merge`, `GET …/completion`
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W8 (lines 1628–1739)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/169 — TASK list (projection only):
  - [ ] TASK-W8-01 — implements REQ-21, REQ-22 — depends_on: [] — files: `src/business_services/merge_readout_service.py` (create), `src/models/merge_readout_models.py` (create), `tests/unit/test_merge_readout_service.py` (create) — exit proof: `make test` — Merged/not-merged + misses; nudge when next wave unblocked
  - [ ] TASK-W8-02 — implements REQ-23, REQ-24 — depends_on: [] — files: `src/business_services/completion_readout_service.py` (create), `src/models/completion_readout_models.py` (create), `tests/unit/test_completion_readout_service.py` (create) — exit proof: `make test` — Ready-to-close iff all Done; empty → no waves found; reuses wave-map logic
  - [ ] TASK-W8-03 — implements REQ-21, REQ-22, REQ-23, REQ-24, REQ-28 — depends_on: [TASK-W8-01, TASK-W8-02] — files: `src/api/v1/initiatives_routes.py` (modify), `tests/unit/test_initiatives_read_api.py` (modify) — exit proof: `make test` — GET `…/merge` and `…/completion` GET-only
  - [ ] TASK-W8-04 — implements REQ-21, REQ-22, REQ-23, REQ-28 — depends_on: [TASK-W8-03] — files: `tests/verify/verify_merge_and_completion.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs — GET-only CAP-08/09; CAP-01 reuse; CAP-05 rollup; zero Forge writes (ADR-009 / REQ-28)
- [x] Plan TASK MDC notes and ADR notes for W8 reviewed
- [x] Every cited ADR is **Accepted** in `docs/specification/adr/` (zero NEW-ADR)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — as-built baseline after W8 (merge + completion live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W8 verification matrix (REQ-21…24 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_merge_and_completion`
- [ ] Unit — `test_merge_readout_service`: merged/not-merged + missing items; nudge when next wave ready; `test_completion_readout_service`: ready-to-close / waiting-on / no-waves-found; reuses wave-map; `test_initiatives_read_api`: GET merge + completion 200/401/404/405
- [ ] Live — co-shipped `tests/verify/verify_merge_and_completion.py` (human at `wave-acceptance`)
- [ ] ADR — no supersede required

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without superseding it
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume prior contracts without Ground Report confirmation
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Introduce a new store / ORM table / Alembic revision unless product explicitly requires it
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from CAP-08/09 (REQ-28)
- [ ] Add non-GET product routes for merge or completion
- [ ] Invent a second wave-status algorithm distinct from CAP-05 (REQ-24)
- [ ] Fork CAP-01 evidence vocabulary for `wave-signoff` (REQ-21)
- [ ] Treat CAP-07 advisory drift as a merge gate (Ground-Report-W7)
- [ ] Regress W1 checkpoints, W4 waves, W5–W7 readout routes
- [ ] Mutate approved WorkManifest intent (exit criteria / deps / live contract)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Merge confirm + nudge; completion rollup; GET-only / 401 / 404 | `make test` |
| Live verify | Product behaviour on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_merge_and_completion` |
| Ground check | Assigned REQs + boundaries | N/A — `/ground-spec` Pass-2 pin skill |

> P15 applicable — new GET surfaces: `/api/v1/initiatives/{initiative_id}/waves/{wave_id}/merge` and `/api/v1/initiatives/{initiative_id}/completion`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_merge_and_completion` (API+worker up; programme token; `tests/config.yaml`)
- [ ] Inspect merge + completion readouts — CAP-01 / CAP-05 reuse; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: [#169](https://github.com/drivestream-lab/gateflow/issues/169) (EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160))
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_merge_and_completion`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `ee1fd89`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gate verdict PASS; WorkManifest clean; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W8.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo slice. TASK-W8-01 ∥ TASK-W8-02 (independent), then TASK-W8-03 → TASK-W8-04.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W8.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W8
    ticket_id: "169"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/169
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: ee1fd89935a991f30df469c696ed3ae57dc13c8b
    wave_branch_planned: feature/INIT-GATEFLOW-011-w8-merge-completion
    prior_wave: W7
    prior_wave_approved: true
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W7.md
    manifest_depends_on: [W1, W4]
    tasks:
      - TASK-W8-01
      - TASK-W8-02
      - TASK-W8-03
      - TASK-W8-04
    implements:
      - REQ-21
      - REQ-22
      - REQ-23
      - REQ-24
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_merge_and_completion
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    p15_applicable: true
    live_script_planned: tests/verify/verify_merge_and_completion.py
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    # Prefer publishing checklist onto develop tip or cut feature branch first in /commit-workspace /
    # /loop-spec per programme practice (W7 published checklist with code on feature branch).
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W8.md
```
