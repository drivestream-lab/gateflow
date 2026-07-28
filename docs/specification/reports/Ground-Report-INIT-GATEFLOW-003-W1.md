# Ground report — INIT-GATEFLOW-003 W1

| Field | Value |
|-------|-------|
| Wave | W1 — implement-lane prove-it + cycle-time + Docker spike |
| Spec | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` |
| Date | 2026-07-25 |
| Branch | `feature/INIT-GATEFLOW-003-w1-ground-report` — wave-signoff (implementation already on `develop` via #44) |
| Status | **human_approved** (2026-07-25) |
| Review deadline | 2026-07-28 |
| Deciders | Tech lead / reviewer: prayog-pe-team — explicit LGTM required |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/21 |
| Plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` Phase W1 |

## Automated check output

`ground_command`: N/A (no Makefile ground target; manual FR validation + toolchain).

```text
$ make check
black / ruff / pyright / lint-imports — all pass
Contracts: 1 kept, 0 broken (layered architecture)

$ make test
110 passed in ~1.3s

$ .venv/bin/python -m tests.verify.verify_implement_lane
# tests/config.yaml: features.implement_lane.enabled + gateflow.require_worker
# PROGRAMME_SERVICE_TOKEN in verify .env; CURSOR_API_KEY on Gateflow make run
[OK] four cursor stages success; terminal status=stopped (wave-human-decision)
[OK] wave_duration_ms present
[OK] evidence file present
[OK] verify_implement_lane passed

Live RunStore evidence (ds_gateflow_db):
  run_id=de780ba2-7841-4827-ad69-362358a8176d
  status_type=stopped outcome_type=stopped workflow_node=wave-human-decision
  stages: pre-implement, loop-spec, verify, ground-spec (all runner=cursor, outcome=success)
  run_events: api_trigger + 4× stage_completed + run_stopped
  wave_duration_ms=492608

Docker spike (TASK-W1-01):
docs/specification/reports/Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md — pass

Human Alembic (DEP-06):
postgres_migrations/versions/7e79269bd50b_add_runs_wave_duration_ms.py
Committed on wave branch; local DB alembic_version=7e79269bd50b
```

## FR checklist

| FR / REQ | Spec claim (W1 slice) | Verified artifact | Status |
|----------|----------------------|-------------------|--------|
| REQ-27 (W1) | Live Cursor implement lane (`pre-implement` → `loop-spec` → `verify` → `ground-spec`) with coding-work evidence; no stub as exit | `verify_implement_lane` green; RunStore stages/events | **pass** |
| REQ-29 (W1) | Auth/start/crash → `failed`; no workflow advance; stage visibility | `RunOrchestrator` failed stage + duration then finalize; unit | **pass** (unit) |
| REQ-30 (W1) | Stage duration on success **and** failure; `runs.wave_duration_ms` on finalize | Unit + Alembic + live `wave_duration_ms=492608` | **pass** |
| REQ-31 | Reuse 001/002 control plane; no rebuild | Wave-start / PR-at-start / ForgeClient unchanged; pin walker + Cursor | **pass** |
| inherit REQ-28 | Missing-key fail-closed at start | SlotValidator + start-gate from W0 | **pass** (inherit) |
| Q-3 quarantine | Stand-in not live exit evidence | `GATEFLOW_AGENT_STUB` removed; unit `mock-*` only | **pass** |
| D-W0-L1 carry | Live coding work | Laptop spike + Docker bridge + implement-lane live SDK | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| AgentRunner in infra; business does not import `cursor_sdk` | ADR-003 | **pass** |
| Secrets via env (`CURSOR_API_KEY`); no committed programme config | ADR-004 | **pass** |
| Fail-closed start-gate for missing Cursor credentials | ADR-006 | **pass** |
| Stage/run persistence via repository only | MDC repository-pattern | **pass** |
| Human owns Alembic revision files | MDC database-migrations | **pass** — `7e79269bd50b` on branch |
| Layered imports (`import-linter`) | MDC python-tooling | **pass** |
| Never pass cloud agent options | Spec + TDD §3.3 | **pass** |
| Stub env not used as live exit | Q-3 | **pass** — env var deleted |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|------------------|--------|--------|
| Local Cursor `run_skill` → `AgentRunResult` | Ground-Report-003-W0 | **yes** |
| Cursor credentials + start-gate | Ground-Report-003-W0 | **yes** |
| Unit doubles (`mock-*` only) | W0 / W1 | **yes** |
| Wave start + orchestration + metrics | 002 / 003-W0 | **yes** |
| Engineering-lane pin `dispatch: orchestrated` | pin `v0.5.0-rc.2` | **yes** |

## Discrepancies

| ID | FR | Finding | Severity | Disposition |
|----|----|---------|----------|-------------|
| D-W1-L1 | REQ-27 | Live implement-lane prove-it open at first Draft | — | **Closed 2026-07-25** — `verify_implement_lane` pass; run `de780ba2-…` |
| D-W1-M1 | REQ-30 | Human Alembic untracked at first Draft | — | **Closed** — `7e79269bd50b` on wave branch |
| D-W0-M1 | REQ-27 | `cursor/auto` mapped via `_sdk_model_id` | Low | **Carry** — document only |

No open code blockers for wave-signoff.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Failure-path stage metrics | `RunOrchestrator` + `MetricsEmitter` | after non-success | FAILED + duration | failed stage + event; run `failed` | No workflow advance | W2 |
| Wave cycle-time field | RunStore + APIs | finalize | accept → stop/fail/complete | `runs.wave_duration_ms` | Live proven | W2 |
| Docker/local bridge readiness | spike + Dockerfile | inspection | image + key + cwd | pass note | No key in image | W2 |
| Implement-lane live verify | `verify_implement_lane` | opt-in module | config + worker + key | four stages; `stopped`; evidence | Not in `verify_all` | W2 Scenario A |
| Pin walker (env + API + pin; no YAML programme file) | `RunOrchestrator` | wave-start Enter-at | `start_node` + runner/model | multi-hop until gate | Lane handoffs `human_checkpoint: false` | W2 |
| Human Alembic `wave_duration_ms` | `7e79269bd50b_…` | Alembic upgrade | nullable Integer | schema ↔ ORM | Human-owned | W2 |

## PR instructions

```
Branch:   feature/INIT-GATEFLOW-003-w1-ground-report
PR title: [INIT-GATEFLOW-003 W1] wave-signoff — human_approved
Issue:    #21
Spec:     docs/specification/product/INIT-GATEFLOW-003-gateflow.md
Verify:   make check && make test
          (opt-in) .venv/bin/python -m tests.verify.verify_implement_lane
```

Implementation already merged: https://github.com/drivestream-lab/gateflow/pull/44

After this signoff PR merges:
  as-built INIT-GATEFLOW-003 W1 = **human_approved**
  → `/pre-implement` for W2

## Ready for human checkpoint?

**yes — human_approved** (2026-07-25). Verifier accepted W1 ground report + live implement-lane prove-it; as-built updated on this branch.

Human must:
- [x] Review FR checklist — all pass or explicitly deferred
- [x] Review §Contracts produced — accurate and complete for next wave
- [x] Confirm live RunStore evidence acceptable
- [x] Mark as-built: INIT-GATEFLOW-003 W1 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W1.md
    digest: sha256:90b29eddefe5b63da0b4181c98ea76bfc7d84273f54ba5fcf18ef26850d7d990
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-003
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/21
    branch: feature/INIT-GATEFLOW-003-w1-ground-report
    contracts_produced: 6
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    unit_tests: 110 passed
    docker_spike: pass
    human_alembic_revision: 7e79269bd50b
    live_implement_lane: pass
    live_run_id: de780ba2-7841-4827-ad69-362358a8176d
    live_wave_duration_ms: 492608
    as_built_status: human_approved
    discrepancies_open: [D-W0-M1]
    discrepancies_closed: [D-W1-L1, D-W1-M1]
    implementation_pr: https://github.com/drivestream-lab/gateflow/pull/44
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
```
