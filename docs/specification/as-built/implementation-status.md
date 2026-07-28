# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-07-26 |
| Source | INIT-GATEFLOW-003 W1 wave-signoff on `feature/INIT-GATEFLOW-003-w1-ground-report`; lane naming adopted (spec / implement) |

## Engineering lane naming

| Name | Legacy | Status |
|------|--------|--------|
| **implement lane** | Scenario B | Live prove-it **pass** (W1) |
| **spec lane** | Scenario A | W2 — live prove-it waits on next PRD + pin CTR-01 |

## Testing harness

| Layer | Command / path | Status |
|-------|----------------|--------|
| Toolchain | `make check` | Wired (black, ruff, pyright, import-linter) |
| Unit | `make test` → `tests/unit/` | INIT-001 + INIT-002 + INIT-003 W0/W1 (110 passed) |
| Live verify | `tests/verify/verify_all.py` | health…board (implement-lane **separate** opt-in) |
| Implement-lane prove-it | `tests/verify/verify_implement_lane.py` | **Live pass** 2026-07-25 (run `de780ba2-…`) |
| CI | `.github/workflows/ci.yml` | Placeholder |

## Capability matrix (INIT-GATEFLOW-001 — human_approved)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Health liveness | scaffold | `GET /health` | `test_health` | `verify_health` | In `verify_all` |
| GitHub App webhooks | FR-1 | `POST /webhooks/github` | `test_webhook_ingress` | `verify_webhook` | Live pass |
| RunStore + jobs | FR-5, FR-17 | ORM/repos + migration | `test_run_store_models` | via webhook | |
| TriggerRouter + preconditions | FR-2–4 | `trigger_router.py` | `test_trigger_policy` | label start disabled in 002 | |
| PolicyEngine | FR-7,8,10 | `policy_engine.py` | `test_trigger_policy` | — | Pin-driven; no allowlists |
| RunOrchestrator walker + Notifier | FR-2,9,11 | `run_orchestrator.py`, `notifier.py` | `test_run_orchestrator` | worker + implement-lane | Multi-hop until gate; hop cap |
| AgentRunner + launchpad | FR-9,17 | `cursor_agent_runner.py`, `launchpad_client.py` | via orchestrator tests | implement-lane | Live local SDK; launchpad W1 stub sync |
| ToolProvider none | FR-14 | (no StageToolResolver; empty tool context) | — | — | Slot map removed with programme.yaml |
| Status + metrics APIs | FR-13,15 | `runs_routes`, `metrics_routes` | `test_programme_token_api` | `verify_status_metrics` | Programme token |
| Orchestration settings | FR-18 | `orchestration_settings.py` (`GATEFLOW_*`) | wave-start / policy tests | — | notifier + hop cap + findings/metrics |
| W1 runbook | FR-19 | `docs/runbooks/orchestrate-new-initiative-repo.md` | — | inspection | |
| API + worker runtime | FR-17 | `src.main` + `src.worker_main` | `test_job_worker` | `docs/runbooks/w1-runtime-api-worker.md` | Dev reload scoped to `src/*.py` + `.env` |

## Capability matrix (INIT-GATEFLOW-002 W0)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Env notifier + SlotValidator | FR-16/23/18 | `GATEFLOW_NOTIFIER` + `slot_validator.py` | `test_slot_validator`, `test_wave_start` | — | No programme.yaml |
| Adapter registry + SlotValidator | FR-17/18 | `adapter_registry.py`, `slot_validator.py` | `test_slot_validator` | — | ADR-006 |
| API wave-start Enter-at | FR-15 | `POST /api/v1/waves/start` (`start_node`+runner/model) | `test_wave_start` | `verify_wave_start` | Programme token; ADR-005; manual node → 400 |
| Label start disabled | FR-15 | `trigger_router.py` | `test_trigger_policy` | note in wave-start | Webhook may still 202 |
| Run list + detail timeline | FR-20 | `runs_routes`, `metrics_emitter` | token + wave-start tests | `verify_wave_start` | Live pass |
| `runs.wave_id` column | FR-15/20 | ORM/repo + Alembic `bc8abad9a701` | — | via wave-start | Human migration applied |

## Capability matrix (INIT-GATEFLOW-002 W1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Per-node runner/model resolve + persist | FR-16 | `dispatch_plan_models` + `node_model_resolver`; API plan | `test_node_model_resolver`, orchestrator | — | Inherit from wave-start; no programme overrides |
| Pin walker until gate | FR-15 inherit | `run_orchestrator.py` loop + PolicyEngine | `test_run_orchestrator` (multi-hop + hop cap) | implement-lane | `GATEFLOW_MAX_ORCHESTRATED_HOPS` |
| PR-at-start via ForgeClient | FR-19 | `ensure_branch_from_base` + `create_or_update_pull_request`; caller head/base | `test_pr_branch_naming`, `test_forge_client`, orchestrator PR order | `verify_pr_thread` (optional worker) | Head from wave-start identity; no programme `pr.*`; no auto-merge |
| Metrics dims + api_trigger | FR-21/22 | `metrics_emitter.py`; retention via `GATEFLOW_METRICS_RETENTION_DAYS` | `test_metrics_emitter` | status/metrics, implement-lane | `by_runner`, `by_model_id` |
| Cursor happy path (unit double) | FR-17 / V-3 | `cursor_agent_runner.py` | `test_cursor_agent_runner` | — | Unit `mock-*` only (`GATEFLOW_AGENT_STUB` removed) |

## Capability matrix (INIT-GATEFLOW-002 W2)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Board APIs (status/link/create/list) | FR-24 | `board_routes.py`, `board_service.py`; ForgeClient `board_*` | `test_board_service`, `test_forge_client_board` | `verify_board` | Issues MVP + labels; idempotent EPIC/Feature |
| Worker isolation | FR-24 | orchestrator / notifier only PR+comment | `test_process_job_never_calls_board_forge_mutations` | — | Zero board mutations on job complete |
| Production gh-free | FR-25/26a | ForgeClient httpx only | source guard test | checklist | `docs/runbooks/gh-free-production-path-checklist.md` |
| Forge auth modes (`pat` \| `app`) | ADR-003 / TDD §3.5a | `GithubTokenProvider` via InfraModule; `GITHUB_AUTH_MODE` required | `test_github_token_provider`, forge init | verify_board (mode+creds) | Explicit mode; no auto; App discovers single installation |
| Laptop vs deploy transport | FR-26b | runbook | — | inspection | `docs/runbooks/laptop-gh-vs-deploy-forgeclient.md` |
| Q-4 exit gate | A-4 | narrowed MVP doc | — | inspection | `docs/specification/reports/Q4-PERMISSION-MATRIX-INIT-GATEFLOW-002-W2.md` |

## Capability matrix (INIT-GATEFLOW-003 W0)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| `cursor-sdk` + `CursorAgentSettings` | REQ-27/29 | Poetry + `cursor_agent_settings.py` | `test_cursor_agent_settings` | — | `CURSOR_API_KEY` env only |
| Local CursorAgentRunner | REQ-27/31 | `cursor_agent_runner.py` | `test_cursor_agent_runner` | W1 implement-lane **pass** | `LocalAgentOptions(cwd)`; no cloud |
| Start-gate missing key | REQ-28/29 | `slot_validator.py`; API runner/model required | `test_slot_validator`, `test_wave_start` | — | 422 before enqueue |
| Unit doubles quarantine | REQ-28 | `mock-*` skill ids | unit only | not live exit | `GATEFLOW_AGENT_STUB` removed |
| Laptop SDK spike | REQ-27 / TDD §3.3 | spike report | inspection | — | `Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md` |

## Capability matrix (INIT-GATEFLOW-003 W1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Docker cursor-sdk bridge spike | REQ-27 / TDD §3.3 | spike report | inspection | — | `Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md` **pass** |
| Failure-path stage + duration | REQ-29/30 | `run_orchestrator.py`, `metrics_emitter.py` | `test_run_orchestrator`, `test_metrics_emitter` | — | FF-05 |
| `runs.wave_duration_ms` | REQ-30 | ORM/DTO/API + finalize | `test_run_orchestrator` | `verify_implement_lane` **pass** | Alembic `7e79269bd50b`; live `492608` ms |
| Implement-lane live prove-it | REQ-27/31 | `verify_implement_lane.py` | — | **pass** 2026-07-25 | Full chain → `stopped` at `wave-human-decision`; D-W1-L1 closed |
| Pin walker (no programme.yaml) | inherit FR-15 | `run_orchestrator.py` + pin outcomes | multi-hop + hop-cap unit | implement-lane | Enter-at `pre-implement`; lane handoffs `human_checkpoint: false` |

## Wave status

| Initiative / Wave | Plan | Ground report | as-built status |
|-------------------|------|---------------|-----------------|
| INIT-001 W0 | Control-plane skeleton | `Ground-Report-INIT-GATEFLOW-001-W0.md` | **human_approved** |
| INIT-001 W1 | Operational control plane | `Ground-Report-INIT-GATEFLOW-001-W1.md` | **human_approved** |
| INIT-002 W0 | API wave-start + run list/detail + stubs | `Ground-Report-INIT-GATEFLOW-002-W0.md` | **human_approved** |
| INIT-002 W1 | Per-node model + PR-at-start + metrics | `Ground-Report-INIT-GATEFLOW-002-W1.md` | **human_approved** |
| INIT-002 W2 | Board APIs + gh-free deploy path | `Ground-Report-INIT-GATEFLOW-002-W2.md` | **human_approved** |
| INIT-003 W0 | Cursor SDK skeleton + start-gate | `Ground-Report-INIT-GATEFLOW-003-W0.md` | **human_approved** |
| INIT-003 W1 | Implement-lane prove-it + cycle-time + Docker spike | `Ground-Report-INIT-GATEFLOW-003-W1.md` | **human_approved** |
| INIT-005 W0 | Bound-input resolve/render + thin Cursor + handoff_path | — | **in_progress** (code on `feature/INIT-GATEFLOW-005-w0-bound-input`; human Alembic pending for `runs.handoff_path`, `stages.prompt_id`, `stages.prompt_revision`) |

## Verdict

INIT-GATEFLOW-001 remains **human_approved**. INIT-GATEFLOW-002 **W0**, **W1**, and **W2** are
**human_approved** (2026-07-24). INIT-GATEFLOW-003 **W0** is **human_approved** (2026-07-24).

INIT-GATEFLOW-003 **W1** is **human_approved** (2026-07-25): live **implement-lane** prove-it
pass (run `de780ba2-7841-4827-ad69-362358a8176d`, four Cursor stages success, terminal
`stopped` at `wave-human-decision`, `wave_duration_ms=492608`). Implementation on `develop`
via #44; wave-signoff on `feature/INIT-GATEFLOW-003-w1-ground-report`.

**Lane naming (2026-07-26):** prefer **spec lane** / **implement lane** over Scenario A/B.

**INIT-GATEFLOW-005 (2026-07-28):** W0 implementation in progress — PromptResolver, message-only
Cursor path, `GATEFLOW_HANDOFF_ROOT` baton define/store, required `ticket_id`. Live prove-it
blocked until human Alembic applies new RunStore columns. W1 ingest-only still pending.
