# Runbook — Orchestrate a new initiative repo (FR-19)

Authorize Gateflow wave runs on a programme repository without editing
WorkflowEngine source.

## 1. GitHub App

1. Use org App **gateflow-dev** / **gateflow-prod** (one App per environment).
2. Install on **Selected** repos including the new initiative repo (and meta if needed).
3. Confirm webhook URL points at this environment’s `POST /webhooks/github`.
4. Put secrets in env only (never commit secrets to the repo):
   - `GITHUB_WEBHOOK_SECRET`
   - `GITHUB_AUTH_MODE=app` (production / App path) or `pat` (non-prod only)
   - `GITHUB_APP_ID` + `GITHUB_PRIVATE_KEY_PATH` when mode is `app`
   - `GITHUB_PERSONAL_ACCESS_TOKEN` when mode is `pat`
   - `PROGRAMME_SERVICE_TOKEN` (wave-start / status / metrics)
   - `CURSOR_API_KEY` when using live Cursor AgentRunner

## 2. Env knobs (no programme.yaml)

Ops and notifier knobs live in **env** (see `.env.example`):

| Env | Purpose |
|-----|---------|
| `GATEFLOW_NOTIFIER` | Notifier adapter id (e.g. `github_comment`) |
| `GATEFLOW_FINDINGS_BUDGET` | Findings loop budget (default 3) |
| `GATEFLOW_METRICS_RETENTION_DAYS` | Metrics lookback days (default 90) |
| `GATEFLOW_MAX_ORCHESTRATED_HOPS` | Hard cap on orchestrated stages per job (default 20) |

Handoff artifact scan uses **code-constant globs** in `HandoffReader` (skill
durable-handoff convention). There is no `config/programme.yaml`.

Wave-start API owns PR targeting (`initiative_id`, `wave_id`, `branch_slug`,
`base_branch`) and Enter-at dispatch (`start_node`, `runner`, `model_id`,
optional `node_dispatch`). Restart API and worker after env changes.

## 3. Skills pin

Ensure `.harness-pin.yaml` / `prayog-skills` pin matches product target
(`v0.5.0-rc.2`). PolicyEngine / WorkflowEngine load `prayog-skills/workflow.yaml`
+ `delivery-contract.yaml` — no hardcoded node allowlists. `start_node` must be
a pin `skill` with `dispatch: orchestrated`.

## 4. Authorize a run (API wave-start)

1. Ensure workspace has pin + optional durable handoff under skill globs
   (hop 1 Enter-at ignores handoff for **node choice**; later hops use handoff
   facts + pin `outcomes` via PolicyEngine until a gate).
2. `POST /api/v1/waves/implement/start` with programme token and Enter-at body
   (spec lane: `POST /api/v1/waves/spec/start` with meta PR + dual workspaces)
   (`start_node`, `runner`, `model_id`, PR targeting fields).
3. Worker walks orchestrated skills until STOP/BLOCK or hop cap; comments land
   on the run PR opened at start.

## 5. Verify

Follow `tests/README.md` (`verify_wave_start`, optional worker prove-it).
