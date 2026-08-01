## Summary

- Deepen `verify_wave_closeout` for Pass-2 dogfood (`dogfood: true` → poll to `wave-signoff`, Learning-Extract artifact assert).
- Config example + feature map: smoke vs dogfood knobs; as-built W2 row + REQ-15 PE-waived deferral for spec-lane closeout live.
- REQ-16 unit guard: `src/` has no retired `gate-1` / `gate-2` / `wave-human-decision` transition ids.

## Test plan

- [x] `make check && make test`
- [ ] Human: `.venv/bin/python -m tests.verify.verify_wave_closeout` with `dogfood: true` + worker + tip PR
- [ ] Capture `Live-Verify-INIT-GATEFLOW-007-W2.md` (run id, tip, learning rows SQL)

## Initiative / Spec

- Initiative: INIT-GATEFLOW-007
- Issue: [#87](https://github.com/drivestream-lab/gateflow/issues/87)
- Spec: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- Verify: `.venv/bin/python -m tests.verify.verify_wave_closeout`
