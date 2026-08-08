# Human-owned Alembic revision required for TASK-W0-02 (agents must not edit versions/).
#
# Create with: ./scripts/create_postgres_migration.sh "add_tenant_registry_tables"
# Then hand-write upgrade/downgrade for tables registered on postgres_metadata:
#
#   tenants
#     - id UUID PK
#     - name VARCHAR(255) NOT NULL
#     - pat TEXT NOT NULL  (plaintext G1 — never select into API responses)
#     - bearer_token VARCHAR(255) NOT NULL UNIQUE
#     - workspace_root TEXT NOT NULL
#     - board_project_owner VARCHAR(255) NULL
#     - board_project_number INTEGER NULL
#     - created_at / updated_at TIMESTAMPTZ
#
#   tenant_repos
#     - id UUID PK
#     - tenant_id UUID NOT NULL FK → tenants.id ON DELETE CASCADE
#     - org VARCHAR(255) NOT NULL
#     - repo VARCHAR(255) NOT NULL
#     - harness_verified BOOLEAN NOT NULL DEFAULT false  (W3 cache; additive now)
#     - UNIQUE (tenant_id, org, repo)
#     - created_at / updated_at TIMESTAMPTZ
#
#   tenant_users
#     - id UUID PK
#     - tenant_id UUID NOT NULL FK → tenants.id ON DELETE CASCADE
#     - identity VARCHAR(512) NOT NULL
#     - UNIQUE (tenant_id, identity)
#     - created_at / updated_at TIMESTAMPTZ
#
# Indexes: tenants.bearer_token (unique), tenant_repos.tenant_id, tenant_users.tenant_id
# ORM SSOT: src/database/postgres/schema/tenant_schema.py
# env.py imports tenant_schema for metadata registration (revision content remains human-written).
#
# Downgrade: DROP TABLE tenant_users, tenant_repos, tenants (order matters for FKs).
