# Wave execution — INIT-GATEFLOW-011 W1

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-011 |
| Wave | W1 — Check persistence + composed readout |
| Wave board issue | [#162](https://github.com/drivestream-lab/gateflow/issues/162) |
| Wave head context | Bound by Forge/human: `develop` (planned coding branch: `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence`) |
| WorkManifest source | plan §9 (immutable intent — not mutated) |
| Pre-implement | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W1.md` (PASS) |
| Outcome | **pass** |

## Completed TASKS

| TASK | Implements | Declared files | Proof expected (manifest) | Observed (command / evidence) | Status |
|------|------------|----------------|---------------------------|-------------------------------|--------|
| TASK-W1-01 | REQ-06 | `policy_types.py`, `run_store_models.py`, `run_store_repository.py`, `checkpoint_evidence_service.py`, `test_checkpoint_persistence.py` (create) | Every evaluate attempt appends `checkpoint_check` run_event with required payload fields | `make check && make test` exit 0; `test_checkpoint_persistence` (4 tests) — appends event with payload (checkpoint_id/owner/repo/pr_number/verdict/checked_sha/checked_at/missing_count/missing_items/stale_reason/initiative_id/wave_id); skips when no run resolvable; persists `could_not_verify` with null checked_sha | green |
| TASK-W1-02 | REQ-03 | `checkpoint_evidence_service.py`, `test_checkpoint_evidence.py` | Stale evidence → not_satisfied with stale reason; checked_sha/checked_at always present | `make check && make test` exit 0; `test_checkpoint_evidence` stale cases — stale approval (commit_id != head) → not_satisfied + `stale — new commits since approval`; fresh approval → satisfied + stale_reason None; no approval → not_satisfied + stale_reason None; checked_sha/checked_at always present on live verdicts | green |
| TASK-W1-03 | REQ-07, REQ-28 | `checkpoints_routes.py`, `test_checkpoints_api.py` | GET /checkpoints/history marks records historical; never claims live verdict | `make check && make test` exit 0; `test_checkpoints_api` — `/history` 200 with `historical=true` + records list; 401 without token; 405 on POST | green |
| TASK-W1-04 | REQ-08, REQ-28 | `checkpoint_evidence_service.py`, `checkpoints_routes.py`, `test_checkpoints_api.py` | Composed readout via initiative+wave; 404 no run found for this wave when unresolved | `make check && make test` exit 0; `test_checkpoints_api` + `test_checkpoint_persistence` — composed 200 via initiative+wave; 400 when neither raw nor composed supplied; 404 `no run found for this wave` (distinct from malformed id); service `evaluate_composed` resolves run → PR → evaluate (persists correlated record) | green |
| TASK-W1-05 | REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 | `verify_checkpoint_history.py` (create), `tests/README.md`, `implementation-status.md` | Live verify exit 0 covering persist/stale/404; as-built W1 row | script created (`tests/verify/verify_checkpoint_history.py`); feature-map + as-built W1 matrix present; `make check && make test` exit 0 (**did not** run live smoke as success) | green |

## Local proof (suite)

- `{check_command}`: `make check` — exit 0 (black, ruff, pyright, import-linter)
- `{test_command}`: `make test` — **302 passed** (was 283 in W0; +19 W1 tests across `test_checkpoint_persistence`, `test_checkpoint_evidence` stale cases, `test_checkpoints_api` history/composed)

## Live verify (human — not claimed here)

- Planned script: `.venv/bin/python -m tests.verify.verify_checkpoint_history`
- Agent created planned FILE: **yes** — **did not** run smoke/sandbox as success
- Covers (when run with `PROGRAMME_SERVICE_TOKEN` + optional `GATEFLOW_CHECKPOINT_PR` / `GATEFLOW_COMPOSED_INITIATIVE`+`GATEFLOW_COMPOSED_WAVE`): 401/405/400/404-no-run-for-wave + history empty 200 (smoke always); live persist + history record + composed readout (with fixture PR / composed env)

## Forge readiness

- After this hop: `commit_workspace` (code + Wave-Execution + PR body on bound `head_ref`)
- Next external-action: `open_draft_pr` / `wave-pr-action`
  - **title:** `[INIT-GATEFLOW-011 W1] Check persistence + composed readout`
  - **body_path:** `docs/specification/reports/PR-body-INIT-GATEFLOW-011-W1.md`
  - **head_ref:** `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence`
  - **base_ref:** `develop`

## Notes (not claimed complete)

- This skill did **not** commit, push, or open a branch.
- Check persistence reuses the existing `run_events` timeline (no new ORM table / no Alembic revision) — `RunEventNameType.CHECKPOINT_CHECK` added to the enum; payload via `CheckpointCheckPayloadDocument` (JSONB).
- Stale detection compares the approval review `commit_id` vs the PR head SHA (A-2); never silently reports stale as pass.
- History records are marked `historical=true` at both the wrapper and per-record level (REQ-07); never substituted for a live verdict.
- Composed readout resolves the run from initiative+wave via `RunRepository.list_runs` (no new repo method required); 404 `no run found for this wave` is distinct from malformed-id 404.
- No Forge write APIs added on any CAP-01/02 path (REQ-05/28); persistence is DB-only.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: loop-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W1.md
    digest: sha256:9b1bf6c7063256da501dd07407c2f2153fc8cf87d5067f6b6782a75ea7ba0c48
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W1
    wave_issue: https://github.com/drivestream-lab/gateflow/issues/162
    ticket_id: 162
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/162
    epic_ticket_id: 160
    wave_head: develop
    wave_branch_planned: feature/INIT-GATEFLOW-011-w1-checkpoint-persistence
    completed_tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    implements_reqs:
      - REQ-03
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_checkpoint_history
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: Todo
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/159
    workmanifest_contract: pass
    p15_applicable: true
    unit_passed: 302
  next_candidates:
    - wave-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels: []
    remove_labels: []
    title: "[INIT-GATEFLOW-011 W1] Check persistence + composed readout"
    body_path: docs/specification/reports/PR-body-INIT-GATEFLOW-011-W1.md
    head_ref: feature/INIT-GATEFLOW-011-w1-checkpoint-persistence
    base_ref: develop
    commit_workspace: required
```
