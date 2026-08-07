# Ground report — INIT-GATEFLOW-011 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Check persistence + composed readout (CAP-02) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` @ `3074e82b7b54bbbd6d015f0420d255fd81a30ea1` — reviewed head for sign-off |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/172 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `3074e82` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W2+ |
| Assigned REQs | REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 — from WorkManifest TASK-W1-01…05 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W1 | Pass-1 **302 passed**; ground re-proof 2026-08-07 **302 passed**; W1 subset **46 passed** (`test_checkpoint_persistence`, `test_checkpoint_evidence`, `test_checkpoints_api`, `test_checkpoint_vocab`, `test_forge_client`) |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; persistence/stale/history/composed inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `3074e82`; human attested live verify (smoke path exit 0) |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `3074e82b7b54bbbd6d015f0420d255fd81a30ea1` on `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence`
- Product content SHA `7c11494` (CAP-02); `8f02e36`/`3074e82` are forge publish-SHA chores only
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **302 passed**
- W1 subset: 46 passed (persistence + evidence + api + vocab + forge_client)
- WorkManifest contract: "WorkManifest contract passed."
- PR [#172](https://github.com/drivestream-lab/gateflow/pull/172) labels: **`wave-accepted`**
- Learning-Extract W1 present with `items: []` (no human-fix signal; W0 L-01 did not recur)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-03 | `checked_sha`/`checked_at` always present; stale evidence → `not_satisfied` with reason `stale — new commits since approval` (never silent pass) | `CheckpointEvidenceService._detect_stale_reason` (approval `commit_id` vs head SHA); `test_checkpoint_evidence` stale/fresh/no-approval cases; `CheckpointStatusResult.checked_sha`/`checked_at`/`stale_reason` | **pass** |
| REQ-06 | Every CAP-01 call persists a `checkpoint_check` run_event (checkpoint id, PR ref, `checked_sha`, `checked_at`, verdict, missing items) into existing run/timeline store, correlated to initiative/wave when resolvable | `CheckpointEvidenceService._persist_check` + `_append_checkpoint_event`; `RunEventNameType.CHECKPOINT_CHECK`; `CheckpointCheckPayloadDocument`; `RunRepository.find_run_by_pr`; `test_checkpoint_persistence` (4 tests) | **pass** |
| REQ-07 | History returns prior persisted records explicitly labeled **historical**; never substituted for a live verdict | `CheckpointEvidenceService.list_history` + `GET /api/v1/checkpoints/history`; `CheckpointHistoryResult.historical=true` + `CheckpointHistoryRecord.historical=true`; `test_checkpoints_api` + `test_checkpoint_persistence` | **pass** |
| REQ-08 | Composed readout via initiative+wave; unresolved pairing → 404 `no run found for this wave` (distinct from malformed id) | `CheckpointEvidenceService.evaluate_composed` (resolves run via `RunRepository.list_runs` → PR → `evaluate`); `/status` composed query params; `test_checkpoints_api` + `test_checkpoint_persistence` | **pass** |
| REQ-28 | GET-only; no `apply_labels`/review/merge/`update_board_status` from any CAP-01/02 path | `/status` + `/history` GET-only (405 on POST); CAP-02 uses only ForgeClient read methods + DB append; no Forge write APIs added; `test_checkpoints_api` (non-GET 405) | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — `CheckpointEvidenceService` uses `RunRepository`/`RunEventRepository` (Pydantic in/out); ORM confined to repos |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — history DTOs in `checkpoint_models.py`; payload doc in `run_store_models.py`; routes import models |
| Programme-token on control-plane reads | ADR-005 | **pass** — `verify_programme_service_token` on `/status` + `/history`; `/api/v1/checkpoints` on `public_paths` |
| Pin forge mutate authority; CAP-02 read-only + DB persist | ADR-009, REQ-05/28 | **pass** — CAP-02 path has no Forge write actions; persistence is DB-only |
| Fail closed on GitHub down / stale / no-run | `fail-fast.mdc`, REQ-01/03/08 error table | **pass** — `could_not_verify`; stale → `not_satisfied` + reason; 404 `no run found for this wave` distinct from malformed id |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns logic; live `verify_checkpoint_history` co-shipped (smoke only) |
| No new ORM table / no Alembic revision | `database-migrations.mdc` | **pass** — reuses `run_events` JSONB; enum extended; no `versions/` touched |
| Import layers | `python-tooling.mdc` (.importlinter) | **pass** — layers KEPT, 1 contract kept |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Live CAP-01 evaluate (W1 wraps with persist + stale) | Ground-Report-W0 | **yes** — `evaluate` extended; signature unchanged |
| Pin checkpoint vocabulary (W1 reuses; stale uses head SHA vs evidence timing) | Ground-Report-W0 | **yes** — `get_github_checkpoint_vocab` unchanged |
| ForgeClient evidence reads (W1 unchanged read surface) | Ground-Report-W0 | **yes** — read methods unchanged; no write APIs added |
| HTTP status surface (W1 adds `/history` + composed under same prefix) | Ground-Report-W0 | **yes** — `/status` present; `/history` + composed added under `/api/v1/checkpoints` on `public_paths` |
| Live verify CAP-01 (W1 adds `verify_checkpoint_history`) | Ground-Report-W0 | **yes** — `verify_checkpoint_status.py` present; `verify_checkpoint_history.py` co-shipped |
| Run-event persistence surface (W1 adds `checkpoint_check` event type) | as-built INIT-001/006 | **yes** — `append_event` + `RunEventCreate` + `RunEventNameType` extended; `find_run_by_pr` added |
| Programme-token auth (W1 reuses for new GET routes) | ADR-005 | **yes** — pattern live; `/api/v1/checkpoints` already on `public_paths` |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W1.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W1 Learning-Extract emitted `items: []` — no human-fix signal; W0 L-01 (acceptance-label vocabulary) did not recur (`wave-accepted` applied correctly on tip `3074e82`) |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W2 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Checkpoint persistence | `CheckpointEvidenceService` | `_persist_check` / `_append_checkpoint_event` (called by `evaluate`) | `CheckpointStatusResult` + PR ref | `checkpoint_check` `RunEventModel` appended to run timeline | Persisted on every evaluate when a run is resolvable via `RunRepository.find_run_by_pr`; payload (`CheckpointCheckPayloadDocument`) carries checkpoint_id/owner/repo/pr_number/verdict/checked_sha/checked_at/missing_count/missing_items/stale_reason/initiative_id/wave_id; skipped (logged) when no run; no Forge writes | W7 (drift safeguard baseline); W3/W8/W9 (composed readout persists correlated record) |
| Stale detection | `CheckpointEvidenceService` | `_detect_stale_reason` (called by `evaluate`) | `CheckpointVocabEntry` + PR head SHA + reviews | `Optional[str]` stale reason or None | Approval `commit_id` ≠ head SHA → `stale — new commits since approval`; never silent pass; `checked_sha`/`checked_at` always present on live verdicts | Any future CAP-01 consumer (W3/W8/W9 composed) |
| History read-out | `CheckpointEvidenceService` + `api/v1/checkpoints_routes` | `list_history(pr_ref, *, checkpoint_id, limit, skip)` / `GET /api/v1/checkpoints/history` | PR ref + optional checkpoint_id/limit/skip | `CheckpointHistoryResult` (`historical=true`, `records[]` of `CheckpointHistoryRecord`) | Records marked `historical=true` at wrapper + per-record; never claims live verdict; empty 200 when no run; filters by checkpoint_id | W7 (closeout drift baseline); future visibility waves |
| Composed readout | `CheckpointEvidenceService` + `api/v1/checkpoints_routes` | `evaluate_composed(initiative_id, wave_id, checkpoint_id)` / `GET /api/v1/checkpoints/status` with `initiative_id`+`wave_id` | initiative_id + wave_id + checkpoint_id | `CheckpointStatusResult` (live) or 404 `no run found for this wave` | 400 when neither raw nor composed supplied; 404 distinct from malformed id; resolves run via `RunRepository.list_runs` → PR → `evaluate` (persists correlated record) | W3 (initiative detail PRD approval), W8 (merge confirm), W9 (closure signoff) |
| Live verify CAP-02 | `tests/verify/verify_checkpoint_history.py` | module main | programme knobs; optional `GATEFLOW_CHECKPOINT_PR` / `GATEFLOW_COMPOSED_INITIATIVE`+`GATEFLOW_COMPOSED_WAVE` | exit 0 under prereqs | Smoke only; covers auth/shape/404 + live persist/stale/composed when env set; does not duplicate unit assertions | W2+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/172 @ `3074e82b7b54bbbd6d015f0420d255fd81a30ea1` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W1.md`
- Accept evidence: `wave-accepted` on tip `3074e82` (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W1.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W1.md`
- Optional/legacy Live-Verify path: n/a (not required)
- As-built: W1 `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `3074e82`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass
- [ ] Review §Contracts produced — accurate for W2+ `/pre-implement`
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#162](https://github.com/drivestream-lab/gateflow/issues/162) → Done; then human merges #172 @ `3074e82` only.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W1.md
    digest: sha256:49c62206d1d265dbcabf5e7f52ee35a5cc27c5148d4558feb578c5080181dcfb
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W1
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/162"
    ticket_id: "162"
    epic_ticket_id: "160"
    pr_number: 172
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/172"
    reviewed_head_sha: "3074e82b7b54bbbd6d015f0420d255fd81a30ea1"
    pass1_tip_sha: "7c11494"
    contracts_produced: 5
    assigned_reqs:
      - REQ-03
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 302
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "162"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w1-checkpoint-persistence
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W1.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W1.md
      - docs/specification/as-built/implementation-status.md
```
