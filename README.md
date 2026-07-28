# gateflow
Gateflow orchestrator API — webhooks, runs, GitHub App, agent dispatch

## Cursor AgentRunner (local SDK)

Live Cursor runs use the official in-process **`cursor-sdk`** package with
`CURSOR_API_KEY` (user or service-account key). Set it in `.env` (see
`.env.example`). Do **not** commit the key; keep it in env / secret store only.

When wave-start selects runner `cursor`, start fails closed (HTTP 422)
if `CURSOR_API_KEY` is missing. Unit tests may use `mock-*` skill ids;
that path is **not** live prove-it evidence.

## Handoff baton root (INIT-GATEFLOW-005)

Packaged-skill automate stores per-run handoff files under
`GATEFLOW_HANDOFF_ROOT` (absolute path; e.g. `/tmp/gateflow/handoffs`).
Do **not** point this at the git workspace by default. Unset or non-absolute
values fail closed before AgentRunner for packaged automate. See `.env.example`.
