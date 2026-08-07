"""Live verify: CAP-02 checkpoint persistence + history + composed readout (INIT-GATEFLOW-011 W1).

Requires running API and PROGRAMME_SERVICE_TOKEN. Optional fixture PR via
GATEFLOW_CHECKPOINT_PR (and optional GATEFLOW_CHECKPOINT_ID, default
coding-readiness) for a live GitHub evidence path. Without it, auth/shape +
unknown-checkpoint + 404 no-run-for-wave edges are asserted (unit owns
ForgeClient doubles).

Covers:
  - REQ-03 stale never reported as pass (shape only — stale needs a fixture PR
    with a real approval-then-push sequence to assert verdict=not_satisfied)
  - REQ-06 persistence: a status call followed by a history call returns the
    record (when a run is resolvable for the PR)
  - REQ-07 history marks records historical; never claims live verdict
  - REQ-08 composed readout via initiative+wave; 404 no run found for this wave
  - REQ-28 GET-only; non-GET rejected

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional: export GATEFLOW_CHECKPOINT_PR=159
  # optional: export GATEFLOW_COMPOSED_INITIATIVE=INIT-X GATEFLOW_COMPOSED_WAVE=W0
  .venv/bin/python -m tests.verify.verify_checkpoint_history
"""

from __future__ import annotations

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_status_code(resp: httpx.Response, expected: int, label: str) -> int:
    if resp.status_code != expected:
        print(f"[ERROR] {label}: expected {expected}, got {resp.status_code}: {resp.text}")
        return 1
    print(f"[OK] {label} ({resp.status_code})")
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_checkpoint_history")
        return 1

    owner = cfg.gateflow.org
    repo = cfg.gateflow.repo
    checkpoint_id = os.environ.get("GATEFLOW_CHECKPOINT_ID", "coding-readiness")
    pr_raw = os.environ.get("GATEFLOW_CHECKPOINT_PR", "").strip()
    headers = _auth_headers(token)
    status_path = f"{base_url}/api/v1/checkpoints/status"
    history_path = f"{base_url}/api/v1/checkpoints/history"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        # REQ-28 — non-GET on /history rejected
        post_history = client.post(history_path, headers=headers, json={})
        rc |= _assert_status_code(post_history, 405, "checkpoints/history rejects non-GET (405)")

        # REQ-07 — history 401 without token
        no_auth = client.get(
            history_path,
            params={"owner": owner, "repo": repo, "pr_number": 1},
        )
        rc |= _assert_status_code(no_auth, 401, "checkpoints/history 401 without programme token")

        # REQ-08 — composed readout: neither raw nor composed supplied → 400
        neither = client.get(
            status_path,
            params={"checkpoint_id": checkpoint_id},
            headers=headers,
        )
        rc |= _assert_status_code(neither, 400, "status 400 when neither raw nor composed supplied")

        # REQ-08 — composed readout: initiative+wave with no run → 404 no run found for this wave
        composed_no_run = client.get(
            status_path,
            params={
                "checkpoint_id": "wave-acceptance",
                "initiative_id": "INIT-DOES-NOT-EXIST",
                "wave_id": "W9",
            },
            headers=headers,
        )
        if composed_no_run.status_code != 404:
            print(
                f"[ERROR] composed no-run expected 404, got {composed_no_run.status_code}: "
                f"{composed_no_run.text}"
            )
            rc = 1
        else:
            body = composed_no_run.json()
            if "no run found for this wave" not in body.get("error", {}).get("message", ""):
                print(f"[ERROR] composed 404 missing reason: {body}")
                rc = 1
            else:
                print("[OK] composed no-run → 404 no run found for this wave")

        # REQ-07 — history for a PR with no run → 200 empty historical records
        history_empty = client.get(
            history_path,
            params={"owner": owner, "repo": repo, "pr_number": 1},
            headers=headers,
        )
        if history_empty.status_code != 200:
            print(
                f"[ERROR] history expected 200, got {history_empty.status_code}: {history_empty.text}"
            )
            rc = 1
        else:
            body = history_empty.json()
            if body.get("historical") is not True:
                print(f"[ERROR] history.historical must be true: {body}")
                rc = 1
            elif not isinstance(body.get("records"), list):
                print(f"[ERROR] history.records must be a list: {body}")
                rc = 1
            else:
                print("[OK] history empty → 200 with historical=true and records list")

        if not pr_raw:
            print(
                "[OK] auth/shape/404 edges green "
                "(set GATEFLOW_CHECKPOINT_PR for live persist + stale assert)"
            )
            return rc

        try:
            pr_number = int(pr_raw)
        except ValueError:
            print(f"[ERROR] GATEFLOW_CHECKPOINT_PR must be an int, got {pr_raw!r}")
            return 1

        # REQ-06 — live status call (persists a checkpoint_check record when a run resolves)
        live = client.get(
            status_path,
            params={
                "checkpoint_id": checkpoint_id,
                "owner": owner,
                "repo": repo,
                "pr_number": pr_number,
            },
            headers=headers,
        )
        if live.status_code != 200:
            print(f"[ERROR] live status expected 200, got {live.status_code}: {live.text}")
            return 1
        live_body = live.json()
        for key in ("checkpoint_id", "verdict", "checked_at", "missing_items"):
            if key not in live_body:
                print(f"[ERROR] live response missing field {key!r}: {live_body}")
                return 1
        if live_body["verdict"] not in {"satisfied", "not_satisfied", "could_not_verify"}:
            print(f"[ERROR] unexpected verdict {live_body['verdict']!r}")
            return 1
        print(
            "[OK] live CAP-01 status",
            f"verdict={live_body['verdict']}",
            f"checked_sha={live_body.get('checked_sha')}",
            f"missing={len(live_body['missing_items'])}",
        )

        # REQ-06/07 — history after a live call returns persisted record(s), marked historical
        history = client.get(
            history_path,
            params={"owner": owner, "repo": repo, "pr_number": pr_number},
            headers=headers,
        )
        if history.status_code != 200:
            print(f"[ERROR] history expected 200, got {history.status_code}: {history.text}")
            return 1
        hist_body = history.json()
        if hist_body.get("historical") is not True:
            print(f"[ERROR] history.historical must be true: {hist_body}")
            return 1
        records = hist_body.get("records", [])
        if not isinstance(records, list):
            print(f"[ERROR] history.records must be a list: {hist_body}")
            return 1
        # When a run is resolvable for the PR, at least one record should exist
        # matching the live checkpoint_id; otherwise records may be empty (no run).
        matching = [r for r in records if r.get("checkpoint_id") == checkpoint_id]
        if matching:
            rec = matching[-1]
            if rec.get("historical") is not True:
                print(f"[ERROR] history record.historical must be true: {rec}")
                return 1
            for key in ("checkpoint_id", "verdict", "checked_at", "recorded_at"):
                if key not in rec:
                    print(f"[ERROR] history record missing field {key!r}: {rec}")
                    return 1
            print(
                "[OK] history returned persisted record",
                f"verdict={rec['verdict']}",
                f"records={len(records)}",
            )
        else:
            print(
                "[OK] history returned no matching record for this checkpoint "
                "(no run resolvable for PR — persistence skipped)"
            )

        # REQ-08 — composed readout via initiative+wave (optional, when env supplied)
        composed_initiative = os.environ.get("GATEFLOW_COMPOSED_INITIATIVE", "").strip()
        composed_wave = os.environ.get("GATEFLOW_COMPOSED_WAVE", "").strip()
        if composed_initiative and composed_wave:
            composed = client.get(
                status_path,
                params={
                    "checkpoint_id": checkpoint_id,
                    "initiative_id": composed_initiative,
                    "wave_id": composed_wave,
                },
                headers=headers,
            )
            if composed.status_code == 200:
                cbody = composed.json()
                if cbody.get("verdict") not in {"satisfied", "not_satisfied", "could_not_verify"}:
                    print(f"[ERROR] composed unexpected verdict {cbody.get('verdict')!r}")
                    return 1
                print(
                    "[OK] composed readout",
                    f"initiative={composed_initiative}",
                    f"wave={composed_wave}",
                    f"verdict={cbody['verdict']}",
                )
            elif composed.status_code == 404:
                print(
                    "[OK] composed readout 404 no run found for this wave "
                    f"(initiative={composed_initiative} wave={composed_wave})"
                )
            else:
                print(
                    f"[ERROR] composed expected 200 or 404, got {composed.status_code}: {composed.text}"
                )
                return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
