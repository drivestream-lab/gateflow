"""Live verify aggregator for gateflow W0 smoke.

Runs verify scripts in order. Requires running API + migrated Postgres.
Webhook step needs GITHUB_WEBHOOK_SECRET in the environment.

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_all
"""

import sys

from tests.verify import verify_health, verify_webhook

# Order: cheap liveness first, then signed webhook enqueue/idempotency.
_VERIFY_STEPS: tuple[tuple[str, object], ...] = (
    ("verify_health", verify_health),
    ("verify_webhook", verify_webhook),
)


def main() -> int:
    failed: list[str] = []
    for name, module in _VERIFY_STEPS:
        print(f"[INFO] --- {name} ---")
        code = int(module.main())
        if code != 0:
            print(f"[ERROR] {name} failed with exit {code}")
            failed.append(name)
        else:
            print(f"[OK] {name} passed")
    if failed:
        print(f"[ERROR] verify_all failed: {', '.join(failed)}")
        return 1
    print("[OK] verify_all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
