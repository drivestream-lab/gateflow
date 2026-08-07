## Pre-implement — gateflow / W5 — Spec lane readout

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W5.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W5 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W5 gate checks pass: prior W4 `human_approved` (tip `ed3d6be` `wave-accepted`; PR #176 merged `0774e1b`) with Ground-Report-W4 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W5 #166 with TASK-W5-01…03, Status In Progress); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `0774e1b` (after W4 merge) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w5-spec-readout` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `0774e1b` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels include `spec-lgtm`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W5 [#166](https://github.com/drivestream-lab/gateflow/issues/166) (OPEN, title `[INIT-GATEFLOW-011 W5] Spec lane readout`, label `INIT-GATEFLOW-011` + programme Status **In Progress**); TASK-W5-01…03 in body; `Board-Seed-INIT-GATEFLOW-011.md` lists W5 #166 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W5 TASK-W5-01…03 in plan §9 (lines 1358–1409); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_spec_readout` (FILE co-shipped in TASK-W5-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT (plan is walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_spec_readout` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_spec_readout.py` (create in TASK-W5-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W4 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W4 row); tip `ed3d6be` `wave-accepted`; PR #176 merged `0774e1b` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W4.md` (2026-08-07; outcome `pass`; §Contracts produced complete for W5+) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W5 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W5 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Manifest note:** WorkManifest W5 `depends_on: [W2]` (data dependency on Gateflow-owned initiative identity + run/PR fields). Programme prior-wave gate is still W4 `human_approved` (sequential delivery). Ground-Report-W4 supplies the nesting path contract (`…/waves` sibling → add `…/spec` on same router).

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch: `feature/INIT-GATEFLOW-011-w5-spec-readout` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Reports)

> Primary identity / runs / parent routes from Ground-Report-W2 / W3.
> Nesting path contract from Ground-Report-W4. Confirm against `src/`.

W5 delivers CAP-04 spec-lane readout: `GET /api/v1/initiatives/{initiative_id}/spec`
returns Draft Spec PR link (when walk has reached `spec-pr-action`), plain-language
generated artifacts, findings/open questions from feasibility/technical-review
stages, and exact next step from pin (REQ-12); before `spec-pr-action`, states
not-ready plainly — no broken URL (REQ-13); GET-only (REQ-28).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Initiative identity + 404 unknown | `InitiativeReadoutService.get_initiative` / GET `/initiatives/{id}` | `initiative_id`, `org`, `repo` + programme token | `InitiativeReadout` or 404 | Ground-Report-W2 / W3 | [x] yes — spec readout nests under same initiative id; unknown initiative should 404 consistently |
| Run fields (PR, workflow node, handoff) | `RunRepository.list_runs` / `RunModel` | `initiative_id?`, … | `pr_number`, `workflow_node`, `handoff_path`, `status_type`, … | Ground-Report-W2; as-built | [x] yes — W5 derives Draft Spec PR / stage progress from run + pin (read-only) |
| Pin / workflow graph (next step) | `WorkflowEngine` / harness pin | node id / pin load | resolved node + outcomes / next candidates | as-built INIT-001+; `workflow_engine.py` | [x] yes present — "exact next step from pin" (REQ-12) must resolve via pin graph, not invent stages |
| Initiative parent router + programme token | `initiatives_routes.py` | programme token | GET handlers under `/initiatives` | Ground-Report-W3 / W4 | [x] yes — W5 adds sibling `GET /initiatives/{initiative_id}/spec` (W4 already nested `…/waves`) |
| GET wave map nesting precedent | `GET /initiatives/{id}/waves` | path + org/repo | `WaveMapResult` | Ground-Report-W4 | [x] yes — same auth/`public_paths` pattern; **W5 must not regress** waves |
| Wave map compose (W4) | `WaveMapService.get_wave_map` | — | — | Ground-Report-W4 | [x] yes present — **W5 does not consume** for CAP-04 fields; must not break W4 route |
| Meta PRD / CAP-01 (W3) | list/detail `prd_approval` | — | — | Ground-Report-W3 | [x] yes present — **W5 does not consume** for CAP-04; must not regress list/detail |
| Programme-token + public_paths | `verify_programme_service_token` | Bearer | void / 401 | ADR-005 | [x] yes — `/api/v1/initiatives` already on `public_paths` |
| Business service + DI precedent | `WaveMapService` / `InitiativeReadoutService` | `@inject` + `get_*_service` | Pydantic in/out | Ground-Report-W0/W2/W4 | [x] yes — W5 `SpecReadoutService` follows same pattern |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W5 on missing Ground Reports.
- **Field-source design risk for `/loop-spec`:** REQ-12 "plain-language generated artifacts" and "findings/open questions from feasibility/technical-review stages" are not a single pre-grounded DTO. Prefer Gateflow-owned evidence already on runs / run events / handoff artifacts over reading ambient workspace report files. Fail closed with an explicit not-ready / unavailable shape when evidence is missing — do not invent URLs or scrape GitHub write APIs. Confirm against product REQ-12/13 wording during implement; keep unit tests for both "Draft Spec PR present" and "before `spec-pr-action`" (REQ-13) paths.
- **File-scope risk:** WorkManifest TASK-W5-01 does **not** list `src/di/modules/business_services_module.py`, but a new `@inject` service needs `binder.bind(SpecReadoutService, scope=singleton)`. Same glue pattern as W2/W4 — include DI bind in the TASK-W5-01 change set and record under observed files in Wave-Execution (do not invent TASK ids).

---

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board, verify pointers
- [x] MDC rules (domain-filtered):
  - [x] `.cursor/rules/architecture.mdc` — `api` → `business_services` → repo; new service + route + models
  - [x] `.cursor/rules/dependency-injection.mdc` — `@inject` + singleton bind + `get_*_service`
  - [x] `.cursor/rules/repository-pattern.mdc` — runs via `RunRepository` (Pydantic); no ORM in service
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `spec_readout_models.py` in `src/models/` only; enums with `Type` suffix; `extra="forbid"`
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET path `/initiatives/{initiative_id}/spec`; query for org/repo; no write body
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative → 404; not-ready is explicit message (REQ-13), not a fake URL
  - [x] `.cursor/rules/strong-typing.mdc` — readiness / next-step fields typed; no bare magic strings for closed vocabularies
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `verify_spec_readout`; unit owns field derivation; live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built W5 row
  - [x] `.cursor/rules/logging-loguru.mdc` — kwargs (`initiative_id`, readiness, pr_number)
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A (no new table expected; compose from existing run/pin data)
- [x] ADRs (keyword-matched — spec readout, pin, runs, programme token, no mutate):
  - [x] ADR-001 — durable store (**Accepted**; read existing runs only)
  - [x] ADR-003 — slot/layer ownership (**Accepted**; Forge reads via established clients if needed)
  - [x] ADR-005 — programme-token reads (**Accepted**)
  - [x] ADR-009 — no mutate from CAP-04 (**Accepted**; REQ-28)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-12, REQ-13 (+ REQ-28); route `GET /api/v1/initiatives/{initiative_id}/spec`
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W5 (lines 387–439, 1349–1441)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/166 — TASK list (projection only):
  - [ ] TASK-W5-01 — implements REQ-12, REQ-13 — depends_on: [] — files: `src/business_services/spec_readout_service.py` (create), `src/models/spec_readout_models.py` (create), `tests/unit/test_spec_readout_service.py` (create) — exit proof: `make test` exit 0 — fields from pin+run; not-ready when no Draft Spec PR
  - [ ] TASK-W5-02 — implements REQ-12, REQ-13, REQ-28 — depends_on: [TASK-W5-01] — files: `src/api/v1/initiatives_routes.py` (modify), `tests/unit/test_initiatives_read_api.py` (modify) — exit proof: `make test` exit 0 — GET `.../spec` GET-only
  - [ ] TASK-W5-03 — implements REQ-12, REQ-28 — depends_on: [TASK-W5-02] — files: `tests/verify/verify_spec_readout.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs — GET-only CAP-04; pin+run composition (ADR-001); zero Forge writes (ADR-009 / REQ-28)
- [x] Plan TASK MDC notes and ADR notes for W5 reviewed
- [x] Every cited ADR is **Accepted** in `docs/specification/adr/` (zero NEW-ADR)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — as-built baseline after W5 (spec readout live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W5 verification row (REQ-12 / REQ-13 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_spec_readout`
- [ ] Unit — `test_spec_readout_service`: Draft Spec PR link when past `spec-pr-action`; plain not-ready before (REQ-13); pin next-step + findings/artifacts fields when evidence present; `test_initiatives_read_api`: GET `/initiatives/{id}/spec` 200 shape, 401, 404 unknown, 405 on non-GET
- [ ] Live — co-shipped `tests/verify/verify_spec_readout.py` (human at `wave-acceptance`)
- [ ] ADR — no supersede required

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without superseding it
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume prior contracts without Ground Report confirmation
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Introduce a new store / ORM table / Alembic revision unless product explicitly requires it (prefer compose from run + pin)
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from CAP-04 (REQ-28)
- [ ] Add non-GET product routes for the spec readout
- [ ] Present a broken/missing Spec PR as a URL when walk has not reached `spec-pr-action` (REQ-13)
- [ ] Regress W3 list/detail meta bridge or W4 wave map routes
- [ ] Mutate approved WorkManifest intent (exit criteria / deps / live contract)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Pin+run field composition; not-ready before `spec-pr-action`; GET-only / 401 / 404 | `make test` |
| Live verify | Product behaviour on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_spec_readout` |
| Ground check | Assigned REQs + boundaries | N/A — `/ground-spec` Pass-2 pin skill |

> P15 applicable — new GET surface: `/api/v1/initiatives/{initiative_id}/spec`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_spec_readout` (API+worker up; programme token; `tests/config.yaml`)
- [ ] Inspect spec readout — Draft Spec PR or plain not-ready; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: [#166](https://github.com/drivestream-lab/gateflow/issues/166)
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_spec_readout`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `0774e1b`; planned `feature/INIT-GATEFLOW-011-w5-spec-readout`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W5 gates satisfied; ready for coding after checklist publish |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W5.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo gateflow CAP-04 slice; depends on prior waves already on `develop` (W2 identity; W4 nesting precedent).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W5.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W5
    ticket_id: "166"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/166
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 0774e1b89d9efeef3907b36950faf051a8cb755d
    wave_branch_planned: feature/INIT-GATEFLOW-011-w5-spec-readout
    prior_wave: W4
    prior_wave_approved: true
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W4.md
    tasks:
      - TASK-W5-01
      - TASK-W5-02
      - TASK-W5-03
    implements:
      - REQ-12
      - REQ-13
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_spec_readout
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    p15_applicable: true
    live_script_planned: tests/verify/verify_spec_readout.py
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    # Prefer publishing checklist onto develop tip or cut feature branch first in /commit-workspace /
    # /loop-spec per programme practice (W4 published checklist with code on feature branch).
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W5.md
```
