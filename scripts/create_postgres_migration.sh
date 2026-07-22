#!/bin/bash

# Script to create a new PostgreSQL migration with Alembic
# Usage: ./scripts/create_postgres_migration.sh "Description of the migration"

set -e

if [ -z "$1" ]; then
    echo "Error: Migration description is required"
    echo "Usage: $0 \"Description of the migration\""
    exit 1
fi

DESCRIPTION="$1"

if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    while IFS='=' read -r key value; do
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        case "$key" in
            POSTGRES_*|DATABASE_*|DB_*)
                value="${value%\"}"
                value="${value#\"}"
                value="${value%\'}"
                value="${value#\'}"
                export "$key=$value"
                ;;
        esac
    done < .env
fi

# Check if database is up to date before creating new migration
CURRENT_REV=$(alembic -c postgres_alembic.ini current 2>/dev/null | awk '{print $1}' || echo "")
HEAD_REV=$(alembic -c postgres_alembic.ini heads 2>/dev/null | awk 'NR==1 {print $1}' || echo "")

if [ -n "$HEAD_REV" ] && [ "$CURRENT_REV" != "$HEAD_REV" ]; then
    echo "ERROR: Target database is not up to date."
    echo "  Current revision: ${CURRENT_REV:-None}"
    echo "  Head revision:   $HEAD_REV"
    echo ""
    echo "Run existing migrations first:"
    echo "  ./scripts/run_postgres_migration.sh head"
    echo ""
    exit 1
fi

echo "Creating new PostgreSQL migration: $DESCRIPTION"
alembic -c postgres_alembic.ini revision --autogenerate -m "$DESCRIPTION"

echo "Migration created successfully!"
echo "The new migration file can be found in postgres_migrations/versions/"
echo ""
echo "IMPORTANT: Please review the generated migration file to ensure:"
echo "1. All table dependencies are correctly managed"
echo "2. Tables are created in the correct order"
