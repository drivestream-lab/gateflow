# Ground report — INIT-GATEFLOW-008 W2

| Field | Value |
|-------|-------|
| Wave | W2 — WorkManifest prayog/v1 + docs |
| Spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Date | 2026-07-31 |
| Wave head (exact) | `feature/INIT-GATEFLOW-008-w2-workmanifest` @ `e274a5334b63fce9bbf33443582426f31228a3e6` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/99 — read-only context |
| Board | https://github.com/drivestream-lab/gateflow/issues/95 |
| Status | **human_approved** (2026-07-31) |
| Review deadline | 2026-08-04 |
| Deciders | Tech lead / reviewer — human merge at wave-signoff |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified against tip + unit + human live-verify; no Blocking GF-*; Contracts produced ready for INIT-007 dogfood |
| Assigned REQs | REQ-13, REQ-14, REQ-15, REQ-16, REQ-17 — from WorkManifest TASK-W2-01…04 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **194 passed** at tip (re-run 2026-07-31 during ground) |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below |
| Live | `Live-Verify-INIT-GATEFLOW-008-W2.md` | Human confirmed `.venv/bin/python -m tests.verify.verify_board` pass @ `e274a53` |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time:

- `make test` → **194 passed**
- Tip SHA `e274a53` = sole commit on wave head vs `origin/develop` (`e83dc20`)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-13 | Pin WorkManifest validator before board create; only `prayog/v1` | `run_workmanifest_contract`; `execute_create_board_tickets`; unit reject launchpad + pass prayog; `verify_board` launchpad assert | **pass** |
| REQ-14 | BoardService projects; board not second SSOT | projection after contract pass; `parse_work_manifest_from_plan` DTO; create path does not mutate approved intent | **pass** |
| REQ-15 | Board create remains `authorization: explicit` | pin `board-tickets-action`; `test_board_tickets_action_remains_explicit_authorize_stop` | **pass** |
| REQ-16 | As-built + feature map (W2 slice) | as-built W2 matrix; `tests/README.md` WorkManifest row; Pass-1 edges retained | **pass** |
| REQ-17 | Ordering vs INIT-007 dogfood | `docs/specification/README.md` + as-built: prove 007 first after 008 on `develop` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Pin validator SSOT (no Gateflow reimplementation of identity) | ADR-009 / TDD §3.5 | **pass** — subprocess pin script |
| Fail closed on bad apiVersion | `fail-fast.mdc` | **pass** — ValidationError before BoardService |
| Board remains explicit | ADR-009 dual mode | **pass** — STOP + authorize |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns authorize path; live owns pin reject + board APIs |
| Models at parse boundary | `pydantic-schemas.mdc` | **pass** — projection DTO after contract |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| EA policy: board stays explicit STOP | Ground-Report W1 | **yes** |
| Shared `apply_external_action` / authorize reuses apply | Ground-Report W1 | **yes** — board seed via authorize |
| Automated wave-pr not regressed | Ground-Report W1 | **yes** — W2 did not change walker apply |
| Job-start ensure_branch-only | Ground-Report W1 | **yes** |
| W1 human_approved on `develop` | as-built / merge #98 | **yes** — base `e83dc20` |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | — | Learning-Extract reports `items: []`, `human_fix_detected: false` — no L-* to cite |

## Contracts produced by this wave

(REQUIRED — handoff for INIT-007 dogfood / next programme; INIT-008 has no W3.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Pin WorkManifest contract | `src/models/work_manifest_models` | `run_workmanifest_contract` | workspace + plan file | pass or ValueError | script under `prayog-skills/scripts/`; nonzero → fail closed | INIT-007 / any board seed |
| Board create gate | `forge_action_service.execute_create_board_tickets` | authorize path | effective forge + workspace | BoardTicketsSeedResult | contract **before** BoardService; prayog/v1 only | INIT-007 must not bypass |
| Projection DTO | `parse_work_manifest_from_plan` | plan markdown | WorkManifestDocument | initiative/epic/work | used only after contract pass; board bodies not SSOT | board tooling |
| Explicit board authorize | pin + `PolicyEngine` | `board-tickets-action` | EA + auth=explicit | STOP + authorize | never APPLY_FORGE for board | INIT-007 closeout must honor |
| Live board verify posture | `tests/verify/verify_board` | live command | API + token (+ forge optional) | exit 0; launchpad reject | documents authorize unit ownership | 007 may reuse |
| Programme sequencing | as-built + `docs/specification/README.md` | docs | — | 007 dogfood first after 008 on develop | REQ-17 | INIT-007 Pass-1 |

## Exact-head human sign-off package

> Ground Report and as-built updates written **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human reviews the **exact wave head**, records approval, and merges manually at `wave-signoff`.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/99 @ `e274a5334b63fce9bbf33443582426f31228a3e6` — **expected reviewed head SHA** (publish closeout docs onto tip before merge so reviewed SHA advances)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W2.md`
- Live evidence path: `docs/specification/reports/Live-Verify-INIT-GATEFLOW-008-W2.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-008-W2.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-008-W2.md`
- As-built row: INIT-008 W2 → **human_approved** (2026-07-31; human gate)
- Checkpoint evidence: `reviewed_head_sha` = `e274a5334b63fce9bbf33443582426f31228a3e6`; `merge_commit_sha` = *(fill after human merge of [#99](https://github.com/drivestream-lab/gateflow/pull/99))*

### Human sign-off / merge checklist

- [x] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [x] Review §Contracts produced — accurate and complete for next programme
- [x] Confirm reviewed head SHA matches the package above (Pass-1 tip; republish closeout docs before merge)
- [x] Mark as-built: INIT-GATEFLOW-008 W2 = human_approved (human only)
- [ ] Merge the wave PR manually (human only) — record merge commit SHA
- [x] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for human checkpoint?

**human_approved** — G1–G10 satisfied; as-built marked. Publish closeout via `/commit-workspace`, then merge [#99](https://github.com/drivestream-lab/gateflow/pull/99) and record `merge_commit_sha`.

## Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | **PASS** — W2 assigned REQs only |
| G2 Ground / evidence | **PASS** — ground_command N/A; manual + `make test` + Live-Verify cited |
| G3 Assigned-REQ coverage | **PASS** — all TASK-W2 implements covered |
| G4 Acceptance evidence | **PASS** — Wave-Execution + unit + Live-Verify |
| G5 ADR boundaries | **PASS** — ADR-009 dual mode; board explicit |
| G6 MDC boundaries | **PASS** — fail-fast / testing / schemas |
| G7 Contracts consumed / produced | **PASS** — section complete for INIT-007 |
| G8 Learning citations | **PASS** — empty extract cited |
| G9 GF-* findings | **PASS** — none open |
| G10 Complete handoff | **PASS** — report + as-built human_approved + envelope; no commit/merge by this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W2.md
  blockers: []
  signals:
    wave: W2
    initiative: INIT-GATEFLOW-008
    pr_number: 99
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/99"
    reviewed_head_sha_expected: "e274a5334b63fce9bbf33443582426f31228a3e6"
    contracts_produced: 6
    assigned_reqs:
      - REQ-13
      - REQ-14
      - REQ-15
      - REQ-16
      - REQ-17
    learning_item_count: 0
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
  forge:
    recommend: commit_workspace
    head_ref: feature/INIT-GATEFLOW-008-w2-workmanifest
    base_ref: develop
```
