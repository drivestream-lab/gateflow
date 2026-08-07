## Summary

- **Initiative / wave:** INIT-GATEFLOW-011 **W8** — CAP-08 merge confirm + CAP-09 completion eligibility
- **Board:** [#169](https://github.com/drivestream-lab/gateflow/issues/169) (EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160))
- **Spec:** `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-21, REQ-22, REQ-23, REQ-24, REQ-28
- **Surfaces:** `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/merge` and `GET /api/v1/initiatives/{initiative_id}/completion`
- **Compose:** `MergeReadoutService` reuses CAP-01 `wave-signoff` + Forge merge fields + CAP-05 nudge; `CompletionReadoutService` pure CAP-05 rollup (ready / waiting / no waves found)
- **Proof:** `make check` 0; `make test` **383 passed**; live FILE `tests/verify/verify_merge_and_completion.py` co-shipped (human at wave-acceptance)

## Test plan

- [ ] `make check` / `make test` green on tip
- [ ] Human: `.venv/bin/python -m tests.verify.verify_merge_and_completion` (API up; `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_INITIATIVE_ID` + `GATEFLOW_WAVE_ID`)
- [ ] Confirm GET-only (405 on POST) for merge + completion; 401 without token; 404 unknown initiative
- [ ] Signal accept with label `wave-accepted` on tip

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Smoke command

```bash
.venv/bin/python -m tests.verify.verify_merge_and_completion
```
