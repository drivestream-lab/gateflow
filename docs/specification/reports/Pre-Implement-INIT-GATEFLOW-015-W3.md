## Pre-implement — gateflow / W3 — Delivery Scorecard API (gateflow-owned half)

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W3.md` |
| Initiative | INIT-GATEFLOW-015 |
| Wave | W3 |
| Date | 2026-08-12 |
| Outcome | `pass` |
| Outcome reason | Prior W2 Ground Report + `human_approved`; WorkManifest pass; board #233 seeded with TASK-W3-01…06; P15 live contract resolved to `verify_delivery_scorecard`; ADR-018 Accepted for REQ-21 tenant classification. |
| Wave head context | Bound by Forge/human context: `develop` @ `4b31ad0` (W2 merged via #236) — not opened by this skill |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `4b31ad0106ed6f758bad54afc9551a372509aa5d` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on #228 |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#229](https://github.com/drivestream-lab/gateflow/issues/229); W3 [#233](https://github.com/drivestream-lab/gateflow/issues/233) `parent`=#229; body lists TASK-W3-01…06 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W3-01…06 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_delivery_scorecard` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:67918ab8c946a976d58f03b4e3b5d8fe6e3ab0b0d3475028c334e4bbe52d4e72` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:8d8b5c83c0d1ac08e56a49b3ef8636a938b5bf02475e53de4cd7108fd10e3666` (as cited on product spec; meta PRD path not re-hashed this session — no tip drift vs W2 checklist) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_delivery_scorecard` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_delivery_scorecard.py` (new FILE; coverage query: zero existing markers) |
| Prior wave as-built row | `human_approved` | [x] W2 = **human_approved** |
| Prior Ground Report exists | W{N-1} | [x] exists — `Ground-Report-INIT-GATEFLOW-015-W2.md` |
| Plan PE sign-off (W0 only) | §0 marked complete | [x] N/A — W3 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Notes (non-blocking):** W3 [#233](https://github.com/drivestream-lab/gateflow/issues/233) board Status may still be **Todo** (optional In Progress hop). REQ-20 composition reuses `ClosurePreviewService` / `CompletionReadoutService` + tenant-filtered runs (not a new persistence table). REQ-21 run-less EPIC tickets use ADR-018 org+repo → tenant read-time classification via `TenantRepository.find_workspace_credential_by_org_repo`.

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Reports)

> Read `Ground-Report-INIT-GATEFLOW-015-W2.md` §Contracts produced (and W1 DI/tenant join as upstream). Confirmed against `source_roots`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Metrics route + DI pattern | `GET /metrics/factory-effectiveness` / `get_factory_effectiveness_service` | TENANT_ADMIN JWT | Pydantic response | Ground-Report-W2 | [x] yes — W3 mirrors for delivery-scorecard |
| Tenant-scoped event/run join | `RunEventRepository` / `RunRepository` via `runs.tenant_id` | tenant_id (+ since) | tenant-scoped rows | Ground-Report-W1/W2 | [x] yes — W3 rework + closed-with-evidence filter |
| Full outcome vocabulary on stages | `stage_completed.outcome_type` | enum incl. findings/blocked/pending | rates / rework detection | Ground-Report-W0 | [x] yes — REQ-19 needs findings/blocked + checkpoint pass |
| Pin human-checkpoint + outcome | WorkflowEngine / stage events | node type + outcome | pass at checkpoint | source + CTR-01 | [x] yes — rework post-checkpoint-only |
| Runs list by tenant | `RunRepository.list_runs` | session + tenant_id / filters | run rows | source | [x] yes — REQ-20/21 composition |
| Closure / completion readout services | `ClosurePreviewService` / `CompletionReadoutService` | initiative context | persisted readout presence | source | [x] yes — exist; W3 composes tenant-filtered |
| Org+repo → tenant lookup | `TenantRepository.find_workspace_credential_by_org_repo` | org + repo | tenant_id or fail-closed | ADR-018 + source | [x] yes — Option A read-time for run-less EPICs |
| ADR-016 tenant join | runs.tenant_id | tenant_id | scoped queries | ADR-016 Accepted | [x] yes |
| ADR-018 board EPIC tenant class | org+repo lookup | EPIC without run_id | scoped into/out of denominator | ADR-018 Accepted | [x] yes — TASK-W3-04 |

**Unconfirmed contracts** (net-new this wave — expected):
- `DeliveryScorecardResponse` + as_of / cumulative / 90-day delta framings — TASK-W3-01
- Rework post-checkpoint-only query — TASK-W3-02
- Initiatives-closed-with-evidence composition — TASK-W3-03
- Factory coverage % + TenantRepository extract for EPIC scoping — TASK-W3-04
- `GET /api/v1/metrics/delivery-scorecard` + DI — TASK-W3-05
- `tests/verify/verify_delivery_scorecard.py` — TASK-W3-06
- Intent→merge lead time field **absent** (REQ-22) — inspection in models

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only; no fabricated fields (REQ-22)
  - [x] `repository-pattern.mdc` — rework aggregation + TenantRepository modify
  - [x] `dependency-injection.mdc` — `@inject`, bind + `_BUSINESS_SERVICE_TYPES`
  - [x] `http-api-conventions.mdc` — GET, no body
  - [x] `architecture.mdc` — `*_service` naming (`DeliveryScorecardService`)
  - [x] `fail-fast.mdc` — honest empty/zero; no fabricated intent→merge
  - [x] `testing-verify-flows.mdc` — opt-in verify, not `verify_all`
  - [x] `strong-typing.mdc` — Pydantic response shapes
  - skipped: `infra-services.mdc`, `database-migrations.mdc` (no new column this wave — ADR-018 read-time only)
- [x] ADRs:
  - [x] **ADR-016** (Accepted) — tenant `run_id`-join for run-bearing records
  - [x] **ADR-018** (Accepted) — CAP-04 board/EPIC tenant scoping Option A (TASK-W3-04)
  - skipped: ADR-017 (lane — W2 complete; not required for scorecard metrics)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` (REQ-18–REQ-23)
- [x] Plan §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-015.md` W3
- [x] Board: https://github.com/drivestream-lab/gateflow/issues/233 — TASK projection:
  - [ ] TASK-W3-01 — REQ-18, REQ-22 — `src/models/delivery_scorecard_models.py` create
  - [ ] TASK-W3-02 — REQ-19 — depends 01 — `run_store_repository.py` modify (rework)
  - [ ] TASK-W3-03 — REQ-20 — depends 01 — `delivery_scorecard_service.py` create (closed-with-evidence)
  - [ ] TASK-W3-04 — REQ-21 — depends 01 — `tenant_repository.py` modify + service (factory coverage %; **ADR-018**)
  - [ ] TASK-W3-05 — REQ-18, REQ-23 — depends 02–04 — route + DI
  - [ ] TASK-W3-06 — REQ-18, REQ-21, REQ-23 — depends 05 — `tests/verify/verify_delivery_scorecard.py` create

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs
- [x] Plan TASK MDC notes and ADR notes for W3 reviewed
- [x] Cited ADRs are **Accepted** (ADR-016, ADR-018)
- [x] No schema migration / Alembic this wave (ADR-018 Option A = read-time org+repo lookup only)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract citations drift
- [ ] `as-built/implementation-status.md` — W3 verification row + `Implementation-Status-INIT-GATEFLOW-015.md`
- [ ] `tests/README.md` — feature map row for `verify_delivery_scorecard`
- [ ] Unit — `tests/unit/test_delivery_scorecard_service.py` (models, rework, closed_with_evidence, factory_coverage, route)
- [ ] Live verification — co-ship `tests/verify/verify_delivery_scorecard.py` (human-run at wave-acceptance)
- [ ] ADR — no supersession this wave

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Fabricate `intent_to_merge_lead_time` or invent partial-data lead time (REQ-22 — field absent)
- [ ] Count pre-checkpoint findings/blocked self-loops as rework (REQ-19 — CAP-02 already owns those)
- [ ] Present factory coverage as total-company coverage (REQ-21 — precise EPIC+run scoped definition only)
- [ ] Count another tenant's EPIC tickets in the denominator (REQ-23 / ADR-018)
- [ ] Add a durable `tenant_id` column on a non-existent board-ticket table (ADR-018 Option C rejected)
- [ ] Add `verify_delivery_scorecard` to `verify_all.py` (opt-in only)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Models, rework, closed-with-evidence, factory coverage, route | `make test` (focus: `pytest tests/unit/test_delivery_scorecard_service.py -v`) |
| Live verify | Auth + as_of/cumulative/delta shape on running API | `.venv/bin/python -m tests.verify.verify_delivery_scorecard` |
| Ground check | Assigned wave REQs satisfied | N/A — `/ground-spec` |

> P15 applies: live script is required; agent implements FILE in `/loop-spec`; human runs at `wave-acceptance`. Prerequisites (plan): API up; `SMOKE_TENANT_ADMIN_TOKEN`; ≥1 closed initiative and ≥1 EPIC ticket for smoke tenant/board.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_delivery_scorecard` (API up; token + board fixtures per plan)
- [ ] Experience / inspect to env depth
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-015
- Issue: [#233](https://github.com/drivestream-lab/gateflow/issues/233) (EPIC [#229](https://github.com/drivestream-lab/gateflow/issues/229))
- Spec path: `docs/specification/product/INIT-GATEFLOW-015-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_delivery_scorecard`
- ADRs in scope: ADR-016 (tenant join); ADR-018 (EPIC org+repo tenant classification)
- Wave head: bound by Forge/human context — `develop` @ `4b31ad0`

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W3 gates clean |
| Next | `loop-spec` (`skill`) — `human_checkpoint: false`, `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish checklist to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W3 single-repo. Depends on W0 outcome vocabulary, W1/W2 metrics DI + tenant join, and existing closure/completion + TenantRepository APIs already on `develop`.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W3.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-015
    wave: W3
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/229"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/233"
    board_seed: seeded
    prior_wave: W2
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-015-W2.md
    prior_as_built: human_approved
    workmanifest_contract: pass
    tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
      - TASK-W3-04
      - TASK-W3-05
      - TASK-W3-06
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_delivery_scorecard"
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
    title: "docs(INIT-GATEFLOW-015): Pre-Implement W3 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-015-W3.md
```
