# Pre-implement — drivestream-lab/gateflow / W1 — Scenario B prove-it + cycle-time + Docker spike

Produced by `/pre-implement` on 2026-07-24 for **INIT-GATEFLOW-003**. **No product code in this stage.**

---

### Gate check (prior wave)

> W1 requires INIT-GATEFLOW-003 W0 Ground Report + as-built `human_approved` (DEP-02).

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — on `develop` @ `728202f` (W0 merged) |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` on `develop` |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — PR [#18](https://github.com/drivestream-lab/gateflow/pull/18) MERGED; label `spec-lgtm`; Approve `commit_id` = head `2e1ae6f317e7a5258036bfd0baf46bee56b63e76` |
| Board seed | Wave issue(s) from plan §9 exist | **seeded** — EPIC [#19](https://github.com/drivestream-lab/gateflow/issues/19); W0 [#20](https://github.com/drivestream-lab/gateflow/issues/20) CLOSED; W1 [#21](https://github.com/drivestream-lab/gateflow/issues/21) OPEN; W2 [#22](https://github.com/drivestream-lab/gateflow/issues/22); all waves are sub-issues of #19 on **drivestream-lab Board** |
| Plan source freshness | all upstream rows `CURRENT` | **current** — spec / feasibility / TDD digests match `shasum -a 256` (`4d0fd484…` / `7fa2b2b0…` / `047e899c…`) |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — meta PR head `4c9cacb8…` map_revision **2**; gateflow scope `sha256:592c1f427ce86de76abad119e1a932d41aea3b3104573e439e99d5cd37f60499` (fetched from meta object; no local `prayog-meta/` clone) |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A | **resolved** — W1 target: `.venv/bin/python -m tests.verify.verify_scenario_b` (name may vary; create in TASK-W1-04); baseline aggregator `.venv/bin/python -m tests.verify.verify_all` |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` skill (no Makefile ground target) |
| Prior wave as-built row | `human_approved` | **INIT-003 W0 = human_approved** in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (recorded; N/A as W1 gate — prior wave approval is the gate) |

**Gate verdict:** PASS

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md` §Contracts produced.
> Confirmed against `src/` (not spec alone).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Cursor credentials settings | `CursorAgentSettings.get_instance` / `has_api_key` / `require_api_key` | env `CURSOR_API_KEY`, optional `CURSOR_DEFAULT_MODEL` | typed settings; blank key = missing | Ground-Report-003-W0 | **yes** — `src/configs/cursor_agent_settings.py`; secret not in programme.yaml |
| Local Cursor AgentRunner | `CursorAgentRunner.run_skill` | workspace path, skill id, prompt context, model profile (+ optional runner/model) | `AgentRunResult` SUCCESS/FAILED | Ground-Report-003-W0 | **yes** — `src/infra_services/cursor_agent_runner.py`; `launch_bridge` + `LocalAgentOptions(cwd)`; never cloud options |
| SDK model id map | `CursorAgentRunner._sdk_model_id` | programme model id (e.g. `cursor/auto`) | SDK model id (e.g. `composer-2`) | Ground-Report-003-W0 | **yes** — mapping present; D-W0-M1 still documents programme vs SDK id gap |
| Unit test doubles quarantine | `CursorAgentRunner.run_skill` | `mock-*` skill or `GATEFLOW_AGENT_STUB=1` | synthetic SUCCESS | Ground-Report-003-W0 | **yes** — docstring + stub path; **W1 live verify must unset stub** |
| Start-gate Cursor key | `SlotValidator.validate_for_run` → `WaveStartService.start_wave` | required runner ids include `cursor` | ok or 422 with `config_key=CURSOR_API_KEY` | Ground-Report-003-W0 | **yes** — credential check before enqueue |
| Laptop SDK spike | spike report inspection | local key + cwd | pass/fail note | Ground-Report-003-W0 | **yes** — `docs/specification/reports/Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md`; later update records live coding via `gateflow-w0-spike` |

**Inherited control-plane contracts W1 reuses (not rebuilt):**

| Assumed contract | Entry point | Confirmed? |
|-----------------|-------------|------------|
| Wave start HTTP + programme token | `POST /api/v1/waves/start` | **yes** — INIT-002 W0 |
| Job orchestration | `RunOrchestrator.process_job` | **yes** — dispatches via `CursorAgentRunner.run_skill`; **failure path does not yet persist stage + duration** (W1 TASK-W1-02) |
| Stage success metrics | `MetricsEmitter.record_stage_duration` + `StageCreate` | **yes** on success only today |
| Run detail / metrics APIs | runs + metrics routes | **yes** — no `wave_duration_ms` yet |
| Scenario B pin dispatch | pinned `workflow.yaml` | **yes** — `pre-implement`, `loop-spec`, `verify`, `ground-spec` are `dispatch: orchestrated` on `v0.5.0-rc.2` |

**Unconfirmed contracts** (new in INIT-003 W1 — no Ground Report backing):

- Failure-path `StageCreate` + `record_stage_duration` with failed outcome (REQ-29/30 / FF-05) — **not implemented** (`process_job` finalizes FAILED without stage/metrics write)
- `runs.wave_duration_ms` column + ORM/DTO/run detail (REQ-30) — **absent** from schema/models; **human Alembic required** (DEP-06)
- Docker/image spike note for `cursor-sdk` + bridge + `CURSOR_API_KEY` + cwd — **not present** (TASK-W1-01)
- Live Scenario B verify script (`tests/verify/verify_scenario_b.py` or equivalent) — **does not exist**
- Orchestrator/SDK timeouts tuned for long agent turns (RISK-03) — **open**

→ Treat the above as **implementation scope**. Do not treat stub/`mock-*` success as REQ-27 exit evidence.

**Carried risk from W0:**

- **D-W0-L1** — Ground Report marked live `finished` gap as blocking for W1 Scenario B until resolved. Spike note later records a successful `gateflow-w0-spike` coding turn; still **do not** skip Docker spike or Scenario B verify. Confirm bridge cleanup / timeout discipline during W1.
- **D-W0-M1** — programme `cursor/auto` / `cursor/fast` map via `_sdk_model_id`; keep mapping or align programme.yaml later.
- **DEP-07** — live verify needs real `CURSOR_API_KEY` + model entitlement; stub env unset.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W1):
  - [x] `architecture.mdc` — API+worker dual process; reuse control plane; no rebuild
  - [x] `infra-services.mdc` — CursorAgentRunner stays infra; business must not import `cursor_sdk`
  - [x] `dependency-injection.mdc` — settings via `get_instance()`; runners singleton lifecycle
  - [x] `repository-pattern.mdc` — ORM only in repos; stage/run persistence via repository boundary
  - [x] `database-migrations.mdc` — agent updates schema/`env.py`; **human** owns `postgres_migrations/versions/` for `wave_duration_ms`
  - [x] `pydantic-schemas.mdc` — DTOs in `src/models/`; expose `wave_duration_ms` on run detail models
  - [x] `fail-fast.mdc` — auth/start/crash → `failed`; no pretend success; no silent stub substitute
  - [x] `testing-verify-flows.mdc` — Scenario B in `tests/verify/`; unit for failure metrics edges; no duplicate full journeys in pytest
  - [x] `strong-typing.mdc` — typed stage/run fields; enums for outcomes
  - [x] `logging-loguru.mdc` — structured kwargs (`run_id`, `workflow_node`, `duration_ms`, `wave_duration_ms`, `outcome`)
  - [x] `spec-driven-development.mdc` — same-PR as-built + tests README with code
  - [x] `python-tooling.mdc` — `make check` / `make test` gates
  - skipped: `http-api-conventions.mdc` — no new write-body shape in W1 (additive field on existing GET detail)
  - skipped: `python-imports.mdc` — no new import-cycle design in this slice
  - skipped: `code-guidelines-index.mdc` — index only
- [x] ADRs (keyword-matched — Accepted):
  - [x] ADR-001 — dual API+worker + Postgres RunStore; human Alembic for `wave_duration_ms`
  - [x] ADR-003 — AgentRunner remains infra slot; Scenario B prove-it consumes `run_skill` I/O
  - [x] ADR-004 — secrets via env (`CURSOR_API_KEY`); never programme.yaml
  - [x] ADR-006 — fail-closed start-gate retained; stub not live exit
  - skipped: ADR-002 / ADR-005 — edge trust / programme-token mutations unchanged this wave
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` (REQ-27, REQ-29, REQ-30, REQ-31; Scenario B; cycle-time)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` Phase W1 (TASK-W1-01…05)
- [x] Prior ground: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md`
- [x] TDD notes: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md` §3.3 Docker / §3.4–3.5 metrics
- [x] `tests/README.md` — W0 map present; W1 Scenario B row to add

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs (reuse ADR-001…006; ADR_REQUIRED = 0; no new ADR)
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed (fail-fast, human migrations, testing-verify-flows, ADR-001/003)
- [x] Every initiative ADR cited for this wave is **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` only if W1 proves contract drift (prefer as-built notes for maturity)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-003 W1 capability rows + wave status
- [ ] `tests/README.md` — Scenario B verify + `CURSOR_API_KEY` / stub-unset prereqs
- [ ] Unit — failure-path stage + duration; `wave_duration_ms` compute/expose (`tests/unit/test_run_orchestrator.py`, `test_metrics_emitter.py`)
- [ ] Live verify — `.venv/bin/python -m tests.verify.verify_scenario_b` (wire into `verify_all` when stable)
- [ ] Docker spike note — `docs/runbooks/` or `docs/specification/reports/` (TASK-W1-01) before Scenario B exit
- [ ] DDL note for human Alembic — describe `runs.wave_duration_ms` (nullable int) for owner; **do not** commit revision as agent
- [ ] ADR — none (no supersession)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate full Scenario B HTTP journeys in unit tests when live verify owns them
- [ ] Treat `GATEFLOW_AGENT_STUB` / `mock-*` success as REQ-27 live prove-it evidence
- [ ] Pass cloud agent options to `cursor-sdk`
- [ ] Rebuild wave-start / PR-at-start / board / ForgeClient
- [ ] Agent-authored files under `postgres_migrations/versions/`
- [ ] Assume W0 live `finished` is fully closed without Docker spike + Scenario B verify evidence
- [ ] Scope Scenario A / CTR-01 pin edits into W1 (those are W2 / prayog-skills)

---

### Implementation focus (engineering contracts)

| Task | Contract to produce | Entry / shape notes |
|------|---------------------|---------------------|
| TASK-W1-01 | Docker spike evidence | Gateflow-like image + key + cwd; document bridge/Node deps; pass/fail blockers |
| TASK-W1-02 | Failure-path stage metrics | On AgentRunner non-success: persist stage (failed outcome) + `record_stage_duration`; finalize `failed`; **no** workflow advance |
| TASK-W1-03 | `runs.wave_duration_ms` | ORM/DTO/repo/API; compute accept/enqueue → stop/fail on finalize; human applies Alembic |
| TASK-W1-04 | Scenario B live verify | Worker + key + stub unset; assert RunStore `runner=cursor` + workspace coding work for Scenario B skill set |
| TASK-W1-05 | Docs/tests/as-built | Unit for duration paths; README + as-built W1 rows |

**Suggested branch:** `feature/INIT-GATEFLOW-003-w1-scenario-b` (plan); verify follow-up may use `feature/INIT-GATEFLOW-003-w1-verify`.

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format / lint / types / layers | `make check` |
| Unit | failure stage+duration; wave_duration_ms; no stub-as-live | `make test` |
| Live verify | Scenario B live Cursor coding work + runner=cursor | `.venv/bin/python -m tests.verify.verify_scenario_b` (create); interim `.venv/bin/python -m tests.verify.verify_all` |
| Spike | Docker/bridge readiness | inspection of Docker spike note |
| Ground check | FRs satisfied; boundaries respected | `/ground-spec` (N/A Makefile) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-003**
- Issue: [#21](https://github.com/drivestream-lab/gateflow/issues/21) — `[INIT-GATEFLOW-003 W1] Scenario B prove-it + cycle-time`
- EPIC: [#19](https://github.com/drivestream-lab/gateflow/issues/19)
- Spec path: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` Phase W1
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_scenario_b`
- ADRs in scope: ADR-001, ADR-003, ADR-004, ADR-006 (reuse)

---

### Merge order (if cross-module / cross-service)

1. **Human Alembic** for `runs.wave_duration_ms` applied to local/dev DB before live verify that asserts the field (DEP-06).
2. Docker spike (TASK-W1-01) **before** Scenario B live exit (DEP-03 / RISK-01).
3. Single-repo wave PR(s) on `feature/INIT-GATEFLOW-003-w1-*` → merge to `develop` → `/ground-spec` W1.
4. Scenario A / prayog-skills CTR-01 remains **W2** — do not block W1 merge on it.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-003-W1.md
    digest: sha256:fa289e60ef5c06d7275926967ffc3f676410cb4e412b0f1458a376790ec44f34
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-003
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/21
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/19
    branch_suggestion: feature/INIT-GATEFLOW-003-w1-scenario-b
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_scenario_b
    ground_command: N/A — /ground-spec skill
    gate_verdict: PASS
    carried_risks: [D-W0-L1, D-W0-M1, DEP-07, RISK-01, RISK-03]
  next_candidates:
    - loop-spec
  human_checkpoint: true
  external_action: false
```
