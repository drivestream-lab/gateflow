## Summary

- **Initiative:** INIT-GATEFLOW-012
- **Wave:** W1 — Repo clone/refresh workspace prep (REQ-10–15)
- **Board:** [#186](https://github.com/drivestream-lab/gateflow/issues/186)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- **PE waiver:** `docs/specification/reports/PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md` (TASK-W1-01 = current pin 0 BROKEN existing nodes; CTR-01 new shapes → W2)

Delivers `TenantGitWorkspaceClient` (subprocess `git` clone/fetch with stored Tenant PAT, per-repo lock), wave-start resolve-before-enqueue for omitted `workspace_path`, and orchestrator removal of `Path.cwd()` fallback for registered repos. Explicit caller paths unchanged (REQ-12). Unregistered omit and mismatch fail closed with **422** and **0 enqueue**.

## Human prerequisites before smoke

1. W0 tenant DDL applied (`DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md`).
2. API (+ programme token); PAT with read access to probe org/repo; resolvable board ticket (same as `verify_wave_start`).
3. Optional: `GATEFLOW_TENANT_WORKSPACE_ROOT` scratch absolute path.

## Smoke command

```bash
.venv/bin/python -m tests.verify.verify_workspace_lifecycle
```

## Test plan

- [x] `make check` (local Pass-1)
- [x] `make test` (432 passed local Pass-1)
- [ ] Human: `.venv/bin/python -m tests.verify.verify_workspace_lifecycle`
- [ ] Label tip `wave-accepted` after live prove

## Notes

- Auth uses `http.extraHeader` Basic (`x-access-token`) — PAT never written into remote URL on disk or logs.
- Deterministic path: `{workspace_root}/{org}/{repo}`.
- `smoke_wave_start_fields` now sets explicit `workspace_path` so existing verify_all paths stay on REQ-12.
