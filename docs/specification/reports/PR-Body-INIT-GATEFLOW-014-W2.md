## Initiative

INIT-GATEFLOW-014 — One identity to call Gateflow, retire shared-secret doors

## Spec path

`docs/specification/product/INIT-GATEFLOW-014-gateflow.md`

## Wave

W2 — JWT cutover for Appendix-C; refuse old doors; per-programme ForgeClient; tenant-scoped runs; catalogue-only agent dispatch

Board: https://github.com/drivestream-lab/gateflow/issues/217

## Summary

- `require_programme_scope` / path-tenant deps; Appendix-C routes on JWT `require_role` (TENANT_ADMIN / PLATFORM_ADMIN)
- `public_paths` shrunk to `/health`, `/internal`, `/webhooks`, `/api/auth` — old programme/tenant shared-secret Bearers refused
- `ForgeClientFactory.for_programme` + `ProgrammePatTokenProvider` (ADR-015)
- Non-nullable `RunSchema.tenant_id` + tenant-scoped run queries (ADR-016); DDL note for human Alembic
- SlotValidator + CursorAgentRunner catalogue-only credentials (no env `CURSOR_API_KEY` gate); orchestrator passes catalogue credential
- Webhooks inspected untouched (REQ-28)
- Co-shipped live verify: `verify_jwt_cutover`, `verify_cross_programme_isolation`

## Smoke command

```bash
# After applying squashed baseline migration 5e85268f844f_first_version (DB reset):
.venv/bin/python -m tests.verify.verify_jwt_cutover
.venv/bin/python -m tests.verify.verify_cross_programme_isolation
```

## Test plan

- [x] `make check`
- [x] `make test` (544+ passed at loop-spec)
- [ ] Human live verify (above) + label `wave-accepted` on tip
