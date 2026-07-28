"""Live verify: spec-lane Cursor prove-it (INIT-GATEFLOW-003 Scenario A / W2).

Spec lane (when pin marks nodes ``dispatch: orchestrated``):

  spec-draft → initiative-feasibility → spec-technical-review →
  spec-implementation-plan → … (gate per pin)

Harness mirrors implement_lane: opt-in via ``features.spec_lane``, wave-start
body owned by that section, evidence path is verify-only.

Until pin + PRD dogfood are ready, leave ``enabled: false`` (this script exits 0).

Usage:
  # edit tests/config.yaml features.spec_lane
  set -a && source .env && set +a
  make run
  .venv/bin/python -m tests.verify.verify_spec_lane
"""

from __future__ import annotations

import sys

from tests._helpers.tests_config import load_tests_config


def main() -> int:
    cfg = load_tests_config()
    lane = cfg.features.spec_lane
    if not lane.enabled:
        print(
            "[INFO] features.spec_lane.enabled is false — skipping spec-lane "
            "live prove-it (W2; awaits PRD + pin). Set enabled: true when ready."
        )
        return 0

    print(
        "[ERROR] features.spec_lane.enabled is true but live prove-it chain "
        "is not implemented yet — leave enabled: false until W2 harness lands"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
