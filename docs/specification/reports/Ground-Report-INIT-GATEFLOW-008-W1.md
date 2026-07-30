# Ground report — INIT-GATEFLOW-008 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Automated forge apply + retire PR-at-start |
| Spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Date | 2026-07-30 |
| Wave head (exact) | `feature/INIT-GATEFLOW-008-w1-automated-forge` @ `bc1900800653b1d7e6f39a42a3603c6bb9096fe0` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/98 — read-only context |
| Board | https://github.com/drivestream-lab/gateflow/issues/94 |
| Status | **human_approved** (2026-07-30) |
| Review deadline | 2026-08-03 |
| Deciders | Tech lead / reviewer — explicit LGTM required (human merge at wave-signoff) |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified against tip + unit + human live-verify; no Blocking GF-*; Contracts produced ready for W2 `/pre-implement` |
| Assigned REQs | REQ-5, REQ-6, REQ-7, REQ-8, REQ-9, REQ-10, REQ-11, REQ-12, REQ-16 — from WorkManifest TASK-W1-01…05 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **191 passed** at tip (re-run 2026-07-30 during ground); policy/orchestrator/forge tests green |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points and tests mapped below |
| Live | `Live-Verify-INIT-GATEFLOW-008-W1.md` | Human confirmed `.venv/bin/python -m tests.verify.verify_implement_lane` pass @ `bc19008` |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time:

- `make test` → **191 passed**
- Tip SHA `bc19008` = sole commit on wave head vs `origin/develop` (`64db0ee`)
- CI on PR [#98](https://github.com/drivestream-lab/gateflow/pull/98): `ci` SUCCESS

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-5 | Required `commit_workspace` on pre-implement / loop-spec via ForgeClient | Pin `workflow.yaml` forge slots; orchestrator `_publish_stage_workspace_if_needed` + W1 walker after coding hops; Wave-Execution forge readiness | **pass** |
| REQ-6 | Do not treat all external-action as STOP | `PolicyEngine._decision_for_external_action`; `PolicyDecisionType.APPLY_FORGE`; `test_trigger_policy` automated path | **pass** |
| REQ-7 | `explicit` → STOP + authorize path retained | Policy STOP for `AuthorizationModeType.EXPLICIT`; `ForgeActionService.authorize` reuses `apply_external_action` | **pass** |
| REQ-8 | `automated` → apply without authorize when requires complete | `run_orchestrator._apply_automated_forge`; walker does not call authorize for automated; unit walker test | **pass** |
| REQ-9 | `head_ref` / `base_ref` from run context when required | `forge_models` slots; apply merges run-context head/base; `_ensure_run_branch` / `_require_run_head_branch` | **pass** |
| REQ-10 | Retire PR-at-start create; ensure_branch-only | `_ensure_run_branch`; `test_ensure_branch_before_stage_*` asserts no `create_or_update_pull_request` at start | **pass** |
| REQ-11 | Pass-1: pre-implement → loop-spec → wave-pr-action → live-verify | Unit multi-hop walker; pin `resolve_next`; live `verify_implement_lane` (human pass) | **pass** |
| REQ-12 | Automated `spec-pr-action` same apply rules | Shared `apply_external_action` + policy `APPLY_FORGE` for any EA with `authorization=automated` (pin matrix includes `spec-pr-action`) | **pass** |
| REQ-16 | As-built + tests/README feature map (W1 slice) | as-built INIT-008 row; `tests/README.md` Pass-1 / PR-at-start superseded note | **pass** (W1 slice; W2 completes remaining docs) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Dual authorization modes | ADR-009 | **pass** — explicit STOP; automated APPLY_FORGE |
| No invent forge labels / action | ADR-009 / forge-side-effects | **pass** — pin ⋉ handoff merge; shared apply |
| Models in `src/models/`; services in business layer | `architecture.mdc`, `pydantic-schemas.mdc` | **pass** |
| Fail closed incomplete requires | `fail-fast.mdc` | **pass** — ValidationError on incomplete forge |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns logic; live owns implement-lane timing |
| No merge / `*-lgtm` from forge | ADR-009 | **pass** — open_draft_pr only |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| `AuthorizationModeType` + resolved node auth | Ground-Report W0 | **yes** — policy branches on carried auth |
| Fail-closed EA parse | Ground-Report W0 | **yes** — missing auth → BLOCK |
| Day-one pin matrix (`wave-pr-action` automated) | Ground-Report W0 / pin | **yes** |
| Pass-1 resolve `loop-spec`/`pass` → `wave-pr-action` | Ground-Report W0 | **yes** — walker applies then STOP `live-verify` |
| W0 human_approved on `develop` | as-built / Pre-Implement W1 | **yes** — base `64db0ee` |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | — | Learning-Extract reports `items: []`, `human_fix_detected: false` — no L-* to cite |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` W2.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| EA policy branch | `src/business_services/policy_engine` | `_decision_for_external_action` | resolved EA + auth enum | STOP (explicit) / APPLY_FORGE (automated) / BLOCK (missing) | never STOP-all-EA; authorize path only for explicit | W2 board remains explicit |
| Shared forge apply | `src/business_services/forge_action_service` | `apply_external_action` | pin node + handoff forge + optional head/base | apply result (e.g. pr_number) or ValidationError | pin wins policy; incomplete requires fail closed; authorize reuses apply | W2 board create via same apply after authorize |
| Automated walker apply | `src/business_services/run_orchestrator` | `_apply_automated_forge` after APPLY_FORGE | run + workspace + EA node | updates `pr_number`; synthetic handoff stage=EA outcome=pass; re-resolve | no `/forge/authorize`; then STOP at next human-checkpoint | W2 must not regress automated open_draft_pr |
| Job-start branch only | `run_orchestrator._ensure_run_branch` | process_job start | initiative/wave/slug/base | branch ensured; `pr_number` may stay null | no Draft PR create at start | W2 verify scripts must not assume PR-at-start |
| Forge head/base slots | `src/models/forge_models` | merge / open_draft_pr readiness | head_ref, base_ref strings | filled from run context when required | wave-pr requires both | W2 board may omit PR slots |
| Pass-1 live timing | `tests/verify/verify_implement_lane` + `tests/README.md` | live command | running API + worker prereqs | exit 0 asserts ensure-branch / PR-after-wave-pr | feature map documents superseded PR-at-start | W2 extends verify_board |

## Exact-head human sign-off package

> Ground Report and as-built updates written **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human reviews the **exact wave head**, records approval, and merges manually at `wave-signoff`.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/98 @ `bc1900800653b1d7e6f39a42a3603c6bb9096fe0` — **expected reviewed head SHA** (publish closeout docs onto tip before merge so reviewed SHA advances)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W1.md`
- Live evidence path: `docs/specification/reports/Live-Verify-INIT-GATEFLOW-008-W1.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-008-W1.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-008-W1.md`
- As-built row: INIT-008 W1 → **human_approved** (2026-07-30; human gate)
- Checkpoint evidence: `reviewed_head_sha` = `bc1900800653b1d7e6f39a42a3603c6bb9096fe0`; `merge_commit_sha` = *(fill after human merge of [#98](https://github.com/drivestream-lab/gateflow/pull/98))*

### Human sign-off / merge checklist

- [x] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [x] Review §Contracts produced — accurate and complete for next wave
- [x] Confirm reviewed head SHA matches the package above (Pass-1 tip; republish closeout docs before merge)
- [x] Mark as-built: INIT-GATEFLOW-008 W1 = human_approved (human only)
- [ ] Merge the wave PR manually (human only) — record merge commit SHA
- [x] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for human checkpoint?

**human_approved** — G1–G10 satisfied; as-built marked. Publish closeout via `/commit-workspace`, then merge [#98](https://github.com/drivestream-lab/gateflow/pull/98) and record `merge_commit_sha`.

## Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | **PASS** — W1 assigned REQs only (not W2 REQ-13…17) |
| G2 Ground / evidence | **PASS** — ground_command N/A; manual + `make test` + Live-Verify cited |
| G3 Assigned-REQ coverage | **PASS** — all TASK-W1 implements covered |
| G4 Acceptance evidence | **PASS** — Wave-Execution + unit + Live-Verify |
| G5 ADR boundaries | **PASS** — ADR-009 dual mode |
| G6 MDC boundaries | **PASS** — fail-fast / architecture / testing |
| G7 Contracts consumed / produced | **PASS** — section complete for W2 |
| G8 Learning citations | **PASS** — empty extract cited |
| G9 GF-* findings | **PASS** — none open |
| G10 Complete handoff | **PASS** — report + as-built pending + envelope below; no commit/merge by this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W1.md
  blockers: []
  signals:
    wave: W1
    initiative: INIT-GATEFLOW-008
    pr_number: 98
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/98"
    reviewed_head_sha_expected: "bc1900800653b1d7e6f39a42a3603c6bb9096fe0"
    contracts_produced: 6
    assigned_reqs:
      - REQ-5
      - REQ-6
      - REQ-7
      - REQ-8
      - REQ-9
      - REQ-10
      - REQ-11
      - REQ-12
      - REQ-16
    learning_item_count: 0
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
  forge:
    # Pin ground-spec commit_workspace: required — publish closeout onto wave head
    recommend: commit_workspace
    head_ref: feature/INIT-GATEFLOW-008-w1-automated-forge
    base_ref: develop
```
