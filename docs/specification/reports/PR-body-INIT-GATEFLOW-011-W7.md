## Summary

- **Initiative / wave:** INIT-GATEFLOW-011 **W7** — CAP-07 closeout readout + advisory drift
- **Board:** [#168](https://github.com/drivestream-lab/gateflow/issues/168) (EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160))
- **Spec:** `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-18, REQ-19, REQ-20, REQ-28
- **Surface:** `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/closeout`
- **Compose:** `CloseoutReadoutService` — implement-lane run; itemized learning/ground additions (REQ-18); drift vs historical `checkpoint_check` at `wave-acceptance` (REQ-19: unknown when missing); `advisory_only=True` never blocks mechanics (REQ-20)
- **Proof:** `make check` 0; `make test` **366 passed**; live FILE `tests/verify/verify_wave_closeout_readout.py` co-shipped (human at wave-acceptance)

## Test plan

- [ ] `make check` / `make test` green on tip
- [ ] Human: `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` (API up; `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_INITIATIVE_ID` + `GATEFLOW_WAVE_ID`)
- [ ] Confirm GET-only (405 on POST); 401 without token; 404 unknown initiative; `advisory_only` true
- [ ] Signal accept with label `wave-accepted` on tip

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Smoke command

```bash
.venv/bin/python -m tests.verify.verify_wave_closeout_readout
```
