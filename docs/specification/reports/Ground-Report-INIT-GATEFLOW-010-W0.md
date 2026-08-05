# Ground report — INIT-GATEFLOW-010 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Pin parse parity + purpose/owner on stops |
| Spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Initiative | INIT-GATEFLOW-010 |
| Date | 2026-08-05 |
| Wave head (exact) | `develop` @ `0ca237631e5d5722af98e471ed2caf6409b40f32` — merge of [#144](https://github.com/drivestream-lab/gateflow/pull/144) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/144 — **MERGED** (Pass-2 backfill after merge) |
| Board | https://github.com/drivestream-lab/gateflow/issues/138 |
| Status | Draft (backfill closeout) |
| Review deadline | 2026-08-07 |
| Deciders | Tech lead / reviewer — closeout docs LGTM on chore backfill PR |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified on merged tip; Live-Verify skipped (P15 N/A); Contracts produced for W1; no Blocking GF-* |
| Assigned REQs | REQ-01, REQ-02, REQ-10 — from WorkManifest TASK-W0-01…05 `implements` |
| Mode | **backfill** — learning + ground after premature `wave-signoff` merge |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W0 | **237 passed** at Pass-1; re-proof 2026-08-05: `test_forge_policy` + `test_run_orchestrator` → **32 passed** |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/unit/` scan | Entry points and tests mapped below |
| Live | `Live-Verify-INIT-GATEFLOW-010-W0.md` | Outcome **skipped** (P15 N/A); human_approved true |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-05):

- `git -C prayog-skills rev-parse --short HEAD` = `6561c7c`
- `git -C prayog-skills describe --exact-match --tags HEAD` = `v0.5.0-rc.2` (matches `.harness-pin.yaml`)
- `.venv/bin/pytest tests/unit/test_forge_policy.py tests/unit/test_run_orchestrator.py -q` → 32 passed
- Merged head: `0ca2376` (PR #144)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Harness pin ref ≡ submodule tip | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2`; tip `6561c7c`; as-built remount note | **pass** |
| REQ-02 | Parse `update_board_status` + status + ticket requires; 0 BROKEN remounted nodes | `parse_node_forge` / `WorkflowEngine.get_node`; `test_forge_policy` board-status matrix + fail-closed invalid status | **pass** |
| REQ-10 | Optional pin `purpose`/`owner` on resolved node; emit on `run_stopped` | `ResolvedWorkflowNode.purpose`/`owner`; `WorkflowEngine._to_resolved`; `RunOrchestrator._finalize_run`; `test_pin_human_checkpoint_carries_purpose_and_owner`; `test_walker_continues_then_stops_at_gate` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Fail-closed forge parse | `fail-fast.mdc` / ADR-009 | **pass** — invalid board-status fails closed in unit |
| Models in `src/models/`; parse in business service | `architecture.mdc`, `pydantic-schemas.mdc` | **pass** |
| Strong typing optional pin fields | `strong-typing.mdc` | **pass** — Optional[str]; absent → None |
| No APPLY_FORGE board-status in W0 | plan Q-3 / REQ-03 deferred W1 | **pass** — parse-only this wave |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — P15 N/A; unit owns W0 |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Pin tip `v0.5.0-rc.2` with board-status forge nodes | remounted `prayog-skills` / Pre-Implement W0 | **yes** |
| `ResolvedWorkflowNode` + forge policy from prior INITs | as-built INIT-008/006; existing engine | **yes** — extended with purpose/owner |
| W0 first wave — no prior INIT-010 Ground Report | Pre-Implement | **yes** — N/A prior INIT-010 contracts |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| GF-01 | — | Wave PR #144 merged before Pass-2 Learning/Ground existed; remediated by this backfill chore | Should fix (process) — not product blocking |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| L-01 | SKILL | Documents premature merge; ground proceeds as backfill; W1 pre-implement must read §Contracts produced from this report |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` W1.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Optional pin purpose/owner on resolved node | `src/models/handoff_models` | `ResolvedWorkflowNode.purpose` / `.owner` | pin node optional string fields | optional strings or null | absent → null; present → string | W1 board-status apply / walker stops |
| Purpose/owner parse | `src/business_services/workflow_engine` | `WorkflowEngine._to_resolved` / `get_node` | pin node mapping | `ResolvedWorkflowNode` | no fail when purpose/owner omitted | W1 must not require fields |
| `run_stopped` payload enrichment | `src/business_services/run_orchestrator` | `_finalize_run` | resolved stop node | timeline `run_stopped` payload may include `purpose`/`owner` | emit only when non-null on stop node | W1 closeout / board-status consumers |
| Board-status forge **parse** (not apply) | forge policy + engine | `parse_node_forge` / `get_node` | pin EA with `update_board_status` | action/status/requires ticket | invalid status fail-closed; 0 BROKEN remounted | W1 APPLY_FORGE apply (REQ-03) |
| Harness pin ≡ tip | `.harness-pin.yaml` + submodule | inspect / describe | pin ref `v0.5.0-rc.2` | tip SHA `6561c7c` | exact-match tag | W1 remount if pin moves |

## Exact-head human sign-off package

> Ground Report and as-built updates written **locally** then published via chore backfill PR. Wave feature PR already merged — this package records post-merge closeout.

- Merged wave head: https://github.com/drivestream-lab/gateflow/pull/144 @ `0ca237631e5d5722af98e471ed2caf6409b40f32` — **merge commit SHA**
- Reviewed feature tip before merge: `5353987fcf5f96c44b82ac92d1e9eaef24dc20c2`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W0.md`
- Live evidence path: `docs/specification/reports/Live-Verify-INIT-GATEFLOW-010-W0.md` (skipped / P15 N/A)
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-010-W0.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-010-W0.md`
- As-built row: INIT-GATEFLOW-010 W0 → **human_approved** (merge already on `develop`; backfill marks SSOT)
- Checkpoint evidence: `reviewed_head_sha` = `5353987…`; `merge_commit_sha` = `0ca2376…`

### Human sign-off / merge checklist

- [x] Review REQ checklist — all wave-assigned REQs pass
- [x] Review §Contracts produced — ready for W1 `/pre-implement`
- [x] Confirm merge commit SHA recorded (`0ca2376`)
- [x] Mark as-built: INIT-GATEFLOW-010 W0 = human_approved (backfill after merge)
- [x] Wave PR already merged (human) — no second wave-signoff merge
- [ ] Merge **chore** backfill PR to `develop` (docs only)
- [ ] Do not ask Gateflow/Forge to auto-merge; no `*-lgtm` from this skill

## Ready for human checkpoint?

**yes (backfill)** — G1–G10 satisfied for product grounding; GF-01 process note only; publish Learning + Ground + as-built via chore PR; next programme hop for W0 closeout board Done is `wave-done-action` (if still open), then W1 `/pre-implement`.

## Checks G1–G10

| ID | Result |
|----|--------|
| G1 | **pass** — W0 only; REQ-01/02/10 |
| G2 | **pass** — ground_command SKIPPED; unit + Live-Verify cited separately |
| G3 | **pass** — all assigned REQs in checklist |
| G4 | **pass** — Wave-Execution + Live-Verify + unit re-proof |
| G5 | **pass** — ADR-009; no contradiction |
| G6 | **pass** — fail-fast / pydantic / testing-verify |
| G7 | **pass** — contracts consumed match; §Contracts produced complete |
| G8 | **pass** — L-01 cited |
| G9 | **pass** — GF-01 process Should-fix only |
| G10 | **pass** — handoff below; as-built updated; no merge by this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-010-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    wave: W0
    contracts_produced: 5
    assigned_reqs: [REQ-01, REQ-02, REQ-10]
    backfill: true
    merge_commit_sha: "0ca237631e5d5722af98e471ed2caf6409b40f32"
    reviewed_head_sha: "5353987fcf5f96c44b82ac92d1e9eaef24dc20c2"
    gf_open_blocking: 0
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "138"
    status: Done
```
