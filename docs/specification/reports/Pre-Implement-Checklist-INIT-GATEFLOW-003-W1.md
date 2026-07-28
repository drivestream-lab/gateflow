# Pre-implement — drivestream-lab/gateflow / W1 — implement-lane prove-it + cycle-time + Docker spike

Produced by `/pre-implement` on 2026-07-25 for **INIT-GATEFLOW-003** (orchestrated run `INIT-SCENB-8544986`). **No product code in this stage.**

---

### Gate check (prior wave)

> W1 requires INIT-GATEFLOW-003 W0 Ground Report + as-built `human_approved` (DEP-02).

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — orchestrated run on `feature/INIT-SCENB-8544986-w1-scenario-b` (PR [#36](https://github.com/drivestream-lab/gateflow/pull/36)); workspace `feature/INIT-GATEFLOW-003-w1-scenario-b` |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` on `develop` (PR [#18](https://github.com/drivestream-lab/gateflow/pull/18) MERGED) |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — label `spec-lgtm`; head `2e1ae6f317e7a5258036bfd0baf46bee56b63e76`; merge `e2d2579ce615149ffb06e4ce849558fdd4e8f511` |
| Board seed | Wave issue(s) from plan §9 exist | **seeded** — EPIC [#19](https://github.com/drivestream-lab/gateflow/issues/19); W0 [#20](https://github.com/drivestream-lab/gateflow/issues/20) CLOSED; W1 [#21](https://github.com/drivestream-lab/gateflow/issues/21) OPEN; W2 [#22](https://github.com/drivestream-lab/gateflow/issues/22) OPEN |
| Plan source freshness | all upstream rows `CURRENT` | **partial** — feasibility `sha256:7fa2b2b0…` and TDR `sha256:047e899c…` match plan; **product spec digest drift on wave branch** (`7b14b3dd…` vs plan `4d0fd484…` — REQ-28 dispatch-plan wording aligned to as-built; reconcile in same wave PR) |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan records revision **2** and scope `sha256:aaf398dc…` @ meta head `4c9cacb8…` (no local `prayog-meta/` clone) |
| `check_command` | resolved | **`make check`** — pass (2026-07-25) |
| `test_command` | resolved | **`make test`** — 111 passed (2026-07-25) |
| `verify_command` | resolved or N/A | **resolved** — `.venv/bin/python -m tests.verify.verify_implement_lane` (opt-in via `tests/config.yaml`); aggregator `.venv/bin/python -m tests.verify.verify_all` |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` skill (no Makefile ground target) |
| Prior wave as-built row | `human_approved` | **INIT-003 W0 = human_approved** in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (N/A as W1 gate — prior wave approval is the gate) |

**Gate verdict:** PASS — prior wave W0 `human_approved`; spec digest drift on wave branch is forward SDD reconciliation (REQ-28), not a missing Gate 2 package.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md` §Contracts produced.
> Confirmed against `src/` on `feature/INIT-GATEFLOW-003-w1-scenario-b` (not spec alone).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Cursor credentials settings | `CursorAgentSettings.get_instance` / `has_api_key` / `require_api_key` | env `CURSOR_API_KEY`, optional `CURSOR_DEFAULT_MODEL`, `timeout_ms` | typed settings; blank key = missing | Ground-Report-003-W0 | **yes** — `src/configs/cursor_agent_settings.py` |
| Local Cursor AgentRunner | `CursorAgentRunner.run_skill` | workspace path, skill id, prompt context, model profile, runner, model_id | `AgentRunResult` SUCCESS/FAILED | Ground-Report-003-W0 | **yes** — `src/infra_services/cursor_agent_runner.py`; `launch_bridge` + `LocalAgentOptions(cwd)`; never cloud |
| SDK model id map | `CursorAgentRunner._sdk_model_id` | programme model id (e.g. `cursor/auto`) | SDK model id (e.g. `composer-2`) | Ground-Report-003-W0 | **yes** — `auto`/`fast`/empty → settings default |
| Unit test doubles quarantine | `CursorAgentRunner.run_skill` | `mock-*` skill or `GATEFLOW_AGENT_STUB=1` | synthetic SUCCESS | Ground-Report-003-W0 | **yes** — docstring + stub path; live verify requires stub unset |
| Start-gate Cursor key | `SlotValidator.validate_for_run` → `WaveStartService.start_wave` | required runner ids include `cursor` | ok or 422 with `config_key=CURSOR_API_KEY` | Ground-Report-003-W0 | **yes** — `src/business_services/slot_validator.py` |
| Laptop SDK spike | spike report inspection | local key + cwd | pass/fail note | Ground-Report-003-W0 | **yes** — `docs/specification/reports/Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md` |

**Inherited control-plane contracts W1 reuses (not rebuilt):**

| Assumed contract | Entry point | Confirmed? |
|-----------------|-------------|------------|
| Wave start HTTP + programme token | `POST /api/v1/waves/start` | **yes** — INIT-002 W0 |
| Job orchestration | `RunOrchestrator.process_job` | **yes** — dispatches via `CursorAgentRunner.run_skill`; failure path persists stage + duration (W1 TASK-W1-02) |
| PR-at-start via ForgeClient | `RunOrchestrator.process_job` → `ensure_branch_from_base` + `create_or_update_pull_request` | **yes** — `src/infra_services/forge_client.py`; head from wave-start identity |
| Stage success/failure metrics | `MetricsEmitter.record_stage_duration` + `StageCreate` | **yes** — success and failure paths in `run_orchestrator.py` |
| Run detail / metrics APIs | runs + metrics routes | **yes** — `wave_duration_ms` on ORM/DTO/API |
| Engineering-lane pin dispatch | pinned `workflow.yaml` | **yes** — `pre-implement`, `loop-spec`, `verify`, `ground-spec` are `dispatch: orchestrated` on `v0.5.0-rc.2` |

**W1 scope items (implemented on branch — confirm before ground-spec):**

| Contract | Entry point | Confirmed? |
|----------|-------------|------------|
| Failure-path stage + duration | `RunOrchestrator.process_job` → `record_stage_duration` + `StageCreate` on FAILED | **yes** — `src/business_services/run_orchestrator.py` |
| `runs.wave_duration_ms` | `_compute_wave_duration_ms` + ORM/DTO | **yes** — schema, models, finalize path; human Alembic note in repo |
| Docker bridge spike | inspection | **yes** — `docs/specification/reports/Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md` **pass** |
| Implement-lane live verify harness | `tests/verify/verify_implement_lane.py` | **yes** — opt-in via `tests/config.yaml` (`features.implement_lane.enabled: true`, `gateflow.require_worker: true`) |

**Unconfirmed contracts** (exit evidence still open):

- Live implement-lane coding-work prove-it with real `CURSOR_API_KEY` + worker (REQ-27 / D-W1-L1) — **this orchestrated run** (`INIT-SCENB-8544986`, `start_node=pre-implement`, branch slug `implement-lane`)
- W1 Ground Report PE sign-off — as-built row still **Draft** (expected until `/ground-spec` + human checkpoint)

**Carried risk from W0/W1:**

- **D-W0-L1** — live `finished` path; Docker bridge **pass**; implement-lane live still the exit gate
- **D-W0-M1** — programme `cursor/auto` mapped via `_sdk_model_id`
- **DEP-07** — live verify needs real `CURSOR_API_KEY` + model entitlement; stub env unset

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W1):
  - [x] `architecture.mdc` — API+worker dual process; reuse control plane
  - [x] `infra-services.mdc` — CursorAgentRunner stays infra; business must not import `cursor_sdk`
  - [x] `dependency-injection.mdc` — settings via `get_instance()`; runners singleton lifecycle
  - [x] `repository-pattern.mdc` — ORM only in repos; stage/run persistence via repository boundary
  - [x] `database-migrations.mdc` — human owns `postgres_migrations/versions/` for `wave_duration_ms`
  - [x] `pydantic-schemas.mdc` — DTOs in `src/models/`; `wave_duration_ms` on run detail
  - [x] `fail-fast.mdc` — auth/start/crash → `failed`; no pretend success
  - [x] `testing-verify-flows.mdc` — implement-lane in `tests/verify/`; no duplicate full journeys in pytest
  - [x] `strong-typing.mdc` — typed stage/run fields; enums for outcomes
  - [x] `logging-loguru.mdc` — structured kwargs (`run_id`, `workflow_node`, `duration_ms`, `wave_duration_ms`)
  - [x] `spec-driven-development.mdc` — same-PR as-built + tests README with code
  - [x] `python-tooling.mdc` — `make check` / `make test` gates
  - skipped: `http-api-conventions.mdc` — no new write-body shape in W1
  - skipped: `python-imports.mdc` — no new import-cycle design
  - skipped: `code-guidelines-index.mdc` — index only
- [x] ADRs (keyword-matched — Accepted):
  - [x] ADR-001 — dual API+worker + Postgres RunStore; human Alembic for `wave_duration_ms`
  - [x] ADR-003 — AgentRunner remains infra slot; implement-lane prove-it consumes `run_skill` I/O
  - [x] ADR-004 — secrets via env (`CURSOR_API_KEY`); dispatch plan not programme YAML for runner/model
  - [x] ADR-006 — fail-closed start-gate retained; stub not live exit
  - skipped: ADR-002 / ADR-005 — edge trust / programme-token mutations unchanged this wave
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` (REQ-27…31; implement-lane)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` Phase W1 (TASK-W1-01…05)
- [x] Prior ground: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md`
- [x] TDD notes: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md` §3.3 Docker / §3.4–3.5 metrics
- [x] `tests/README.md` — W1 implement-lane map + prereqs

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR (reuse ADR-001…006; ADR_REQUIRED = 0)
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed
- [x] Every initiative ADR cited for this wave is **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code)

- [ ] Product spec — REQ-28 dispatch-plan wording already on wave branch; finalize in loop-spec/ground-spec PR if drift remains
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-003 W1 capability rows + wave status (after live prove-it)
- [ ] `tests/README.md` — keep implement-lane prereqs current
- [x] Unit — failure-path stage + duration; `wave_duration_ms` (`tests/unit/test_run_orchestrator.py`, `test_metrics_emitter.py`)
- [ ] Live verify — `.venv/bin/python -m tests.verify.verify_implement_lane` (this orchestrated run is the live prove-it path)
- [x] Docker spike note — `docs/specification/reports/Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md`
- [ ] W1 Ground Report PE sign-off — after `/ground-spec`

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate full implement-lane HTTP journeys in unit tests when live verify owns them
- [ ] Treat `GATEFLOW_AGENT_STUB` / `mock-*` success as REQ-27 live prove-it evidence
- [ ] Pass cloud agent options to `cursor-sdk`
- [ ] Rebuild wave-start / PR-at-start / board / ForgeClient
- [ ] Agent-authored files under `postgres_migrations/versions/`
- [ ] Scope Scenario A / CTR-01 pin edits into W1 (W2 / prayog-skills)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format / lint / types / layers | `make check` |
| Unit | failure stage+duration; wave_duration_ms; no stub-as-live | `make test` |
| Live verify | Implement-lane live Cursor coding work + runner=cursor + PR-at-start | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Spike | Docker/bridge readiness | inspection of Docker spike note |
| Ground check | FRs satisfied; boundaries respected | `/ground-spec` (N/A Makefile) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-003** (orchestrated verify id: **INIT-SCENB-8544986**)
- Orchestrated PR: [#36](https://github.com/drivestream-lab/gateflow/pull/36) — `feature/INIT-SCENB-8544986-w1-scenario-b`
- Issue: [#21](https://github.com/drivestream-lab/gateflow/issues/21) — `[INIT-GATEFLOW-003 W1] implement-lane prove-it + cycle-time`
- EPIC: [#19](https://github.com/drivestream-lab/gateflow/issues/19)
- Spec path: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` Phase W1
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_implement_lane`
- ADRs in scope: ADR-001, ADR-003, ADR-004, ADR-006 (reuse)

---

### Merge order (if cross-module / cross-service)

1. Human Alembic for `runs.wave_duration_ms` applied before live verify asserting the field (DEP-06).
2. Docker spike (TASK-W1-01) **before** implement-lane live exit — **done** (pass).
3. Orchestrated implement-lane chain on `feature/INIT-SCENB-8544986-w1-scenario-b`: `/pre-implement` → `/loop-spec` → `/verify` → `/ground-spec`.
4. Product wave PR on `feature/INIT-GATEFLOW-003-w1-*` → merge to `develop` → `/ground-spec` W1 PE sign-off.
5. Scenario A / prayog-skills CTR-01 remains **W2**.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-003-W1.md
    digest: sha256:b64a38630ffc93a1ad14755289edd957c59879712bb228521568c103b5827300
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-003
    orchestrated_initiative_id: INIT-SCENB-8544986
    wave: W1
    workflow_node: pre-implement
    board_issue: https://github.com/drivestream-lab/gateflow/issues/21
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/19
    orchestrated_pr: https://github.com/drivestream-lab/gateflow/pull/36
    branch: feature/INIT-SCENB-8544986-w1-scenario-b
    workspace_branch: feature/INIT-GATEFLOW-003-w1-scenario-b
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    ground_command: N/A — /ground-spec skill
    gate_verdict: PASS
    spec_digest_note: wave-branch REQ-28 forward edit; feasibility+TDR CURRENT
    carried_risks: [D-W0-L1, D-W0-M1, DEP-07, D-W1-L1]
    implement_lane_evidence: /Users/kumar.deepak1/Workspace/handson/drivestream-lab/run_gateflow/evidence/implement-lane-live.json
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```
