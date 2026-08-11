"""Live verify aggregator — product smoke for Gateflow.

Answers: do the core features work together on a running Gateflow?

Steps (short HTTP checks; ephemeral wave identity where needed):

  health → webhook → status/metrics → wave_start → pr_thread → board

Uses ``gateflow:`` from ``tests/config.yaml`` (base_url, org/repo, …).
Client secrets stay in ``.env`` (``SMOKE_TENANT_ADMIN_TOKEN`` /
tenant_admin login, ``GITHUB_WEBHOOK_SECRET``).

**Not** in this aggregator (opt-in deep waves — run separately):

  - ``python -m tests.verify.verify_implement_lane``  # features.implement_lane
  - ``python -m tests.verify.verify_spec_lane``       # features.spec_lane

Usage:
  cp tests/config.yaml.example tests/config.yaml   # gateflow: target
  set -a && source .env && set +a
  make run   # API (+ worker if gateflow.require_worker)
  .venv/bin/python -m tests.verify.verify_all
"""

import sys
from typing import Callable

from tests.verify import (
    verify_board,
    verify_health,
    verify_pr_thread,
    verify_status_metrics,
    verify_wave_start,
    verify_webhook,
)

# Product smoke only — one step per core feature surface.
_VERIFY_STEPS: tuple[tuple[str, Callable[[], int]], ...] = (
    ("verify_health", verify_health.main),
    ("verify_webhook", verify_webhook.main),
    ("verify_status_metrics", verify_status_metrics.main),
    ("verify_wave_start", verify_wave_start.main),
    ("verify_pr_thread", verify_pr_thread.main),
    ("verify_board", verify_board.main),
)


def main() -> int:
    print(
        "[INFO] verify_all — Gateflow product smoke "
        f"({len(_VERIFY_STEPS)} features; deep lanes not included)"
    )
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
    print("[OK] verify_all passed — core Gateflow features green together")
    return 0


if __name__ == "__main__":
    sys.exit(main())
