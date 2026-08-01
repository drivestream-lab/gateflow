# Tests for gateflow

## Lane naming

| Name | Legacy name | Pin skills (today) | Verify |
|------|-------------|--------------------|--------|
| **spec lane** | Scenario A | `spec-draft` … `spec-implementation-plan` | `verify_spec_lane` (scaffold; W2) |
| **implement lane** | Scenario B | `pre-implement` → `loop-spec` → automated `wave-pr-action` → `live-verify` STOP | `verify_implement_lane` |

Both are wave-shaped Gateflow features.

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
# .venv/bin/python -m tests.verify.verify_pr_thread    # metrics dims + api_trigger (no PR-at-start)
# .venv/bin/python -m tests.verify.verify_board        # board APIs (auth + optional forge)
# .venv/bin/python -m tests.verify.verify_implement_lane  # opt-in deep wave (Draft PR via wave-pr-action)
# .venv/bin/python -m tests.verify.verify_spec_lane       # opt-in (scaffold until W2)
#
# Draft PR live timing (INIT-008): use verify_implement_lane, not verify_pr_thread.
#   set gateflow.require_worker: true + worker + forge creds for deep lane prove-it
```

## Configuration split

| Concern | Where |
|---------|--------|
| Gateflow **runtime** (DB, Redis, forge, `CURSOR_API_KEY`, handoff root, …) | `.env` (process that runs `make run`) |
| Verify **client** secrets (`PROGRAMME_SERVICE_TOKEN`, `GITHUB_WEBHOOK_SECRET`) | `.env` for now (verify signs webhooks / calls API) |
| Verify **target + features** | `tests/config.yaml` (from `tests/config.yaml.example`) |

```yaml
# tests/config.yaml (gitignored)
gateflow:                 # client → running product (verify_all needs this)
  base_url: …
  require_worker: …
  org / repo / base_branch: …

features:                 # omit sections you do not run
  implement_lane:         # deep wave prove-it (not in verify_all)
    enabled: …
    evidence: …           # [VERIFY only]
    timeout_s: …
    wave_start: …         # [API] body for this feature only
  spec_lane: …            # same shape when ready

forge: …                  # debug_forge_client only
```

`verify_all` = product smoke (uses `gateflow:` + ephemeral wave identity).  
Deep lanes read **only** their `features.*` wave_start — no shared flat `ticket_id`/`start_node`.

```bash
cp tests/config.yaml.example tests/config.yaml
```

Legacy flat `verify:` keys still migrate via the config loader into `gateflow:` /
`features.implement_lane`. Prefer the nested shape in `config.yaml.example`.

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
| API wave-start + label ingress ack | `python -m tests.verify.verify_wave_start` (in `verify_all`) | — |
| Full live smoke (product) | `python -m tests.verify.verify_all` | — |
| Worker claim | `src.worker_main` (manual / compose) | `tests/unit/test_job_worker.py` |
| Handoff / workflow resolve | — | `tests/unit/test_handoff_workflow.py` |
| Pin `forge:` policy + handoff.forge | — | `tests/unit/test_forge_policy.py` |
| Workspace commit path filter | — | `tests/unit/test_workspace_commit_paths.py` |
| ForgeClient forbid gates + commit_paths | — | `tests/unit/test_forge_client.py` |

## Feature map (INIT-GATEFLOW-002 — W0)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Env notifier (`GATEFLOW_NOTIFIER`) | — | `test_wave_start`, `test_slot_validator` |
| Adapter registry / SlotValidator fail-closed | — | `test_slot_validator` |
| API implement-lane start Enter-at (FR-15 / REQ-14) | `python -m tests.verify.verify_wave_start` (in `verify_all`) | `test_wave_start` |
| API closeout start Enter-at `learning-extract` (INIT-007 W0) | `python -m tests.verify.verify_wave_closeout` (smoke: `enabled` + `pr_number`) | `test_wave_closeout` |
| Learning Postgres ingest after `learning-extract` (INIT-007 W1) | W2 dogfood artifact assert; DB rows via Live-Verify SQL (no learning HTTP) | `test_learning_ingest` |
| Pass-2 closeout dogfood → `wave-signoff` (INIT-007 W2) | `python -m tests.verify.verify_wave_closeout` with `dogfood: true` + `require_worker: true` | — |
| API spec-lane start (REQ-16/17) | `python -m tests.verify.verify_spec_lane` (opt-in) | `test_wave_start`, `test_meta_pr_intake` |
| Label start disabled (FR-15) | unit + note in `verify_wave_start` | `test_trigger_policy` |
| Run list/detail timeline (FR-20) | `verify_wave_start` + `verify_status_metrics` | programme token / wave start tests |
| Stub fail-closed (FR-18) | — | `test_slot_validator`, `test_wave_start` |

## Feature map (INIT-GATEFLOW-002 — W1)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Dispatch plan resolve + persist (FR-16) | — | `test_node_model_resolver`, `test_run_orchestrator` |
| Pin walker until gate + hop cap | — | `test_run_orchestrator` (multi-hop / hop-cap) |
| PR-at-start + ForgeClient (FR-19) | **superseded for implement jobs by INIT-008 W1** — ensure_branch-only at start; Draft PR via automated `wave-pr-action` | `test_pr_branch_naming`, `test_forge_client`, `test_run_orchestrator` (`test_ensure_branch_before_stage_*`) |
| Metrics dims + api_trigger (FR-21/22) | `verify_pr_thread` + `verify_status_metrics` | `test_metrics_emitter` |
| Cursor stub happy path (V-3) | — | `test_cursor_agent_runner` |

## Feature map (INIT-GATEFLOW-002 — W2)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Board APIs create/list/status/link (FR-24) | `verify_board` (in `verify_all`) | `test_board_service`, `test_forge_client_board` |
| WorkManifest pin contract before board seed (INIT-008 W2) | `verify_board` asserts launchpad/v1 reject; authorize path unit | `test_forge_action_service` (`prayog_v1` / `rejects_launchpad_v1`), `test_forge_merge` |
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
| Spec-lane live prove-it | `python -m tests.verify.verify_spec_lane` (scaffold; **not** in `verify_all`) | — |

## Feature map (INIT-GATEFLOW-005 — BOUNDINPUT)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| `GATEFLOW_HANDOFF_ROOT` settings | — | `test_orchestration_settings` |
| PromptResolver resolve/bind/render | — | `test_prompt_resolver` |
| Required `ticket_id` on wave-start | `verify_wave_start` (supply ticket) | `test_wave_start` |
| Message-only Cursor + anti-hardcode | — | `test_cursor_agent_runner` |
| Stage `prompt_id` / `prompt_revision` | `verify_implement_lane` (assert fields) | `test_run_orchestrator` |
| Ingest from stored `handoff_path` only (REQ-8b) | `verify_implement_lane` (W1 live) | `test_handoff_workflow`, `test_run_orchestrator` |
| Dual-run baton isolation | — | `test_dual_run_isolation_distinct_handoff_paths` |
| Stage forge workspace publish (ADR-009 authority) | `verify_implement_lane` (assert `stage_commit` / non-bootstrap tip) | `test_forge_policy`, `test_workspace_commit_paths`, `test_publish_stage_workspace_*` |
| External-action forge authorize (as-built / pin) | — (API authorize after STOP) | `test_forge_merge`, `test_forge_action_service`, `test_forge_client` open_draft_pr |
| Sparse PR run-event comments (as-built) | — | `test_notifier` (stage hops skip Forge comment; `run_stopped` posts) |

Requires absolute `GATEFLOW_HANDOFF_ROOT` in `.env` and human Alembic for
`runs.handoff_path` + `stages.prompt_id` / `stages.prompt_revision` before live prove-it.
Packaged-skill automate ingest SSOT is the stored baton path under that root
(`{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md`) — not ambient repo globs/mtime.

### Implement-lane live verify prereqs

Pin chain (Enter-at `pre-implement`; Pass 1):  
`pre-implement` → `loop-spec` → STOP at `live-verify`  
(`verify` is `dispatch: manual`; closeout Enter-at `learning-extract` → `ground-spec`
is INIT-GATEFLOW-007).

App secrets in `.env`; verify flags in `tests/config.yaml`. Shared Postgres/Redis via
`POSTGRES_*` / `REDIS_*` — do not require `docker compose` when those already
point at shared infra.

```bash
# Ensure migration applied (wave_duration_ms):
# ./scripts/run_postgres_migration.sh head

cp tests/config.yaml.example tests/config.yaml
# edit tests/config.yaml:
#   gateflow.require_worker: true
#   features.implement_lane.enabled: true
#   features.implement_lane.evidence: /absolute/path/...
#   features.implement_lane.wave_start:  # API body for this feature only
#     initiative_id / wave_id / ticket_id / branch_slug / start_node / …

# Terminal — API + worker (CURSOR_API_KEY in Gateflow .env)
make run

# Separate terminal — lane prove-it only (do not mix with verify_all while Cursor runs)
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_implement_lane
```

Keep `features.implement_lane.enabled: false` for routine smoke.

### Closeout start + Pass-2 dogfood (INIT-GATEFLOW-007)

```bash
# Smoke (W0): auth/validation always; happy enqueue when enabled:
#   features.wave_closeout.enabled: true
#   features.wave_closeout.pr_number: <existing wave PR>
#   features.wave_closeout.wave_start.workspace: /absolute/path/on/tip  # optional
#
# Dogfood (W2): after enqueue, poll Pass-2 to wave-signoff:
#   gateflow.require_worker: true
#   features.wave_closeout.dogfood: true
#   features.wave_closeout.timeout_s: 3600
#   features.wave_closeout.assert_learning_artifact: true
#   features.wave_closeout.wave_start.workspace: /absolute/checkout/with/tip
#   features.wave_closeout.wave_start.wave_id: W2   # matches Learning-Extract-*-W2.md

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_wave_closeout
```

Without `enabled: true`, the script still asserts 401 + body validation (smoke).
With `dogfood: true`, requires worker and asserts `learning-extract` + `ground-spec`
success and terminal `stopped` at `wave-signoff` (Learning-Extract file when configured).
Postgres `learning_extracts` row evidence is human Live-Verify (no learning HTTP).

See spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` /
`docs/specification/product/INIT-GATEFLOW-003-gateflow.md`.
See also: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`.
