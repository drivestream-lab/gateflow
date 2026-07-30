# Ground report — INIT-GATEFLOW-008 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Authorization parse + Pass-1 unit hygiene |
| Spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Date | 2026-07-30 |
| Wave head (exact) | `feature/INIT-GATEFLOW-008-w0-auth-parse` @ `12a0364b8e025e04320898147206d08283bb101e` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/96 — read-only context |
| Board | https://github.com/drivestream-lab/gateflow/issues/93 |
| Status | Draft |
| Review deadline | 2026-08-03 |
| Deciders | Tech lead / reviewer — explicit LGTM required (human merge at wave-signoff) |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified against tip + unit evidence; no Blocking GF-*; Contracts produced ready for W1 `/pre-implement` |
| Assigned REQs | REQ-1, REQ-2, REQ-3, REQ-4, REQ-11 (pin-edge unit slice), REQ-16 (as-built slice) — from WorkManifest TASK-W0-01…05 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **189 passed** at tip (re-run 2026-07-30 during ground); key auth/Pass-1 tests green |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/unit/` scan | Entry points and tests mapped below |
| Live | P15 N/A; human checkpoint | No `Live-Verify-*` artifact required; human confirmed N/A gate after Draft PR |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time:

- `git -C prayog-skills rev-parse HEAD` = `355f403…`
- `git -C prayog-skills rev-parse v0.5.0-rc.2^{commit}` = same SHA (matches `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2`)
- `make test` → 189 passed

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-1 | Harness pin ref ≡ submodule tip; remount recorded | `.harness-pin.yaml` `v0.5.0-rc.2`; tip `355f403`; as-built remount note; pin load resolves `wave-pr-action` | **pass** |
| REQ-2 | Parse EA `authorization` (`explicit`\|`automated`); omit/unknown fail closed | `AuthorizationModeType`; `WorkflowEngine._parse_authorization`; tests omit/unknown + day-one matrix | **pass** |
| REQ-3 | Carry auth on resolved node for policy/orchestrator | `ResolvedWorkflowNode.authorization`; `get_node` / `resolve_next` | **pass** |
| REQ-4 | ADR-009 Accepted with dual-authorization amendment | `docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md` Status **Accepted** + Option D amendment | **pass** |
| REQ-11 | Pass-1 pin edges in unit (full walker W1) | `test_loop_spec_pass_resolves_to_wave_pr_action`; pre-implement commit **required**; walker hygiene documents incomplete forge until W1 | **pass** (W0 slice only — full automated walk deferred W1 per plan) |
| REQ-16 | As-built W0 + INIT-006 REQ-7 superseded for automated | as-built INIT-008 / INIT-006 W2 rows | **pass** (W0 slice; full feature-map / Pass-1 docs continue W1–W2) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Fail closed on invalid pin auth | `fail-fast.mdc` / ADR-009 | **pass** — ValueError on omit/unknown |
| Models in `src/models/`; parse in business service | `architecture.mdc`, `pydantic-schemas.mdc` | **pass** |
| Enum closed vocabulary | `strong-typing.mdc` | **pass** — `AuthorizationModeType` |
| No Forge mutate from content skill | ADR-009 / forge-side-effects | **pass** — W0 parse only |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — P15 N/A; unit owns W0 |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Pin tip with `authorization` on all EA nodes | remounted `prayog-skills` / Pre-Implement W0 | **yes** |
| ADR-009 dual mode Accepted | ADR file + TDD | **yes** |
| Prior INIT-006 forge / ResolvedWorkflowNode + forge policy | as-built INIT-006; existing engine | **yes** — extended with `authorization` field |
| W0 first wave — no prior INIT-008 Ground Report | Pre-Implement | **yes** — N/A prior contracts |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | — | Learning-Extract reports `items: []`, `human_fix_detected: false` — no L-* to cite |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` W1.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Authorization enum | `src/models/forge_types` | `AuthorizationModeType` | wire string `explicit` \| `automated` | enum members | no other values; no default for EA | W1 policy/orchestrator |
| Resolved node auth | `src/models/handoff_models` | `ResolvedWorkflowNode.authorization` | optional enum | enum when EA; null otherwise | required when `node_type=external-action` at parse time | W1 STOP vs apply branch |
| Fail-closed EA parse | `src/business_services/workflow_engine` | `WorkflowEngine.get_node` / `_to_resolved` / `_parse_authorization` | pin node mapping | `ResolvedWorkflowNode` or `ValueError` | omit/unknown → fail; non-EA → auth null | W1 must not bypass |
| Day-one pin matrix | pin `workflow.yaml` via engine | `get_node(<ea-id>)` | node id | `authorization` enum | `wave-pr-action`/`spec-pr-action`=automated; board/prd/merges=explicit | W1 automated apply |
| Pass-1 resolve edge | pin + `WorkflowEngine.resolve_next` | handoff `loop-spec`/`pass` | stage+outcome | next=`wave-pr-action` EA automated | not `live-verify` directly | W1 walker + apply |
| Pre-implement publish policy | pin forge | `get_node("pre-implement").forge.commit_workspace` | — | `required` | matches remounted pin | W1 Pass-1 publish |

## Exact-head human sign-off package

> Ground Report and as-built updates written **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human reviews the **exact wave head**, records approval, and merges manually at `wave-signoff`.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/96 @ `12a0364b8e025e04320898147206d08283bb101e` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W0.md`
- Live evidence path: N/A — P15 N/A (human confirm recorded in Learning-Extract / programme)
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-008-W0.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-008-W0.md`
- As-built row prepared locally: INIT-008 W0 → **pending human_approved** (not marked `human_approved` by this skill)
- Required checkpoint evidence fields (human fills at `wave-signoff`; not `handoff.forge`): `reviewed_head_sha`, `merge_commit_sha`

### Human sign-off / merge checklist

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above (**after** publishing closeout docs to tip if needed)
- [ ] Mark as-built: INIT-GATEFLOW-008 W0 = human_approved (human only)
- [ ] Merge the wave PR manually (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for human checkpoint?

**yes** — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete; exact-head package ready. Publish Ground Report + Learning-Extract + as-built via `/commit-workspace` before merge so tip includes closeout artifacts.

## Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | **PASS** — W0 assigned REQs only |
| G2 Ground / evidence | **PASS** — ground_command N/A; manual + `make test` cited |
| G3 Assigned-REQ coverage | **PASS** — all TASK implements covered |
| G4 Acceptance evidence | **PASS** — Wave-Execution + unit + human N/A confirm |
| G5 ADR boundaries | **PASS** — ADR-009 Accepted dual mode |
| G6 MDC boundaries | **PASS** — fail-fast / models / typing |
| G7 Contracts consumed / produced | **PASS** — section complete |
| G8 Learning citations | **PASS** — empty extract cited |
| G9 GF-* findings | **PASS** — none open |
| G10 Complete handoff | **PASS** — report + as-built pending + envelope below; no commit/merge by this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W0.md
  blockers: []
  signals:
    wave: W0
    initiative: INIT-GATEFLOW-008
    pr_number: 96
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/96"
    reviewed_head_sha_expected: "12a0364b8e025e04320898147206d08283bb101e"
    contracts_produced: 6
    assigned_reqs:
      - REQ-1
      - REQ-2
      - REQ-3
      - REQ-4
      - REQ-11
      - REQ-16
    learning_item_count: 0
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```
