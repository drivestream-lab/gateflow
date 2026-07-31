## Summary

- Add programme-token `POST /api/v1/waves/closeout/start` (fixed Enter-at `learning-extract`, required PR + workspace + branch targeting).
- Unit coverage (`test_wave_closeout`) + Pass-2 pin walker assertions; mock hygiene off `wave-human-decision`.
- Co-ship smoke `tests/verify/verify_wave_closeout.py` + feature map / as-built / product+TDD contract updates.

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative INIT-GATEFLOW-007, Spec path, Verify command
- [x] As-built / feature map updated

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-007 |
| Issue | #85 |
| Spec path | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` |
| Verify command | `.venv/bin/python -m tests.verify.verify_wave_closeout` |

## Test plan

- [x] `make check`
- [x] `make test` (204 passed)
- [ ] Live smoke with API up + `features.wave_closeout.enabled: true` + existing `pr_number`
