# Tests for gateflow

## Lane naming (engineering)

| Name | Legacy | Pin skills (today) | Verify |
|------|--------|--------------------|--------|
| **spec lane** | Scenario A | `spec-draft` … `spec-implementation-plan` (still `manual` until pin) | `verify_spec_lane` (W2; awaits PRD + pin) |
| **implement lane** | Scenario B / engineering-lane | `pre-implement` … `ground-spec` (`orchestrated`) | `verify_implement_lane` |

Both are engineering lanes. Prefer the new names in docs and config.

## Structure

```
tests/
  unit/        Pure unit tests — no real infra, no network calls.
               Run: make test
  verify/      Live verify scripts (not collected by make test).
  debug/       Exploratory live scripts (e.g. ForgeClient .env probe).
  _helpers/    Shared fixtures and helpers (e.g. verify preflight).
  config.yaml.example  Committed example — copy to config.yaml (gitignored)
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
# Prefer: make run  (API + worker; required for wave-start / implement-lane)
# set -a && source .env && set +a
#   needs GITHUB_WEBHOOK_SECRET + PROGRAMME_SERVICE_TOKEN
# .venv/bin/python -m tests.verify.verify_all
#
# Individual scripts:
# .venv/bin/python -m tests.verify.verify_health
#
# ForgeClient .env probe (no API server required — uses PAT/App from .env):
#   cp tests/config.yaml.example tests/config.yaml   # optional org/repo
#   set -a && source .env && set +a
#   .venv/bin/python -m tests.debug.debug_forge_client
#   GATEFLOW_FORGE_PROBE_CLEANUP=0  # leave PR/branch open for inspection
# .venv/bin/python -m tests.verify.verify_webhook
# .venv/bin/python -m tests.verify.verify_status_metrics
# .venv/bin/python -m tests.verify.verify_wave_start   # primary wave-start (002)
# .venv/bin/python -m tests.verify.verify_pr_thread    # metrics dims + api_trigger (+ optional PR)
# .venv/bin/python -m tests.verify.verify_board        # board APIs (auth + optional forge)
# .venv/bin/python -m tests.verify.verify_wave_smoke   # label ingress ack only
#
# Full PR-at-start live assert (optional):
#   set verify.require_worker: true in tests/config.yaml with worker + forge creds
```

## Configuration split

| Concern | Where |
|---------|--------|
| App runtime (DB, Redis, forge auth, Cursor key, programme token, findings/metrics) | `.env` (from `.env.example`) |
| Live verify URLs, org/repo, worker/implement-lane flags, evidence path, Enter-at defaults | `tests/config.yaml` (from `tests/config.yaml.example`) |

```bash
cp tests/config.yaml.example tests/config.yaml
```

Legacy `verify.engineering_lane*` keys in an old `tests/config.yaml` still map to
`implement_lane*` via the config loader.

See also: `docs/runbooks/w1-runtime-api-worker.md`,
`docs/runbooks/laptop-gh-vs-deploy-forgeclient.md`.

## Feature map (INIT-GATEFLOW-001 — delivered)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Health | `python -m tests.verify.verify_health` (in `verify_all`) | `tests/unit/test_health.py` |
| RunStore DTOs | — | `tests/unit/test_run_store_models.py` |
| Webhook signature / idempotency | `python -m tests.verify.verify_webhook` (in `verify_all`) | `tests/unit/test_webhook_ingress.py` |
| Trigger / policy | — | `tests/unit/test_trigger_policy.py` |
| Orchestrator walker | — | `tests/unit/test_run_orchestrator.py` |
| Programme-token status/metrics | `python -m tests.verify.verify_status_metrics` (in `verify_all`) | `tests/unit/test_programme_token_api.py` |
| Labelled wave enqueue smoke | `python -m tests.verify.verify_wave_smoke` (superseded as primary) | — |
| Full live smoke | `python -m tests.verify.verify_all` | — |
| Worker claim | `src.worker_main` (manual / compose) | `tests/unit/test_job_worker.py` |
| Handoff / workflow resolve | — | `tests/unit/test_handoff_workflow.py` |
| ForgeClient forbid gates | — | `tests/unit/test_forge_client.py` |

## Feature map (INIT-GATEFLOW-002 — W0)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Env notifier (`GATEFLOW_NOTIFIER`) | — | `test_wave_start`, `test_slot_validator` |
| Adapter registry / SlotValidator fail-closed | — | `test_slot_validator` |
| API wave-start Enter-at (FR-15) | `python -m tests.verify.verify_wave_start` (in `verify_all`) | `test_wave_start` |
| Label start disabled (FR-15) | unit + note in `verify_wave_start` | `test_trigger_policy` |
| Run list/detail timeline (FR-20) | `verify_wave_start` + `verify_status_metrics` | programme token / wave start tests |
| Stub fail-closed (FR-18) | — | `test_slot_validator`, `test_wave_start` |

## Feature map (INIT-GATEFLOW-002 — W1)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Dispatch plan resolve + persist (FR-16) | — | `test_node_model_resolver`, `test_run_orchestrator` |
| Pin walker until gate + hop cap | — | `test_run_orchestrator` (multi-hop / hop-cap) |
| PR-at-start + ForgeClient (FR-19) | `verify_pr_thread` (PR assert with `verify.require_worker: true`) | `test_pr_branch_naming`, `test_forge_client`, `test_run_orchestrator` |
| Metrics dims + api_trigger (FR-21/22) | `verify_pr_thread` + `verify_status_metrics` | `test_metrics_emitter` |
| Cursor stub happy path (V-3) | — | `test_cursor_agent_runner` |

## Feature map (INIT-GATEFLOW-002 — W2)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Board APIs create/list/status/link (FR-24) | `verify_board` (in `verify_all`) | `test_board_service`, `test_forge_client_board` |
| Forge auth modes `pat` \| `app` (ADR-003) | `verify_board` when mode+creds set | `test_github_token_provider`, `test_forge_client` |
| Worker isolation — zero board mutations | — | `test_process_job_never_calls_board_forge_mutations` |
| Production gh-free path (FR-25/26a) | inspection checklist | `test_forge_client_source_has_no_gh_subprocess` |
| Laptop gh vs deploy ForgeClient (FR-26b) | docs inspection | — |

## Feature map (INIT-GATEFLOW-003 — W0)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| CursorAgentSettings (`CURSOR_API_KEY`) | — | `test_cursor_agent_settings` |
| Local cursor-sdk AgentRunner (mocked) | implement-lane = W1 | `test_cursor_agent_runner` |
| Start-gate missing key (422) | via wave-start live later | `test_slot_validator`, `test_wave_start` |
| Laptop SDK spike note | inspection | `docs/specification/reports/Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md` |

## Feature map (INIT-GATEFLOW-003 — W1)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Docker/image cursor-sdk bridge spike | inspection | `docs/specification/reports/Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md` |
| Failure-path stage + duration_ms | — | `test_run_orchestrator`, `test_metrics_emitter` |
| `runs.wave_duration_ms` + run detail | implement-lane verify (opt-in) | `test_run_orchestrator` |
| Implement-lane live Cursor prove-it | `python -m tests.verify.verify_implement_lane` (opt-in; **not** in `verify_all`) | — |

## Feature map (INIT-GATEFLOW-005 — BOUNDINPUT)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| `GATEFLOW_HANDOFF_ROOT` settings | — | `test_orchestration_settings` |
| PromptResolver resolve/bind/render | — | `test_prompt_resolver` |
| Required `ticket_id` on wave-start | `verify_wave_start` (supply ticket) | `test_wave_start` |
| Message-only Cursor + anti-hardcode | — | `test_cursor_agent_runner` |
| Stage `prompt_id` / `prompt_revision` | `verify_implement_lane` (assert fields) | `test_run_orchestrator` |

Requires absolute `GATEFLOW_HANDOFF_ROOT` in `.env` and human Alembic for
`runs.handoff_path` + `stages.prompt_id` / `stages.prompt_revision` before live prove-it.

### Implement-lane live verify prereqs

Pin chain (Enter-at `pre-implement`):  
`pre-implement` → `loop-spec` → `verify` → `ground-spec` → STOP at `wave-human-decision`.

App secrets in `.env`; verify flags in `tests/config.yaml`. Shared Postgres/Redis via
`POSTGRES_*` / `REDIS_*` — do not require `docker compose` when those already
point at shared infra.

```bash
# Ensure migration applied (wave_duration_ms):
# ./scripts/run_postgres_migration.sh head

cp tests/config.yaml.example tests/config.yaml
# edit tests/config.yaml:
#   verify.implement_lane: true
#   verify.require_worker: true
#   verify.implement_lane_evidence: /absolute/path/...
#   verify.start_node: pre-implement

# Terminal — API + worker
make run

# Separate terminal — lane prove-it only (do not mix with verify_all while Cursor runs)
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_implement_lane
```

Keep `verify.implement_lane: false` for routine smoke.

See spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` /
`docs/specification/product/INIT-GATEFLOW-003-gateflow.md`.
