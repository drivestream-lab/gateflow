# Ground report — INIT-GATEFLOW-003 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Scenario B prove-it + cycle-time + Docker spike |
| Spec | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` |
| Date | 2026-07-24 |
| Branch | `feature/INIT-GATEFLOW-003-w1-scenario-b` — same branch as wave code |
| Status | **Draft** |
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
84 passed in ~0.5s

$ .venv/bin/python -m tests.verify.verify_scenario_b
[INFO] GATEFLOW_VERIFY_SCENARIO_B not set — skipping live Scenario B
(exit 0 — opt-in skip; not live prove-it evidence)

Docker spike (TASK-W1-01):
docs/specification/reports/Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md — pass
(build + import + ldd + launch_bridge/aclose with CURSOR_API_KEY + cwd)

Human Alembic (DEP-06):
postgres_migrations/versions/7e79269bd50b_add_runs_wave_duration_ms.py
Local DB: alembic_version=7e79269bd50b; runs.wave_duration_ms column present
```

## FR checklist

| FR / REQ | Spec claim (W1 slice) | Verified artifact | Status |
|----------|----------------------|-------------------|--------|
| REQ-27 (W1) | Live Cursor Scenario B (`pre-implement`, `loop-spec`, `verify`, `ground-spec`) with coding-work evidence; no stub as exit | Docker spike **pass**; `verify_scenario_b.py` (opt-in); unit mocked path only | **partial** — infrastructure + verify harness ready; **live opt-in Scenario B not executed** this ground |
| REQ-29 (W1) | Auth/start/crash → `failed`; no workflow advance; stage visibility | `RunOrchestrator` persists failed `StageCreate` + `record_stage_duration(outcome=failed)` then `_finalize_run`; `test_agent_failure_marks_run_failed` | **pass** (unit) |
| REQ-30 (W1) | Stage duration on success **and** failure; `runs.wave_duration_ms` on finalize; expose on run detail/list | Orchestrator compute + update; ORM/DTO/API fields; metrics emitter; human Alembic applied locally; unit asserts failure duration + `wave_duration_ms` | **pass** (code + unit + local migration); live field assert deferred with Scenario B opt-in |
| REQ-31 | Reuse 001/002 control plane; no rebuild | Wave-start / PR-at-start / board / ForgeClient roles unchanged; Cursor infra + orchestrator metrics only | **pass** |
| inherit REQ-28 | Not-live / stub fail-closed at start | SlotValidator + start-gate retained from W0 | **pass** (inherit) |
| Q-3 quarantine | Stub/`mock-*` not live exit evidence | `verify_scenario_b` rejects `GATEFLOW_AGENT_STUB`; README documents unset | **pass** |
| D-W0-L1 carry | Live `finished` / coding work | W0 laptop spike later recorded coding via `gateflow-w0-spike`; Docker bridge **pass**; Scenario B live still open | **partial** — bridge closed; Scenario B coding prove-it still D-W1-L1 |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| AgentRunner in infra; business does not import `cursor_sdk` | ADR-003 + MDC infra-services | **pass** |
| Secrets via env (`CURSOR_API_KEY`), never programme.yaml | ADR-004 | **pass** |
| Fail-closed start-gate for missing Cursor credentials | ADR-006 + REQ-29 #12 | **pass** (inherit W0) |
| Stage/run persistence via repository only | MDC repository-pattern | **pass** |
| Human owns Alembic revision files | MDC database-migrations | **pass** — human revision `7e79269bd50b` present; agent updated ORM only |
| Layered imports (`import-linter`) | MDC python-tooling | **pass** |
| Never pass cloud agent options | Spec + TDD §3.3 | **pass** (inherit) |
| Stub not used as Scenario B exit | Q-3 / verify script | **pass** (guard present) |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|------------------|--------|--------|
| Local Cursor `run_skill` → `AgentRunResult` | Ground-Report-003-W0 | **yes** — consumed for success and failure paths |
| Cursor credentials settings + start-gate | Ground-Report-003-W0 | **yes** |
| Unit doubles quarantine (`mock-*` / stub env) | Ground-Report-003-W0 | **yes** — verify requires stub unset |
| Wave start + job orchestration + stage success metrics | Ground-Report-003-W0 / 002 | **yes** — extended with failure-path stage metrics |
| Scenario B pin `dispatch: orchestrated` | pin `v0.5.0-rc.2` | **yes** — unchanged; W2 Scenario A still separate |
| Laptop SDK spike | Ground-Report-003-W0 | **yes** — Docker spike completed as W1 follow-on |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|----------|
| D-W1-L1 | REQ-27 | Live Scenario B prove-it (`GATEFLOW_VERIFY_SCENARIO_B=1` + worker + coding evidence) **not run** this ground; verify exits 0 on skip | **Medium** — PE must either run opt-in verify before `human_approved` **or** explicitly accept harness+Docker+unit as W1 code exit with live deferred to PE ops |
| D-W1-M1 | REQ-30 | Human migration file `7e79269bd50b_add_runs_wave_duration_ms.py` is **untracked** on the wave branch until committed with the PR | **Low** — applied locally; must land in same wave PR |
| D-W0-M1 | REQ-27 | Programme `cursor/auto` / `cursor/fast` still mapped via `_sdk_model_id` | Low — carry-forward; document only |

No **code** blockers for W1 merge if PE accepts D-W1-L1 disposition. Prefer running opt-in Scenario B before approving when feasible.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Failure-path stage metrics | `RunOrchestrator` + `MetricsEmitter` | `process_job` after `run_skill` non-success | AgentRunner FAILED + duration_ms + resolved runner/model | `StageCreate` failed + `stage_completed` event with `outcome=failed`; then run `failed` | No workflow advance; no pretend success stage | W2 |
| Wave cycle-time field | RunStore + run detail/list APIs | `_compute_wave_duration_ms` / finalize + success complete | run `created_at` → stop/fail/complete timestamp | `runs.wave_duration_ms` (nullable int ms) on header + `GET /api/v1/runs/{id}` / list | Present after human Alembic; computed on finalize paths | W2 metrics honesty |
| Docker/local bridge readiness | spike report + Dockerfile | inspection / image build | Gateflow image + `CURSOR_API_KEY` + cwd | pass/fail spike note | Vendor Node in `cursor-sdk`; slim glibc OK; no key in image | W2 deploy path |
| Scenario B live verify harness | `tests.verify.verify_scenario_b` | module main (opt-in) | env: Scenario B flag, worker flag, key, stub unset, workspace | exit 0 on pass; asserts `runner=cursor`, Scenario B node, `wave_duration_ms`, coding evidence file | Skip (exit 0) without opt-in — **not** live evidence | W2 Scenario A pattern |
| Human Alembic `wave_duration_ms` | `postgres_migrations/versions/7e79269bd50b_…` | Alembic upgrade | nullable Integer column on `runs` | schema aligned with ORM | Human-owned revision; downgrade drops column | W2 |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit before PR is marked ready). Ground report and code are reviewed together on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-003-w1-scenario-b
PR title: [INIT-GATEFLOW-003 W1] scenario-b — implementation + ground report
Issue:    #21
Spec:     docs/specification/product/INIT-GATEFLOW-003-gateflow.md
Verify:   make check && make test
          (opt-in) GATEFLOW_VERIFY_SCENARIO_B=1 GATEFLOW_VERIFY_WORKER=1 \
                   .venv/bin/python -m tests.verify.verify_scenario_b
```

Required reviewer: per CODEOWNERS / prayog-pe-team  
Review deadline: 2026-07-28

Include in the same PR:
- Human Alembic `7e79269bd50b_add_runs_wave_duration_ms.py` (currently untracked until committed)

After reviewer approves:
  Update as-built: INIT-GATEFLOW-003 W1 → **human_approved**
  Merge PR
  → `/pre-implement` for W2 (reads §Contracts produced above; DEP-05 prayog-skills CTR-01 still blocks Scenario A prove-it)

## Ready for human checkpoint?

**yes** — Draft ground report ready for PE wave-signoff.

Human must:
- [ ] Review FR checklist — pass / partial / deferred accepted
- [ ] Review §Contracts produced — accurate and complete for W2
- [ ] Disposition D-W1-L1 (run opt-in Scenario B **or** accept deferral)
- [ ] Confirm human Alembic committed on the wave PR
- [ ] Mark as-built: INIT-GATEFLOW-003 W1 = human_approved *(human only)*

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W1.md
    digest: sha256:fc297dadeb35e7488fe55fc104e0de23ee851f46bad4fbb47bebbc59ea6665dc
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-003
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/21
    branch: feature/INIT-GATEFLOW-003-w1-scenario-b
    contracts_produced: 5
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_scenario_b
    unit_tests: 84 passed
    docker_spike: pass
    human_alembic_revision: 7e79269bd50b
    live_scenario_b: not_run_opt_in_skip
    discrepancies: [D-W1-L1, D-W1-M1, D-W0-M1]
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
```
