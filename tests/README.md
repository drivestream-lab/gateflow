# Tests for gateflow

## Lane naming

| Name | Legacy name | Pin skills (today) | Verify |
|------|-------------|--------------------|--------|
| **spec lane** | Scenario A | `spec-draft` … `technical-review-approval` STOP | `verify_spec_lane` — **INIT-009 W1 live proven** |
| **implement lane** | Scenario B | `pre-implement` → `loop-spec` → automated `wave-pr-action` → `wave-acceptance` STOP | `verify_implement_lane` — **INIT-009 W0 live proven** |

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
# .venv/bin/python -m tests.verify.verify_tenant_registry  # INIT-012 W0 tenant registry
# .venv/bin/python -m tests.verify.verify_workspace_lifecycle  # INIT-012 W1 clone/fetch
# .venv/bin/python -m tests.verify.verify_branch_lifecycle     # INIT-012 W2 branch create-or-reuse
# .venv/bin/python -m tests.verify.verify_harness_readiness    # INIT-012 W3 harness-readiness
# .venv/bin/python -m tests.verify.verify_create_tickets  # WorkManifest → EPIC/wave seed
# .venv/bin/python -m tests.verify.verify_implement_lane  # opt-in deep wave (Draft PR via wave-pr-action)
# .venv/bin/python -m tests.verify.verify_spec_lane       # opt-in — INIT-009 W1 live proven
# .venv/bin/python -m tests.verify.verify_wave_closeout   # opt-in — INIT-009 W2 live proven (Pass-2)
# .venv/bin/python -m tests.verify.verify_checkpoint_status  # INIT-011 CAP-01
# authorize live (REQ-15): PE-waived for INIT-009 — unit only; no verify_authorize yet
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
| WorkManifest → EPIC/wave board seed (create_board_tickets projection) | `verify_create_tickets` (opt-in; **not** in `verify_all`) | `test_forge_action_service` (authorize path) |
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
`pre-implement` → `loop-spec` → automated `wave-pr-action` → STOP at `wave-acceptance`  
(no `/verify` content skill; closeout Enter-at `learning-extract` → `ground-spec`
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

## Feature map (INIT-GATEFLOW-010 W1 — board-status + implement In Progress)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| APPLY_FORGE `update_board_status` apply | `verify_implement_lane` (forge_executed timeline) | `test_apply_update_board_status_*`, `test_forge_merge` |
| Implement-start In Progress pre-hop (REQ-04) | `verify_implement_lane` (`assert_board_in_progress`) | `test_implement_wave_start_ok`, `test_implement_in_progress_idempotent_*` |
| No same-run resume after create-tickets (REQ-11) | — | `test_policy_create_tickets_pass_stops_same_run_resume` |
| Pin `ticket` slot merge for board-status hops | — | `test_merge_update_board_status_*` |

`features.implement_lane.assert_board_in_progress: true` (default) checks board column after implement/start when `ticket_id` is numeric.

### Create board tickets from WorkManifest (INIT-GATEFLOW-010)

After spec merge (plan §9 on `develop`), seed EPIC + wave tickets before implement-lane:

```bash
# features.create_tickets.enabled: true
# features.create_tickets.workspace: /absolute/path/to/gateflow
# features.create_tickets.plan_path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md
# features.create_tickets.initiative: INIT-GATEFLOW-010
# features.create_tickets.wave_id: W0
# features.create_tickets.project_number: 3   # org Project v2 number (deterministic)
# features.create_tickets.project_owner: drivestream-lab  # optional; defaults to gateflow.org
# optional dry_run: true  → contract + parse only
# optional authorize_run_id: <uuid>  → forge/authorize when run STOPPED at board-tickets-action

make run   # API; forge board creds required for creates
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_create_tickets
# → paste printed ticket_id into features.implement_lane.wave_start.ticket_id
# → enable implement_lane and run verify_implement_lane
```

Not in `verify_all`. Idempotent on `initiative_id` (+ wave suffix) like forge seed.

## Feature map (INIT-GATEFLOW-010 W2 — ticket gates + create predicates)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Create triple predicate gate (REQ-06) | `verify_board` / `verify_create_tickets` (authorize path docs) | `test_authorize_create_board_tickets_*`, `test_create_board_tickets_gate` patterns in forge tests |
| Create success epic + wave ids (REQ-07) | authorize positive path prints ids | `test_authorize_create_board_tickets_prayog_v1`, `test_authorize_create_board_tickets_success_requires_wave_ids` |
| Implement-start ticket 400/422 matrix (REQ-08) | `verify_wave_start` negative probes | `test_implement_malformed_ticket_id_400`, `test_implement_unresolvable_dual_identity_422`, `test_implement_rejects_done_ticket_422`, `test_implement_dual_identity_disagree` |
| Live co-ship (REQ-17 partial) | `verify_wave_start` extended | unit matrix above |

Human live-verify: `.venv/bin/python -m tests.verify.verify_wave_start` (+ `verify_board` / `verify_create_tickets` for create predicates when knobs set).

## Feature map (INIT-GATEFLOW-010 W3 — closeout Done + no merge/lgtm/auto-chain)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Closeout Done hop after ground-spec.pass (REQ-05) | `verify_wave_closeout` dogfood asserts `wave-done-action` forge_executed | `test_closeout_walk_applies_done_then_stops_at_wave_signoff` |
| Terminal purpose at wave-signoff (REQ-05) | `verify_wave_closeout` dogfood asserts `run_stopped.purpose` | `test_closeout_walk_applies_done_then_stops_at_wave_signoff`, `test_pin_human_checkpoint_carries_purpose_and_owner` |
| No Forge merge action (REQ-09) | secondary (code guard) | `test_forge_action_type_excludes_merge`, `test_forge_client_forbids_auto_merge` |
| Never auto-apply `*-lgtm` (REQ-16) | secondary | `test_apply_external_action_rejects_lgtm_apply_labels`, `test_parse_node_forge_forbids_lgtm_apply_labels` |
| No auto-chain after wave-signoff (REQ-19) | `verify_wave_closeout` dogfood forbids pre-implement/closure stages | `test_policy_wave_signoff_pass_stops_no_auto_chain`, `test_policy_wave_complete_pass_stops_no_auto_chain` |
| Live co-ship closeout slice (REQ-17 partial) | `verify_wave_closeout` (+ `verify_spec_lane` for spec Pass-1 when knobs set) | `test_wave_closeout`, orchestrator closeout tests |

Human live-verify: `.venv/bin/python -m tests.verify.verify_wave_closeout` (dogfood knobs + worker); optional `.venv/bin/python -m tests.verify.verify_spec_lane` for spec Pass-1 green.

## Feature map (INIT-GATEFLOW-010 W4 — closure Enter-at + Done-gate + EPIC hygiene + freeze)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Closure route 400/202 matrix (REQ-12) | `verify_initiative_closure` smoke | `test_closure_start` |
| Done-gate 422 + EPIC untouched (REQ-13) | `verify_initiative_closure` optional not_done probe | `test_closure_done_gate_*` |
| EPIC Done before purge-app (REQ-14) | `verify_initiative_closure` happy enqueue timeline | `test_closure_start_ok` (board update before enqueue) |
| Purge walk stops at signoff-app; no meta (REQ-15) | `verify_initiative_closure` run detail stage guard | `test_closure_walk_purge_then_pr_action_stops_at_signoff_app` |
| Partial failure after EPIC Done (REQ-20) | human Live-Verify | `test_closure_partial_failure_after_epic_done_records_req20` |
| Live co-ship closure slice (REQ-17) | `verify_initiative_closure` | unit matrix above |
| Feature-readiness freeze (REQ-18) | inspection | `Feature-Readiness-INIT-GATEFLOW-010.md` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_initiative_closure` with API + programme token + board tickets for Done-gate positives/negatives per knobs below.

## Feature map (INIT-GATEFLOW-011 W0 — checkpoint status-check foundation)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| ForgeClient list_reviews / list_check_runs / merge fields (REQ-02) | secondary (fixture PR) | `test_forge_client` |
| Pin checkpoint vocabulary from delivery-contract (REQ-02) | — | `test_checkpoint_vocab` |
| Live CAP-01 evaluate + itemized misses + no mutate (REQ-01/04/05) | `verify_checkpoint_status` | `test_checkpoint_evidence` |
| GET `/api/v1/checkpoints/status` programme-token (REQ-01/05/28) | `verify_checkpoint_status` | `test_checkpoints_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_checkpoint_status` (API + `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_CHECKPOINT_PR` for live GitHub evidence).

### Checkpoint status (INIT-GATEFLOW-011 W0)

```bash
# Smoke (always): 401 without token, 405 on POST, 404 unknown checkpoint_id
# Live GitHub evidence when:
#   export GATEFLOW_CHECKPOINT_PR=<fixture PR number>
#   # optional: GATEFLOW_CHECKPOINT_ID=coding-readiness (default)
#   gateflow.org / gateflow.repo from tests/config.yaml

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_checkpoint_status
```

## Feature map (INIT-GATEFLOW-011 W1 — check persistence + composed readout)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Persist `checkpoint_check` run_event on every evaluate (REQ-06) | `verify_checkpoint_history` | `test_checkpoint_persistence` |
| Stale evidence → not_satisfied + reason; checked_sha/checked_at always present (REQ-03) | — | `test_checkpoint_evidence` (stale cases) |
| GET `/api/v1/checkpoints/history` marks records historical (REQ-07/28) | `verify_checkpoint_history` | `test_checkpoints_api` |
| Composed readout via initiative+wave; 404 no run found for this wave (REQ-08/28) | `verify_checkpoint_history` | `test_checkpoints_api`, `test_checkpoint_persistence` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_checkpoint_history` (API + `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_CHECKPOINT_PR` for live persist + optional `GATEFLOW_COMPOSED_INITIATIVE`/`GATEFLOW_COMPOSED_WAVE` for composed readout).

### Checkpoint history + composed readout (INIT-GATEFLOW-011 W1)

```bash
# Smoke (always): 401/405/400/404-no-run-for-wave + history empty 200
# Live persist + stale when:
#   export GATEFLOW_CHECKPOINT_PR=<fixture PR number>
#   # optional: GATEFLOW_CHECKPOINT_ID=coding-readiness (default)
#   # optional composed readout:
#   export GATEFLOW_COMPOSED_INITIATIVE=INIT-X GATEFLOW_COMPOSED_WAVE=W0

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_checkpoint_history
```

## Feature map (INIT-GATEFLOW-011 W2 — initiative list/detail Gateflow-owned)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Initiative list/detail from runs + board EPIC tickets (REQ-09/10) | `verify_initiatives_readout` | `test_initiative_readout`, `test_initiatives_read_api` |
| `prd_approval` present (W2 stub unavailable; W3 populates via meta) (REQ-09/10) | `verify_initiatives_readout` | `test_initiative_readout`, `test_initiatives_read_api` |
| GET-only on `/initiatives` + `/initiatives/{id}`; 401 without token; 404 unknown initiative (REQ-28) | `verify_initiatives_readout` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_initiatives_readout` (API + `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_INITIATIVE_ID` for a live detail assert). Prefer **W3** `verify_initiative_meta_bridge` once the meta bridge is on the tip.

### Initiative list/detail (INIT-GATEFLOW-011 W2)

```bash
# Smoke (always): 401/405/404-unknown-initiative + list shape
# Live detail when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   gateflow.org / gateflow.repo from tests/config.yaml (board EPIC repo)

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_initiatives_readout
```

## Feature map (INIT-GATEFLOW-011 W3 — meta bridge + partial success)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| PRD approval via CAP-01 on meta PR (REQ-09) | `verify_initiative_meta_bridge` | `test_initiative_readout` |
| Meta-down / missing meta → 200 + `unavailable` + owned fields (REQ-11) | `verify_initiative_meta_bridge` | `test_initiative_readout` |
| GET-only / 401 / 404 unknown (REQ-28) | `verify_initiative_meta_bridge` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` (API + `PROGRAMME_SERVICE_TOKEN`).

### Initiative meta bridge (INIT-GATEFLOW-011 W3)

```bash
# Smoke (always): 401/405/404 + list prd_approval vocabulary + owned fields
# Live meta-up detail when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   optional: export GATEFLOW_EXPECT_PRD_APPROVAL=satisfied|not_satisfied|unavailable|could_not_verify
# Live meta-down detail when:
#   export GATEFLOW_META_DOWN_INITIATIVE_ID=<initiative without meta_pr_url>
#   (expects prd_approval=unavailable on HTTP 200)

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_initiative_meta_bridge
```

## Feature map (INIT-GATEFLOW-011 W4 — wave map readout)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Per-wave status ∈ {done, ready-to-start, blocked, active}; blocked names why (REQ-14) | `verify_wave_map` | `test_wave_map_service`, `test_initiatives_read_api` |
| Derived from board Feature tickets + runs only — no new store (REQ-15) | `verify_wave_map` | `test_wave_map_service` |
| GET `/initiatives/{id}/waves` GET-only; 401 / 404 unknown (REQ-28) | `verify_wave_map` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_wave_map` (API + `PROGRAMME_SERVICE_TOKEN`).

### Wave map (INIT-GATEFLOW-011 W4)

```bash
# Smoke (always): 401/405/404 on /initiatives/{id}/waves
# Live shape when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   (expects 200 + waves[] with closed status vocabulary; blocked → block_reason)

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_wave_map
```

## Feature map (INIT-GATEFLOW-011 W5 — spec lane readout)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Draft Spec PR + pin next step + findings when ready (REQ-12) | `verify_spec_readout` | `test_spec_readout_service`, `test_initiatives_read_api` |
| Plain not-ready before `spec-pr-action`; no broken URL (REQ-13) | `verify_spec_readout` | `test_spec_readout_service` |
| GET `/initiatives/{id}/spec` GET-only; 401 / 404 unknown (REQ-28) | `verify_spec_readout` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_spec_readout` (API + `PROGRAMME_SERVICE_TOKEN`).

### Spec lane readout (INIT-GATEFLOW-011 W5)

```bash
# Smoke (always): 401/405/404 on /initiatives/{id}/spec
# Live shape when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   (expects 200 + readiness vocabulary; not_ready/unavailable ⇒ null draft_spec_pr_url)

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_spec_readout
```

## Feature map (INIT-GATEFLOW-011 W6 — wave implementation progress)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Per-task timeline + Draft PR when `wave-pr-action` succeeded (REQ-16) | `verify_wave_implementation` | `test_implementation_readout_service`, `test_initiatives_read_api` |
| Named task + reason on failure / needs-input stop (REQ-17) | `verify_wave_implementation` | `test_implementation_readout_service` |
| GET `.../waves/{wave_id}/implementation` GET-only; 401 / 404 unknown (REQ-28) | `verify_wave_implementation` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_wave_implementation` (API + `PROGRAMME_SERVICE_TOKEN`).

### Wave implementation progress (INIT-GATEFLOW-011 W6)

```bash
# Smoke (always): 401/405/404 on /initiatives/{id}/waves/{wave_id}/implementation
# Live shape when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   export GATEFLOW_WAVE_ID=W6
#   (expects 200 + tasks list; draft_pr_url null when absent)

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_wave_implementation
```

## Feature map (INIT-GATEFLOW-011 W7 — closeout readout + drift)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Itemized closeout additions (REQ-18) | `verify_wave_closeout_readout` | `test_closeout_readout_service`, `test_initiatives_read_api` |
| Advisory drift / unknown baseline (REQ-19/20) | `verify_wave_closeout_readout` | `test_closeout_readout_service` |
| GET `.../waves/{wave_id}/closeout` GET-only; 401 / 404 unknown (REQ-28) | `verify_wave_closeout_readout` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` (API + `PROGRAMME_SERVICE_TOKEN`).

### Wave closeout readout (INIT-GATEFLOW-011 W7)

```bash
# Smoke (always): 401/405/404 on /initiatives/{id}/waves/{wave_id}/closeout
# Live shape when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   export GATEFLOW_WAVE_ID=W7
#   (expects 200 + additions list + advisory_only true)

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_wave_closeout_readout
```

## Feature map (INIT-GATEFLOW-011 W8 — merge confirm + completion)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Merge confirm via CAP-01 wave-signoff (REQ-21) | `verify_merge_and_completion` | `test_merge_readout_service`, `test_initiatives_read_api` |
| Next-wave nudge after merge (REQ-22) | `verify_merge_and_completion` | `test_merge_readout_service` |
| Completion eligibility rollup (REQ-23/24) | `verify_merge_and_completion` | `test_completion_readout_service` |
| GET merge + completion GET-only; 401 / 404 (REQ-28) | `verify_merge_and_completion` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_merge_and_completion` (API + `PROGRAMME_SERVICE_TOKEN`).

### Merge confirm + completion (INIT-GATEFLOW-011 W8)

```bash
# Smoke (always): 401/405/404 on .../merge and .../completion
# Live shape when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
#   export GATEFLOW_WAVE_ID=W8

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_merge_and_completion
```

## Feature map (INIT-GATEFLOW-011 W9 — closure preview)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Pre-purge plan from purge allowlist; not yet run (REQ-25) | `verify_closure_preview` | `test_closure_preview_service`, `test_initiatives_read_api` |
| Post-purge deleted/kept from handoff signals (REQ-26) | `verify_closure_preview` | `test_closure_preview_service` |
| CAP-01 reuse for closure signoff-app/meta (REQ-27) | `verify_closure_preview` | `test_closure_preview_service` |
| GET `/initiatives/{id}/closure` GET-only; 401 / 404 (REQ-28) | `verify_closure_preview` | `test_initiatives_read_api` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_closure_preview` (API + `PROGRAMME_SERVICE_TOKEN`).

### Closure preview (INIT-GATEFLOW-011 W9)

```bash
# Smoke (always): 401/405/404 on .../closure
# Live shape when:
#   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_closure_preview
```

### Initiative-closure start (INIT-GATEFLOW-010 W4)

```bash
# Smoke (always): auth/validation; optional Done-gate 422 when not_done_wave_ticket_id set
# Happy enqueue when:
#   features.initiative_closure.enabled: true
#   features.initiative_closure.epic_ticket_id: <EPIC>
#   features.initiative_closure.wave_ticket_ids: [<all Done>]
#   features.initiative_closure.workspace: /absolute/path
#
# Dogfood (poll purge → Draft PR → signoff-app):
#   gateflow.require_worker: true
#   features.initiative_closure.dogfood: true
#   features.initiative_closure.timeout_s: 3600
# Note: purge deletes allowlisted docs under workspace; restore with
#   git restore docs/specification/reports/   before a re-run on develop.

set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_initiative_closure
```

Without `enabled: true`, the script still asserts 401 + 400 validation (smoke).
With `dogfood: true`, requires worker and asserts purge-app success, automated
`open_draft_pr`, terminal `stopped` at `initiative-closure-signoff-app`, and no
meta purge stages (REQ-15).

### Closeout start + Pass-2 dogfood (INIT-GATEFLOW-007)

```bash
# Smoke (W0): auth/validation always; happy enqueue when enabled:
#   features.wave_closeout.enabled: true
#   features.wave_closeout.pr_number: <existing wave PR>
#   # Publish head = that PR's head.ref (branch_slug optional / non-binding)
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
success, automated `wave-done-action` Done hop, terminal `stopped` at `wave-signoff`
with `purpose=wave-signoff`, and no auto-chain to pre-implement/closure (INIT-010 W3 /
REQ-05, REQ-19). Learning-Extract file when configured.
Postgres `learning_extracts` row evidence is human Live-Verify (no learning HTTP).

See spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` /
`docs/specification/product/INIT-GATEFLOW-003-gateflow.md`.
See also: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`.

## Feature map (INIT-GATEFLOW-009 — factory prove-out freeze)

| Capability | Live verify | Unit / notes |
|------------|-------------|--------------|
| Spec Pass-1 | `verify_spec_lane` — **live** ([Live-Verify W1](../docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W1.md)) | `test_wave_start`, `test_meta_pr_intake` |
| Implement Pass-1 | `verify_implement_lane` — **live** (Live-Verify W0) | implement-lane suite |
| Closeout Pass-2 | `verify_wave_closeout` — **live** ([Live-Verify W2](../docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W2.md)) | `test_wave_closeout` |
| Authorize live | **PE-waived** (INIT-009) | `test_forge_action_service` unit only |
| Feature readiness + CI | inspection + GitHub Actions `ci` | [`Feature-Readiness-INIT-GATEFLOW-009.md`](../docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md) |

## Feature map (INIT-GATEFLOW-012 W0 — tenant registry)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Register + one-time tenant bearer (REQ-01/03/09) | `verify_tenant_registry` | `test_tenant_service`, `test_tenant_routes` |
| PAT never in responses (REQ-02/32) | `verify_tenant_registry` | `test_tenant_service`, `test_tenant_routes` |
| Eager PAT probe itemized 422 (REQ-06) | `verify_tenant_registry` | `test_github_pat_probe`, `test_tenant_service` |
| Absolute `workspace_root` → 400 (REQ-07) | `verify_tenant_registry` | `test_tenant_service` |
| Tenant token 401 + attach boundary (REQ-04; ADR-011) | `verify_tenant_registry` | `test_tenant_token`, `test_tenant_routes` |
| Board default when project omitted (REQ-08) | secondary | `test_board_service` (`test_resolve_board_default_*`) |

Human live-verify: `.venv/bin/python -m tests.verify.verify_tenant_registry` (API + human DDL for tenants tables + PAT with read access to `gateflow.org`/`gateflow.repo`).

### Tenant registry (INIT-GATEFLOW-012 W0)

```bash
# Prerequisites: human Alembic for tenants / tenant_repos / tenant_users
#   (see docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md)
# PAT: GITHUB_PERSONAL_ACCESS_TOKEN or GATEFLOW_TENANT_PAT
# Optional: GATEFLOW_TENANT_ORG / GATEFLOW_TENANT_REPO / GATEFLOW_TENANT_WORKSPACE_ROOT

make run
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_tenant_registry
```

## Feature map (INIT-GATEFLOW-012 W1 — workspace clone/refresh)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Omitted path + registered → clone/fetch (REQ-10/13) | `verify_workspace_lifecycle` | `test_tenant_git_workspace_client`, `test_wave_start`, `test_run_orchestrator` |
| Explicit `workspace_path` unchanged (REQ-12) | secondary | `test_implement_explicit_path_skips_tenant_resolve` |
| Mismatch checkout → 422 untouched (REQ-14) | `verify_workspace_lifecycle` | `test_resolve_mismatch_*`, `test_implement_mismatch_422_*` |
| Omitted + unregistered → 422 0 enqueue (REQ-15) | `verify_workspace_lifecycle` | `test_implement_omitted_path_unregistered_*` |
| Tenant PAT auth on git (REQ-11) | inspection + live | client uses stored PAT; never logged |
| Per-repo lock (TF-01) | — | `test_per_repo_lock_serializes_*` |
| Pin 0 BROKEN existing nodes (PE-1 W1 waiver) | — | `test_all_remounted_pin_nodes_parse` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_workspace_lifecycle`

### Workspace lifecycle (INIT-GATEFLOW-012 W1)

```bash
# Prerequisites: W0 tenant DDL applied; API up; PROGRAMME_SERVICE_TOKEN;
# PAT with read access; resolvable board ticket (same as verify_wave_start).
# Optional: GATEFLOW_TENANT_WORKSPACE_ROOT (scratch absolute path)

make run
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_workspace_lifecycle
```

## Feature map (INIT-GATEFLOW-012 W2 — branch create-or-reuse)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| New wave forks from live develop tip (REQ-16) | `verify_branch_lifecycle` | `test_resolve_branch_new_wave_*` |
| Deterministic naming; no second scheme (REQ-17) | secondary | `test_pr_branch_naming`, `test_branch_slug_from_head_ref_*` |
| Continuation reuses head; zero new refs (REQ-18) | `verify_branch_lifecycle` | `test_resolve_branch_continuation_*`, `test_process_job_continuation_missing_*` |
| Never-cloned workspace + continuation (REQ-19) | `verify_branch_lifecycle` | checkout companion + live |
| Missing continuation head → named fail-closed | secondary | `test_resolve_branch_explicit_head_missing_*` |
| PE-1 existing-node 0 BROKEN (W2 coding-start waiver) | — | `test_all_remounted_pin_nodes_parse` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_branch_lifecycle`

### Branch lifecycle (INIT-GATEFLOW-012 W2)

```bash
# Prerequisites: W0 DDL + W1 workspace contracts; API + worker;
# gateflow.require_worker: true; PROGRAMME_SERVICE_TOKEN; PAT with branch write;
# resolvable board ticket fields (same as verify_wave_start).
# Optional: GATEFLOW_TENANT_WORKSPACE_ROOT (scratch absolute path)

make run
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_branch_lifecycle
```

## Feature map (INIT-GATEFLOW-012 W3 — harness-readiness)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Missing harness artifacts → 422 (REQ-21) | `verify_harness_readiness` | `test_launchpad_client`, `test_implement_harness_missing_*`, `test_harness_missing_fails_*` |
| Ready harness past gate (REQ-20) | `verify_harness_readiness` | `test_sync_harness_ready_*`, orchestrator wire |
| Cache skip + force re-check (REQ-22) | secondary | `test_implement_harness_cache_*`, `test_harness_force_recheck_*`, `test_harness_cache_skips_*` |
| Wire after workspace before Enter-at (REQ-20) | secondary | `test_harness_missing_fails_before_enter_at` |

Human live-verify: `.venv/bin/python -m tests.verify.verify_harness_readiness`

### Harness readiness (INIT-GATEFLOW-012 W3)

```bash
# Prerequisites: API + Postgres; PROGRAMME_SERVICE_TOKEN; resolvable board
# ticket fields (same as verify_wave_start). Script uses temp dirs with/without
# .harness-pin.yaml + .harness/.

make run
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_harness_readiness
```

## Feature map (INIT-GATEFLOW-012 W4 — repo-scoped NO_CONCURRENT_RUN)

| Capability | Verify script | Pytest |
|------------|---------------|--------|
| Same-repo ACTIVE second start → 409 (REQ-23) | `verify_wave_start` | `test_run_store_concurrency`, `test_implement_concurrent_409` |
| Cross-repo never blocked (REQ-24) | `verify_wave_start` (optional env) | `test_ff06_cross_repo_*` |
| No new isolation infra (REQ-25) | inspection | source guard in `test_ff06_source_is_org_repo_active_only` |
| FF-06 fixture before query change | — | `test_run_store_concurrency` (landed before broaden) |

Human live-verify: `.venv/bin/python -m tests.verify.verify_wave_start`

Optional cross-repo allow probe: set `GATEFLOW_VERIFY_CROSS_ORG` + `GATEFLOW_VERIFY_CROSS_REPO`.

### Repo concurrency (INIT-GATEFLOW-012 W4)

```bash
# Prerequisites: API + Postgres; PROGRAMME_SERVICE_TOKEN; resolvable board ticket.
# First start leaves an ACTIVE run; script asserts same-repo second start → 409.

make run
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_wave_start
```
