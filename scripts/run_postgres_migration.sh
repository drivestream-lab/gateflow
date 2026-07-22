#!/bin/bash

# Script to run PostgreSQL migrations with Alembic
# Usage: ./scripts/run_postgres_migration.sh [target]
# Examples:
#   ./scripts/run_postgres_migration.sh         # Run all migrations to head
#   ./scripts/run_postgres_migration.sh head    # Run all migrations to head
#   ./scripts/run_postgres_migration.sh +1      # Run one migration forward
#   ./scripts/run_postgres_migration.sh -1      # Roll back one migration

set -e

TARGET=${1:-head}

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

COMMAND="upgrade"

if [[ "$TARGET" == -1 ]]; then
    # Roll back one migration: resolve current revision and downgrade to its parent
    COMMAND="downgrade"
    CURRENT_REV=$(alembic -c postgres_alembic.ini current 2>/dev/null | awk '{print $1}' || echo "")
    if [ -z "$CURRENT_REV" ] || [ "$CURRENT_REV" = "None" ]; then
        echo "No current revision; nothing to downgrade."
        exit 1
    fi
    # Parent = first column of the history line that has "-> current_rev" (format: "parent -> child")
    TARGET=$(alembic -c postgres_alembic.ini history 2>/dev/null | grep -E -- "->.*${CURRENT_REV}" | head -1 | awk '{print $1}' || echo "")
    if [ -z "$TARGET" ] || [[ ! "$TARGET" =~ ^[a-f0-9]+$ ]]; then
        echo "Could not determine parent revision for downgrade (current: $CURRENT_REV)."
        exit 1
    fi
    echo "Downgrading one step: $CURRENT_REV -> $TARGET"
elif [[ "$TARGET" =~ ^-[0-9]+$ ]]; then
    echo "Only -1 (roll back one) is supported. Use: ./scripts/run_postgres_migration.sh <revision> to downgrade to a specific revision."
    exit 1
elif [[ "$TARGET" != "head" && "$TARGET" != "+"* ]]; then
    # Explicit revision: downgrade if it's an ancestor of current (target is in the past)
    CURRENT_REV=$(alembic -c postgres_alembic.ini current 2>/dev/null | awk '{print $1}' || echo "")
    if [ -n "$CURRENT_REV" ] && [ "$CURRENT_REV" != "None" ] && [ "$CURRENT_REV" != "$TARGET" ]; then
        # Build chain from current down to base; if TARGET appears in that chain, we downgrade
        SEEN=""
        REV="$CURRENT_REV"
        while [ -n "$REV" ]; do
            [ "$REV" = "$TARGET" ] && COMMAND="downgrade" && break
            PARENT=$(alembic -c postgres_alembic.ini history 2>/dev/null | grep -E -- "->.*${REV}" | head -1 | awk '{print $1}' || echo "")
            [ -z "$PARENT" ] || [ "$PARENT" = "<base>" ] && break
            REV="$PARENT"
        done
    fi
fi

echo "Running PostgreSQL migrations: $COMMAND to target: $TARGET"
alembic -c postgres_alembic.ini $COMMAND "$TARGET"

echo "PostgreSQL migration completed successfully!"
