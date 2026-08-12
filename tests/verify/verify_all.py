"""Live verify aggregator — product smoke for Gateflow.

Answers: do the core features work together on a running Gateflow?

Steps (dependency order):

  health → webhook → auth_bootstrap → status/metrics → wave_start → pr_thread → board

Uses ``tests/config.yaml`` only (no process ``.env`` for verify client knobs).
``auth_bootstrap`` seeds platform_admin and ensures tenant_admin (login or
attach-to-existing-programme + write-back). GitHub-live / deep lanes stay opt-in.

Usage:
  cp tests/config.yaml.example tests/config.yaml
  # fill auth.platform_admin + client.github_webhook_secret
  # ensure at least one Programme exists in Gateflow (or run programme onboard once)
  make run
  .venv/bin/python -m tests.verify.verify_all
"""

import sys
from typing import Callable

from tests.verify import (
    verify_auth_bootstrap,
    verify_board,
    verify_health,
    verify_pr_thread,
    verify_status_metrics,
    verify_wave_start,
    verify_webhook,
)

# Product smoke — bootstrap before tenant-scoped APIs.
_VERIFY_STEPS: tuple[tuple[str, Callable[[], int]], ...] = (
    ("verify_health", verify_health.main),
    ("verify_webhook", verify_webhook.main),
    ("verify_auth_bootstrap", verify_auth_bootstrap.main),
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
