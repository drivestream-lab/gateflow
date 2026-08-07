## Pre-implement — gateflow / W4 — Wave map readout

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W4.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W4 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W4 gate checks pass: prior W3 `human_approved` (tip `438761a` `wave-accepted`; PR #175 merged `cdfbbc8`) with Ground-Report-W3 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W4 #165 with TASK-W4-01…03, Status In Progress); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `cdfbbc8` (after W3 merge) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w4-wave-map` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `cdfbbc8` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED 2026-08-07; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels `["spec-lgtm"]`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W4 [#165](https://github.com/drivestream-lab/gateflow/issues/165) (OPEN, title `[INIT-GATEFLOW-011 W4] Wave map readout`, label `INIT-GATEFLOW-011`); TASK-W4-01…03 in body; programme Status **In Progress**; `Board-Seed-INIT-GATEFLOW-011.md` B1–B8 PASS |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W4 TASK-W4-01…03 in plan §9 (lines 1265–1316); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_wave_map` (FILE co-shipped in TASK-W4-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT (plan is walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_wave_map` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_wave_map.py` (create in TASK-W4-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W3 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W3 row); tip `438761a` `wave-accepted`; PR #175 merged `cdfbbc8` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W3.md` (2026-08-07; outcome `pass`; §Contracts produced complete for W4+) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W4 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W4 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Manifest note:** WorkManifest W4 `depends_on: [W2]` (data dependency on Gateflow-owned initiative + board/run composition). Programme prior-wave gate is still W3 `human_approved` (sequential delivery).

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch: `feature/INIT-GATEFLOW-011-w4-wave-map` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Reports)

> Primary data contracts from Ground-Report-W2 (initiative identity + board/runs).
> Nesting / path contract from Ground-Report-W3. Confirm against `src/`.

W4 delivers CAP-05 wave map: `GET /api/v1/initiatives/{initiative_id}/waves`
returns per-wave status ∈ {`done`, `ready-to-start`, `blocked`, `active`}
derived **only** from board Feature tickets + run state (REQ-14 / REQ-15) —
no new wave-state store; GET-only (REQ-28).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Initiative identity + 404 unknown | `InitiativeReadoutService.get_initiative` / GET `/initiatives/{id}` | `initiative_id`, `org`, `repo` + programme token | `InitiativeReadout` or 404 `no run or EPIC ticket found for initiative` | Ground-Report-W2 / W3 | [x] yes — wave map nests under same initiative id; unknown initiative should 404 consistently |
| Board Feature tickets (per-wave) | `BoardService.list_tickets` | `org`, `repo`, `initiative_id?`, `ticket_type=Feature`, `state` | `BoardTicketListResponse` (`tickets[]` with `ticket_id`, `title`, `column?`, `initiative_id?`, …) | as-built INIT-002 W2; `board_service.py` | [x] yes — Feature type exists (`BoardTicketType.FEATURE`); W4 derives wave rows from Feature tickets for the initiative (read-only) |
| Run data (active / wave_id) | `RunRepository.list_runs` | `initiative_id?`, `wave_id?`, `status_type?`, … | `list[RunModel]` (`wave_id`, `status_type`, …) | Ground-Report-W2; as-built | [x] yes — W4 uses runs to mark `active` when an in-flight run exists for a wave |
| Initiative list/detail parent path | `initiatives_routes.py` | programme token | GET handlers under `/initiatives` | Ground-Report-W3 | [x] yes — W4 adds sibling `GET /initiatives/{initiative_id}/waves` on same router |
| Programme-token + public_paths | `verify_programme_service_token` | Bearer | void / 401 | ADR-005 | [x] yes — `/api/v1/initiatives` already on `public_paths` |
| Business service + DI precedent | `InitiativeReadoutService` / `CheckpointEvidenceService` | `@inject` + `get_*_service` | Pydantic in/out | Ground-Report-W0/W2 | [x] yes — W4 `WaveMapService` follows same pattern |
| Meta PRD / CAP-01 (W3) | `_resolve_prd_approval` | — | `prd_approval` on list/detail | Ground-Report-W3 | [x] yes present — **W4 does not consume** for wave-map status (REQ-15 = board+run only); must not regress list/detail |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W4.
- **File-scope risk for `/loop-spec`:** WorkManifest TASK-W4-01 does **not** list `src/di/modules/business_services_module.py`, but a new `@inject` service needs `binder.bind(WaveMapService, scope=singleton)` to resolve via `provide_service` / FastAPI Depends. Do **not** invent TASK ids; implement DI bind as necessary glue when creating the service (same pattern as W2) and record the path under observed files in Wave-Execution — or fail closed if policy forbids any undeclared path. Prefer including the DI bind in the TASK-W4-01 change set and noting the manifest omission.
- Wave id / predecessor ordering: derive from Feature ticket titles/labels / `wave_id` on runs + board column vocabulary (`Done`, `In Progress`, …) already used by CAP-03 — confirm against live board ticket shapes during implement; fail closed on ambiguous mapping rather than inventing a parallel store.

---

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board, verify pointers
- [x] MDC rules (domain-filtered):
  - [x] `.cursor/rules/architecture.mdc` — `api` → `business_services` → repo; new service + route + models
  - [x] `.cursor/rules/dependency-injection.mdc` — `@inject` + singleton bind + `get_*_service`
  - [x] `.cursor/rules/repository-pattern.mdc` — runs via `RunRepository` (Pydantic); no ORM in service
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `wave_map_models.py` in `src/models/` only; `Type`-suffix enums for status vocabulary; `extra="forbid"`
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET path `/initiatives/{initiative_id}/waves`; query for org/repo filters; no write body
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative → 404; blocked reason explicit when status=`blocked`; no silent defaults
  - [x] `.cursor/rules/strong-typing.mdc` — status enum not bare `str`; typed block reason
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `verify_wave_map`; unit owns derivation; live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built W4 row
  - [x] `.cursor/rules/logging-loguru.mdc` — kwargs (`initiative_id`, wave status counts)
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A (no new table; REQ-15 forbids new wave-state store)
- [x] ADRs (keyword-matched — wave map, board, runs, programme token, pin mutate):
  - [x] ADR-001 — durable store (**Accepted**; read existing runs only)
  - [x] ADR-003 — ForgeClient via BoardService (**Accepted**; read-only board list)
  - [x] ADR-005 — programme-token reads (**Accepted**)
  - [x] ADR-009 — no mutate from CAP-05 (**Accepted**; REQ-28)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-14, REQ-15 (+ REQ-28); route `GET /api/v1/initiatives/{initiative_id}/waves`
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W4 (lines 331–380, 1256–1346)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/165 — TASK list (projection only):
  - [ ] TASK-W4-01 — implements REQ-14, REQ-15 — depends_on: [] — files: `src/business_services/wave_map_service.py` (create), `src/models/wave_map_models.py` (create), `tests/unit/test_wave_map_service.py` (create) — exit proof: `make test` exit 0 — per-wave status + block reason; no new wave-state store
  - [ ] TASK-W4-02 — implements REQ-14, REQ-15, REQ-28 — depends_on: [TASK-W4-01] — files: `src/api/v1/initiatives_routes.py` (modify), `tests/unit/test_initiatives_read_api.py` (modify) — exit proof: `make test` exit 0 — GET `.../waves` GET-only
  - [ ] TASK-W4-03 — implements REQ-14, REQ-28 — depends_on: [TASK-W4-02] — files: `tests/verify/verify_wave_map.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs — GET-only CAP-05; board+run derivation only (REQ-15 / ADR-001); zero Forge writes (ADR-009)
- [x] Plan TASK MDC notes and ADR notes for W4 reviewed
- [x] Every cited ADR is **Accepted** in `docs/specification/adr/` (zero NEW-ADR)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — as-built baseline after W4 (wave map live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W4 verification row (REQ-14 / REQ-15 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_wave_map`
- [ ] Unit — `test_wave_map_service`: status ∈ {done, ready-to-start, blocked, active}; blocked includes reason (e.g. predecessor not Done); derivation from board Feature + runs only; no parallel store; `test_initiatives_read_api`: GET `/initiatives/{id}/waves` 200 shape, 401, 404 unknown initiative, 405 on non-GET
- [ ] Live — co-shipped `tests/verify/verify_wave_map.py` (human at `wave-acceptance`)
- [ ] ADR — no supersede required

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without superseding it
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume prior contracts without Ground Report confirmation
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Introduce a new wave-state store / ORM table / Alembic revision (REQ-15 / `database-migrations.mdc`)
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from CAP-05 (REQ-28)
- [ ] Add non-GET product routes for the wave map
- [ ] Derive wave status from meta PRD / CAP-01 (that is CAP-03; REQ-15 = board + run only)
- [ ] Mutate approved WorkManifest intent (exit criteria / deps / live contract)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Per-wave status vocabulary + block reason; board+run-only derivation; GET-only / 401 / 404 | `make test` |
| Live verify | Product behaviour on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_wave_map` |
| Ground check | Assigned REQs + boundaries | N/A — `/ground-spec` Pass-2 pin skill |

> P15 applicable — new GET surface: `/api/v1/initiatives/{initiative_id}/waves`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_map` (API+worker up; programme token; `tests/config.yaml`)
- [ ] Inspect wave-map response — statuses in vocabulary; blocked rows name why; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: #165 — https://github.com/drivestream-lab/gateflow/issues/165
- EPIC: #160 — https://github.com/drivestream-lab/gateflow/issues/160
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_map`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `cdfbbc8` (planned coding branch: `feature/INIT-GATEFLOW-011-w4-wave-map`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W4 gates satisfied; WorkManifest clean; P15 live command resolved; prior W3 human_approved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W4.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo CAP-05. Manifest data-depends on W2 (board+runs + initiative identity); W3 already merged on `develop` (path nesting + no regress of list/detail).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W4.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W4
    ticket_id: "165"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/165
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: cdfbbc8f72e36cfaf1a2d2c2c47bac327be39498
    wave_branch_planned: feature/INIT-GATEFLOW-011-w4-wave-map
    prior_wave: W3
    prior_wave_approved: true
    prior_wave_tip_sha: 438761a21aa7bc110458b9d42b944a3ef4c542c4
    prior_wave_merge_sha: cdfbbc8f72e36cfaf1a2d2c2c47bac327be39498
    tasks:
      - TASK-W4-01
      - TASK-W4-02
      - TASK-W4-03
    implements_reqs:
      - REQ-14
      - REQ-15
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_map
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: In Progress
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/159
    spec_merge_commit: 234f66a1b4d5e9d34522cb6bceb016c5672626a4
    workmanifest_contract: pass
    p15_applicable: true
    live_verify_path: tests/verify/verify_wave_map.py
    di_module_file_scope_gap: true
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W4.md
```
