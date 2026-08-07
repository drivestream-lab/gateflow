## Summary

- **Initiative / wave:** INIT-GATEFLOW-011 **W9** — CAP-10 closure preview + CAP-01 reuse for closure signoffs
- **Board:** [#170](https://github.com/drivestream-lab/gateflow/issues/170) (EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160))
- **Spec:** `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-25, REQ-26, REQ-27, REQ-28
- **Surface:** `GET /api/v1/initiatives/{initiative_id}/closure` (distinct from `POST .../closure/start`)
- **Compose:** `ClosurePreviewService` — purge allowlist plan (`not yet run` when purge-app not executed); post-purge lists from handoff signals; CAP-01 `evaluate` for `initiative-closure-signoff-app` / `initiative-closure-signoff-meta` when a closure PR exists
- **Proof:** `make check` 0; `make test` **394 passed**; live FILE `tests/verify/verify_closure_preview.py` co-shipped (human at wave-acceptance)

## Test plan

- [ ] `make check` / `make test` green on tip
- [ ] Human: `.venv/bin/python -m tests.verify.verify_closure_preview` (API up; `PROGRAMME_SERVICE_TOKEN`; optional `GATEFLOW_INITIATIVE_ID`)
- [ ] Confirm GET-only (405 on POST to `.../{id}/closure`); 401 without token; 404 unknown initiative
- [ ] Confirm plan cites artifact-write-contract; `not yet run` when purge not executed
- [ ] Signal accept with label `wave-accepted` on tip

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Smoke command

```bash
.venv/bin/python -m tests.verify.verify_closure_preview
```
