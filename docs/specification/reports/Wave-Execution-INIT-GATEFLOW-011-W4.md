# Wave execution — INIT-GATEFLOW-011 W4

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-011 |
| Wave | W4 — Wave map readout |
| Wave head context | Bound by Forge/human: `develop` @ `cdfbbc8` (planned coding branch `feature/INIT-GATEFLOW-011-w4-wave-map`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Date | 2026-08-07 |
| Outcome | pass |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W4-01 | REQ-14, REQ-15 | `src/business_services/wave_map_service.py` (create); `src/models/wave_map_models.py` (create); `tests/unit/test_wave_map_service.py` (create) | `make test` exit 0; Per-wave status + block reason; no new wave-state store | `make check` exit 0; `make test` → 335 passed. `WaveMapService` composes Feature tickets + runs; status priority done > active > blocked (predecessor) > ready-to-start; DI glue `binder.bind(WaveMapService)` in `business_services_module.py` (manifest omission noted in Pre-Implement) | green |
| TASK-W4-02 | REQ-14, REQ-15, REQ-28 | `src/api/v1/initiatives_routes.py` (modify); `tests/unit/test_initiatives_read_api.py` (modify) | `make test` exit 0; GET .../waves route wired GET-only | Same check/test green (335). `GET /initiatives/{initiative_id}/waves` + programme token; API tests cover 200 shape, 401, 404, 405 | green |
| TASK-W4-03 | REQ-14, REQ-28 | `tests/verify/verify_wave_map.py` (create); `tests/README.md` (modify); `docs/specification/as-built/implementation-status.md` (modify) | `make check && make test` exit 0; Live wave-map smoke; as-built W4 row | `make check` exit 0; `make test` → 335 passed; co-shipped `verify_wave_map.py` (import OK; **not** run as success here); `tests/README.md` W4 feature-map; as-built W4 capability matrix + gap (`code complete (unit)`) | green |

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_wave_map` under `live_verify_dir`
- Agent created planned FILE: **yes** — `tests/verify/verify_wave_map.py` (import verified; **did not** run smoke/sandbox as success)
- Human runs at `wave-acceptance` with API+worker up, `PROGRAMME_SERVICE_TOKEN`, `tests/config.yaml`; optional `GATEFLOW_INITIATIVE_ID` for live shape assert

## Forge readiness

- After this hop: `commit_workspace` (code on bound `head_ref` — `develop` or `feature/INIT-GATEFLOW-011-w4-wave-map` once cut)
- Next external-action: `open_draft_pr` / `wave-pr-action` (`authorization: automated` — no interactive STOP when requires complete)
  - title: `[INIT-GATEFLOW-011 W4] Wave map readout`
  - body_path: `docs/specification/reports/PR-body-INIT-GATEFLOW-011-W4.md`
  - head_ref: `feature/INIT-GATEFLOW-011-w4-wave-map`
  - base_ref: `develop`

## Files touched (observed)

- `src/models/wave_map_models.py` (create) — `WaveMapStatusType`, `WaveMapItem`, `WaveMapResult`
- `src/business_services/wave_map_service.py` (create) — CAP-05 composition
- `src/di/modules/business_services_module.py` (modify) — `WaveMapService` singleton bind (glue; not in WorkManifest `files[]`)
- `tests/unit/test_wave_map_service.py` (create) — status / 404 / epic-only / skip-title unit coverage
- `src/api/v1/initiatives_routes.py` (modify) — `GET /initiatives/{initiative_id}/waves`
- `tests/unit/test_initiatives_read_api.py` (modify) — waves 401/200/404/405
- `tests/verify/verify_wave_map.py` (create) — live smoke script
- `tests/README.md` (modify) — W4 feature-map + run knobs
- `docs/specification/as-built/implementation-status.md` (modify) — W4 capability matrix + gap row; Source line notes W4 code complete
- `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W4.md` (from prior hop — publish with checklist)
- `docs/specification/reports/PR-body-INIT-GATEFLOW-011-W4.md` (create) — Draft PR body
- `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W4.md` (this file)

## REQ coverage (observed)

| REQ | How verified |
|-----|--------------|
| REQ-14 | Status ∈ {done, ready-to-start, blocked, active}; blocked includes `block_reason` — `test_wave_map_service`, `test_initiatives_read_api` |
| REQ-15 | Composition from Feature tickets + runs only; no new store — service design + unit (no parallel persistence) |
| REQ-28 | GET-only waves route; 401 without token; 404 unknown; no Forge writes — `test_initiatives_read_api` + service read-only |

## Boundaries respected

- `api` → `business_services` → `database.repository` (import-linter KEPT, 1 contract kept)
- No ORM in `WaveMapService`; runs via `RunRepository`; board via `BoardService`
- Models in `src/models/wave_map_models.py` only; none defined in `src/api/`
- Programme-token on GET waves; no new mutate surface
- No new ORM table / no Alembic revision
- No Forge write APIs called from CAP-05 path (read-only)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W4.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W4
    ticket_id: "165"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/165
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: cdfbbc8f72e36cfaf1a2d2c2c47bac327be39498
    wave_branch_planned: feature/INIT-GATEFLOW-011-w4-wave-map
    current_task: none
    implements:
      - REQ-14
      - REQ-15
      - REQ-28
    completed_tasks:
      - TASK-W4-01
      - TASK-W4-02
      - TASK-W4-03
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_map
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    unit_passed: 335
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
    head_ref: feature/INIT-GATEFLOW-011-w4-wave-map
    base_ref: develop
    next_action: open_draft_pr
    title: "[INIT-GATEFLOW-011 W4] Wave map readout"
    body_path: docs/specification/reports/PR-body-INIT-GATEFLOW-011-W4.md
    commit_workspace: required
    paths:
      - src/models/wave_map_models.py
      - src/business_services/wave_map_service.py
      - src/di/modules/business_services_module.py
      - tests/unit/test_wave_map_service.py
      - src/api/v1/initiatives_routes.py
      - tests/unit/test_initiatives_read_api.py
      - tests/verify/verify_wave_map.py
      - tests/README.md
      - docs/specification/as-built/implementation-status.md
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W4.md
      - docs/specification/reports/PR-body-INIT-GATEFLOW-011-W4.md
      - docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W4.md
```
