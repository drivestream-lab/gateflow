# OPS-NOTE — Launchpad CLI for Gateflow (INIT-GATEFLOW-013 W3 / FF-06)

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Wave | W3 (ops consume of Launchpad 0.5.35) |
| Setting | `APP_LAUNCHPAD_CLI_PATH` (default `launchpad`) |
| ADR | ADR-013 Option B — inspect-only `LaunchpadStatusClient`; admit setup uses a separate apply client |

## Requirement

Gateflow's API and worker processes must be able to invoke the **Launchpad CLI**
for:

1. **Admit setup** — `apply-harness --apply` after clone (materialize gitignored
   skill hubs). Gateflow **does not** git-add or commit the result.
2. **Inspect-only `status`** (REQ-17/18 on the status client) after apply, on
   readiness refresh, and on wave-start.

The binary is **preinstalled** in runtime images (or available on `PATH`);
Gateflow does not fetch or install it at request time.

**Minimum version: 0.5.35** (`--no-client` on `status` and `apply-harness`,
`--format json` on stdout, TTY on stderr).

Install / upgrade on the host:

```bash
pipx install --force "launchpad @ git+https://github.com/drivestream-lab/launchpad@v0.5.35"
```

## Configuration

- Env: `APP_LAUNCHPAD_CLI_PATH` — absolute path to the binary, or a name
  resolved via `PATH` (default: `launchpad`).
- `LaunchpadStatusClient.health_check` / `inspect_status` and
  `LaunchpadApplyHarnessClient.health_check` / `apply_harness` fail closed with
  reason `tool_unavailable` when the binary is missing or not executable
  (REQ-20 — distinct from repo-not-ready).

## Invocation (Launchpad >= 0.5.35 service-mode)

Operator `--client` / `~/.config/launchpad` is **not** used.

```text
# Child process env only — programme PAT from Gateflow DB, never argv
GITHUB_TOKEN=<programme-pat>
```

### Admit — apply then status

```text
launchpad apply-harness \
  --no-client \
  --config-dir {synced_meta}/config \
  --workspace {GATEFLOW_WORKSPACE_ROOT}/{org} \
  --repo {repo} \
  --apply \
  --format json

launchpad status \
  --no-client \
  --config-dir {synced_meta}/config \
  --workspace {GATEFLOW_WORKSPACE_ROOT}/{org} \
  --repo {repo} \
  --format json
```

### Refresh and wave-start — status only

Same `status` argv as above. Do **not** call `apply-harness` on refresh or
wave-start.

- `--repo` is the **repo name only** (not `org/repo`).
- `--no-client` skips `clients.yaml` / `env.d` on the service user's home.
- `--workspace` is the parent of the repo clone (same meaning as
  `clients.yaml` `workspace`).
- PAT is injected as child-process `GITHUB_TOKEN` only — never a CLI flag.
- Parse **stdout only** as JSON v1
  `{ ok, command, repo, exit, error, checks: [{ id, ok, detail }] }`.
- Status check ids: `governance`, `board`, `clone`, `scaffold`, `harness`,
  `forge`, `drift`. Apply check ids: `clone`, `apply` (and `profile` if skipped).
- Named Gateflow ready verdict ignores advisory checks `board` and `forge`
  (Launchpad may still exit 1). Blocking ids: `governance`, `clone`,
  `scaffold`, `harness`, `drift`. Advisory failures are logged as
  `advisory_failures`; they do not produce `status_failed`.
- After apply, Gateflow does **not** commit. Skill hubs are gitignored; pin /
  AGENTS may change on disk.

Operator laptop path (`launchpad --client <id> status …`) is unchanged on the
Launchpad side; Gateflow always uses service-mode above.

## REQ-18 exception (as-built)

Accepted INIT-GATEFLOW-013 REQ-18 still means **status is inspect-only**.
Admit setup is allowed to run **`apply-harness --apply`** so a fleet clone is
usable (hubs are gitignored and must be materialized). Status, refresh, and
wave-start never pass apply/install/mutate verbs.

## Live verify

Human smoke for W3:

```bash
.venv/bin/python -m tests.verify.verify_harness_status
```

Prerequisites: CLI **0.5.35+** present per this note; programme meta synced;
W0–W2 paths live. Stale forge templates and missing programme board are
advisory — they must not fail admit. Harness/clone/scaffold failures still do.

## Related CR

Launchpad 0.5.35 shipped the service-mode apply + JSON contract. Gateflow
consume: [`CR-Launchpad-service-mode-apply-harness.md`](CR-Launchpad-service-mode-apply-harness.md).

## Forbidden

- Do not point status or apply at operator-local `~/.config/launchpad/clients.yaml`
  as the programme source of truth (CTR-02 — use Gateflow-synced meta config dir).
- Do not put `--apply` on `LaunchpadStatusClient` argv (REQ-18 for status).
- Do not call `apply-forge-templates` from Gateflow.
- Do not git-add / commit the VM clone after `apply-harness`.
