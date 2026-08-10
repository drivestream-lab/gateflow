# DDL-NOTE — tenant_repos.readiness_source (INIT-GATEFLOW-013 W3)

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-013 |
| Wave | W3 |
| Owner | Human (Alembic) |
| Agent scope | ORM schema only — **do not** add `postgres_migrations/versions/` |

## Required DDL (human)

Add nullable provenance column on `tenant_repos`:

```sql
ALTER TABLE tenant_repos
  ADD COLUMN readiness_source VARCHAR(32) NULL;

COMMENT ON COLUMN tenant_repos.readiness_source IS
  'filesystem | launchpad_status; NULL = legacy pre-INIT (treat as filesystem)';
```

Downgrade:

```sql
ALTER TABLE tenant_repos DROP COLUMN IF EXISTS readiness_source;
```

## Semantics

| Value | Evaluator at wave-start / orchestrator |
|-------|----------------------------------------|
| `NULL` | `LaunchpadClient.sync_harness` (filesystem) |
| `filesystem` | same |
| `launchpad_status` | `LaunchpadStatusClient.inspect_status` |

Selection-admitted repos (post W3) set `launchpad_status` at `add_tenant_repos`.
Status path must not rewrite rows that remain NULL/`filesystem` (REQ-22).

## Apply

```bash
./scripts/create_postgres_migration.sh "add_tenant_repos_readiness_source"
# hand-write upgrade/downgrade, then:
./scripts/run_postgres_migration.sh head
```
