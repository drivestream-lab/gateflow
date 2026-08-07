# Ground report — INIT-GATEFLOW-011 W4

| Field | Value |
|-------|-------|
| Wave | W4 — Wave map readout (CAP-05) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w4-wave-map` @ `ed3d6be9ac47ae6ff1e4988399d115cb7a957152` — reviewed head for sign-off (product tip; Pass-2 docs may tip-ahead) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/176 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `ed3d6be` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W5+ |
| Assigned REQs | REQ-14, REQ-15, REQ-28 — from WorkManifest TASK-W4-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W4 | Pass-1 **335 passed**; ground re-proof 2026-08-07 **335 passed**; W4 service subset **6 passed** (`test_wave_map_service`); API waves tests in `test_initiatives_read_api` |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/route/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `ed3d6be`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `ed3d6be9ac47ae6ff1e4988399d115cb7a957152` on `feature/INIT-GATEFLOW-011-w4-wave-map` (product Pass-1; `wave-accepted`)
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **335 passed**
- W4 subset: 6 passed (`test_wave_map_service`)
- PR [#176](https://github.com/drivestream-lab/gateflow/pull/176) labels: **`wave-accepted`**
- Learning-Extract W4 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-14 | Wave map returns per-wave status ∈ {`done`, `ready-to-start`, `blocked`, `active`}; when `blocked`, names why | `WaveMapService.get_wave_map` + `WaveMapStatusType`; `_derive_status` priority Done → active → blocked (predecessor) → ready-to-start; `block_reason` when blocked; `test_wave_map_service`; GET `/initiatives/{id}/waves`; `verify_wave_map` co-shipped | **pass** |
| REQ-15 | Wave status derived only from existing board Feature tickets + run state — no new wave-state store | `BoardService.list_tickets(Feature)` + `RunRepository.list_runs`; wave id from Feature title `\bW\d+\b`; no new ORM table / Alembic; DI uses existing Postgres + board | **pass** |
| REQ-28 | No CAP path introduces mutate routes or Forge write actions | New surface is GET-only `/initiatives/{id}/waves`; programme token; 401/404/405 covered; zero `apply_labels`/review/merge/`update_board_status` from CAP-05; `test_initiatives_read_api` + `verify_wave_map` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — `WaveMapService` uses `RunRepository` (Pydantic) + `BoardService` |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `wave_map_models.py`; none in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — GET waves + `/api/v1/initiatives` on `public_paths` |
| Pin forge mutate authority; CAP-05 read-only | ADR-009, REQ-28 | **pass** — no Forge writes from wave-map path |
| Fail closed on unknown initiative | `fail-fast.mdc` | **pass** — 404 when no run / EPIC / Feature |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns derivation; live `verify_wave_map` smoke only |
| No new ORM table / no Alembic revision | `database-migrations.mdc`, REQ-15 | **pass** |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT, 1 contract kept |
| DI singleton for new business service | `dependency-injection.mdc` | **pass** — `binder.bind(WaveMapService)` (glue noted in Pre-Implement / Wave-Execution) |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Initiative identity + 404 unknown | Ground-Report-W2 / W3 | **yes** — wave map nests under same initiative id; 404 message pattern aligned |
| Board Feature tickets list | as-built / Ground-Report-W3 pre-implement | **yes** — `BoardTicketType.FEATURE` via `BoardService.list_tickets` |
| Run data (`wave_id`, `status_type=active`) | Ground-Report-W2 | **yes** — marks `active` when in-flight run exists |
| Initiative parent routes + programme token | Ground-Report-W3 | **yes** — sibling GET on `initiatives_routes.py` |
| Meta PRD / CAP-01 (W3) | Ground-Report-W3 | **yes present** — **W4 does not consume** for wave-map status (REQ-15 = board+run only); list/detail not regressed |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W4.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W4 Learning-Extract emitted `items: []` — no human-fix signal; tip `ed3d6be` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W5 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Wave map compose | `WaveMapService` | `get_wave_map(initiative_id, org=, repo=)` | initiative id + forge org/repo | `WaveMapResult` (`waves[]` of `WaveMapItem`) | Status ∈ {done, ready-to-start, blocked, active}; blocked ⇒ non-empty `block_reason`; no new store | W5+ (W8 completion rollup reuses CAP-05 logic) |
| Wave status derivation | `WaveMapService._derive_status` | internal | board column, active-run flag, predecessor Done | `WaveMapStatusType` + optional reason | Priority: Done column → done; active run → active; predecessor not Done → blocked; else ready-to-start | W8 rollup must not invent parallel status rules |
| Wave id from Feature title | `WaveMapService._parse_wave_id` | Feature ticket title | string title | `W\d+` token or skip | Missing token → skip with warning; sort numeric by wave number | W5+ board Feature shapes |
| GET wave map route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/waves` | path id + query org/repo + programme token | `WaveMapResult` JSON | GET-only; 401 without token; 404 unknown initiative; 405 non-GET | W5 nests sibling `…/spec` under same router |
| Live verify CAP-05 | `tests/verify/verify_wave_map.py` | module main | programme knobs; optional `GATEFLOW_INITIATIVE_ID` | exit 0 under prereqs | Smoke only; does not duplicate unit derivation | W5+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/176 @ `ed3d6be9ac47ae6ff1e4988399d115cb7a957152` — **expected reviewed product head SHA** (`wave-accepted`); Pass-2 docs tip may tip-ahead after `commit_workspace`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W4.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W4.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W4.md`
- Accept evidence: `wave-accepted` on tip `ed3d6be` (wave-acceptance) — human approved already
- As-built: W4 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `ed3d6be`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-14 / REQ-15 / REQ-28)
- [ ] Review §Contracts produced — accurate for W5 `/pre-implement`
- [ ] Confirm reviewed product head SHA matches `ed3d6be` (or note Pass-2 docs tip-ahead)
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#165](https://github.com/drivestream-lab/gateflow/issues/165) → Done; then human merges #176 (product tip `ed3d6be` + Pass-2 docs tip).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W4.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W4
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/165"
    ticket_id: "165"
    epic_ticket_id: "160"
    pr_number: 176
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/176"
    reviewed_head_sha: "ed3d6be9ac47ae6ff1e4988399d115cb7a957152"
    pass1_tip_sha: "ed3d6be"
    contracts_produced: 5
    assigned_reqs:
      - REQ-14
      - REQ-15
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 335
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "165"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w4-wave-map
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W4.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W4.md
      - docs/specification/as-built/implementation-status.md
```
