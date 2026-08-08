## Summary

- **Initiative:** INIT-GATEFLOW-012
- **Wave:** W0 — Tenant registry (REQ-01–09, REQ-32)
- **Board:** [#185](https://github.com/drivestream-lab/gateflow/issues/185)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- **ADR:** `docs/specification/adr/adr-011-tenant-scoped-bearer-token-trust-zone.md` (Accepted, Option A)

Delivers tenant register / attach / list / detail with eager per-repo PAT probe (422 itemized), absolute `workspace_root` (400), plaintext PAT never echoed (G1), tenant-scoped bearer trust zone (fourth zone; no AuthMiddleware reuse), and board default resolution when `project_number` is omitted (REQ-08).

## Human prerequisites before smoke

1. Create/apply Alembic revision from `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md` (agents do not write `postgres_migrations/versions/`).
2. API + Postgres up; PAT with read access to probe org/repo.

## Smoke command

```bash
.venv/bin/python -m tests.verify.verify_tenant_registry
```

## Test plan

- [x] `make check` (local Pass-1)
- [x] `make test` (419 passed local Pass-1)
- [ ] Human: apply tenant DDL
- [ ] Human: `.venv/bin/python -m tests.verify.verify_tenant_registry`
- [ ] Label tip `wave-accepted` after live prove

## Notes

- `POST /api/v1/tenants` is JWT-public; auth is tenant bearer dependency on subsequent routes (ADR-011).
- Probe uses per-call httpx with submitted PAT — not ForgeClient singleton credential.
