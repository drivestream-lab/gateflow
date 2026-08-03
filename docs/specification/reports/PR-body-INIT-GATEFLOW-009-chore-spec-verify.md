## Summary

- Fix stale `test_spec_rejects_manual_start_node` — `spec-draft` is now orchestrated on pin v0.5.0-rc.2; use `spec-implementation-plan` (`dispatch: manual`) to exercise the reject path.
- Deepen `verify_spec_lane.py` with hop polling to the manual stop at `spec-implementation-plan` (reuses `evaluate_lane_poll` like `verify_implement_lane`); asserts `spec-draft` + `initiative-feasibility` Cursor success, `pr_number` after automated `spec-pr-action`, and terminal `stopped` at the manual gate.
- Update docstring — "REQ-21 hop prove-it deferred" is stale; the pin orchestrates spec-draft.

## Why a chore (before spec-lane dogfood)

Spec-lane dogfood (INIT-GATEFLOW-009 W1) needs `make test` green and a verify script that proves the walk, not just start-accept.

## Test plan

- [x] `make check && make test` → 216 passed
- [ ] Human: `.venv/bin/python -m tests.verify.verify_spec_lane` with dogfood knobs after merge

## Initiative / Spec

- Initiative: INIT-GATEFLOW-009 (H1.5 closeout — draft PRD on prayog-meta#23)
- Spec: TBD (PRD in flight)
- Verify: `.venv/bin/python -m tests.verify.verify_spec_lane`
