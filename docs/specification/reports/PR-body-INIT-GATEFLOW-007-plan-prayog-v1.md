## Summary

- Backfill INIT-GATEFLOW-007 Implementation Plan §9 to pin **`prayog/v1`** WorkManifest (`files` / `exit` / wave `verification`; drop mutable `status`).
- Align P14/P16, PR instructions, product A-9, feasibility next-steps, TDD delivery note, and as-built gap with INIT-008 W2 contract (no board re-seed — keep #84–#87).

## Why

Pre-implement on W0 blocked: plan still had `apiVersion: launchpad/v1` (40 contract errors). Pin validator after INIT-008 W2 is fail-closed.

## Test plan

- [x] `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` → pass
- [ ] PE `spec-lgtm` + Approve on exact head
- [ ] After merge: re-run implement W0 `/pre-implement` (expect pass → loop-spec); do **not** `/create-board-tickets`
