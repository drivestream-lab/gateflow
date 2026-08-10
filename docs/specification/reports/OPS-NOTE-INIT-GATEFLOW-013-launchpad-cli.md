# OPS-NOTE — Launchpad CLI for Gateflow (INIT-GATEFLOW-013 W3 / FF-06)

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Wave | W3 |
| Setting | `APP_LAUNCHPAD_CLI_PATH` (default `launchpad`) |
| ADR | ADR-013 Option B — inspect-only `LaunchpadStatusClient` |

## Requirement

Gateflow's API and worker processes must be able to invoke the **Launchpad CLI**
for inspect-only `status` (REQ-17/18). The binary is **preinstalled** in runtime
images (or available on `PATH`); Gateflow does not fetch or install it at
request time.

## Configuration

- Env: `APP_LAUNCHPAD_CLI_PATH` — absolute path to the binary, or a name
  resolved via `PATH` (default: `launchpad`).
- `LaunchpadStatusClient.health_check` / `inspect_status` fail closed with
  reason `tool_unavailable` when the binary is missing or not executable
  (REQ-20 — distinct from repo-not-ready).

## Live verify

Human smoke for W3:

```bash
.venv/bin/python -m tests.verify.verify_harness_status
```

Prerequisites: CLI present per this note; programme meta synced; W0–W2 paths live.

## Forbidden

- Do not point status at operator-local `~/.config/launchpad/clients.yaml` as
  the programme source of truth (CTR-02 — use Gateflow-synced meta config dir).
- Do not invoke `apply` / install / mutate verbs from Gateflow (REQ-18).
