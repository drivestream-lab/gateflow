# Wave execution — INIT-GATEFLOW-011 W2

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-011 |
| Wave | W2 — Initiative list/detail (Gateflow-owned) |
| Wave head context | Bound by Forge/human: `develop` @ `7e5ad7e` (planned coding branch `feature/INIT-GATEFLOW-011-w2-initiatives-owned`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Date | 2026-08-07 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W2-01 | REQ-09, REQ-10 | `src/business_services/initiative_readout_service.py` (create); `src/models/initiative_readout_models.py` (create); `tests/unit/test_initiative_readout.py` (create); `src/di/modules/business_services_module.py` (modify) | `make test` exit 0; List/detail returns Gateflow-owned fields; prd_approval=unavailable | `make test` → 319 passed (W2 subset 9: `test_initiative_readout`); `make check` exit 0 (black, ruff, pyright, import-linter KEPT). Service composes from runs (`RunRepository.list_runs`) + board EPIC tickets (`BoardService.list_tickets`); `PrdApprovalStateType.UNAVAILABLE` with reason "meta bridge not yet wired (W3)"; affected_repos deduped; current_stage from active run / EPIC column / latest run; 404 when no run and no EPIC | green |
| TASK-W2-02 | REQ-09, REQ-10, REQ-28 | `src/api/v1/initiatives_routes.py` (modify); `tests/unit/test_initiatives_read_api.py` (create) | `make test` exit 0; GET list/detail routes programme-token; GET-only guard | `make test` → 319 passed (W2 subset 8: `test_initiatives_read_api`); `make check` exit 0. Added `GET /initiatives` + `GET /initiatives/{initiative_id}` (programme-token via `verify_programme_service_token`; `/api/v1/initiatives` already on `public_paths`); non-GET 405; 401 without token; 404 unknown initiative; existing `POST /initiatives/closure/start` (INIT-010 W4) unchanged | green |
| TASK-W2-03 | REQ-09, REQ-10, REQ-28 | `tests/verify/verify_initiatives_readout.py` (create); `tests/README.md` (modify); `docs/specification/as-built/implementation-status.md` (modify) | `make check && make test` exit 0; Live smoke exit 0; as-built W2 row | `make check` exit 0; `make test` → 319 passed; co-shipped `verify_initiatives_readout.py` (syntax + import OK; **not** run as success here); `tests/README.md` W2 feature-map row added; as-built W2 capability matrix + gap row added (status: code complete (unit), human wave-acceptance pending) | green |

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_initiatives_readout` under `live_verify_dir`
- Agent created planned FILE: **yes** — `tests/verify/verify_initiatives_readout.py` (syntax + import verified; **did not** run smoke/sandbox as success)
- Human runs at `wave-acceptance` with API+worker up, `PROGRAMME_SERVICE_TOKEN`, `tests/config.yaml`; optional `GATEFLOW_INITIATIVE_ID` for a live detail assert.

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref` — `develop` or `feature/INIT-GATEFLOW-011-w2-initiatives-owned` once cut)
- Next external-action: `open_draft_pr` / `wave-pr-action` (`authorization: automated` — no interactive STOP when requires complete)
  - title: `[INIT-GATEFLOW-011 W2] Initiative list/detail (Gateflow-owned)`
  - body_path: `docs/specification/reports/PR-body-INIT-GATEFLOW-011-W2.md`
  - head_ref: `feature/INIT-GATEFLOW-011-w2-initiatives-owned`
  - base_ref: `develop`

## Files touched (observed)

- `src/models/initiative_readout_models.py` (create) — `InitiativeStageType`, `PrdApprovalStateType`, `InitiativeRunLink`, `InitiativeListItem`, `InitiativeReadout`, `InitiativeListResult`
- `src/business_services/initiative_readout_service.py` (create) — `InitiativeReadoutService` + `get_initiative_readout_service`
- `src/di/modules/business_services_module.py` (modify) — bind `InitiativeReadoutService` singleton
- `src/api/v1/initiatives_routes.py` (modify) — add `GET /initiatives` + `GET /initiatives/{initiative_id}` (POST closure/start unchanged)
- `tests/unit/test_initiative_readout.py` (create) — 9 service tests
- `tests/unit/test_initiatives_read_api.py` (create) — 8 API tests
- `tests/verify/verify_initiatives_readout.py` (create) — live smoke script
- `tests/README.md` (modify) — W2 feature-map row + run instructions
- `docs/specification/as-built/implementation-status.md` (modify) — W2 capability matrix + gap row; updated date

## REQ coverage (observed)

| REQ | How verified |
|-----|--------------|
| REQ-09 | List/detail return id, name, affected_repos, current_stage, in_flight_run, epic link; fields present or `unavailable`; 404 unknown initiative — `test_initiative_readout`, `test_initiatives_read_api` |
| REQ-10 | Composed only from runs (`RunRepository.list_runs`) + board EPIC tickets (`BoardService.list_tickets`); no meta read in W2; `prd_approval=unavailable` — `test_initiative_readout` |
| REQ-28 | GET-only on `/initiatives` + `/initiatives/{id}` (non-GET 405); 401 without programme token; no `apply_labels`/review/merge/`update_board_status` from path — `test_initiatives_read_api` |

## Boundaries respected

- `api` → `business_services` → `database.repository` (import-linter KEPT, 1 contract kept)
- No ORM in `InitiativeReadoutService` or routes; `RunRepository` returns Pydantic `RunModel`
- Models in `src/models/initiative_readout_models.py` only; none defined in `src/api/`
- Programme-token on new GET routes; `/api/v1/initiatives` already on `public_paths`
- No new ORM table / no Alembic revision (reads existing `runs` + board via ForgeClient)
- No Forge write APIs called from CAP-03 path (read-only)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W2
    ticket_id: "163"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/163
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 7e5ad7e
    wave_branch_planned: feature/INIT-GATEFLOW-011-w2-initiatives-owned
    current_task: none
    implements:
      - REQ-09
      - REQ-10
      - REQ-28
    completed_tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_initiatives_readout
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    unit_passed: 319
    check_passed: true
    p15_applicable: true
    live_script_created: true
    live_smoke_claimed: false
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: commit_workspace
    head_ref: feature/INIT-GATEFLOW-011-w2-initiatives-owned
    base_ref: develop
    next_action: open_draft_pr
    title: "[INIT-GATEFLOW-011 W2] Initiative list/detail (Gateflow-owned)"
    body_path: docs/specification/reports/PR-body-INIT-GATEFLOW-011-W2.md
```

