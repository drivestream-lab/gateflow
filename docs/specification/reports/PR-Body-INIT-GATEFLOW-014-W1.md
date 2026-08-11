## Initiative

INIT-GATEFLOW-014 — One identity to call Gateflow, retire shared-secret doors

## Spec path

`docs/specification/product/INIT-GATEFLOW-014-gateflow.md`

## Wave

W1 — Programme validate-then-create + tenant_admin attach + platform DB agent catalogue

Board: https://github.com/drivestream-lab/gateflow/issues/216

## Summary

- Programme entity (PAT, workspace, meta location, reserved App fields, lane defaults) + repository
- `ProgrammeService.validate_then_create` — PAT probe + meta clone/parse before durable write (fail-closed)
- `platform_admin`-only HTTP: create/list/attach/lane-defaults + agent catalogue provision/resolve
- Platform agent catalogue with effective-runner resolution (no env `CURSOR_API_KEY` fallback)
- Rename INIT-013 meta-connection symbols to `catalogue_connection_*` (URLs unchanged)
- Co-shipped live verify: `verify_programme_onboarding`, `verify_agent_catalogue`
- Human DDL note: `DDL-NOTE-INIT-GATEFLOW-014-W1-programmes-agent-catalogue.md`

## Smoke command

```bash
# After human Alembic for programmes + platform_agent_catalogue:
.venv/bin/python -m tests.verify.verify_programme_onboarding
.venv/bin/python -m tests.verify.verify_agent_catalogue
```

## Test plan

- [x] `make check`
- [x] `make test` (525 passed at loop-spec)
- [ ] Human live verify (above) + label `wave-accepted` on tip
