# Ground report — INIT-GATEFLOW-011 W5

| Field | Value |
|-------|-------|
| Wave | W5 — Spec lane readout (CAP-04) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w5-spec-readout` @ `069989e5bcf57bab9109af5ea9745accad5a4a30` — reviewed product tip for sign-off (Pass-2 docs may tip-ahead) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/177 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `069989e` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W6+ |
| Assigned REQs | REQ-12, REQ-13, REQ-28 — from WorkManifest TASK-W5-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W5 | Pass-1 **345 passed**; ground re-proof 2026-08-07 **345 passed**; W5 service subset **6 passed** (`test_spec_readout_service`); API spec tests in `test_initiatives_read_api` |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/route/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `069989e`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `069989e5bcf57bab9109af5ea9745accad5a4a30` on `feature/INIT-GATEFLOW-011-w5-spec-readout` (product Pass-1; `wave-accepted`)
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **345 passed**
- W5 subset: 6 passed (`test_spec_readout_service`)
- PR [#177](https://github.com/drivestream-lab/gateflow/pull/177) labels: **`wave-accepted`**
- Learning-Extract W5 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-12 | Spec-lane readout returns Draft Spec PR link, plain-language artifacts, findings/open questions, exact next step from pin | `SpecReadoutService.get_spec_readout`; READY when `pr_number` or `forge_executed@spec-pr-action`; findings from handoff/stop blockers; next step via pin/`next_candidates`; stage artifact labels; `test_spec_readout_service`; GET `/initiatives/{id}/spec`; `verify_spec_readout` co-shipped | **pass** |
| REQ-13 | Before `spec-pr-action`, plain not-ready — no broken/missing URL | `readiness=not_ready` + `readiness_reason`; `draft_spec_pr_url=null`; unavailable when no spec-lane run (`meta_pr_url`); `test_spec_readout_service` | **pass** |
| REQ-28 | No CAP path introduces mutate routes or Forge write actions | GET-only `/initiatives/{id}/spec`; programme token; 401/404/405; zero Forge writes; `test_initiatives_read_api` + `verify_spec_readout` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — runs/stages/events via repositories; board via `BoardService`; handoff via `HandoffReader`; pin via `WorkflowEngine` |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `spec_readout_models.py`; none in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — GET spec + `/api/v1/initiatives` on `public_paths` |
| Pin forge mutate authority; CAP-04 read-only | ADR-009, REQ-28 | **pass** — no Forge writes from spec-readout path |
| Fail closed on unknown initiative | `fail-fast.mdc` | **pass** — 404 when no run / EPIC |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns derivation; live `verify_spec_readout` smoke only |
| Prefer Gateflow-owned evidence over workspace scrape | Pre-Implement W5; fail-fast | **pass** — baton/events/runs only; no ambient report file reads |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT, 1 contract kept |
| DI singleton for new business service | `dependency-injection.mdc` | **pass** — `binder.bind(SpecReadoutService)` (glue noted in Pre-Implement / Wave-Execution) |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Initiative identity + 404 unknown | Ground-Report-W2 / W3 | **yes** — same fail-closed message pattern |
| Run fields (`pr_number`, `workflow_node`, `meta_pr_url`, `handoff_path`) | Ground-Report-W2; as-built | **yes** — spec lane selected via `meta_pr_url` |
| Pin / workflow graph | as-built; `WorkflowEngine` | **yes** — next step from pin / handoff candidates |
| GET nesting on `initiatives_routes` | Ground-Report-W4 | **yes** — sibling `…/spec` beside `…/waves` |
| Wave map compose (W4) | Ground-Report-W4 | **yes present** — **W5 does not consume** for CAP-04 fields; must not regress waves |
| Meta PRD / CAP-01 (W3) | Ground-Report-W3 | **yes present** — **W5 does not consume**; must not regress list/detail |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W5.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W5 Learning-Extract emitted `items: []` — no human-fix signal; tip `069989e` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W6 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Spec readout compose | `SpecReadoutService` | `get_spec_readout(initiative_id, org=, repo=)` | initiative id + forge org/repo | `SpecReadoutResult` | readiness ∈ {ready, not_ready, unavailable}; ready ⇒ PR number+URL; not ready ⇒ null URL + reason | W6+ |
| Draft Spec PR readiness | `SpecReadoutService._is_draft_spec_ready` | internal | run + events | boolean | READY iff `pr_number` or `forge_executed@spec-pr-action` | W6+ consumers of Spec PR existence |
| Spec-lane run selection | `SpecReadoutService._select_spec_run` | internal | initiative runs | run with `meta_pr_url` or none | Prefer active; else latest with meta URL | W6+ must not confuse implement-lane runs |
| GET spec route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/spec` | path id + query org/repo + programme token | `SpecReadoutResult` JSON | GET-only; 401; 404 unknown; 405 non-GET | W6 nests sibling implementation under same router |
| Live verify CAP-04 | `tests/verify/verify_spec_readout.py` | module main | programme knobs; optional `GATEFLOW_INITIATIVE_ID` | exit 0 under prereqs | Smoke only; does not duplicate unit | W6+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/177 @ `069989e5bcf57bab9109af5ea9745accad5a4a30` — **expected reviewed product head SHA** (`wave-accepted`); Pass-2 docs tip may tip-ahead after `commit_workspace`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W5.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W5.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W5.md`
- Accept evidence: `wave-accepted` on tip `069989e` (wave-acceptance) — human approved already
- As-built: W5 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `069989e`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-12 / REQ-13 / REQ-28)
- [ ] Review §Contracts produced — accurate for W6 `/pre-implement`
- [ ] Confirm reviewed product head SHA matches `069989e` (or note Pass-2 docs tip-ahead)
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#166](https://github.com/drivestream-lab/gateflow/issues/166) → Done; then human merges #177 (product tip `069989e` + Pass-2 docs tip).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W5.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W5
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/166"
    ticket_id: "166"
    epic_ticket_id: "160"
    pr_number: 177
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/177"
    reviewed_head_sha: "069989e5bcf57bab9109af5ea9745accad5a4a30"
    pass1_tip_sha: "069989e"
    contracts_produced: 5
    assigned_reqs:
      - REQ-12
      - REQ-13
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 345
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "166"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w5-spec-readout
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W5.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W5.md
      - docs/specification/as-built/implementation-status.md
```
