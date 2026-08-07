# Ground report — INIT-GATEFLOW-011 W7

| Field | Value |
|-------|-------|
| Wave | W7 — Closeout readout + drift safeguard (CAP-07) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w7-closeout-drift` @ `6bd833606c2fd09624010cc6db91a5cc096c4cb0` — reviewed product tip for sign-off (Pass-2 docs may tip-ahead) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/179 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `6bd8336` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W8+ |
| Assigned REQs | REQ-18, REQ-19, REQ-20, REQ-28 — from WorkManifest TASK-W7-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W7 | Pass-1 **366 passed**; ground re-proof 2026-08-07 **366 passed**; closeout service subset **6 passed** (`test_closeout_readout_service`); API closeout tests in `test_initiatives_read_api` |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/route/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `6bd8336`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `6bd833606c2fd09624010cc6db91a5cc096c4cb0` on `feature/INIT-GATEFLOW-011-w7-closeout-drift` (product Pass-1; `wave-accepted`)
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **366 passed**
- Closeout subset: 6 passed (`test_closeout_readout_service`)
- PR [#179](https://github.com/drivestream-lab/gateflow/pull/179) labels: **`wave-accepted`**
- Learning-Extract W7 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-18 | Closeout read-out lists what closeout added (lessons / learning-store) after `learning-extract` / `ground-spec` | `CloseoutReadoutService.get_closeout_readout` → `additions[]` from learning rows + stages; `test_closeout_readout_service`; GET `.../waves/{wave_id}/closeout`; `verify_wave_closeout_readout` co-shipped | **pass** |
| REQ-19 | Drift vs wave-acceptance baseline SHA (REQ-06 `checkpoint_check`); mismatch → product-changed flag; missing baseline → `unknown — no baseline recorded` | `_compute_drift` / `_baseline_sha_from_events` (historical `checkpoint_check` with `wave-acceptance`); PR head via Forge GET; statuses `none` / `drifted` / `unknown_no_baseline` / `unavailable`; unit covers unknown + drifted + match | **pass** |
| REQ-20 | Drift is advisory only — does not block closeout mechanics | `advisory_only=True` always on `CloseoutReadoutResult`; unit + API assert; no mutate of closeout lane | **pass** |
| REQ-28 | No CAP path introduces mutate routes or Forge write actions | GET-only `.../closeout`; programme token; 401/404/405; Forge used read-only for PR head; `test_initiatives_read_api` + `verify_wave_closeout_readout` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — runs/stages/events/learning via repositories; board via `BoardService`; PR head via `ForgeClient` read |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `closeout_readout_models.py`; none in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — GET closeout + `/api/v1/initiatives` on `public_paths` |
| Pin forge mutate authority; CAP-07 read-only | ADR-009, REQ-28 | **pass** — no Forge writes from closeout-readout path |
| Fail closed on unknown initiative | `fail-fast.mdc` | **pass** — 404 when no run / EPIC; no-run-for-wave → empty additions + `no_run_reason` |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns derivation; live `verify_wave_closeout_readout` smoke only |
| Prefer Gateflow-owned evidence over workspace scrape | Pre-Implement W7; fail-fast | **pass** — learning table + stages/events; not ambient report scrape |
| Drift baseline = historical acceptance check, not live CAP-01 | Ground-Report-W1; Pre-Implement W7 | **pass** — `checkpoint_check` events filtered to `wave-acceptance`; not live `evaluate_composed` as baseline |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT, 1 contract kept |
| DI singleton for new business service | `dependency-injection.mdc` | **pass** — `binder.bind(CloseoutReadoutService)` |
| Do not redefine CAP-06 implementation progress | Ground-Report-W6 | **pass** — reuses implement-lane run selection pattern; sibling route only |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Wave path nesting + programme token | Ground-Report-W6 | **yes** — nests sibling `…/closeout` under same router as `…/implementation` |
| Implement-lane run selection | Ground-Report-W6 | **yes** — prefer no `meta_pr_url`; then active; else latest for `wave_id` |
| Draft wave PR number for closeout-time head | Ground-Report-W6 | **yes** — PR from `pr_number` / forge_executed; Forge GET for head SHA |
| Checkpoint persistence (REQ-06) | Ground-Report-W1 | **yes** — drift baseline from persisted `checkpoint_check` |
| Checkpoint history (REQ-07) | Ground-Report-W1 | **yes** — events carry historical checked_sha; not live verdict substitution |
| Initiative identity + 404 unknown | Ground-Report-W2 | **yes** — same fail-closed pattern |
| Learning store (INIT-007) | as-built INIT-007 | **yes** — learning rows for REQ-18 itemization |
| Wave map / CAP-05 | Ground-Report-W4 | **yes present** — **W7 does not consume** for CAP-07 fields; must not regress |
| Spec readout / CAP-04 | Ground-Report-W5 | **yes present** — **W7 does not consume**; must not regress |
| Implementation readout / CAP-06 | Ground-Report-W6 | **yes present** — **must not regress** `…/implementation` |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W7.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W7 Learning-Extract emitted `items: []` — no human-fix signal; tip `6bd8336` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W8 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Closeout readout compose | `CloseoutReadoutService` | `get_closeout_readout(initiative_id, wave_id, org=, repo=)` | initiative + wave + forge org/repo | `CloseoutReadoutResult` | additions[] itemized; drift_status set; advisory_only always true | W8+ |
| Implement-lane run selection (reuse) | `CloseoutReadoutService._select_implement_run` | internal | initiative runs + wave_id | run or none | Prefer no `meta_pr_url`; same pattern as CAP-06 | W8+ must not use meta-lane as closeout evidence |
| Closeout additions | `CloseoutReadoutService._build_additions` | internal | learning rows + stages | `CloseoutAdditionItem[]` | From Gateflow-owned learning + `learning-extract` / `ground-spec` stages | W8 may cite closeout evidence |
| Advisory drift | `CloseoutReadoutService._compute_drift` | internal | events + PR head | drift_status + message + SHAs | Baseline = historical `checkpoint_check` @ `wave-acceptance`; missing → unknown_no_baseline; never blocks mechanics | W8 merge-confirm must not treat this as merge gate |
| GET closeout route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/closeout` | path ids + query org/repo + programme token | `CloseoutReadoutResult` JSON | GET-only; 401; 404 unknown initiative; 405 non-GET | W8 nests merge/completion under initiative tree; must not regress closeout |
| Live verify CAP-07 | `tests/verify/verify_wave_closeout_readout.py` | module main | programme knobs; optional `GATEFLOW_INITIATIVE_ID` + `GATEFLOW_WAVE_ID` | exit 0 under prereqs | Smoke only; does not duplicate unit | W8+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/179 @ `6bd833606c2fd09624010cc6db91a5cc096c4cb0` — **expected reviewed product head SHA** (`wave-accepted`); Pass-2 docs tip may tip-ahead after `commit_workspace`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W7.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W7.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W7.md`
- Accept evidence: `wave-accepted` on tip `6bd8336` (wave-acceptance) — human approved already
- As-built: W7 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `6bd8336`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-18 / REQ-19 / REQ-20 / REQ-28)
- [ ] Review §Contracts produced — accurate for W8 `/pre-implement`
- [ ] Confirm reviewed product head SHA matches `6bd8336` (or note Pass-2 docs tip-ahead)
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#168](https://github.com/drivestream-lab/gateflow/issues/168) → Done; then human merges #179 (product tip `6bd8336` + Pass-2 docs tip).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W7.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W7
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/168"
    ticket_id: "168"
    epic_ticket_id: "160"
    pr_number: 179
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/179"
    reviewed_head_sha: "6bd833606c2fd09624010cc6db91a5cc096c4cb0"
    pass1_tip_sha: "6bd8336"
    contracts_produced: 6
    assigned_reqs:
      - REQ-18
      - REQ-19
      - REQ-20
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 366
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "168"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w7-closeout-drift
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W7.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W7.md
      - docs/specification/as-built/implementation-status.md
```
