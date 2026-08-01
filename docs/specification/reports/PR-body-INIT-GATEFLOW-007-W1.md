## Summary

- Persist Learning-Extract YAML into Postgres (`learning_extracts` / `learning_items`) after the `learning-extract` hop.
- `LearningIngestService` + repository + DI; orchestrator order: publish → handoff → ingest → policy.
- Human Alembic `cc5feda8fe3d`; unit coverage in `test_learning_ingest` (live ingest dogfood in W2).

## Initiative / board

- **Initiative:** INIT-GATEFLOW-007
- **Wave:** W1 — board [#86](https://github.com/drivestream-lab/gateflow/issues/86)
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- **Verify command:** N/A (P15 — no new HTTP surface); `make check && make test`

## Test plan

- [x] `make check`
- [x] `make test` (214 unit, including `test_learning_ingest`)
- [x] Human Alembic applied locally (`cc5feda8fe3d`)
- [ ] Live learning rows — deferred to W2 dogfood (`verify_wave_closeout`)

## Checklist

- [x] **App / service** (feature branch → `develop`)
- [x] Board fields: Initiative, Spec path, Verify command
- [x] As-built / feature map updated
