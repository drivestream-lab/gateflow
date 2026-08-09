# Human-owned Alembic revision required for INIT-GATEFLOW-013 W0 (agents must not edit versions/).
#
# Create with: ./scripts/create_postgres_migration.sh "add_tenant_programme_connections"
# Then hand-write upgrade/downgrade for tables registered on postgres_metadata:
#
#   tenant_programme_connections
#     - id UUID PK
#     - tenant_id UUID NOT NULL FK → tenants.id ON DELETE CASCADE
#     - org VARCHAR(255) NOT NULL
#     - repo VARCHAR(255) NOT NULL
#     - ref VARCHAR(512) NULL
#     - last_synced_at TIMESTAMPTZ NOT NULL
#     - created_at / updated_at TIMESTAMPTZ
#     - UNIQUE (tenant_id)  — exactly one active programme connection per tenant (REQ-28)
#
# Indexes: tenant_programme_connections.tenant_id (unique covers lookups)
# ORM SSOT: src/database/postgres/schema/tenant_schema.py
#           (TenantProgrammeConnectionSchema)
# env.py already imports tenant_schema for metadata registration
# (revision content remains human-written).
#
# Downgrade: DROP TABLE tenant_programme_connections
