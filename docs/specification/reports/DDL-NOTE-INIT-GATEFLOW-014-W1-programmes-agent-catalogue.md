# Human-owned Alembic revision required for INIT-GATEFLOW-014 W1
#
# Agents must not edit postgres_migrations/versions/.
#
# Create with: ./scripts/create_postgres_migration.sh "add_programmes_and_agent_catalogue"
# Then hand-write upgrade/downgrade for tables registered on postgres_metadata via:
#   - src.database.postgres.schema.programme_schema
#   - src.database.postgres.schema.platform_agent_catalogue_schema
# (imported in postgres_migrations/env.py)
#
# programmes
#   - id UUID PK
#   - name VARCHAR(255) NOT NULL
#   - tenant_id UUID NOT NULL UNIQUE FK → tenants.id (RESTRICT)
#   - github_pat TEXT NOT NULL
#   - workspace_root TEXT NOT NULL
#   - meta_org VARCHAR(255) NOT NULL
#   - meta_repo VARCHAR(255) NOT NULL
#   - meta_ref VARCHAR(512) NULL
#   - github_app_id VARCHAR(255) NULL          (REQ-14 reserved unused)
#   - github_installation_id VARCHAR(255) NULL (REQ-14 reserved unused)
#   - lane_defaults JSONB NOT NULL DEFAULT '{}'
#   - created_at / updated_at TIMESTAMPTZ
#   - INDEX on tenant_id
#
# platform_agent_catalogue
#   - id UUID PK
#   - runner_id VARCHAR(128) NOT NULL UNIQUE
#   - credential TEXT NULL
#   - display_name VARCHAR(255) NULL
#   - created_at / updated_at TIMESTAMPTZ
#   - INDEX on runner_id
#
# Apply with: ./scripts/run_postgres_migration.sh head
#
# Live verify:
#   .venv/bin/python -m tests.verify.verify_programme_onboarding
#   .venv/bin/python -m tests.verify.verify_agent_catalogue
