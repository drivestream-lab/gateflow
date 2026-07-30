# Feasibility report — INIT-GATEFLOW-008

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| Spec digest | `sha256:044c330b5ca539cedc0cf4e878e1670e62226ae4858d34ca2f759cf7f7986b7d` |
| PRD digest | TBD — **missing** (no meta PRD) |
| Impact map / revision | TBD — **missing** (no `Impact-Map-INIT-GATEFLOW-008.md`) |
| Repo scope digest | TBD |
| Approved meta PR head | TBD |
| Impact-map approval | TBD |
| Source freshness | **STALE** — Gate 1 handoff fields all TBD; no canonical PRD/map/APPROVED head to match |
| Prior stage | `/spec-draft` outcome was `needs-input` (Q-1 / D1) — feasibility run is **out of happy-path order** but executed per user request |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-30 |
| Branch | `chore/INIT-GATEFLOW-008-spec-gateflow` (local; no Forge publish from this skill) |
| Initiative segment | `INIT-GATEFLOW-008` |
| Status | Draft |
| Review deadline | 2026-08-02 |
| Deciders | PM: PE/programme · Domain SME: N/A (pin consume) |

## Summary

INIT-GATEFLOW-008 is **buildable in this repo** once Gate 1 freshness is fixed and
**ADR-009 is amended**: the pin tip already defines `authorization` +
`wave-pr-action`, and Gateflow already has ForgeClient publish, authorize,
WorkManifest parse, and PR-at-start to retire. It is **not** merge-ready or
implementation-plan-ready today because (1) approved handoff is **STALE/missing**,
and (2) Accepted ADR-009 still requires **explicit** authorize for all
external-action mutates — a **Critical** conflict with REQ-4/REQ-8.

**Findings:** 6 total (2 Critical, 2 Should fix, 1 Verify, 1 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 1 | 0 | 0 |
| PE / ADR | 2 | 2 | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 1 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 2 |
| Should fix | 2 |
| Verify / Gap (informational) | 2 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `stale` |
| Rationale | First matching rubric row: PRD digest / impact-map / approved meta head / scope digest are TBD — source freshness STALE vs required CURRENT handoff |
| Next (from workflow) | `spec-draft` |

After freshness is restored (PE Gate 1 waive written into header **or** meta
PRD+map+APPROVED), re-run `/spec-draft` then `/initiative-feasibility`. Expect
outcome **`findings`** (not `pass`) until ADR-009 amend lands via
`/spec-technical-review` (FF-01).

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — forge policy, forge client, forge action, orchestrator publish, workspace paths, PR naming | `make test` layout; `test_forge_*`, `test_run_orchestrator`, `test_workspace_commit_paths` |
| Live verify | `verify_implement_lane`, `verify_pr_thread` (PR-at-start), no automated wave-pr assert | `tests/README.md` |
| As-built | 006 forge unit-complete; 008 draft not started; 007 dogfood parked | `implementation-status.md` |
| Pin submodule | Tip `355f403` has `authorization` + `wave-pr-action`; harness pin still `v0.5.0-rc.2` | `.harness-pin.yaml`; `prayog-skills/workflow.yaml` |
| WorkManifest pin assets | Contract + validator present in submodule | `prayog-skills/references/workmanifest-contract.md`, `scripts/workmanifest_contract.py` |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-1 / W0 | Remount; harness pin == submodule | `.harness-pin.yaml` ref `v0.5.0-rc.2` vs submodule `355f403` | — | — | **drift** |
| REQ-2–3 / W0 | Parse/carry `authorization` | `workflow_engine._to_resolved` only `parse_node_forge`; no authorization field on `ResolvedWorkflowNode` | `test_forge_policy` (no auth enum) | — | **gap** |
| REQ-4 / W0 | Amend ADR-009 dual mode | `adr-009` still “explicit authorization” for all EA mutates | — | — | **conflict** (ADR) |
| REQ-5 / W1 | required commit_workspace | `_publish_stage_workspace_if_needed` + #89 dirty∪ahead | `test_publish_stage_workspace_*` | implement_lane stage_commit | **partial** (exists; pin modes need remount) |
| REQ-6–8 / W1 | Branch STOP vs automated apply | `policy_engine._STOP_NODE_TYPES` includes all `external-action`; no automated apply in orchestrator | policy / walker tests assume STOP | — | **gap** |
| REQ-7 / W1 | explicit authorize retain | `ForgeActionService.authorize_and_execute`; `POST …/forge/authorize` | `test_forge_action_service` | — | **exists** |
| REQ-9 / W1 | head_ref/base_ref from run context | Authorize request has `head`/`base`; merge slots lack head_ref/base_ref; publish uses `build_wave_head_branch` | forge merge tests | — | **partial** |
| REQ-10 / W1 | Retire PR-at-start | `run_orchestrator._ensure_run_pr` always before stages | `test_pr_opened_before_stage_*` | `verify_pr_thread` | **drift** (opposite of target) |
| REQ-11 / W1 | Pass-1 edges via wave-pr | Pin has edges; Gateflow tests still `loop-spec`→`live-verify` | `test_loop_spec_pass_stops_at_live_verify` | README Pass-1 chain | **drift** vs remounted pin |
| REQ-12 / W1 | automated spec-pr | Same as REQ-8; spec-pr-action automated on pin | — | — | **gap** |
| REQ-13–15 / W2 | prayog/v1 + pin validator | `work_manifest_models.py` docstring “launchpad”; no call to pin `workmanifest_contract.py` | forge board tests | — | **gap** |
| REQ-16–17 / W2 | docs + 007 ordering | README/as-built already point at 008 blocking 007 | — | — | **partial** (docs started) |

## ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-009 | pin forge publish/mutate, authorize | **Accepted** — **conflicts** with automated EA |
| ADR-010 | lane intake | Accepted — aligned (no change required for 008 core) |
| ADR-003 | ForgeClient infra | Accepted — aligned |
| ADR-005 | programme token | Accepted — authorize path retain |
| ADR-001 | Postgres | Accepted — N/A for 008 core |

## MDC pass (pre-T2)

| MDC | Domain | Read / skipped |
|-----|--------|----------------|
| `architecture.mdc` | layering, Forge in infra | read |
| `fail-fast.mdc` | missing authorization fail closed | read |
| `spec-driven-development.mdc` | same-PR as-built | read |
| `testing-verify-flows.mdc` | unit vs verify | read |
| `dependency-injection.mdc` | services | skipped (no DI redesign) |
| `database-migrations.mdc` | — | skipped (no DDL in 008) |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-4, REQ-8 | ADR-009 | **conflict** | FF-01 Critical |
| REQ-5, publish | ADR-009 | aligned | — |
| REQ-7 authorize | ADR-009 / ADR-005 | aligned for **explicit** | — |
| REQ-10 PR-at-start | ADR-009 / FR-19 as-built | product change; ADR allows run-context head — PR create timing is INIT | FF-03 Should fix (design in TDD) |
| REQ-13 WorkManifest | NEW-ADR? / pin contract | pin SSOT sufficient; no NEW-ADR if validator is pin script only | FF-04 Verify |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F13 | REQ-4/REQ-8 automated Forge without interactive STOP | ADR-009 §Recommendation 2 + Consequences (“require the explicit authorization path”) | **Critical conflict** — amend or supersede before implement |
| FF-02 | F1/F5/F10 | Harness pin must match submodule | `.harness-pin.yaml` vs `prayog-skills` HEAD | **Critical** remount drift for REQ-1 claim |
| FF-03 | F14/F5 | Retire PR-at-start | `run_orchestrator._ensure_run_pr`; tests assert PR before stage | Should-fix — TDD must specify ensure_branch-only vs delete path |
| FF-04 | F9/F2 | Pin WorkManifest validator | Gateflow-local parse; pin `scripts/workmanifest_contract.py` unused | Should-fix — wire pin validator; reject launchpad/v1 |
| FF-05 | F3 | Pass-1 verify map | `tests/README` still `pre-implement→loop-spec→live-verify` | Verify — update after remount |
| FF-06 | F7 | overlap | unit owns algorithm; live via 007 (REQ-17) | Gap — acceptable; document in plan |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F13 | Spec REQ-4/8 contradict Accepted ADR-009 (all EA mutates need explicit authorize). Implementation without ADR amend is unconstitutional under SDD. | Spec REQ-4; `adr-009-…md` lines on explicit authorization; pin `authorization: automated` |
| FF-02 | F1/F5 | Cannot claim remount (REQ-1) while harness pin `v0.5.0-rc.2` ≠ submodule `355f403`. | `.harness-pin.yaml`; `git submodule status` |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F2/F5 | PR-at-start still creates Draft PR before skills; opposite of REQ-10. | `run_orchestrator._ensure_run_pr`; `verify_pr_thread` |
| FF-04 | F2/F9 | WorkManifest path does not enforce `prayog/v1` or call pin validator. | `work_manifest_models.py` (“launchpad”); no import of `workmanifest_contract.py` |

### Verify / Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-05 | F3 | Feature map / verify docs lag remounted Pass-1 edges. | `tests/README.md` |
| FF-06 | F7/F8 | Live prove deferred to INIT-007 (REQ-17) — OK if plan states CI=unit only for 008. | Spec REQ-17; as-built |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 remount + parse | `.harness-pin.yaml`, submodule; `forge_types.py`, `forge_models.py` / node parse, `workflow_engine.py`, `handoff_models.ResolvedWorkflowNode` | `test_forge_policy`, new auth parse tests |
| W0 ADR | `docs/specification/adr/adr-009-…md` (amend) | inspection |
| W1 algorithm | `policy_engine.py`, `run_orchestrator.py`, `forge_action_service.py` (shared apply) | walker + publish + authorize tests |
| W1 PR-at-start | `run_orchestrator._ensure_run_pr` | `test_run_orchestrator`, `verify_pr_thread` |
| W2 WorkManifest | `work_manifest_models.py`, `forge_action_service.execute_create_board_tickets` | board/manifest unit tests |
| W2 docs | as-built, `tests/README.md` | inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Running feasibility while `/spec-draft` = `needs-input` | Outcome `stale`; return to spec-draft after Q-1 |
| R-2 | Automated open without filled `title`/`body_path` in handoff | Fail closed (REQ-8); skill packages must fill forge slots |
| R-3 | head_ref in pin requires vs authorize `head` field naming | TDD maps run context → requires check |
| A-spec | PE will waive or land Gate 1 | Q-1 / freshness |

## Recommended spec edits

- Record Gate 1 waive **or** fill meta digests in header after PE action (unblocks D1 / freshness).
- Keep REQ-4 as ADR amend mandate; do not soften automated semantics without pin change.
- Optionally split REQ-10 acceptance: “ensure_branch allowed; create_or_update_pull_request forbidden at job start.”
- Note `/spec-draft` must re-pass before treating this feasibility as CURRENT.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| OQ-1 | PM / PE | Gate 1 PRD+Impact-Map+APPROVED **or** explicit waive for 008 catch-up | **yes** | PE | **resolved** — **Gate 1 waived** 2026-07-30 | spec-draft re-run | waived | Spec Q-1; header | Spec Q-1 resolution |
| FF-01 | PE / ADR | Amend ADR-009 for `authorization` dual mode | **yes** | PE | open | technical review | none | ADR-009 vs REQ-4/8 | `/spec-technical-review` |
| FF-02 | PE | Pin harness ref to immutable SHA/tag matching submodule | **yes** | PE | open | W0 / remount | pin `355f403` until tag | harness vs submodule | Spec Q-4 |
| FF-03 | PE | ensure_branch-only vs drop `_ensure_run_pr` entirely | no | PE | open | TDD W1 | ensure_branch yes; no PR create | REQ-10; orchestrator | Spec Q-3 |
| FF-04 | PE | How to invoke pin `workmanifest_contract.py` from Gateflow (subprocess vs port) | no | PE | open | TDD W2 | subprocess pinned script path | pin scripts | TDD |
| FF-05 | auto-fix | Update tests/README Pass-1 chain string after remount | no | eng | open | W2 docs | — | README | later forge publish |

### PM questions

#### Blocking — must resolve before spec merge
1. ~~**OQ-1:** Gate 1~~ — **resolved 2026-07-30: PE waives Gate 1** for 008 pin-consume catch-up.

#### Defer
1. None.

### PE questions

#### Blocking for implementation plan
1. **FF-01:** ADR-009 amend vs ADR-011 — resolve in `/spec-technical-review` before plan.
2. **FF-02:** Exact pin ref string for REQ-1.

#### Defer with default
1. **FF-03:** Default ensure_branch-only before first publish.
2. **FF-04:** Default call pinned validator script from delivery-contract path.

### Domain clarifications

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None | — | — |

### Auto-fixable

| # | Item | Fix |
|---|------|-----|
| AF-1 | README / verify feature-map Pass-1 edge string | Update when pin remounted (FF-05) |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline | PASS (with drift noted) | FF-02 |
| F2 Spec→code | FAIL (gaps) | FF-03, FF-04, auth parse gap |
| F3 Spec→verify | PASS (informational lag) | FF-05 |
| F4 Spec→unit | PASS | areas identifiable |
| F5 As-built drift | FAIL | FF-02, PR-at-start, STOP-all-EA |
| F6 Docs drift | PASS (partial updates started) | FF-05 |
| F7 Overlap | PASS | FF-06 Gap OK |
| F8 CI vs live | PASS | unit CI; live via 007 |
| F9 Cross-service | PASS | pin contracts exist; wiring gap FF-04 |
| F10 Assumptions | FAIL | Gate 1 / pin match unverified |
| F11 Effort drivers | PASS | W0 parse+ADR; W1 orchestrator; W2 validator |
| F12 PM questions | PASS | OQ-1 numbered |
| F13 ADR | FAIL | FF-01 Critical |
| F14 MDC | PASS | fail-fast/SDD aligned with fail-closed auth parse |

**Check PASS (severity-aware):** **FAIL** — unresolved Critical FF-01, FF-02 + freshness STALE.

---

## Next steps

1. ~~Resolve **OQ-1**~~ — **done** (Gate 1 waived 2026-07-30) → re-run **`/spec-draft`** to CURRENT/`pass`.
2. Open/publish Draft spec PR via Forge when `pass` (not this skill).
3. Re-run **`/initiative-feasibility`** on CURRENT handoff → expect **`findings`** (FF-01 ADR).
4. Run **`/spec-technical-review`** to amend ADR-009 and resolve FF-01…FF-04.
5. Only then **`/spec-implementation-plan`** and implement — still **no INIT-007 dogfood** until 008 W0–W1 on `develop`.

**No GitHub side effects from this skill.** Persist report locally; Forge publish later onto spec PR branch.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: stale
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md
    digest: sha256:c9bec0588f7b7b7ddade1f82991d889daad6b3e598a6924824e9eacbd9761d63
  blockers:
    - FF-01
    - FF-02
  signals:
    new_adr: true
    adr_amend: ADR-009
    freshness: STALE_PENDING_SPEC_DRAFT_RERUN
    gate1_waived: true
    gate1_waived_at: "2026-07-30"
    prior_spec_draft_outcome: needs-input
    findings_critical: 2
    findings_should_fix: 2
    brand: 006A
    blocks_init_007_dogfood: true
    ripple_action: re-draft
  next_candidates:
    - spec-draft
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Instance readiness for later Forge publish of this report onto spec branch —
    # not authorized by this skill; pin commit_workspace on this stage is required.
```

> **2026-07-30:** OQ-1 / Gate 1 **waived**. Feasibility outcome `stale` remains until
> `/spec-draft` re-run refreshes CURRENT handoff; then expect `findings` (FF-01).
