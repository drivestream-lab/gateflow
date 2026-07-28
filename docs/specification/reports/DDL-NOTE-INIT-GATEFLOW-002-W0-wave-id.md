# Human-owned Alembic revision required for INIT-GATEFLOW-002 TASK-W0-03
# (agents must not edit postgres_migrations/versions/).
#
# Create with: ./scripts/create_postgres_migration.sh "add_runs_wave_id"
# Then hand-write upgrade/downgrade:
#
#   ALTER TABLE runs ADD COLUMN wave_id VARCHAR(64) NULL;
#   CREATE INDEX ix_runs_wave_id ON runs (wave_id);
#
# Downgrade:
#   DROP INDEX IF EXISTS ix_runs_wave_id;
#   ALTER TABLE runs DROP COLUMN wave_id;
#
# ORM SSOT: src/database/postgres/schema/run_store_schema.py (wave_id on RunSchema)
# Concurrent active-run lookup may use (org, repo, initiative_id, wave_id).
