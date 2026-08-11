# Human-owned Alembic revision required for INIT-GATEFLOW-014 W0
#
# Agents must not edit postgres_migrations/versions/.
#
# Create with: ./scripts/create_postgres_migration.sh "add_user_identities"
# Then hand-write upgrade/downgrade for the table registered on postgres_metadata
# via `src.database.postgres.schema.user_identity_schema` (imported in env.py):
#
#   user_identities
#     - id UUID PK
#     - credential_identifier VARCHAR(512) NOT NULL
#     - password_hash TEXT NOT NULL
#     - role VARCHAR(64) NOT NULL
#         (wire values: platform_admin | tenant_admin)
#     - tenant_id UUID NULL
#         (required for tenant_admin rows; null for platform_admin)
#     - created_at / updated_at TIMESTAMPTZ
#     - UNIQUE (credential_identifier)
#     - INDEX on credential_identifier
#
# Apply with: ./scripts/run_postgres_migration.sh head
#
# Live verify: `.venv/bin/python -m tests.verify.verify_jwt_login`
