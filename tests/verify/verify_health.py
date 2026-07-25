"""Live verify: health liveness + detailed postgres/redis (W0 smoke).

Requires running API (+ Postgres/Redis for detailed=true).

Usage:
  .venv/bin/python -m tests.verify.verify_health
"""

import sys

import httpx

from src.models.health_models import HealthLivenessType, HealthStatusType
from tests._helpers.api_paths import require_base_url


def main() -> int:
    base_url = require_base_url()
    simple_url = f"{base_url}/health"
    detailed_url = f"{base_url}/health?detailed=true"

    try:
        with httpx.Client(timeout=30.0) as client:
            simple = client.get(simple_url)
            if simple.status_code != 200:
                print(f"[ERROR] GET {simple_url} expected 200, got {simple.status_code}")
                return 1
            body = simple.json()
            if body.get("status") != HealthLivenessType.OK.value:
                print(f"[ERROR] unexpected health body: {body}")
                return 1
            print("[OK] GET /health → status=ok")

            detailed = client.get(detailed_url)
            if detailed.status_code != 200:
                print(
                    f"[ERROR] GET {detailed_url} expected 200, got {detailed.status_code}: "
                    f"{detailed.text}"
                )
                return 1
            detail = detailed.json()
            if detail.get("status") != HealthStatusType.UP.value:
                print(f"[ERROR] aggregate health not up: {detail}")
                return 1
            services = detail.get("services") or {}
            for name in ("postgres", "redis"):
                entry = services.get(name) or {}
                if entry.get("status") != HealthStatusType.UP.value:
                    print(f"[ERROR] detailed health {name} not up: {detail}")
                    return 1
            print("[OK] GET /health?detailed=true → postgres/redis up")
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure talking to {base_url}: {exc}")
        return 1

    print("[OK] verify_health passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
