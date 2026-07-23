"""Live verify aggregator for gateflow W0/W1 smoke.

Requires running API + migrated Postgres.
Needs GITHUB_WEBHOOK_SECRET and PROGRAMME_SERVICE_TOKEN in the environment.

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_all
"""

import sys
from typing import Callable

from tests.verify import (
    verify_health,
    verify_status_metrics,
    verify_wave_smoke,
    verify_webhook,
)

_VERIFY_STEPS: tuple[tuple[str, Callable[[], int]], ...] = (
    ("verify_health", verify_health.main),
    ("verify_webhook", verify_webhook.main),
    ("verify_status_metrics", verify_status_metrics.main),
    ("verify_wave_smoke", verify_wave_smoke.main),
)


def main() -> int:
    failed: list[str] = []
    for name, step in _VERIFY_STEPS:
        print(f"[INFO] --- {name} ---")
        code = int(step())
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
