# Ground report — INIT-GATEFLOW-001 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Operational control plane |
| Spec | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` |
| Date | 2026-07-23 |
| Branch | `feature/INIT-GATEFLOW-001-w1-operational-control-plane` |
| Status | **human_approved** |
| Review deadline | 2026-07-27 |
| Deciders | Tech lead / reviewer: @nikd10x — human LGTM recorded 2026-07-23 (live `verify_all` green) |

## Automated check output

`ground_command`: N/A. Evidence: `make check`, `make test`, `.venv/bin/python -m tests.verify.verify_all`.

### `make check` (exit 0)

```
.venv/bin/black --line-length 100 src/ tests/
All done! 115 files left unchanged.
.venv/bin/ruff check --fix src/ tests/
All checks passed!
.venv/bin/pyright
0 errors, 0 warnings, 0 informations
.venv/bin/lint-imports
Layered architecture — no cross-layer imports KEPT
Contracts: 1 kept, 0 broken.
```

### `make test` (exit 0)

```
collected 38 items
38 passed
```

(Includes fix: programme-token unit tests force `PROGRAMME_SERVICE_TOKEN` so a sourced `.env` cannot desync Bearer vs settings singleton.)

### Live verify `.venv/bin/python -m tests.verify.verify_all` (exit 0)

```
[OK] verify_health passed
[OK] verify_webhook passed (401 / 202 / duplicate)
[OK] verify_status_metrics passed (401 / 404 / 200 metrics shape)
[OK] verify_wave_start passed (labelled enqueue + metrics)
[OK] verify_all passed
```

Note: wave smoke proves labelled webhook enqueue + programme-token APIs; full worker→PolicyEngine→Forge stop-comment dogfood remains operator soak (documented in verify output).

## FR checklist

W1 scope (plan): FR-2, FR-3, FR-4, FR-7 (policy), FR-8, FR-9, FR-10, FR-11, FR-13, FR-14, FR-15, FR-16, FR-17, FR-19. Prior W0 FRs remain in force.

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-2 | Concurrent active-run reject | `TriggerRouter` PC-06; `test_concurrent_*`; orchestrator unit | **pass** (unit) |
| FR-3 | Programme trigger label | `TriggerRouter` + `programme.yaml` `trigger.label`; `verify_wave_start` | **pass** |
| FR-4 | Wave-run precondition checklist | PC-01…04 + PC-06 in `trigger_router.py`; unit failures | **pass** (unit); live full checklist soak partial |
| FR-7 | PolicyEngine pin-driven dispatch | `PolicyEngine.evaluate_dispatch`; unit dispatch/block/stop | **pass** (unit) |
| FR-8 | Stop on human/external/decision/terminal | Policy stop node types + handoff flags; orchestrator stop unit | **pass** (unit) |
| FR-9 | Cursor AgentRunner fail-closed | `CursorAgentRunner.run_skill` stub; orchestrator agent-failure unit | **partial** — stub/fail-closed; no live Cursor SDK |
| FR-10 | Findings retry budget | PolicyEngine budget stop unit | **pass** (unit) |
| FR-11 | Notifier run-event comments | `Notifier.post_run_event_comment` → ForgeClient | **pass** (unit/inspection); live comment not in verify_all |
| FR-13 | Metrics aggregate API | `GET /api/v1/metrics/runs`; `verify_status_metrics` | **pass** (shape); p50/p95 from events unit/inspection |
| FR-14 | Tools none | `StageToolResolver`; `test_stage_tools` | **pass** |
| FR-15 | Programme-token status API | `GET /api/v1/runs/{id}`; unit + verify | **pass** |
| FR-16 | Runner/model from programme config | Programme config keys + orchestrator stage fields | **pass** (inspection/unit path) |
| FR-17 | API + worker dual process | `src.main` + `src.worker_main` + runbook; job worker unit | **partial** — code+docs; live worker claim not in verify_all |
| FR-19 | Orchestrate-new-repo runbook | `docs/runbooks/orchestrate-new-initiative-repo.md` | **pass** (inspection) |
| FR-1/5/6/12/18 | W0 baselines | Ground-Report-W0 + still green verify | **pass** (carried) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Dual process; jobs in Postgres | ADR-001 | **pass** (code + runbook) |
| Three trust zones; programme token on status/metrics | ADR-002 | **pass** — `public_paths` includes `/api/v1/runs`, `/api/v1/metrics` |
| Forge/AgentRunner/launchpad = infra; policy/orchestrator = business | ADR-003 | **pass** |
| Programme config authority; secrets in env | ADR-004 | **pass** — `PROGRAMME_SERVICE_TOKEN` in env |
| Models in `src/models/`; repos map ORM→Pydantic | pydantic-schemas / repository-pattern | **pass** |
| import-linter layers | python-tooling | **pass** |
| Cohesive RunStore schema/repo family (not 1:1 file rule) | repository-pattern Placement | **pass** — accepted aggregate clubbing |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| ProgrammeConfig load | Ground-Report-W0 | yes |
| Webhook enqueue | Ground-Report-W0 | yes — still live-verified |
| Job claim stub → now orchestrator | Ground-Report-W0 | yes — worker calls `RunOrchestrator.process_job` |
| RunStore persistence | Ground-Report-W0 | yes — `find_active_run` / `update_run` added |
| HandoffReader / WorkflowEngine resolve | Ground-Report-W0 | yes — used by policy/orchestrator |
| ForgeClient comments + forbids | Ground-Report-W0 | yes — Notifier path |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|----------|
| D-W1-A1 | FR-9 | AgentRunner is fail-closed **stub** (mock-*/GATEFLOW_AGENT_STUB); real Cursor SDK not proven live | Medium — accept if PE accepts H1 stub + fail-closed |
| D-W1-V1 | FR-4/8/11/17 | Live verify does not assert worker claim → stop comment → RunStore timeline end-to-end | Medium — deferred dogfood / operator soak |
| D-W1-T1 | FR-15 | Unit tests flaked when shell `.env` token ≠ test Bearer; fixed by forcing env in fixtures | Low — fixed this ground run |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Trigger authorize | TriggerRouter | `authorize_and_check` | event type, delivery id, payload, programme config | authorized flag + context or precondition failures | Label from programme config only; PC-06 concurrent reject | W2+ / ops |
| Policy decision | PolicyEngine | `evaluate_dispatch` | handoff, trigger, config, retry counter | decision dispatch\|stop\|block + optional next node | Dispatch only skill+orchestrated; pin failure → block | W2+ |
| Job orchestration | RunOrchestrator | `process_job` | claimed job DTO | run summary (run id, terminal status, dispatched) | No dispatch when policy denies; agent fail → failed no advance | W2+ |
| Run event notify | Notifier | `post_run_event_comment` | org/repo/issue + run event fields | comment id or notify_pending | Comments only; no gate labels | W2+ |
| Tool resolve | StageToolResolver | `resolve` | node id + programme tools.slots | ToolContext (H1 empty slots) | No hardcoded node→slot map | H2 tools |
| Agent run | CursorAgentRunner | `run_skill` | workspace, skill id, prompt context, model profile | AgentRunResult | Fail-closed; launchpad sync before call | Real SDK spike |
| Harness sync | LaunchpadClient | `sync_harness` | workspace path | void / error if path missing | Called before agent dispatch | CTR-04 deepen |
| Run status read | runs route + MetricsEmitter | `GET /api/v1/runs/{run_id}` | Bearer programme token + run id | RunStatusResponse | 401 without/invalid token; 404 unknown | gateflow-ops |
| Metrics aggregate | metrics route + MetricsEmitter | `GET /api/v1/metrics/runs` | Bearer programme token | retention_days + by_workflow_node p50/p95 | Read-only | gateflow-ops |
| Wave smoke verify | tests.verify | `verify_all` / `verify_wave_start` | running API + secrets | exit 0 | Labelled enqueue + token APIs | dogfood |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit before PR is marked ready). Ground report and code are reviewed together on the same PR.

Branch:   `feature/INIT-GATEFLOW-001-w1-operational-control-plane`
PR title: `[INIT-GATEFLOW-001 W1] operational-control-plane — implementation + ground report`
Required reviewer: prayog-pe-team / CODEOWNERS
Review deadline: 2026-07-27

After reviewer approves:
  Update as-built: W1 → human_approved
  Merge PR
  → next initiative wave / Phase B dogfood (no W2 in this INIT plan)

## Ready for human checkpoint?

**yes — human_approved** (2026-07-23). Live `verify_all` re-validated by human; D-W1-A1 / D-W1-V1 accepted as deferred for H1 stub / dogfood soak.

- [x] Review FR checklist — all pass or explicitly deferred
- [x] Review §Contracts produced — accurate for consumers
- [x] Mark as-built: INIT-GATEFLOW-001 W1 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: human_approved
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W1.md
    digest: sha256:3f4948d20c0be19d148f34d205f901298f66744b22df7e67b7ee106c8cba34db
  blockers: []
  signals:
    wave: W1
    contracts_produced: 10
    unit_pass: true
    live_verify_pass: true
    verify_command: .venv/bin/python -m tests.verify.verify_all
    deferred:
      - D-W1-A1
      - D-W1-V1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/7
    branch: feature/INIT-GATEFLOW-001-w1-operational-control-plane
  next_candidates: []
  human_checkpoint: true
  external_action: false
```
