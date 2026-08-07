# Ground report — INIT-GATEFLOW-011 W6

| Field | Value |
|-------|-------|
| Wave | W6 — Wave implementation progress (CAP-06) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w6-implementation-readout` @ `0b0f14478ab63564be5be3ce68e01093d918790d` — reviewed product tip for sign-off (Pass-2 docs may tip-ahead) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/178 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `0b0f144` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W7+ |
| Assigned REQs | REQ-16, REQ-17, REQ-28 — from WorkManifest TASK-W6-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W6 | Pass-1 **356 passed**; ground re-proof 2026-08-07 **356 passed**; W6 service subset **7 passed** (`test_implementation_readout_service`); API implementation tests in `test_initiatives_read_api` |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/route/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `0b0f144`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `0b0f14478ab63564be5be3ce68e01093d918790d` on `feature/INIT-GATEFLOW-011-w6-implementation-readout` (product Pass-1; `wave-accepted`)
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **356 passed**
- W6 subset: 7 passed (`test_implementation_readout_service`)
- PR [#178](https://github.com/drivestream-lab/gateflow/pull/178) labels: **`wave-accepted`**
- Learning-Extract W6 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-16 | In-progress wave read-out returns task-by-task progress from run timeline; Draft PR link when `wave-pr-action` succeeds | `ImplementationReadoutService.get_implementation_readout`; tasks from stages + current node; Draft PR when `pr_number` or `forge_executed@wave-pr-action`; prefer implement-lane (`wave_id`, no `meta_pr_url`); `test_implementation_readout_service`; GET `.../waves/{wave_id}/implementation`; `verify_wave_implementation` co-shipped | **pass** |
| REQ-17 | On task failure or run stop (`needs-input`), name which task and why | `failed_task_id` + `failure_reason` from failed stages / handoff blockers / `run_stopped` handoff_context; `test_implementation_readout_service` | **pass** |
| REQ-28 | No CAP path introduces mutate routes or Forge write actions | GET-only `.../implementation`; programme token; 401/404/405; zero Forge writes; `test_initiatives_read_api` + `verify_wave_implementation` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — runs/stages/events via repositories; board via `BoardService`; handoff via `HandoffReader`; pin via `WorkflowEngine` |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `implementation_readout_models.py`; none in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — GET implementation + `/api/v1/initiatives` on `public_paths` |
| Pin forge mutate authority; CAP-06 read-only | ADR-009, REQ-28 | **pass** — no Forge writes from implementation-readout path |
| Fail closed on unknown initiative | `fail-fast.mdc` | **pass** — 404 when no run / EPIC; no-run-for-wave → empty tasks + `no_run_reason` (not invented PR) |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns derivation; live `verify_wave_implementation` smoke only |
| Prefer Gateflow-owned evidence over workspace scrape | Pre-Implement W6; fail-fast | **pass** — stages/events/handoff/stop only |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT, 1 contract kept |
| DI singleton for new business service | `dependency-injection.mdc` | **pass** — `binder.bind(ImplementationReadoutService)` (glue noted in Pre-Implement / Wave-Execution) |
| Do not redefine CAP-05 status rules | Ground-Report-W4; REQ-15 | **pass** — W6 does not invent parallel wave-state store |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Wave id vocabulary + map rows | Ground-Report-W4 | **yes** — path `{wave_id}` matches W4 tokens; select run by `wave_id` |
| GET wave map nesting parent | Ground-Report-W4 | **yes** — nests `…/waves/{wave_id}/implementation` |
| Initiative identity + 404 unknown | Ground-Report-W2 / W3 | **yes** — same fail-closed message pattern |
| Run fields (`pr_number`, `workflow_node`, `wave_id`, `handoff_path`) | Ground-Report-W2; as-built | **yes** — implement-lane preferred (no `meta_pr_url`) |
| GET nesting siblings (`…/spec`, `…/waves`) | Ground-Report-W4 / W5 | **yes** — same router; **must not regress** waves or spec |
| Spec-lane run selection (W5) | Ground-Report-W5 | **yes present** — **W6 does not consume** for CAP-06 fields; must not confuse meta-lane vs implement-lane |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W6.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W6 Learning-Extract emitted `items: []` — no human-fix signal; tip `0b0f144` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W7 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Implementation readout compose | `ImplementationReadoutService` | `get_implementation_readout(initiative_id, wave_id, org=, repo=)` | initiative + wave + forge org/repo | `ImplementationReadoutResult` | tasks[] per stage; Draft PR URL only when number known; failed_task_id ⇒ failure_reason | W7+ |
| Implement-lane run selection | `ImplementationReadoutService._select_implement_run` | internal | initiative runs + wave_id | run or none | Prefer no `meta_pr_url`; then active; else latest | W7+ must not use meta-lane as wave progress |
| Draft wave PR readiness | `ImplementationReadoutService._draft_pr_number` | internal | run + events | int or null | PR iff `pr_number` or `forge_executed@wave-pr-action` | W7+ / W8 merge consumers |
| Named failure | `ImplementationReadoutService._named_failure` | internal | run + tasks + handoff/stop | task id + reason | REQ-17 on fail/stop/needs-input | W7 closeout may cite stop context similarly |
| GET implementation route | `api/v1/initiatives_routes` | `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/implementation` | path ids + query org/repo + programme token | `ImplementationReadoutResult` JSON | GET-only; 401; 404 unknown initiative; 405 non-GET | W7 nests `…/closeout` under same wave path |
| Live verify CAP-06 | `tests/verify/verify_wave_implementation.py` | module main | programme knobs; optional `GATEFLOW_INITIATIVE_ID` + `GATEFLOW_WAVE_ID` | exit 0 under prereqs | Smoke only; does not duplicate unit | W7+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/178 @ `0b0f14478ab63564be5be3ce68e01093d918790d` — **expected reviewed product head SHA** (`wave-accepted`); Pass-2 docs tip may tip-ahead after `commit_workspace`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W6.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W6.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W6.md`
- Accept evidence: `wave-accepted` on tip `0b0f144` (wave-acceptance) — human approved already
- As-built: W6 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `0b0f144`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-16 / REQ-17 / REQ-28)
- [ ] Review §Contracts produced — accurate for W7 `/pre-implement`
- [ ] Confirm reviewed product head SHA matches `0b0f144` (or note Pass-2 docs tip-ahead)
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#167](https://github.com/drivestream-lab/gateflow/issues/167) → Done; then human merges #178 (product tip `0b0f144` + Pass-2 docs tip).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W6.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W6
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/167"
    ticket_id: "167"
    epic_ticket_id: "160"
    pr_number: 178
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/178"
    reviewed_head_sha: "0b0f14478ab63564be5be3ce68e01093d918790d"
    pass1_tip_sha: "0b0f144"
    contracts_produced: 6
    assigned_reqs:
      - REQ-16
      - REQ-17
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 356
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "167"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w6-implementation-readout
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W6.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W6.md
      - docs/specification/as-built/implementation-status.md
```
