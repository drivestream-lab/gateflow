## Pre-implement — gateflow / W2 — Factory Effectiveness API

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W2.md` |
| Initiative | INIT-GATEFLOW-015 |
| Wave | W2 |
| Date | 2026-08-12 |
| Outcome | `pass` |
| Outcome reason | Prior W1 Ground Report + `human_approved`; W0 lane contracts available; WorkManifest pass; board #232 seeded with TASK-W2-01…07; P15 live contract resolved to `verify_factory_effectiveness`. |
| Wave head context | Bound by Forge/human context: `develop` @ `3835853` (W1 merged) — not opened by this skill |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `3835853` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on #228 |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#229](https://github.com/drivestream-lab/gateflow/issues/229); W2 [#232](https://github.com/drivestream-lab/gateflow/issues/232) `parent`=#229; body lists TASK-W2-01…07 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W2-01…07 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_factory_effectiveness` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_factory_effectiveness` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_factory_effectiveness.py` (FILE-W2-09) |
| Prior wave as-built row | `human_approved` | [x] W1 = **human_approved** |
| Prior Ground Report exists | W{N-1} | [x] exists — `Ground-Report-INIT-GATEFLOW-015-W1.md` |
| Plan PE sign-off (W0 only) | §0 marked complete | [x] N/A — W2 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Notes (non-blocking):** W2 [#232](https://github.com/drivestream-lab/gateflow/issues/232) board Status may still be **Todo** (optional In Progress hop). Cross-wave dep: TASK-W2-05 also consumes W0 lane contracts (Ground-Report-W0) — confirmed Accepted ADR-017 + source `lane=` write path.

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Reports)

> Read `Ground-Report-INIT-GATEFLOW-015-W1.md` §Contracts produced and W0 lane contracts for REQ-16 read. Confirmed against `source_roots`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Tenant-scoped event join pattern | `RunEventRepository.list_stage_completed_for_tenant` | tenant_id + since | tenant-scoped rows via `runs.tenant_id` | Ground-Report-W1 | [x] yes — W2 extends same join for factory aggregates |
| Metrics route + DI pattern | `GET /metrics/skill-efficacy` / `get_skill_efficacy_service` | TENANT_ADMIN + session | Pydantic response | Ground-Report-W1 | [x] yes — W2 mirrors for factory-effectiveness |
| Lane on stage_completed | `MetricsEmitter.record_stage_duration(lane=)` | optional non-empty lane from job | JSONB `payload.lane` when present | Ground-Report-W0 | [x] yes — W2 cycle-time read (never fabricate `"unknown"` on write; unknown bucket is read-side) |
| Lane on run_stopped | `RunOrchestrator._finalize_run` | job payload optional lane | `run_stopped` JSONB may include `lane` | Ground-Report-W0 | [x] yes |
| Pin node type / authorization | `WorkflowEngine.get_node` / `known_node_ids` | node_id | `node_type`, `authorization` | source + CTR-01 | [x] yes — W2 unattended streak (REQ-12) |
| Runs have initiative/wave/duration | `RunSchema` | N/A | `initiative_id`, `wave_id`, `wave_duration_ms`, `status_type`, timestamps | source | [x] yes — dwell + cycle-time |
| ADR-016 tenant join | runs.tenant_id | tenant_id | scoped queries | ADR-016 Accepted | [x] yes |
| ADR-017 lane in JSONB | payload field | lane string | no new column | ADR-017 Accepted | [x] yes — read-only this wave |

**Unconfirmed contracts** (net-new this wave — expected):
- `FactoryEffectivenessResponse` + models — TASK-W2-01
- Unattended Pass-1 streak composition — TASK-W2-02
- `stop_reason` breakdown query — TASK-W2-03
- Continuation / dwell-time lookup — TASK-W2-04
- Lane cycle-time p50/p95 grouping + unknown bucket — TASK-W2-05
- `GET /api/v1/metrics/factory-effectiveness` + DI — TASK-W2-06
- `tests/verify/verify_factory_effectiveness.py` — TASK-W2-07

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only, `extra="forbid"`
  - [x] `repository-pattern.mdc` — aggregation / continuation queries in repository
  - [x] `dependency-injection.mdc` — `@inject`, bind + `_BUSINESS_SERVICE_TYPES`
  - [x] `http-api-conventions.mdc` — GET, no body
  - [x] `architecture.mdc` — `*_service` naming
  - [x] `fail-fast.mdc` — open/waiting dwell never fabricated as zero (REQ-15)
  - [x] `testing-verify-flows.mdc` — opt-in verify, not `verify_all`
  - [x] `database-migrations.mdc` — **no new column** this wave (A3 / ADR-017)
  - skipped: `infra-services.mdc`
- [x] ADRs:
  - [x] **ADR-016** (Accepted) — tenant `run_id`-join reuse
  - [x] **ADR-017** (Accepted) — lane JSONB read for cycle-time (TASK-W2-05)
  - skipped: ADR-018 (W3 only)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` (REQ-11–REQ-17; REQ-16 read half)
- [x] Plan §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md` W2
- [x] Board: https://github.com/drivestream-lab/gateflow/issues/232 — TASK projection:
  - [ ] TASK-W2-01 — REQ-11,13,14,15,16 — `src/models/factory_effectiveness_models.py` create
  - [ ] TASK-W2-02 — REQ-11,12 — depends 01 — `factory_effectiveness_service.py` create (unattended streak)
  - [ ] TASK-W2-03 — REQ-13 — depends 01 — `run_store_repository.py` modify (`stop_reason`)
  - [ ] TASK-W2-04 — REQ-14,15 — depends 01 — `run_store_repository.py` modify (dwell continuation)
  - [ ] TASK-W2-05 — REQ-16 — depends W0-03 + 01 — service + repository (lane cycle-time)
  - [ ] TASK-W2-06 — REQ-11,17 — depends 02–05 — route + DI
  - [ ] TASK-W2-07 — REQ-11,13,17 — depends 06 — `tests/verify/verify_factory_effectiveness.py` create

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs
- [x] Plan TASK MDC notes and ADR notes for W2 reviewed
- [x] Cited ADRs are **Accepted** (ADR-016, ADR-017)
- [x] No schema migration / Alembic this wave (dwell inferred; lane from JSONB)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract citations drift
- [ ] `as-built/implementation-status.md` — W2 verification row
- [ ] `tests/README.md` — feature map row for `verify_factory_effectiveness`
- [ ] Unit — `tests/unit/test_factory_effectiveness_service.py`
- [ ] Live verification — co-ship `tests/verify/verify_factory_effectiveness.py` (human-run at wave-acceptance)
- [ ] ADR — no supersession this wave

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Add a `lane` or dwell schema column (ADR-017 / A3 — JSONB + inferred continuation only)
- [ ] Fabricate zero/negative dwell for open/waiting STOPs (REQ-15)
- [ ] Hardcode a gateflow-side `stop_reason` taxonomy (REQ-13 — passthrough)
- [ ] Treat automated `external-action` hops as breaking the unattended streak (REQ-12)
- [ ] Add `verify_factory_effectiveness` to `verify_all.py` (opt-in only)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Models, unattended, stop_reason, dwell, lane cycle-time, route | `make test` (focus: `pytest tests/unit/test_factory_effectiveness_service.py -v`) |
| Live verify | Auth + response shape on running API | `.venv/bin/python -m tests.verify.verify_factory_effectiveness` |
| Ground check | Assigned wave REQs satisfied | N/A — `/ground-spec` |

> P15 applies: live script is required; agent implements FILE in `/loop-spec`; human runs at `wave-acceptance`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_factory_effectiveness` (API up; `SMOKE_TENANT_ADMIN_TOKEN`)
- [ ] Experience / inspect to env depth
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-015
- Issue: [#232](https://github.com/drivestream-lab/gateflow/issues/232) (EPIC [#229](https://github.com/drivestream-lab/gateflow/issues/229))
- Spec path: `docs/specification/product/INIT-GATEFLOW-015-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_factory_effectiveness`
- ADRs in scope: ADR-016 (tenant join); ADR-017 (lane JSONB read)
- Wave head: bound by Forge/human context — `develop` @ `3835853`

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W2 gates clean |
| Next | `loop-spec` (`skill`) — `human_checkpoint: false`, `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish checklist to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W2 single-repo. Depends on W0 lane write + W1 tenant/DI patterns already merged to `develop`.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-015
    wave: W2
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/229"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/232"
    board_seed: seeded
    prior_wave: W1
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W1.md
    prior_as_built: human_approved
    workmanifest_contract: pass
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
      - TASK-W2-05
      - TASK-W2-06
      - TASK-W2-07
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_factory_effectiveness"
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
    title: "docs(INIT-GATEFLOW-015): Pre-Implement W2 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W2.md
```
