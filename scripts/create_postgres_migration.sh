#!/usr/bin/env bash

# Create a new PostgreSQL migration revision with Alembic (project .venv).
# Usage: ./scripts/create_postgres_migration.sh "Description of the migration"
#
# Uses .venv/bin/alembic — run `make setup` first. Do not rely on conda PATH.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [ -z "${1:-}" ]; then
    echo "[ERROR] Migration description is required"
    echo "Usage: $0 \"Description of the migration\""
    exit 1
fi

DESCRIPTION="$1"

ALEMBIC="${REPO_ROOT}/.venv/bin/alembic"
if [ ! -x "${ALEMBIC}" ]; then
    echo "[ERROR] Alembic not found at ${ALEMBIC}"
    echo "        Create the project venv first: make setup"
    echo "        (Do not use conda — this repo uses Python 3.12 + .venv only.)"
    exit 1
fi

ALEMBIC_CONFIG="${REPO_ROOT}/postgres_migrations/alembic.ini"
if [ ! -f "${ALEMBIC_CONFIG}" ]; then
    echo "[ERROR] Missing Alembic config: ${ALEMBIC_CONFIG}"
    exit 1
fi

if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    while IFS='=' read -r key value || [ -n "${key:-}" ]; do
        [[ -z "${key}" || "${key}" =~ ^# ]] && continue
        case "${key}" in
            POSTGRES_*|DATABASE_*|DB_*)
                value="${value%\"}"
                value="${value#\"}"
                value="${value%\'}"
                value="${value#\'}"
                export "${key}=${value}"
                ;;
        esac
    done < .env
fi

# Check if database is up to date before creating new migration
CURRENT_REV=$("${ALEMBIC}" -c "${ALEMBIC_CONFIG}" current 2>/dev/null | awk '{print $1}' || echo "")
HEAD_REV=$("${ALEMBIC}" -c "${ALEMBIC_CONFIG}" heads 2>/dev/null | awk 'NR==1 {print $1}' || echo "")

if [ -n "${HEAD_REV}" ] && [ "${CURRENT_REV}" != "${HEAD_REV}" ]; then
    echo "[ERROR] Target database is not up to date."
    echo "  Current revision: ${CURRENT_REV:-None}"
    echo "  Head revision:   ${HEAD_REV}"
    echo ""
    echo "Run existing migrations first:"
    echo "  ./scripts/run_postgres_migration.sh head"
    echo ""
    exit 1
fi

echo "Creating new PostgreSQL migration: ${DESCRIPTION}"
echo "Using: ${ALEMBIC}"
"${ALEMBIC}" -c "${ALEMBIC_CONFIG}" revision --autogenerate -m "${DESCRIPTION}"

echo "Migration created successfully!"
echo "The new migration file can be found in postgres_migrations/versions/"
echo ""
echo "IMPORTANT: Please review the generated migration file to ensure:"
echo "1. All table dependencies are correctly managed"
echo "2. Tables are created in the correct order"
echo "3. upgrade/downgrade match the intended DDL (prefer intentional edits over raw autogen)"
