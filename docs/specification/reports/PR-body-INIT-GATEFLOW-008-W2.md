## Summary

- Pin `workmanifest_contract.py` subprocess before `create_board_tickets`; accept only `apiVersion: prayog/v1`.
- Reject `launchpad/v1` fail closed (no BoardService mutate).
- `board-tickets-action` remains `authorization: explicit` (STOP + authorize).
- `verify_board` asserts launchpad reject; feature map + as-built + REQ-17 (007 dogfood next).

## Initiative / board

- **Initiative:** INIT-GATEFLOW-008 (006A)
- **Wave:** W2 — board [#95](https://github.com/drivestream-lab/gateflow/issues/95)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- **Wave execution:** `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-008-W2.md`

## Test plan

- [x] `make check`
- [x] `make test` (194 unit)
- [ ] Live: `.venv/bin/python -m tests.verify.verify_board` (human at live-verify)

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] As-built / feature map updated for W2 WorkManifest + Pass-1 edges
