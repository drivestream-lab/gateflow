# Ground report — INIT-GATEFLOW-011 W9

| Field | Value |
|-------|-------|
| Wave | W9 — Closure preview + CAP-01 reuse (CAP-10) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w9-closure-preview` @ `1ce031f54df0f09d0da3e3d80683ab488358d98f` — reviewed product tip for sign-off (Pass-2 docs may tip-ahead) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/181 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `1ce031f` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete (final CAP wave — handoff for initiative-closure / CAP-10 consumers) |
| Assigned REQs | REQ-25, REQ-26, REQ-27, REQ-28 — from WorkManifest TASK-W9-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W9 | Pass-1 **394 passed**; ground re-proof 2026-08-07 **394 passed**; closure service **7 passed**; API closure tests **4 passed** |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/route/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `1ce031f`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `1ce031f54df0f09d0da3e3d80683ab488358d98f` on `feature/INIT-GATEFLOW-011-w9-closure-preview` (product Pass-1; `wave-accepted`)
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **394 passed**
- Closure subset: 7 passed (`test_closure_preview_service`); API closure: 4 passed (`test_initiatives_read_api` -k closure)
- PR [#181](https://github.com/drivestream-lab/gateflow/pull/181) labels: **`wave-accepted`**
- Learning-Extract W9 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-25 | Pre-purge lists delete vs keep from purge skill manifest/plan; "not yet run" when skill not executed | `build_purge_plan_preview` + `PurgePreviewPhaseType.NOT_YET_RUN` / message `not yet run`; `test_closure_preview_service`; GET `.../closure` | **pass** |
| REQ-26 | Post-purge lists actual deleted/kept for before/after | `PurgeExecutionPreview` from handoff `signals.deleted` / `refused` / `missing_ok`; stage SUCCESS or later closure stages; unit | **pass** |
| REQ-27 | Once closure PR exists, reuse CAP-01 for `initiative-closure-signoff-app` / `initiative-closure-signoff-meta` | `CheckpointEvidenceService.evaluate` both ids when `closure_pr_number` set; nested `CheckpointStatusResult`; unit | **pass** |
| REQ-28 | No CAP path introduces mutate product routes or Forge write actions | GET-only `.../{id}/closure` (distinct from POST `.../closure/start`); 401/404/405; no Forge writes from preview path; `test_initiatives_read_api` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — runs/stages/events via repos; board + CAP-01 + handoff reader |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `closure_preview_models.py`; none in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — GET closure on `/api/v1/initiatives` |
| Pin forge mutate authority; CAP-10 read-only | ADR-009, REQ-28 | **pass** — CAP-01 evaluate may persist check (reuse side effect); no Forge/board writes from preview |
| Fail closed on unknown initiative | `fail-fast.mdc` | **pass** — 404 when no run/EPIC; explicit `not yet run` when epic exists without purge |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns derivation; live `verify_closure_preview` smoke only |
| Purge plan from skill SSOT (no invent) | Pre-Implement W9; purge-app / artifact-write-contract | **pass** — `plan_source` cites contract; allowlist patterns match skill |
| Reuse CAP-01 vocabulary (no fork) | Ground-Report-W1; REQ-27 | **pass** — evaluate with pin checkpoint ids only |
| Do not regress merge/completion | Ground-Report-W8 | **pass** — nested `…/closure` near completion; prior routes untouched |
| Do not dispatch purge / closure start from GET | ADR-010; Pre-Implement | **pass** — readout only |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT |
| DI singleton for new business service | `dependency-injection.mdc` | **pass** — `binder.bind(ClosurePreviewService)` |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| CAP-01 evaluate | Ground-Report-W1 | **yes** — `evaluate(initiative-closure-signoff-app\|meta, CheckpointPrRef)` |
| Forge PR reads (via CAP-01) | Ground-Report-W0/W1 | **yes** — nested checkpoint results when PR present |
| Completion / merge nesting neighbor | Ground-Report-W8 | **yes** — `…/closure` sibling under initiatives; merge/completion not regress |
| Initiative identity + 404 | Ground-Report-W2 | **yes** — no run/EPIC → 404 |
| Closure start Enter-at purge-app | as-built INIT-010; ADR-010 | **yes present** — GET does not call start |
| Purge allowlist SSOT | purge-app skill / artifact-write-contract | **yes** — plan projection |
| Handoff signals deleted/refused/missing_ok | purge-app handoff | **yes** — execution preview |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W9.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W9 Learning-Extract emitted `items: []` — no human-fix signal; tip `1ce031f` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for initiative-closure / CAP-10 consumers; W9 is final CAP wave of INIT-GATEFLOW-011.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next consumer |
|----------|--------------------|-------------|-------------|--------------|------------|---------------|
| Closure preview compose | `ClosurePreviewService` | `get_closure_preview(initiative_id, org=, repo=)` | initiative + forge org/repo | `ClosurePreviewResult` | Plan always from purge allowlist; phase `not_yet_run` until purge-app evidence; CAP-01 when PR | initiative-closure / CAP-10 clients |
| Purge plan projection | `build_purge_plan_preview` | function(initiative_id) | INIT id | `PurgePlanPreview` | Matches artifact-write-contract + purge-app allowlist; does not invent deletes | same |
| Purge execution preview | `ClosurePreviewService` | internal from handoff/events | closure-lane run | `PurgeExecutionPreview` or null | deleted/kept/missing_ok from signals; null when not yet run | same |
| CAP-01 closure signoffs | nested `signoff_app` / `signoff_meta` | CAP-01 evaluate | closure PR ref | `CheckpointStatusResult` ×2 | No separate approval logic | same |
| GET closure route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/closure` | path + org/repo + programme token | `ClosurePreviewResult` JSON | GET-only; 401; 404; 405; ≠ POST `…/closure/start` | must not regress |
| Live verify CAP-10 | `tests/verify/verify_closure_preview.py` | module main | programme knobs; optional initiative env | exit 0 under prereqs | Smoke only | closure dogfood / future |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/181 @ `1ce031f54df0f09d0da3e3d80683ab488358d98f` — **expected reviewed product head SHA** (`wave-accepted`); Pass-2 docs tip may tip-ahead after `commit_workspace`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W9.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W9.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W9.md`
- Accept evidence: `wave-accepted` on tip `1ce031f` (wave-acceptance) — human approved already
- As-built: W9 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `1ce031f`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-25 / REQ-26 / REQ-27 / REQ-28)
- [ ] Review §Contracts produced — accurate for CAP-10 / initiative-closure consumers
- [ ] Confirm reviewed product head SHA matches `1ce031f` (or note Pass-2 docs tip-ahead)
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#170](https://github.com/drivestream-lab/gateflow/issues/170) → Done; then human merges #181 (product tip `1ce031f` + Pass-2 docs tip).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W9.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W9
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/170"
    ticket_id: "170"
    epic_ticket_id: "160"
    pr_number: 181
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/181"
    reviewed_head_sha: "1ce031f54df0f09d0da3e3d80683ab488358d98f"
    pass1_tip_sha: "1ce031f"
    contracts_produced: 6
    assigned_reqs:
      - REQ-25
      - REQ-26
      - REQ-27
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 394
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "170"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w9-closure-preview
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W9.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W9.md
      - docs/specification/as-built/implementation-status.md
```
