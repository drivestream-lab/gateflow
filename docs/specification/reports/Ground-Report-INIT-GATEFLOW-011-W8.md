# Ground report — INIT-GATEFLOW-011 W8

| Field | Value |
|-------|-------|
| Wave | W8 — Merge confirm + completion eligibility (CAP-08 / CAP-09) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w8-merge-completion` @ `a0de226c72968af2796bf0c91008f96b230a99c6` — reviewed product tip for sign-off (Pass-2 docs may tip-ahead) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/180 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `a0de226` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W9+ |
| Assigned REQs | REQ-21, REQ-22, REQ-23, REQ-24, REQ-28 — from WorkManifest TASK-W8-01…04 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W8 | Pass-1 **383 passed**; ground re-proof 2026-08-07 **383 passed**; merge subset **5 passed**; completion subset **4 passed**; API merge/completion tests in `test_initiatives_read_api` |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; services/routes/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `a0de226`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `a0de226c72968af2796bf0c91008f96b230a99c6` on `feature/INIT-GATEFLOW-011-w8-merge-completion` (product Pass-1; `wave-accepted`)
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **383 passed**
- Merge subset: 5 passed (`test_merge_readout_service`); completion subset: 4 passed (`test_completion_readout_service`)
- PR [#180](https://github.com/drivestream-lab/gateflow/pull/180) labels: **`wave-accepted`**
- Learning-Extract W8 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-21 | Merge confirm reuses CAP-01 against `wave-signoff` → merged state + merge commit SHA, or itemized missing items | `MergeReadoutService.get_merge_readout` → `CheckpointEvidenceService.evaluate("wave-signoff")` + Forge PR `merged` / `merge_commit_sha`; `test_merge_readout_service`; GET `.../waves/{wave_id}/merge` | **pass** |
| REQ-22 | After confirmed merge, if next wave unblocked → surface "wave W{n+1} is now unblocked" | `next_wave_nudge` when next CAP-05 status is `ready-to-start`; `test_merge_readout_service` | **pass** |
| REQ-23 | Ready to close iff all waves Done; else waiting on wave N; empty → no waves found | `CompletionReadoutService` eligibility enum + messages; `test_completion_readout_service`; GET `.../completion` | **pass** |
| REQ-24 | Pure rollup of CAP-05 wave-map — no second board query with different logic | Completion injects only `WaveMapService.get_wave_map`; unit proves rollup from map rows | **pass** |
| REQ-28 | No CAP path introduces mutate routes or Forge write actions | GET-only merge + completion; programme token; 401/404/405; CAP-01 may persist check on evaluate (side effect of reuse) — no Forge writes from new paths; `test_initiatives_read_api` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — merge uses checkpoint + forge + wave map + runs/board; completion uses wave map only |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `merge_readout_models.py`, `completion_readout_models.py`; none in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — GET merge + completion on `/api/v1/initiatives` public_paths |
| Pin forge mutate authority; CAP-08/09 read-only | ADR-009, REQ-28 | **pass** — Forge read for PR merge fields; no writes from new paths |
| Fail closed on unknown initiative | `fail-fast.mdc` | **pass** — merge 404 when no run/EPIC; completion propagates wave-map 404 |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns derivation; live `verify_merge_and_completion` smoke only |
| Reuse CAP-01 vocabulary (no fork) | Ground-Report-W1; Pre-Implement W8 | **pass** — `evaluate` with checkpoint id `wave-signoff` |
| Reuse CAP-05 status rules (no parallel) | Ground-Report-W4; REQ-24 | **pass** — completion does not invent Done semantics |
| Do not treat CAP-07 drift as merge gate | Ground-Report-W7 | **pass** — merge path independent of closeout drift |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT |
| DI singleton for new business services | `dependency-injection.mdc` | **pass** — `binder.bind(MergeReadoutService)`, `binder.bind(CompletionReadoutService)` |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Composed / live CAP-01 evaluate | Ground-Report-W1 | **yes** — `evaluate("wave-signoff", CheckpointPrRef)`; missing items + verdict reused |
| Forge PR merge fields | Ground-Report-W0/W1; ForgeClient | **yes** — `merged`, `merge_commit_sha` on PR document |
| Wave map compose + status derivation | Ground-Report-W4 | **yes** — nudge + completion rollup |
| Initiative identity + 404 | Ground-Report-W2 | **yes** — same fail-closed pattern for merge |
| Implement-lane run selection | Ground-Report-W6/W7 | **yes** — merge selects implement-lane run for PR |
| Nesting under initiatives router | Ground-Report-W7 | **yes** — `…/merge` sibling; `…/completion` under initiative |
| Closeout / implementation / spec / waves GETs | Ground-Report-W4–W7 | **yes present** — **must not regress** |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W8.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W8 Learning-Extract emitted `items: []` — no human-fix signal; tip `a0de226` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W9 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Merge confirm compose | `MergeReadoutService` | `get_merge_readout(initiative_id, wave_id, org=, repo=)` | initiative + wave + forge org/repo | `MergeReadoutResult` | CAP-01 `wave-signoff` verdict + PR merged/SHA; missing_items when not merged | W9+ |
| Next-wave nudge | `MergeReadoutService._next_wave_nudge` | internal | wave map after merge | optional plain string | Only when `pr.merged` and next status `ready-to-start` | W9 may surface similar unblock signals |
| Completion eligibility | `CompletionReadoutService` | `get_completion_readout(initiative_id, org=, repo=)` | initiative + org/repo | `CompletionReadoutResult` | Pure CAP-05 rollup; empty → no_waves_found never ready_to_close | W9 closure preview |
| GET merge route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/merge` | path + org/repo + programme token | `MergeReadoutResult` JSON | GET-only; 401; 404 unknown; 405 non-GET | W9 must not regress |
| GET completion route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/completion` | path + org/repo + programme token | `CompletionReadoutResult` JSON | GET-only; 401; 404 unknown; 405 non-GET | W9 nests closure preview nearby |
| Live verify CAP-08/09 | `tests/verify/verify_merge_and_completion.py` | module main | programme knobs; optional initiative/wave env | exit 0 under prereqs | Smoke only | W9+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/180 @ `a0de226c72968af2796bf0c91008f96b230a99c6` — **expected reviewed product head SHA** (`wave-accepted`); Pass-2 docs tip may tip-ahead after `commit_workspace`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W8.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W8.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W8.md`
- Accept evidence: `wave-accepted` on tip `a0de226` (wave-acceptance) — human approved already
- As-built: W8 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `a0de226`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-21 / REQ-22 / REQ-23 / REQ-24 / REQ-28)
- [ ] Review §Contracts produced — accurate for W9 `/pre-implement`
- [ ] Confirm reviewed product head SHA matches `a0de226` (or note Pass-2 docs tip-ahead)
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#169](https://github.com/drivestream-lab/gateflow/issues/169) → Done; then human merges #180 (product tip `a0de226` + Pass-2 docs tip).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W8.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W8
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/169"
    ticket_id: "169"
    epic_ticket_id: "160"
    pr_number: 180
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/180"
    reviewed_head_sha: "a0de226c72968af2796bf0c91008f96b230a99c6"
    pass1_tip_sha: "a0de226"
    contracts_produced: 6
    assigned_reqs:
      - REQ-21
      - REQ-22
      - REQ-23
      - REQ-24
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 383
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "169"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w8-merge-completion
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W8.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W8.md
      - docs/specification/as-built/implementation-status.md
```
