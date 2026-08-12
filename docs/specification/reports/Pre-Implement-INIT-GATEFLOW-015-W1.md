## Pre-implement — gateflow / W1 — Skill/Spec Efficacy API

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W1.md` |
| Initiative | INIT-GATEFLOW-015 |
| Wave | W1 |
| Date | 2026-08-12 |
| Outcome | `pass` |
| Outcome reason | Prior W0 Ground Report + `human_approved`; WorkManifest pass; board #231 seeded with TASK-W1-01…07; P15 live contract resolved to `verify_skill_efficacy`. |
| Wave head context | Bound by Forge/human context: `develop` @ `cfd565a` (W0 merged) — not opened by this skill |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `cfd565a` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified (prior W0 gate; unchanged) |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#229](https://github.com/drivestream-lab/gateflow/issues/229); W1 [#231](https://github.com/drivestream-lab/gateflow/issues/231) `parent`=#229; body lists TASK-W1-01…07 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W1-01…07 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_skill_efficacy` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_skill_efficacy` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_skill_efficacy.py` (FILE-W1-10) |
| Prior wave as-built row | `human_approved` | [x] W0 = **human_approved** |
| Prior Ground Report exists | W{N-1} | [x] exists — `Ground-Report-INIT-GATEFLOW-015-W0.md` |
| Plan PE sign-off (W0 only) | §0 marked complete | [x] N/A — W1 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Notes (non-blocking):** W1 [#231](https://github.com/drivestream-lab/gateflow/issues/231) board Status is still **Todo** (optional In Progress hop).

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-015-W0.md` §Contracts produced. Confirmed against `source_roots`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Stage outcome vocabulary | `MetricsEmitter.record_stage_duration` / `RunOrchestrator._run_orchestrated_stage` | handoff.outcome / outcome string | full `RunOutcomeType` on `stages` + `stage_completed` | Ground-Report-W0 | [x] yes — W1 rates read these values |
| No historical backfill | W0 write path | N/A | N/A | Ground-Report-W0 | [x] yes — W1 boundary field must not treat old `None` as success |
| Tenant run_id-join scoping | ADR-016 Option C (existing list/get patterns) | tenant_id + run_events→runs join | tenant-scoped rows only | ADR-016 + as-built | [x] yes — reuse for metrics aggregation |
| Existing metrics route auth pattern | `GET /metrics/runs` | `require_role(TENANT_ADMIN)` | RunMetricsResponse | `metrics_routes.py` | [x] yes — W1 mirrors this |
| LearningRepository exists | `LearningRepository.list_items` | initiative/wave filters today | Learning items + `codify_hint` JSONB | source | [x] yes — W1 adds org-wide codify-rate query |
| Lane on events | stage_completed / run_stopped payload | optional lane | JSONB `lane` | Ground-Report-W0 | [ ] N/A for W1 rates — consumed in W2 |

**Unconfirmed contracts** (net-new this wave — expected):
- `SkillEfficacyService` + response models — TASK-W1-01/04
- Tenant-scoped `stage_completed` aggregation query — TASK-W1-02
- Org-wide learning codify-rate query + unjoined bucket — TASK-W1-03
- `outcome_vocabulary_available_since` boundary field — TASK-W1-05
- `GET /api/v1/metrics/skill-efficacy` + DI — TASK-W1-06
- `tests/verify/verify_skill_efficacy.py` — TASK-W1-07

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only, `extra="forbid"`
  - [x] `repository-pattern.mdc` — aggregation queries in repository layer
  - [x] `dependency-injection.mdc` — `@inject`, bind in BusinessServicesModule + `_BUSINESS_SERVICE_TYPES`
  - [x] `http-api-conventions.mdc` — GET query filters, no body
  - [x] `architecture.mdc` — `*_service` naming; import from service module
  - [x] `fail-fast.mdc` — no silent treat of old `None` as success (REQ-03)
  - [x] `testing-verify-flows.mdc` — opt-in verify script, not `verify_all`
  - skipped: `database-migrations.mdc` (no schema change), `infra-services.mdc`
- [x] ADRs:
  - [x] **ADR-016** (Accepted) — reuse tenant `run_id`-join pattern (not a new decision)
  - [x] **ADR-017** (Accepted) — lane write already done in W0; W1 does not read lane
  - skipped: ADR-018 (W3 only)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` (REQ-03 boundary half, REQ-04–REQ-10)
- [x] Plan §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md` W1
- [x] Board: https://github.com/drivestream-lab/gateflow/issues/231 — TASK projection:
  - [ ] TASK-W1-01 — REQ-04,07,08,09 — `src/models/skill_efficacy_models.py` create — models validate
  - [ ] TASK-W1-02 — REQ-04,05,06,10 — `run_store_repository.py` modify — tenant-scoped aggregation
  - [ ] TASK-W1-03 — REQ-08,09 — `learning_repository.py` modify — org-wide codify query
  - [ ] TASK-W1-04 — REQ-04,05,06,07 — depends 01–03 — `skill_efficacy_service.py` create — composition
  - [ ] TASK-W1-05 — REQ-03 — depends 04 — boundary `outcome_vocabulary_available_since`
  - [ ] TASK-W1-06 — REQ-04,10 — depends 04 — route + DI
  - [ ] TASK-W1-07 — REQ-04,07,10 — depends 06 — `tests/verify/verify_skill_efficacy.py` create

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed
- [x] Cited ADRs are **Accepted** (ADR-016, ADR-017)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract citations drift
- [ ] `as-built/implementation-status.md` — W1 verification row
- [ ] `tests/README.md` — feature map row for `verify_skill_efficacy`
- [ ] Unit — `tests/unit/test_skill_efficacy_service.py`
- [ ] Live verification — co-ship `tests/verify/verify_skill_efficacy.py` (human-run at wave-acceptance)
- [ ] ADR — no supersession this wave

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Add methods onto `MetricsEmitter` instead of new `SkillEfficacyService` (plan module decision)
- [ ] Silently treat historical `None` outcomes as `success` in rates
- [ ] Add `verify_skill_efficacy` to `verify_all.py` (opt-in only)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Models, rates, tenant scope, codify join, boundary, route | `make test` (focus: `pytest tests/unit/test_skill_efficacy_service.py -v`) |
| Live verify | Auth + response shape on running API | `.venv/bin/python -m tests.verify.verify_skill_efficacy` |
| Ground check | Assigned wave REQs satisfied | N/A — `/ground-spec` |

> P15 applies: live script is required; agent implements FILE in `/loop-spec`; human runs at `wave-acceptance`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_skill_efficacy` (API up; `SMOKE_TENANT_ADMIN_TOKEN`)
- [ ] Experience / inspect to env depth
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-015
- Issue: [#231](https://github.com/drivestream-lab/gateflow/issues/231) (EPIC [#229](https://github.com/drivestream-lab/gateflow/issues/229))
- Spec path: `docs/specification/product/INIT-GATEFLOW-015-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_skill_efficacy`
- ADRs in scope: ADR-016 (tenant join reuse); ADR-017 out of W1 coding path
- Wave head: bound by Forge/human context — `develop` @ `cfd565a`

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W1 gates clean |
| Next | `loop-spec` (`skill`) — `human_checkpoint: false`, `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish checklist to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W1 single-repo. Depends on W0 contracts already merged to `develop`.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W1.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-015
    wave: W1
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/229"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/231"
    board_seed: seeded
    prior_wave: W0
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W0.md
    prior_as_built: human_approved
    workmanifest_contract: pass
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
      - TASK-W1-06
      - TASK-W1-07
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_skill_efficacy"
    ground_command: null
    wave_head: develop
    codegraph_provider: degraded-none
    grounding_depth: light
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-015): Pre-Implement W1 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W1.md
```
