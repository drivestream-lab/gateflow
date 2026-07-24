# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-07-24 |
| Source | INIT-GATEFLOW-002 W2 on `feature/INIT-GATEFLOW-002-w2-board` |

## Testing harness

| Layer | Command / path | Status |
|-------|----------------|--------|
| Toolchain | `make check` | Wired (black, ruff, pyright, import-linter) |
| Unit | `make test` → `tests/unit/` | INIT-001 + INIT-002 W0/W1/W2 |
| Live verify | `tests/verify/verify_all.py` | health, webhook, status/metrics, wave-start, pr_thread, **board** |
| CI | `.github/workflows/ci.yml` | Placeholder |

## Capability matrix (INIT-GATEFLOW-001 — human_approved)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Health liveness | scaffold | `GET /health` | `test_health` | `verify_health` | In `verify_all` |
| GitHub App webhooks | FR-1 | `POST /webhooks/github` | `test_webhook_ingress` | `verify_webhook` | Live pass |
| RunStore + jobs | FR-5, FR-17 | ORM/repos + migration | `test_run_store_models` | via webhook | |
| TriggerRouter + preconditions | FR-2–4 | `trigger_router.py` | `test_trigger_policy` | label start disabled in 002 | |
| PolicyEngine | FR-7,8,10 | `policy_engine.py` | `test_trigger_policy` | — | Pin-driven; no allowlists |
| RunOrchestrator + Notifier | FR-2,9,11 | `run_orchestrator.py`, `notifier.py` | `test_run_orchestrator` | worker manual | |
| AgentRunner + launchpad | FR-9,17 | `cursor_agent_runner.py`, `launchpad_client.py` | via orchestrator tests | — | Stub fail-closed |
| Tools none | FR-14 | `stage_tool_resolver.py` | `test_stage_tools` | — | |
| Status + metrics APIs | FR-13,15 | `runs_routes`, `metrics_routes` | `test_programme_token_api` | `verify_status_metrics` | Programme token |
| Programme config | FR-18 | `config/programme.yaml` | `test_programme_config` | — | |
| W1 runbook | FR-19 | `docs/runbooks/orchestrate-new-initiative-repo.md` | — | inspection | |
| API + worker runtime | FR-17 | `src.main` + `src.worker_main` | `test_job_worker` | `docs/runbooks/w1-runtime-api-worker.md` | |

## Capability matrix (INIT-GATEFLOW-002 W0)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Programme notifier + override coerce | FR-16/23 | `programme_config_models.py` | `test_programme_config` | — | `notifier.default` required |
| Adapter registry + SlotValidator | FR-17/18 | `adapter_registry.py`, `slot_validator.py` | `test_slot_validator` | — | ADR-006 |
| API wave-start | FR-15 | `POST /api/v1/waves/start` | `test_wave_start` | `verify_wave_start` | Programme token; ADR-005 |
| Label start disabled | FR-15 | `trigger_router.py` | `test_trigger_policy` | note in wave-start | Webhook may still 202 |
| Run list + detail timeline | FR-20 | `runs_routes`, `metrics_emitter` | token + wave-start tests | `verify_wave_start` | Live pass |
| `runs.wave_id` column | FR-15/20 | ORM/repo + Alembic `bc8abad9a701` | — | via wave-start | Human migration applied |

## Capability matrix (INIT-GATEFLOW-002 W1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Per-node runner/model resolve + persist | FR-16 | `node_model_resolver.py`, orchestrator | `test_node_model_resolver`, orchestrator | — | ≥2 overrides in programme.yaml |
| PR-at-start via ForgeClient | FR-19 | `forge_client.create_or_update_pull_request`, orchestrator | `test_forge_client`, orchestrator PR order | `verify_pr_thread` (optional worker) | Same `pr.*` naming; no auto-merge |
| Metrics dims + api_trigger | FR-21/22 | `metrics_emitter.py` | `test_metrics_emitter` | `verify_pr_thread`, status/metrics | `by_runner`, `by_model_id` |
| Cursor happy path (stub) | FR-17 / V-3 | `cursor_agent_runner.py` | `test_cursor_agent_runner` | — | Stub/`mock-*`/`GATEFLOW_AGENT_STUB`; **real SDK deferred** |

## Capability matrix (INIT-GATEFLOW-002 W2)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Board APIs (status/link/create/list) | FR-24 | `board_routes.py`, `board_service.py`, ForgeClient `board_*` | `test_board_service`, `test_forge_client_board` | `verify_board` | Issues MVP + labels; idempotent EPIC/Feature |
| Worker isolation | FR-24 | orchestrator / notifier only PR+comment | `test_process_job_never_calls_board_forge_mutations` | — | Zero board mutations on job complete |
| Production gh-free | FR-25/26a | ForgeClient httpx only | source guard test | checklist | `docs/runbooks/gh-free-production-path-checklist.md` |
| Laptop vs deploy transport | FR-26b | runbook | — | inspection | `docs/runbooks/laptop-gh-vs-deploy-forgeclient.md` |
| Q-4 exit gate | A-4 | narrowed MVP doc | — | inspection | `docs/specification/reports/Q4-PERMISSION-MATRIX-INIT-GATEFLOW-002-W2.md` |

## Wave status

| Initiative / Wave | Plan | Ground report | as-built status |
|-------------------|------|---------------|-----------------|
| INIT-001 W0 | Control-plane skeleton | `Ground-Report-INIT-GATEFLOW-001-W0.md` | **human_approved** |
| INIT-001 W1 | Operational control plane | `Ground-Report-INIT-GATEFLOW-001-W1.md` | **human_approved** |
| INIT-002 W0 | API trigger + run list/detail + stubs | `Ground-Report-INIT-GATEFLOW-002-W0.md` | **human_approved** |
| INIT-002 W1 | Per-node model + PR-at-start + metrics | `Ground-Report-INIT-GATEFLOW-002-W1.md` | **human_approved** |
| INIT-002 W2 | Board APIs + gh-free deploy path | `Ground-Report-INIT-GATEFLOW-002-W2.md` | **human_approved** |

## Verdict

INIT-GATEFLOW-001 remains **human_approved**. INIT-GATEFLOW-002 **W0**, **W1**, and **W2** are
**human_approved** (2026-07-24). No W3 in plan — initiative complete after W2 PR merge.
