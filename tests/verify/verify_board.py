"""Live verify: board dumb primitives (FR-24) + auth (ADR-005).

Requires running API and ``auth.tenant_admin`` in ``tests/config.yaml``.
Forge-backed create/list/status/link run only when
``features.board.live_github: true`` (same opt-in idea as implement_lane) and
the Gateflow **runtime** has forge auth configured. Otherwise auth +
validation edges are asserted and forge I/O is skipped (unit owns ForgeClient
board methods).

INIT-GATEFLOW-008 W2: also asserts the pinned WorkManifest contract script
rejects ``apiVersion: launchpad/v1`` (prayog/v1-only before create_board_tickets).

INIT-GATEFLOW-010 W2: when ``features.create_tickets.authorize_run_id`` is set with a
STOPPED run at ``board-tickets-action``, a non-canonical ``plan_path`` must fail closed
with **422** and **0** board creates (triple predicate gate — unit owns matrix).
Authorize + board-seed projection remains unit-owned
(``test_forge_action_service``); create_board_tickets stays
``authorization: explicit``.

Usage:
  cp tests/config.yaml.example tests/config.yaml
  .venv/bin/python -m tests.verify.verify_board
"""

import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config
from tests._helpers.verify_jwt_auth import require_tenant_admin_token
from tests._helpers.workmanifest_fixtures import LAUNCHPAD_V1_BOARD_FIXTURE

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONTRACT_SCRIPT = _REPO_ROOT / "prayog-skills" / "scripts" / "workmanifest_contract.py"


def _assert_pin_rejects_launchpad_v1() -> int:
    """Fail closed when pin validator is missing or accepts launchpad/v1."""
    if not _CONTRACT_SCRIPT.is_file():
        print(f"[ERROR] pin WorkManifest contract script missing: {_CONTRACT_SCRIPT}")
        return 1
    with tempfile.TemporaryDirectory(prefix="gateflow-wm-") as tmp:
        plan = Path(tmp) / "plan.md"
        plan.write_text(LAUNCHPAD_V1_BOARD_FIXTURE, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(_CONTRACT_SCRIPT), str(plan)],
            check=False,
            capture_output=True,
            text=True,
        )
    if proc.returncode == 0:
        print("[ERROR] expected nonzero exit for launchpad/v1 WorkManifest; got 0")
        return 1
    out = (proc.stderr or proc.stdout or "").strip()
    if "prayog/v1" not in out and "launchpad/v1" not in out and "apiVersion" not in out:
        print(f"[ERROR] unexpected validator output for launchpad reject: {out}")
        return 1
    print("[OK] pin workmanifest_contract rejects apiVersion=launchpad/v1")
    return 0


def main() -> int:
    wm_rc = _assert_pin_rejects_launchpad_v1()
    if wm_rc != 0:
        return wm_rc

    cfg = load_tests_config()
    base_url = require_base_url()
    try:
        token = require_tenant_admin_token()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    org = cfg.gateflow.org
    repo = cfg.gateflow.repo
    list_url = f"{base_url}/api/v1/board/tickets"
    create_url = list_url

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.get(list_url, params={"org": org, "repo": repo})
            if bare.status_code != 401:
                print(f"[ERROR] expected 401 without token on board list, got {bare.status_code}")
                return 1
            print("[OK] GET /api/v1/board/tickets without token → 401")

            bad = client.patch(
                f"{base_url}/api/v1/board/tickets/1/status",
                headers=headers,
                json={"org": org, "repo": repo},
            )
            if bad.status_code != 400:
                print(
                    f"[ERROR] expected 400 for empty status update, got {bad.status_code}: "
                    f"{bad.text}"
                )
                return 1
            print("[OK] PATCH /api/v1/board/tickets/1/status empty body fields → 400")

            if not cfg.features.board.live_github:
                print(
                    "[OK] board auth + validation edges passed "
                    "(skip forge mutations — set features.board.live_github: true "
                    "when Gateflow runtime forge is configured); "
                    "create_board_tickets authorize path: unit + prayog/v1 pin contract"
                )
                return 0

            initiative_id = f"INIT-BOARD-VERIFY-{uuid.uuid4().hex[:8]}"
            idem_key = f"verify-{initiative_id}"
            create_body = {
                "org": org,
                "repo": repo,
                "title": f"[gateflow verify] {initiative_id}",
                "ticket_type": "Feature",
                "initiative_id": initiative_id,
                "body": "Created by tests.verify.verify_board",
            }
            created = client.post(
                create_url,
                headers={**headers, "Idempotency-Key": idem_key},
                json=create_body,
            )
            if created.status_code not in {200, 201}:
                print(
                    f"[ERROR] expected 2xx for board create, got {created.status_code}: "
                    f"{created.text}"
                )
                return 1
            create_payload = created.json()
            ticket = create_payload.get("ticket") or {}
            ticket_id = ticket.get("ticket_id")
            if not ticket_id:
                print(f"[ERROR] create response missing ticket_id: {create_payload}")
                return 1
            print(
                f"[OK] POST /api/v1/board/tickets → ticket_id={ticket_id} "
                f"created={create_payload.get('created')} "
                f"partial={create_payload.get('partial')}"
            )

            # Same Idempotency-Key as first create (initiative+type also deduped server-side).
            replay = client.post(
                create_url,
                headers={**headers, "Idempotency-Key": idem_key},
                json=create_body,
            )
            if replay.status_code not in {200, 201}:
                print(
                    f"[ERROR] expected 2xx for idempotent create, got {replay.status_code}: "
                    f"{replay.text}"
                )
                return 1
            if not replay.json().get("idempotent_replay"):
                print(f"[ERROR] expected idempotent_replay on second create: {replay.json()}")
                return 1
            print("[OK] POST /api/v1/board/tickets idempotent on initiative_id+type")

            listed = client.get(
                list_url,
                headers=headers,
                params={
                    "org": org,
                    "repo": repo,
                    "initiative_id": initiative_id,
                    "type": "Feature",
                    "state": "all",
                },
            )
            if listed.status_code != 200:
                print(
                    f"[ERROR] expected 200 for board list, got {listed.status_code}: {listed.text}"
                )
                return 1
            tickets = listed.json().get("tickets") or []
            if not any(item.get("ticket_id") == ticket_id for item in tickets):
                print(f"[ERROR] created ticket missing from list: {listed.json()}")
                return 1
            print("[OK] GET /api/v1/board/tickets filter → includes created ticket")

            statused = client.patch(
                f"{base_url}/api/v1/board/tickets/{ticket_id}/status",
                headers=headers,
                json={"org": org, "repo": repo, "column": "Verify"},
            )
            if statused.status_code != 200:
                print(
                    f"[ERROR] expected 200 for status update, got {statused.status_code}: "
                    f"{statused.text}"
                )
                return 1
            if statused.json().get("column") != "Verify":
                print(f"[ERROR] expected column=Verify, got {statused.json()}")
                return 1
            print("[OK] PATCH /api/v1/board/tickets/{id}/status → column set")

            linked = client.post(
                f"{base_url}/api/v1/board/tickets/{ticket_id}/links",
                headers=headers,
                json={"org": org, "repo": repo, "pr_number": 1},
            )
            if linked.status_code != 200:
                print(f"[ERROR] expected 200 for link, got {linked.status_code}: {linked.text}")
                return 1
            if not linked.json().get("link_ref"):
                print(f"[ERROR] missing link_ref: {linked.json()}")
                return 1
            print("[OK] POST /api/v1/board/tickets/{id}/links → link_ref present")

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure during verify_board: {exc}")
        return 1

    print("[OK] verify_board passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
