# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-07-23 |
| Source | INIT-GATEFLOW-001 W1 on `feature/INIT-GATEFLOW-001-w1-operational-control-plane` |

## Testing harness

| Layer | Command / path | Status |
|-------|----------------|--------|
| Toolchain | `make check` | Wired (black, ruff, pyright, import-linter) |
| Unit | `make test` → `tests/unit/` | W0 + W1 control-plane (38 tests) |
| Live verify | `tests/verify/verify_all.py` | health, webhook, status/metrics, wave smoke |
| CI | `.github/workflows/ci.yml` | Placeholder |

## Capability matrix

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Health liveness | scaffold | `GET /health` | `test_health` | `verify_health` | In `verify_all` |
| GitHub App webhooks | FR-1 | `POST /webhooks/github` | `test_webhook_ingress` | `verify_webhook` | Live pass (W0) |
| RunStore + jobs | FR-5, FR-17 | ORM/repos + migration | `test_run_store_models` | via webhook | |
| TriggerRouter + preconditions | FR-2–4 | `trigger_router.py` | `test_trigger_policy` | `verify_wave_smoke` (enqueue) | Concurrent = PC-06 |
| PolicyEngine | FR-7,8,10 | `policy_engine.py` | `test_trigger_policy` | — | Pin-driven; no allowlists |
| RunOrchestrator + Notifier | FR-2,9,11 | `run_orchestrator.py`, `notifier.py` | `test_run_orchestrator` | worker manual | |
| AgentRunner + launchpad | FR-9,17 | `cursor_agent_runner.py`, `launchpad_client.py` | via orchestrator tests | — | Stub fail-closed |
| Tools none | FR-14 | `stage_tool_resolver.py` | `test_stage_tools` | — | |
| Status + metrics APIs | FR-13,15 | `runs_routes`, `metrics_routes` | `test_programme_token_api` | `verify_status_metrics` | Programme token |
| Programme config | FR-18 | `config/programme.yaml` | `test_programme_config` | — | |
| W1 runbook | FR-19 | `docs/runbooks/orchestrate-new-initiative-repo.md` | — | inspection | |
| API + worker runtime | FR-17 | `src.main` + `src.worker_main` | `test_job_worker` | `docs/runbooks/w1-runtime-api-worker.md` | Clears D-W0-V2 docs path |

## Wave status

| Wave | Plan | Ground report | as-built status |
|------|------|---------------|-----------------|
| W0 | Control-plane skeleton | `Ground-Report-INIT-GATEFLOW-001-W0.md` | **human_approved** |
| W1 | Operational control plane | pending `/ground-spec` | **in_progress** — code + unit green; live verify pending human stack |

## Verdict

**W1 implementation is code-complete on the feature branch** (trigger, policy, orchestrator, notifier, tools, AgentRunner/launchpad stubs, status/metrics, verify scripts, runbooks). Do **not** mark `human_approved` until `/ground-spec` and human checkpoint.
