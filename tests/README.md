# Tests for gateflow

## Structure

```
tests/
  unit/        Pure unit tests — no real infra, no network calls.
               Run: make test
  verify/      Live verify scripts (not collected by make test).
  _helpers/    Shared fixtures and helpers (e.g. verify preflight).
```

## Running

```bash
# Unit only (CI gate)
make check && make test

# Live verify (integration) — requires running API + Postgres with RunStore migration:
# docker compose -f docker/docker-compose.yml up -d
# ./scripts/run_postgres_migration.sh head
#   (INIT-GATEFLOW-002 W0: apply human Alembic for runs.wave_id — see
#    docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-002-W0-wave-id.md)
# .venv/bin/python -m src.main
# optional worker: .venv/bin/python -m src.worker_main
# set -a && source .env && set +a
#   needs GITHUB_WEBHOOK_SECRET + PROGRAMME_SERVICE_TOKEN
# .venv/bin/python -m tests.verify.verify_all
#
# Individual scripts:
# .venv/bin/python -m tests.verify.verify_health
# .venv/bin/python -m tests.verify.verify_webhook
# .venv/bin/python -m tests.verify.verify_status_metrics
# .venv/bin/python -m tests.verify.verify_wave_start   # primary wave-start (002)
# .venv/bin/python -m tests.verify.verify_pr_thread    # metrics dims + api_trigger (+ optional PR)
# .venv/bin/python -m tests.verify.verify_board        # board APIs (auth + optional forge)
# .venv/bin/python -m tests.verify.verify_wave_smoke   # label ingress ack only
#
# Full PR-at-start live assert (optional):
#   GATEFLOW_VERIFY_WORKER=1 with worker + forge credentials running
```

See also: `docs/runbooks/w1-runtime-api-worker.md`,
`docs/runbooks/laptop-gh-vs-deploy-forgeclient.md`.

## Feature map (INIT-GATEFLOW-001 — delivered)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Health | `python -m tests.verify.verify_health` (in `verify_all`) | `tests/unit/test_health.py` |
| Programme config | — | `tests/unit/test_programme_config.py` |
| RunStore DTOs | — | `tests/unit/test_run_store_models.py` |
| Webhook signature / idempotency | `python -m tests.verify.verify_webhook` (in `verify_all`) | `tests/unit/test_webhook_ingress.py` |
| Trigger / policy | — | `tests/unit/test_trigger_policy.py` |
| Orchestrator paths | — | `tests/unit/test_run_orchestrator.py` |
| Tools none | — | `tests/unit/test_stage_tools.py` |
| Programme-token status/metrics | `python -m tests.verify.verify_status_metrics` (in `verify_all`) | `tests/unit/test_programme_token_api.py` |
| Labelled wave enqueue smoke | `python -m tests.verify.verify_wave_smoke` (superseded as primary) | — |
| Full live smoke | `python -m tests.verify.verify_all` | — |
| Worker claim | `src.worker_main` (manual / compose) | `tests/unit/test_job_worker.py` |
| Handoff / workflow resolve | — | `tests/unit/test_handoff_workflow.py` |
| ForgeClient forbid gates | — | `tests/unit/test_forge_client.py` |

## Feature map (INIT-GATEFLOW-002 — W0)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Programme config notifier + override coerce | — | `test_programme_config` |
| Adapter registry / SlotValidator fail-closed | — | `test_slot_validator` |
| API wave-start (FR-15) | `python -m tests.verify.verify_wave_start` (in `verify_all`) | `test_wave_start` |
| Label start disabled (FR-15) | unit + note in `verify_wave_start` | `test_trigger_policy` |
| Run list/detail timeline (FR-20) | `verify_wave_start` + `verify_status_metrics` | programme token / wave start tests |
| Stub fail-closed (FR-18) | — | `test_slot_validator`, `test_wave_start` |

## Feature map (INIT-GATEFLOW-002 — W1)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Per-node runner/model resolve + persist (FR-16) | — | `test_node_model_resolver`, `test_run_orchestrator` |
| PR-at-start + ForgeClient (FR-19) | `verify_pr_thread` (PR assert with `GATEFLOW_VERIFY_WORKER=1`) | `test_forge_client`, `test_run_orchestrator` |
| Metrics dims + api_trigger (FR-21/22) | `verify_pr_thread` + `verify_status_metrics` | `test_metrics_emitter` |
| Cursor stub happy path (V-3) | — | `test_cursor_agent_runner` |

## Feature map (INIT-GATEFLOW-002 — W2)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Board APIs create/list/status/link (FR-24) | `verify_board` (in `verify_all`) | `test_board_service`, `test_forge_client_board` |
| Worker isolation — zero board mutations | — | `test_process_job_never_calls_board_forge_mutations` |
| Production gh-free path (FR-25/26a) | inspection checklist | `test_forge_client_source_has_no_gh_subprocess` |
| Laptop gh vs deploy ForgeClient (FR-26b) | docs inspection | — |

## Feature map (INIT-GATEFLOW-003 — W0)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| CursorAgentSettings (`CURSOR_API_KEY`) | — | `test_cursor_agent_settings` |
| Local cursor-sdk AgentRunner (mocked) | Scenario B = W1 | `test_cursor_agent_runner` |
| Start-gate missing key (422) | via wave-start live later | `test_slot_validator`, `test_wave_start` |
| Laptop SDK spike note | inspection | `docs/specification/reports/Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md` |

## Feature map (INIT-GATEFLOW-003 — W1)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Docker/image cursor-sdk bridge spike | inspection | `docs/specification/reports/Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md` |
| Failure-path stage + duration_ms | — | `test_run_orchestrator`, `test_metrics_emitter` |
| `runs.wave_duration_ms` + run detail | Scenario B verify (opt-in) | `test_run_orchestrator` |
| Scenario B live Cursor prove-it | `python -m tests.verify.verify_scenario_b` (opt-in; in `verify_all`) | — |

### Scenario B live verify prereqs

```bash
# Human Alembic first (see DDL-NOTE-INIT-GATEFLOW-003-W1-wave-duration-ms.md):
# ./scripts/create_postgres_migration.sh "add_runs_wave_duration_ms"
# ./scripts/run_postgres_migration.sh head

unset GATEFLOW_AGENT_STUB
export GATEFLOW_VERIFY_SCENARIO_B=1 GATEFLOW_VERIFY_WORKER=1
# CURSOR_API_KEY + PROGRAMME_SERVICE_TOKEN already in .env
# API + worker running; workspace has Scenario B handoff
.venv/bin/python -m tests.verify.verify_scenario_b
```

Without `GATEFLOW_VERIFY_SCENARIO_B=1`, `verify_scenario_b` exits 0 (skip) so
`verify_all` stays green for CI/local smoke without live Cursor.

See spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` /
`docs/specification/product/INIT-GATEFLOW-003-gateflow.md`.
