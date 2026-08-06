# Ground report — INIT-GATEFLOW-010 W4

| Field | Value |
|-------|-------|
| Wave | W4 — Initiative closure Enter-at + freeze |
| Spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Initiative | INIT-GATEFLOW-010 |
| Date | 2026-08-06 |
| Wave head (exact) | `feature/INIT-GATEFLOW-010-w4-implement-lane` @ `64f34e7d3921857bbb626f804223f5460e97686f` — reviewed head for sign-off |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/152 (Draft — open for Pass-2 closeout) |
| Status | Draft |
| Review deadline | 2026-08-10 |
| Deciders | Tech lead / reviewer: PE — explicit LGTM required at `wave-signoff` |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified on tip + unit re-proof + Pass-1 human live-verify + closure smoke; §Contracts produced complete (final eng wave); no Blocking GF-*; exact-head sign-off package ready |
| Assigned REQs | REQ-12, REQ-13, REQ-14, REQ-15, REQ-17 (partial), REQ-18, REQ-20 — from WorkManifest TASK-W4-01…07 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W4 | **266 passed** at ground time (2026-08-06); W4-focused subset **10 passed** (`test_closure_start`, closure walk, REQ-20 partial failure) |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points and tests mapped below; `verify_closure` smoke auth/validation OK |
| Live | `Live-Verify-INIT-GATEFLOW-010-W4.md` | Human confirmed `.venv/bin/python -m tests.verify.verify_implement_lane` pass; run `6f14f48f-0afb-46ca-a880-c34fa6245648`; board #142 In Progress; `human_approved: true` |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-06):

- Tip SHA `64f34e7d3921857bbb626f804223f5460e97686f` on `feature/INIT-GATEFLOW-010-w4-implement-lane`
- Pass-1 tip `fac3058ec1caa580eb6ef9e4384d0de22860e00c`; post-tip `19a1908` + `64f34e7` docs-only (Live-Verify `human_approved`, commit-workspace records); no product-code human fix
- `make check` → exit 0 (black, ruff, pyright, import-linter)
- `make test` → **266 passed**
- W4 subset: `.venv/bin/pytest tests/unit/test_closure_start.py tests/unit/test_run_orchestrator.py::test_closure_walk_purge_then_pr_action_stops_at_signoff_app tests/unit/test_run_orchestrator.py::test_closure_partial_failure_after_epic_done_records_req20 -q` → **10 passed**
- Closure smoke: `.venv/bin/python -m tests.verify.verify_closure` → exit 0 (401/4xx probes; `features.initiative_closure.enabled: false` — happy 202 not exercised)
- Draft PR [#152](https://github.com/drivestream-lab/gateflow/pull/152) open; human live-verify `human_approved: true`

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-12 | `POST /api/v1/initiatives/closure/start` → 202 + run_id; malformed → 4xx | `initiatives_routes.start_initiative_closure`; `ClosureStartService.start_closure`; `test_closure_start_ok`, `test_closure_rejects_*`; `verify_closure` 401/4xx smoke | **pass** |
| REQ-13 | Closure Done-gate: any wave not Done → 422; 0 enqueue; EPIC untouched | `closure_done_gate.assert_closure_done_gate`; `test_closure_done_gate_rejects_not_done`, `test_closure_done_gate_unit`; service path skips EPIC update on gate fail | **pass** |
| REQ-14 | After Done-gate: EPIC → Done before purge-app Enter-at enqueue | `ClosureStartService.start_closure` EPIC `update_ticket_status` before job enqueue; `test_closure_start_ok` call order | **pass** |
| REQ-15 | Closure walk purge-app → closure PR → signoff-app; never purge-meta | `RunOrchestrator._closure_forbids_node` + `_CLOSURE_META_FORBIDDEN_NODES`; `test_closure_walk_purge_then_pr_action_stops_at_signoff_app`; `verify_closure._CLOSURE_FORBIDDEN_STAGES` guard | **pass** |
| REQ-17 (partial) | Verify suite covers closure Enter-at + Done-gate slice | `tests/verify/verify_closure.py` co-shipped + README feature map; smoke green; unit matrix for REQ-12–15; human Pass-1 implement_lane live pass | **pass** (W4 slice; full closure happy 202 human-run optional at signoff) |
| REQ-18 | Feature-readiness freeze doc (proven vs deferred) | [`Feature-Readiness-INIT-GATEFLOW-010.md`](Feature-Readiness-INIT-GATEFLOW-010.md) — proven/deferred table + human checkpoints | **pass** |
| REQ-20 | Partial failure after EPIC Done recorded; no closure-complete claim | `RunOrchestrator._partial_closure_failure_payload`; `test_closure_partial_failure_after_epic_done_records_req20` (`partial_closure_failure=True`, `closure_complete_claim=False`) | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Programme token on closure start | ADR-010 §7; http-api-conventions | **pass** — `verify_programme_service_token` dependency |
| Fail closed on Done-gate / malformed body | fail-fast.mdc | **pass** — 422/400 before enqueue |
| No cross-layer imports | architecture.mdc / import-linter | **pass** — `make check` contracts 0 broken |
| Closure lane never dispatches meta purge nodes | ADR-010 §7; REQ-15 | **pass** — orchestrator guard + unit timeline |
| No Forge merge / auto `*-lgtm` (consumed) | Ground-Report W3 | **pass** — unchanged on tip |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Closeout Done hop after ground-spec pass | Ground-Report W3 §Contracts produced | **yes** — W4 implement lane uses same board-status apply family; wave-done-action precedes signoff |
| No auto-chain after wave-signoff | Ground-Report W3 | **yes** — closure Enter-at is separate API (`POST …/closure/start`), not auto-chained |
| Board label + Project Status dual-write | Ground-Report W2 | **yes** — EPIC Done uses `BoardService.update_ticket_status` |
| Create triple predicate + implement ticket gates | Ground-Report W2 | **yes** — unchanged; closure uses programme token path |
| Board-status APPLY_FORGE apply | Ground-Report W1 | **yes** — wave-done-action on closeout lane |
| Pin tip `v0.5.0-rc.2` / `6561c7c` | Ground-Report W0 | **yes** — pin unchanged on wave branch |
| W3 human_approved on `develop` | as-built / merge #150 | **yes** — W4 branch includes W3 backfill |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| GF-01 | REQ-17 | `verify_closure` happy-path 202 enqueue not exercised at ground time (`features.initiative_closure.enabled: false`); smoke auth/validation pass; unit timeline covers REQ-12–15/20 — optional full dogfood at `wave-signoff` | Verify |
| GF-02 | — | W0 L-01 applies: keep PR [#152](https://github.com/drivestream-lab/gateflow/pull/152) open until Pass-2 closeout published + human `wave-signoff` merge — do not merge before sign-off | Verify (process) |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| — | — | Learning-Extract W4 empty (`human_fix_detected: false`); no post-live-verify product-code patches |

## Contracts produced by this wave

(REQUIRED — final eng wave; documents closure surface for ops / future INIT consumers and PM-deferred follow-on.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Initiative closure Enter-at | `src/api/v1/initiatives_routes` + `ClosureStartService` | `POST /api/v1/initiatives/closure/start` | programme token; body: org, repo, initiative_id, epic_ticket_id, wave_ticket_ids[], branch_slug, base_branch, runner, model_id, absolute workspace path | 202 + `{run_id}` | Malformed → 4xx; concurrent active run → 409; enqueue only after gates pass | N/A — final eng wave; PM Enter-at deferred |
| Closure Done-gate | `src/business_services/closure_done_gate` | `assert_closure_done_gate(board_service, org, repo, wave_ticket_ids)` | list of numeric wave ticket ids | void or 422 with `not_done_ticket_ids` | Every wave ticket column must be Done; 0 enqueue on fail; EPIC not updated on fail | N/A |
| EPIC Done before purge walk | `ClosureStartService.start_closure` | service method after gate | validated `ClosureStartRequest` | job enqueued at pin `CLOSURE_START_NODE` | EPIC board column set Done before orchestrator walk; failure before enqueue surfaces 503 | N/A |
| Closure purge walk (eng only) | `src/business_services/run_orchestrator` | `process_job` with `lane=closure` payload | job payload with initiative_id, branch_slug, workspace bind | STOP at `initiative-closure-signoff-app`; timeline through purge-app + closure PR action | Never dispatch `purge-initiative-artifacts-meta` or meta closure nodes; meta forbidden set enforced | N/A — PM meta purge out of scope |
| Partial closure failure hygiene | `RunOrchestrator._partial_closure_failure_payload` | forge failure handler on closure lane | job payload + failed stage context | run payload flags: `partial_closure_failure: true`, `closure_complete_claim: false` | After EPIC Done, downstream forge failure must not claim closure complete (REQ-20) | N/A |
| Live verify closure slice | `tests/verify/verify_closure.py` | module `main` | programme token; optional `features.initiative_closure` knobs | exit 0 under prereqs | Smoke always runs auth/validation; happy 202 requires enabled knobs + board fixtures | Human optional at signoff |
| Feature-readiness freeze | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md` | review artifact | — | proven vs deferred eng capabilities table | REQ-18 SSOT for initiative exit; PM/ops items explicitly deferred | Post-initiative ops |

## Exact-head human sign-off package

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human reviews the **exact wave head**, records approval, and merges manually at `wave-signoff`.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/152 @ `64f34e7d3921857bbb626f804223f5460e97686f` — **expected reviewed head SHA**
- Pass-1 product tip: `fac3058ec1caa580eb6ef9e4384d0de22860e00c`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W4.md`
- Live evidence path: `docs/specification/reports/Live-Verify-INIT-GATEFLOW-010-W4.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-010-W4.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-010-W4.md`
- Feature-readiness path: `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md`
- As-built row: INIT-GATEFLOW-010 W4 → **pending human_approved**
- Required checkpoint evidence fields (human fills at `wave-signoff`; not `handoff.forge`): `reviewed_head_sha`, `merge_commit_sha`
- Optional Pass-2 dogfood: `.venv/bin/python -m tests.verify.verify_closure` with `features.initiative_closure.enabled: true`

### Human sign-off / merge checklist

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for initiative exit
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Mark as-built: INIT-GATEFLOW-010 W4 = human_approved (human only)
- [ ] Merge the wave PR manually (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for human checkpoint?

**yes** — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete; exact-head sign-off package ready; next hop is `wave-done-action` (board Done) then `wave-signoff` (human merge).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W4.md
    digest: sha256:f0f6f91c420b160dd2fa40c539b2e1bbd0648d9a55b67e83702e16b37107be3f
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    wave: W4
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/142"
    ticket_id: "142"
    pr_number: 152
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/152"
    pass1_tip_sha: "fac3058ec1caa580eb6ef9e4384d0de22860e00c"
    tip_sha: "64f34e7d3921857bbb626f804223f5460e97686f"
    reviewed_head_sha_expected: "64f34e7d3921857bbb626f804223f5460e97686f"
    human_approved: false
    human_fix_detected: false
    contracts_produced: 7
    assigned_reqs:
      - REQ-12
      - REQ-13
      - REQ-14
      - REQ-15
      - REQ-17
      - REQ-18
      - REQ-20
    learning_item_count: 0
    live_verify_run_id: "6f14f48f-0afb-46ca-a880-c34fa6245648"
    verify_command: ".venv/bin/python -m tests.verify.verify_implement_lane"
    closure_verify_command: ".venv/bin/python -m tests.verify.verify_closure"
    gf_open_blocking: 0
    unit_test_count: 266
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "142"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-010-w4-implement-lane
    paths:
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W4.md
      - docs/specification/as-built/implementation-status.md
```
