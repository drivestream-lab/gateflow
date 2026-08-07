## Summary

- **Initiative / wave:** INIT-GATEFLOW-011 **W6** — CAP-06 wave implementation progress readout
- **Board:** [#167](https://github.com/drivestream-lab/gateflow/issues/167) (EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160))
- **Spec:** `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-16, REQ-17, REQ-28
- **Surface:** `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/implementation`
- **Compose:** `ImplementationReadoutService` — implement-lane run (`wave_id`, prefer no `meta_pr_url`); task timeline from stages; Draft PR when `pr_number` or `forge_executed@wave-pr-action`; named failure from stage/handoff/stop (REQ-17)
- **Proof:** `make check` 0; `make test` **356 passed**; live FILE `tests/verify/verify_wave_implementation.py` co-shipped (human at wave-acceptance)

## Test plan

- [ ] `make check` / `make test` green on tip
- [ ] Human: `.venv/bin/python -m tests.verify.verify_wave_implementation` (API up; `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_INITIATIVE_ID` + `GATEFLOW_WAVE_ID`)
- [ ] Confirm GET-only (405 on POST); 401 without token; 404 unknown initiative
- [ ] Signal accept with label `wave-accepted` on tip

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Smoke command

```bash
.venv/bin/python -m tests.verify.verify_wave_implementation
```
