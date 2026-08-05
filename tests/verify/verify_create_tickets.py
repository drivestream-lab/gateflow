"""Live verify: WorkManifest → board EPIC + wave tickets (create_board_tickets projection).

Covers the post–spec-merge board seed surface used before implement-lane:

1. Pin ``workmanifest_contract.py`` pass on Implementation-Plan §9 (prayog/v1)
2. Parse WorkManifest; create EPIC + Feature tickets via ``POST /api/v1/board/tickets``
   (same BoardService projection as ``ForgeActionService.execute_create_board_tickets``)
3. Print ``epic_ticket_id`` + ``wave_ticket_ids`` for ``features.implement_lane`` config

Optional: when ``authorize_run_id`` is set, call
``POST /api/v1/runs/{run_id}/forge/authorize`` instead (run must already be STOPPED
at pin ``board-tickets-action`` with handoff.forge initiative + plan_path).

Does **not** replace the human ``/create-board-tickets`` skill; this is Gateflow
HTTP smoke for dogfood. Not in ``verify_all``.

Usage:
  cp tests/config.yaml.example tests/config.yaml
  # set features.create_tickets.enabled: true + workspace/plan_path/initiative
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_create_tickets
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

from src.models.board_models import BoardTicketType
from src.models.work_manifest_models import (
    parse_work_manifest_from_plan,
    run_workmanifest_contract,
)
from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def _print_implement_snippet(
    *,
    initiative: str,
    wave_id: str,
    epic_ticket_id: str,
    wave_ticket_id: str,
) -> None:
    print("[OK] seed summary for implement_lane config:")
    print(f"  initiative_id: {initiative}")
    print(f"  epic_ticket_id: {epic_ticket_id}")
    print(f"  wave_id: {wave_id}")
    print(f"  ticket_id: {wave_ticket_id}   # ← features.implement_lane.wave_start.ticket_id")
    print(
        "Paste ticket_id into tests/config.yaml, set implement_lane.enabled: true, "
        "then: .venv/bin/python -m tests.verify.verify_implement_lane"
    )


def _authorize_path(
    *,
    base_url: str,
    headers: dict[str, str],
    run_id: str,
    workspace: Path,
    wave_id: str,
) -> int:
    try:
        UUID(run_id)
    except ValueError:
        print(f"[ERROR] features.create_tickets.authorize_run_id is not a UUID: {run_id!r}")
        return 1

    url = f"{base_url}/api/v1/runs/{run_id}/forge/authorize"
    body = {
        "authorized": True,
        "workspace_path": str(workspace),
    }
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=body, headers=headers)
    if resp.status_code not in {200, 201}:
        print(f"[ERROR] forge/authorize failed status={resp.status_code}: {resp.text}")
        return 1
    payload = resp.json()
    action = payload.get("action")
    board = payload.get("board") or {}
    if action != "create_board_tickets":
        print(f"[ERROR] expected action=create_board_tickets, got {action!r}: {payload}")
        return 1
    epic = str(board.get("epic_ticket_id") or "").strip()
    wave_ids = board.get("wave_ticket_ids") or []
    if not epic or not isinstance(wave_ids, list) or not wave_ids:
        print(f"[ERROR] authorize response missing epic/wave ticket ids: {payload}")
        return 1
    print(f"[OK] POST forge/authorize → epic_ticket_id={epic} " f"wave_ticket_ids={wave_ids}")
    # Map wave_id → ticket by order when titles unknown; prefer first matching
    # wave index from printed list (caller should set wave_id=W0 → index 0).
    wave_ticket = str(wave_ids[0])
    if wave_id.upper().startswith("W") and wave_id[1:].isdigit():
        idx = int(wave_id[1:])
        if 0 <= idx < len(wave_ids):
            wave_ticket = str(wave_ids[idx])
    initiative = str(board.get("initiative") or "").strip() or "(see handoff)"
    _print_implement_snippet(
        initiative=initiative,
        wave_id=wave_id,
        epic_ticket_id=epic,
        wave_ticket_id=wave_ticket,
    )
    return 0


def _board_seed_path(
    *,
    base_url: str,
    headers: dict[str, str],
    org: str,
    repo: str,
    workspace: Path,
    plan_file: Path,
    initiative: str,
    wave_id: str,
    dry_run: bool,
) -> int:
    try:
        run_workmanifest_contract(workspace=workspace, plan_file=plan_file)
    except ValueError as exc:
        print(f"[ERROR] WorkManifest contract failed: {exc}")
        return 1
    print("[OK] workmanifest_contract pass (prayog/v1)")

    try:
        manifest = parse_work_manifest_from_plan(plan_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"[ERROR] WorkManifest parse failed: {exc}")
        return 1

    if manifest.initiative != initiative:
        print(
            f"[ERROR] config initiative {initiative!r} != "
            f"WorkManifest.initiative {manifest.initiative!r}"
        )
        return 1

    wave_ids_in_plan = [w.id for w in manifest.work]
    if wave_id not in wave_ids_in_plan:
        print(
            f"[ERROR] features.create_tickets.wave_id={wave_id!r} not in "
            f"WorkManifest work[] ids={wave_ids_in_plan}"
        )
        return 1

    print(f"[OK] parsed WorkManifest initiative={manifest.initiative} " f"waves={wave_ids_in_plan}")

    if dry_run:
        print("[OK] dry_run=true — skipping board creates")
        return 0

    create_url = f"{base_url}/api/v1/board/tickets"
    with httpx.Client(timeout=120.0) as client:
        epic_body: dict[str, Any] = {
            "org": org,
            "repo": repo,
            "title": manifest.epic.title,
            "body": manifest.epic.body,
            "ticket_type": BoardTicketType.EPIC.value,
            "initiative_id": manifest.initiative,
        }
        epic_resp = client.post(create_url, json=epic_body, headers=headers)
        if epic_resp.status_code not in {200, 201}:
            print(
                f"[ERROR] EPIC create failed status={epic_resp.status_code}: " f"{epic_resp.text}"
            )
            return 1
        epic_payload = epic_resp.json()
        epic_ticket = (epic_payload.get("ticket") or {}).get("ticket_id")
        if not epic_ticket:
            print(f"[ERROR] EPIC response missing ticket_id: {epic_payload}")
            return 1
        print(
            f"[OK] EPIC ticket_id={epic_ticket} "
            f"created={epic_payload.get('created')} "
            f"replay={epic_payload.get('idempotent_replay')}"
        )

        wave_ticket_by_id: dict[str, str] = {}
        for wave in manifest.work:
            body = wave.body or ""
            if epic_ticket:
                body = f"Parent EPIC: #{epic_ticket}\n\n{body}".strip()
            wave_body = {
                "org": org,
                "repo": repo,
                "title": wave.title,
                "body": body or None,
                "ticket_type": BoardTicketType.FEATURE.value,
                "initiative_id": f"{manifest.initiative}:{wave.id}",
            }
            wave_resp = client.post(create_url, json=wave_body, headers=headers)
            if wave_resp.status_code not in {200, 201}:
                print(
                    f"[ERROR] wave {wave.id} create failed "
                    f"status={wave_resp.status_code}: {wave_resp.text}"
                )
                return 1
            wave_payload = wave_resp.json()
            tid = (wave_payload.get("ticket") or {}).get("ticket_id")
            if not tid:
                print(f"[ERROR] wave {wave.id} missing ticket_id: {wave_payload}")
                return 1
            wave_ticket_by_id[wave.id] = str(tid)
            print(
                f"[OK] wave {wave.id} ticket_id={tid} "
                f"created={wave_payload.get('created')} "
                f"replay={wave_payload.get('idempotent_replay')}"
            )

    _print_implement_snippet(
        initiative=manifest.initiative,
        wave_id=wave_id,
        epic_ticket_id=str(epic_ticket),
        wave_ticket_id=wave_ticket_by_id[wave_id],
    )
    evidence = {
        "initiative": manifest.initiative,
        "epic_ticket_id": str(epic_ticket),
        "wave_ticket_ids": wave_ticket_by_id,
    }
    print(f"[OK] evidence_json={json.dumps(evidence, sort_keys=True)}")
    return 0


def main() -> int:
    cfg = load_tests_config()
    feature = cfg.features.create_tickets
    if not feature.enabled:
        print(
            "[INFO] features.create_tickets.enabled is false — skipping "
            "(set enabled: true to seed board tickets from WorkManifest)"
        )
        return 0

    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_create_tickets")
        return 1

    workspace_raw = feature.workspace.strip()
    if not workspace_raw:
        print("[ERROR] features.create_tickets.workspace is required (absolute app root)")
        return 1
    workspace = Path(workspace_raw).expanduser().resolve()
    if not workspace.is_dir():
        print(f"[ERROR] workspace is not a directory: {workspace}")
        return 1

    base_url = require_base_url()
    headers = {"Authorization": f"Bearer {token}"}
    org = cfg.gateflow.org
    repo = cfg.gateflow.repo
    wave_id = feature.wave_id.strip() or "W0"

    authorize_run_id = feature.authorize_run_id.strip()
    if authorize_run_id:
        print(
            f"[INFO] using forge/authorize path run_id={authorize_run_id} "
            "(board-tickets-action STOP required)"
        )
        return _authorize_path(
            base_url=base_url,
            headers=headers,
            run_id=authorize_run_id,
            workspace=workspace,
            wave_id=wave_id,
        )

    plan_rel = feature.plan_path.strip()
    initiative = feature.initiative.strip()
    if not plan_rel or not initiative:
        print(
            "[ERROR] features.create_tickets.plan_path and initiative are required "
            "for board projection seed"
        )
        return 1

    plan_file = (workspace / plan_rel).resolve()
    try:
        plan_file.relative_to(workspace)
    except ValueError:
        print(f"[ERROR] plan_path escapes workspace: {plan_rel}")
        return 1
    if not plan_file.is_file():
        print(f"[ERROR] plan_path not found: {plan_file}")
        return 1

    return _board_seed_path(
        base_url=base_url,
        headers=headers,
        org=org,
        repo=repo,
        workspace=workspace,
        plan_file=plan_file,
        initiative=initiative,
        wave_id=wave_id,
        dry_run=feature.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
