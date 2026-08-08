"""Live verify: harness-readiness gate (INIT-GATEFLOW-012 W3).

Proves REQ-20 / REQ-21 on a running API (human at wave-acceptance):
  - explicit workspace without harness artifacts → 422; 0 enqueue
  - explicit workspace with ``.harness-pin.yaml`` + ``.harness/`` → past harness
    (enqueue or board-path success; not ``harness_artifacts_missing``)

Requires: API + Postgres, PROGRAMME_SERVICE_TOKEN, resolvable board ticket
fields (same as verify_wave_start).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_harness_readiness
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, smoke_wave_start_fields


def _write_ready_harness(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".harness-pin.yaml").write_text(
        "profile: python-backend\nref: verify-fixture\n",
        encoding="utf-8",
    )
    (root / ".harness").mkdir(exist_ok=True)


def main() -> int:
    base = require_base_url()
    cfg = load_tests_config()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    start_url = f"{base}/api/v1/waves/implement/start"

    with tempfile.TemporaryDirectory(prefix="gateflow-harness-") as tmp:
        tmp_root = Path(tmp)
        bare = tmp_root / "bare"
        bare.mkdir()
        ready = tmp_root / "ready"
        _write_ready_harness(ready)

        with httpx.Client(base_url=base, timeout=60.0) as client:
            # --- REQ-21 negative: missing artifacts → 422 ---------------------
            _identity, bare_body = smoke_wave_start_fields(
                cfg.gateflow,
                branch_slug="harness-bare",
                wave_id="W3",
                initiative_prefix="INIT-HRB",
            )
            bare_body["workspace_path"] = str(bare.resolve())
            bare_body["force_harness_recheck"] = True
            r = client.post(start_url, json=bare_body, headers=headers)
            if r.status_code != 422:
                print(
                    f"[ERROR] expected 422 for missing harness, " f"got {r.status_code}: {r.text}"
                )
                return 1
            detail = r.json()
            details = detail.get("details") or {}
            reason = details.get("reason") if isinstance(details, dict) else None
            if reason != "harness_artifacts_missing":
                # Some envelopes nest under detail/details differently
                text = r.text
                if "harness_artifacts_missing" not in text:
                    print(f"[ERROR] expected harness_artifacts_missing in 422: {text}")
                    return 1
            print("[OK] missing harness artifacts → 422 (REQ-21)")

            # --- REQ-20/21 positive: ready workspace past harness --------------
            _identity2, ready_body = smoke_wave_start_fields(
                cfg.gateflow,
                branch_slug="harness-ready",
                wave_id="W3",
                initiative_prefix="INIT-HRR",
            )
            ready_body["workspace_path"] = str(ready.resolve())
            ready_body["force_harness_recheck"] = True
            r = client.post(start_url, json=ready_body, headers=headers)
            if r.status_code == 422 and "harness_artifacts_missing" in r.text:
                print(f"[ERROR] ready workspace still failed harness: {r.text}")
                return 1
            if r.status_code not in {200, 201}:
                # Board / concurrency / other gates may still fail; harness must not.
                if "harness" in r.text.lower() and "harness_artifacts_missing" in r.text:
                    print(f"[ERROR] harness gate failed on ready tree: {r.text}")
                    return 1
                print(
                    f"[WARNING] ready path returned {r.status_code} "
                    f"(harness cleared; other gate): {r.text[:500]}"
                )
                # Still treat as pass for harness contract when reason is not harness miss
                if r.status_code == 422:
                    details = (r.json() or {}).get("details") or {}
                    if isinstance(details, dict) and details.get("reason") == (
                        "harness_artifacts_missing"
                    ):
                        return 1
                    print("[OK] harness ready (422 from non-harness gate)")
                    return 0
                print(f"[ERROR] unexpected status {r.status_code}: {r.text}")
                return 1
            body = r.json()
            if not body.get("run_id") or not body.get("job_id"):
                print(f"[ERROR] expected run/job ids on success: {body}")
                return 1
            print("[OK] harness-ready workspace enqueued (REQ-20/21)")

    print("[OK] verify_harness_readiness passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
