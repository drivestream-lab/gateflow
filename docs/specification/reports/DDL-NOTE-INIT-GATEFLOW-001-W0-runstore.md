# Human-owned Alembic revision required for TASK-W0-02 (agents must not edit versions/).
#
# Create with: ./scripts/create_postgres_migration.sh "add_run_store_tables"
# Then hand-write upgrade/downgrade for tables registered on postgres_metadata:
#
#   webhook_deliveries  — delivery_id UNIQUE, event_type, payload JSONB + base UUID/timestamps
#   runs                — org, repo, status_type, outcome_type, workflow_node,
#                         pr_number, issue_number, initiative_id, retry_counter, notify_pending
#   stages              — run_id FK CASCADE, workflow_node, outcome_type, started_at/ended_at,
#                         runner, model_profile, model_id, model_provider
#   run_events          — run_id FK CASCADE, event_type, workflow_node, outcome_type, payload JSONB
#   jobs                — status_type, payload JSONB, delivery_id, webhook_delivery_id FK SET NULL,
#                         claimed_at, processed_at, error_message
#
# Indexes: delivery_id (unique), jobs.status_type, jobs.delivery_id, stages.run_id, run_events.run_id
# ORM SSOT: src/database/postgres/schema/run_store_schema.py
# env.py imports run_store_schema for autogen visibility (revision content remains human-written).
