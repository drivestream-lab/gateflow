# Runbook — Orchestrate a new initiative repo (W1 / FR-19)

Authorize Gateflow wave runs on a programme repository without editing
WorkflowEngine source.

## 1. GitHub App

1. Use org App **gateflow-dev** / **gateflow-prod** (one App per environment).
2. Install on **Selected** repos including the new initiative repo (and meta if needed).
3. Confirm webhook URL points at this environment’s `POST /webhooks/github`.
4. Put secrets in env only (never in `config/programme.yaml`):
   - `GITHUB_WEBHOOK_SECRET`
   - `GITHUB_APP_ID`
   - `GITHUB_PRIVATE_KEY_PATH`
   - `PROGRAMME_SERVICE_TOKEN` (status/metrics reads)

## 2. Programme config

Edit `config/programme.yaml` in **gateflow** (not harness/meta YAML):

| Key | Purpose |
|-----|---------|
| `trigger.label` | Label that authorizes a wave (default `gateflow:run-wave`) |
| `handoff.*` | Ref strategy + artifact globs for durable handoff blocks |
| `retry.findings_budget` | Findings loop budget |
| `metrics.retention_days` | Retention hint for aggregates |
| `runner.default` / `model.profiles` | H1 defaults |
| `tools.slots` | H1 empty `{}` |

Restart API and worker after config changes.

## 3. Skills pin

Ensure `.harness-pin.yaml` / `prayog-skills` pin matches product target
(`v0.5.0-rc.2`). PolicyEngine loads `prayog-skills/workflow.yaml` +
`delivery-contract.yaml` — no hardcoded node allowlists.

## 4. Authorize a run

1. Open a PR (or issue) on the installed repo with a durable `handoff:` block
   under configured globs.
2. Apply the programme trigger label.
3. Confirm API returns 202 for the webhook delivery.
4. Confirm worker claims the job and posts Forge comments (start/stop) when
   credentials allow.
5. Read status: `GET /api/v1/runs/{run_id}` with `Authorization: Bearer $PROGRAMME_SERVICE_TOKEN`.

## 5. Stop conditions PE should expect

- Concurrent active run for same PR/issue → block comment, no dispatch
- `human-checkpoint` / unresolved blockers / non-orchestrated skill → stop + comment
- AgentRunner failure → run `failed`, no workflow advance
- Findings budget exhausted → stop + comment (no auto-issue)

## 6. Halt dispatch

Disable the App webhook or stop the worker process. Runs remain in Postgres.
