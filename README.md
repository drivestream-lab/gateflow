# gateflow
Gateflow orchestrator API — webhooks, runs, GitHub App, agent dispatch

## Cursor AgentRunner (local SDK)

Live Cursor runs use the official in-process **`cursor-sdk`** package with
`CURSOR_API_KEY` (user or service-account key). Set it in `.env` (see
`.env.example`). Do **not** commit the key; keep it in env / secret store only.

When wave-start selects runner `cursor`, start fails closed (HTTP 422)
if `CURSOR_API_KEY` is missing. Unit tests may use `mock-*` skills or
`GATEFLOW_AGENT_STUB=1`; those doubles are **not** live prove-it evidence.
