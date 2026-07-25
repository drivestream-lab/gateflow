# Human-owned Alembic revision required for INIT-GATEFLOW-003 TASK-W1-03
# (agents must not edit postgres_migrations/versions/).
#
# Create with: ./scripts/create_postgres_migration.sh "add_runs_wave_duration_ms"
# Then hand-write upgrade/downgrade:
#
#   ALTER TABLE runs ADD COLUMN wave_duration_ms INTEGER NULL;
#
# Downgrade:
#   ALTER TABLE runs DROP COLUMN wave_duration_ms;
#
# ORM SSOT: src/database/postgres/schema/run_store_schema.py
#   (wave_duration_ms on RunSchema — nullable int milliseconds)
# Semantics (REQ-30 / TDD §3.4–3.5): accept/enqueue (runs.created_at) →
# stop at next contract node or terminal failed / completed.
#
# Apply: ./scripts/run_postgres_migration.sh head
