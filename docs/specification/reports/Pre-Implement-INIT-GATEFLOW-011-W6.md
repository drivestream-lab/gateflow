## Pre-implement — gateflow / W6 — Wave implementation progress

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W6.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W6 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W6 gate checks pass: prior W5 `human_approved` (tip `069989e` `wave-accepted`; PR #177 merged `0d4c76e`) with Ground-Report-W5 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W6 #167 with TASK-W6-01…03, Status In Progress); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `0d4c76e` (after W5 merge) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w6-implementation-readout` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `0d4c76e` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels include `spec-lgtm`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W6 [#167](https://github.com/drivestream-lab/gateflow/issues/167) (OPEN, title `[INIT-GATEFLOW-011 W6] Wave implementation progress`, programme Status **In Progress**); TASK-W6-01…03 in body; `Board-Seed-INIT-GATEFLOW-011.md` lists W6 #167 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W6 TASK-W6-01…03 in plan §9 (lines 1451–1502); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_wave_implementation` (FILE co-shipped in TASK-W6-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT (plan is walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop`; product file digest `sha256:0edf9b72…` matches plan `source_spec_digest` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_implementation` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_implementation.py` (create in TASK-W6-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W5 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W5 row); tip `069989e` `wave-accepted`; PR #177 merged `0d4c76e` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W5.md` (2026-08-07; outcome `pass`; §Contracts produced complete for W6+) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W6 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W6 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Manifest note:** WorkManifest W6 `depends_on: [W4]` (path/data dependency on CAP-05 wave ids + `GET …/waves` nesting). Programme prior-wave gate is still W5 `human_approved` (sequential delivery). Ground-Report-W4 supplies `wave_id` vocabulary + parent route; Ground-Report-W5 supplies sibling nesting precedent (`…/spec` must not regress) and confirms GET-only CAP pattern.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch: `feature/INIT-GATEFLOW-011-w6-implementation-readout` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Reports)

> Primary wave identity / nesting from Ground-Report-W4.
> Initiative / run / PR fields from Ground-Report-W2 / W3.
> Nesting sibling + GET-only CAP pattern from Ground-Report-W5.
> Confirm against `src/`.

W6 delivers CAP-06 wave implementation progress:  
`GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/implementation`  
returns task-by-task progress from the run timeline and Draft PR link when
`wave-pr-action` has succeeded (REQ-16); on task failure or run stop
(`needs-input`), names which task and why (REQ-17); GET-only (REQ-28).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Wave id vocabulary + map rows | `WaveMapService.get_wave_map` / `WaveMapItem.wave_id` | initiative id + org/repo | `WaveMapResult` (`waves[]`) | Ground-Report-W4 | [x] yes — path `{wave_id}` must match W4 tokens (`W\d+`); unknown wave → fail closed (404 or explicit not-found), not invent rows |
| GET wave map nesting parent | `GET /api/v1/initiatives/{id}/waves` | path + org/repo + programme token | `WaveMapResult` JSON | Ground-Report-W4 | [x] yes — W6 nests `…/waves/{wave_id}/implementation` under same router |
| Wave status derivation (present) | `WaveMapService._derive_status` | board + run + predecessor | `WaveMapStatusType` | Ground-Report-W4 | [x] yes present — **W6 does not redefine** CAP-05 status rules; may *read* active run for the named wave |
| Initiative identity + 404 unknown | `InitiativeReadoutService` / GET `/initiatives/{id}` | `initiative_id`, org, repo | readout or 404 | Ground-Report-W2 / W3 | [x] yes — unknown initiative → 404 consistently |
| Run fields (PR, node, handoff, wave_id) | `RunRepository` / run models | initiative / wave filters | `pr_number`, `workflow_node`, `handoff_path`, `wave_id`, status | Ground-Report-W2; as-built | [x] yes — Draft PR + timeline + stop reason from run + events/handoff (read-only) |
| GET nesting sibling (spec) | `GET /initiatives/{id}/spec` | — | `SpecReadoutResult` | Ground-Report-W5 | [x] yes present — **W6 does not consume** CAP-04 fields; **must not regress** `…/spec` |
| Spec-lane vs implement-lane run selection | `SpecReadoutService._select_spec_run` | — | — | Ground-Report-W5 | [x] yes present — **W6 must not** confuse meta-lane runs with implement-lane wave progress |
| Programme-token + public_paths | `verify_programme_service_token` | Bearer | void / 401 | ADR-005; Ground-Report-W4/W5 | [x] yes — `/api/v1/initiatives` already on `public_paths` |
| Business service + DI precedent | `WaveMapService` / `SpecReadoutService` | `@inject` + `get_*_service` | Pydantic in/out | Ground-Report-W0/W4/W5 | [x] yes — W6 `ImplementationReadoutService` follows same pattern |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W6 on missing Ground Reports.
- **Field-source design risk for `/loop-spec`:** REQ-16 "task-by-task progress from run timeline" and REQ-17 "named task + reason" are not a single pre-grounded DTO. Prefer Gateflow-owned evidence already on runs / run events / handoff stop payloads over scraping GitHub or ambient workspace TASK files. Fail closed with an explicit empty/not-started or unavailable shape when the wave has no implement-lane run — do not invent PR URLs. Unit tests must cover: (a) per-task progress + Draft PR when `pr_number` / `wave-pr-action` evidence present; (b) named task+reason on failure/`needs-input`; (c) no Draft PR URL when walk has not opened the wave PR.
- **File-scope risk:** WorkManifest TASK-W6-01 does **not** list `src/di/modules/business_services_module.py`, but a new `@inject` service needs `binder.bind(ImplementationReadoutService, scope=singleton)`. Same glue pattern as W4/W5 — include DI bind in the TASK-W6-01 change set and record under observed files in Wave-Execution (do not invent TASK ids).

---

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board, verify pointers
- [x] MDC rules (domain-filtered):
  - [x] `.cursor/rules/architecture.mdc` — `api` → `business_services` → repo; new service + route + models
  - [x] `.cursor/rules/dependency-injection.mdc` — `@inject` + singleton bind + `get_*_service`
  - [x] `.cursor/rules/repository-pattern.mdc` — runs/events via repositories (Pydantic); no ORM in service
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `implementation_readout_models.py` in `src/models/` only; enums with `Type` suffix; `extra="forbid"`
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET path `/initiatives/{initiative_id}/waves/{wave_id}/implementation`; query for org/repo; no write body
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative/wave → 404; stop reason explicit, not silent omit
  - [x] `.cursor/rules/strong-typing.mdc` — task status / readiness fields typed; no bare magic strings for closed vocabularies
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `verify_wave_implementation`; unit owns derivation; live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built W6 row
  - [x] `.cursor/rules/logging-loguru.mdc` — kwargs (`initiative_id`, `wave_id`, `pr_number`, task id)
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A (no new table expected; compose from existing run/event/handoff data)
- [x] ADRs (keyword-matched — implementation readout, runs, programme token, no mutate):
  - [x] ADR-001 — durable store (**Accepted**; read existing runs/events only)
  - [x] ADR-003 — slot/layer ownership (**Accepted**; Forge reads via established clients if needed)
  - [x] ADR-005 — programme-token reads (**Accepted**)
  - [x] ADR-009 — no mutate from CAP-06 (**Accepted**; REQ-28)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-16, REQ-17 (+ REQ-28); route `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/implementation`
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W6 (lines 441–494, 1442–1534)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/167 — TASK list (projection only):
  - [ ] TASK-W6-01 — implements REQ-16, REQ-17 — depends_on: [] — files: `src/business_services/implementation_readout_service.py` (create), `src/models/implementation_readout_models.py` (create), `tests/unit/test_implementation_readout_service.py` (create) — exit proof: `make test` exit 0 — per-task progress + Draft PR when present; named task+reason on failure
  - [ ] TASK-W6-02 — implements REQ-16, REQ-17, REQ-28 — depends_on: [TASK-W6-01] — files: `src/api/v1/initiatives_routes.py` (modify), `tests/unit/test_initiatives_read_api.py` (modify) — exit proof: `make test` exit 0 — GET `.../implementation` GET-only
  - [ ] TASK-W6-03 — implements REQ-16, REQ-28 — depends_on: [TASK-W6-02] — files: `tests/verify/verify_wave_implementation.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs — GET-only CAP-06; run/event composition (ADR-001); zero Forge writes (ADR-009 / REQ-28)
- [x] Plan TASK MDC notes and ADR notes for W6 reviewed
- [x] Every cited ADR is **Accepted** in `docs/specification/adr/` (zero NEW-ADR)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — as-built baseline after W6 (implementation readout live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W6 verification row (REQ-16 / REQ-17 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_wave_implementation`
- [ ] Unit — `test_implementation_readout_service`: per-task timeline; Draft PR when present; named task+reason on failure/`needs-input`; no invented URL when PR absent; `test_initiatives_read_api`: GET `/initiatives/{id}/waves/{wave_id}/implementation` 200 shape, 401, 404 unknown initiative/wave, 405 on non-GET
- [ ] Live — co-shipped `tests/verify/verify_wave_implementation.py` (human at `wave-acceptance`)
- [ ] ADR — no supersede required

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without superseding it
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume prior contracts without Ground Report confirmation
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Introduce a new store / ORM table / Alembic revision unless product explicitly requires it (prefer compose from run + events + handoff)
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from CAP-06 (REQ-28)
- [ ] Add non-GET product routes for the implementation readout
- [ ] Present a broken/missing Draft PR as a URL when `wave-pr-action` has not succeeded (mirror REQ-13 spirit for CAP-06)
- [ ] Regress W3 list/detail, W4 wave map, or W5 spec readout routes
- [ ] Redefine CAP-05 status vocabulary or invent a parallel wave-state store (REQ-15 remains W4)
- [ ] Mutate approved WorkManifest intent (exit criteria / deps / live contract)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Task timeline + Draft PR + named failure; GET-only / 401 / 404 | `make test` |
| Live verify | Product behaviour on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_wave_implementation` |
| Ground check | Assigned REQs + boundaries | N/A — `/ground-spec` Pass-2 pin skill |

> P15 applicable — new GET surface: `/api/v1/initiatives/{initiative_id}/waves/{wave_id}/implementation`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_implementation` (API+worker up; programme token; `tests/config.yaml`)
- [ ] Inspect implementation readout — task timeline / Draft PR / named stop reason; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: [#167](https://github.com/drivestream-lab/gateflow/issues/167)
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_implementation`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `0d4c76e`; planned `feature/INIT-GATEFLOW-011-w6-implementation-readout`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W6 gates satisfied; ready for coding after checklist publish |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W6.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo gateflow CAP-06 slice; depends on prior waves already on `develop` (W2 identity; W4 wave ids + nesting; W5 sibling GET pattern).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W6.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W6
    ticket_id: "167"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/167
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 0d4c76e7345176725ce349abe4a88764cafdd9a1
    wave_branch_planned: feature/INIT-GATEFLOW-011-w6-implementation-readout
    prior_wave: W5
    prior_wave_approved: true
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W5.md
    manifest_depends_on: [W4]
    tasks:
      - TASK-W6-01
      - TASK-W6-02
      - TASK-W6-03
    implements:
      - REQ-16
      - REQ-17
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_implementation
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    p15_applicable: true
    live_script_planned: tests/verify/verify_wave_implementation.py
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    # Prefer publishing checklist onto develop tip or cut feature branch first in /commit-workspace /
    # /loop-spec per programme practice (W5 published checklist with code on feature branch).
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W6.md
```
