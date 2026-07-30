# Feasibility report — INIT-GATEFLOW-008

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| Spec digest | `sha256:8e4333dcf72dcfdf03288fc64a3b5bf1c98bfc9070393b83ffadb3099d8ba980` |
| PRD digest | **waived** — Gate 1 PE waive (Q-1, 2026-07-30); no meta PRD |
| Impact map / revision | **waived** — no Impact-Map-INIT-GATEFLOW-008 |
| Repo scope digest | **waived** — gateflow-only pin consume |
| Approved meta PR head | **waived** |
| Impact-map approval | **waived** — PE Gate 1 waive recorded in Spec Q-1 |
| Source freshness | **CURRENT** — `/spec-draft` `pass` + Gate 1 waive; Draft spec PR [#91](https://github.com/drivestream-lab/gateflow/pull/91) head `b3cb6c0` carries the spec; prior feasibility `stale` superseded by this re-run |
| Prior stage | `/spec-draft` → `/commit-workspace` → `/open-draft-pr` (#91, `spec-pending`) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-30 |
| Branch | `chore/INIT-GATEFLOW-008-spec-gateflow` — Draft PR #91 |
| Initiative segment | `INIT-GATEFLOW-008` |
| Status | Draft |
| Review deadline | 2026-08-04 |
| Deciders | PM: PE/programme · Domain SME: N/A (pin consume) |

## Summary

INIT-GATEFLOW-008 is **buildable in this repo** as a pin-consume + orchestrator
change. The delivery pin tip already defines `authorization` and post-`loop-spec`
`wave-pr-action`; harness pin `v0.5.0-rc.2` **exact-matches** submodule
`355f403` (prior FF-02 remount-record Critical is **resolved**). Gateflow still
treats every `external-action` as STOP, opens Draft PRs via PR-at-start, and
does not parse `authorization` — those are expected **gaps**, not freshness
failures. Implementation remains blocked by **Accepted ADR-009**, which still
requires explicit authorize for all external-action mutates (**Critical** vs
REQ-4/REQ-8). Unit tests already **fail** against the remounted Pass-1 edges.

**Findings:** 6 total (1 Critical, 3 Should fix, 1 Verify, 1 Gap) — plus 1 Critical resolved.

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 0 | 1 (OQ-1 / Q-1) |
| PE / ADR | 1 | 3 | 1 (FF-02 remount record) |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 1 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 1 |
| Should fix | 3 |
| Verify / Gap (informational) | 2 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `findings` |
| Rationale | Source freshness CURRENT; unresolved blocking PE/ADR item FF-01 (ADR-009 vs automated mutate) |
| Next (from workflow) | `spec-technical-review` |

Do **not** run `/spec-implementation-plan` until TDD/ADR amend clears FF-01 (and
TDD resolves Should-fix PE items).

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — forge policy, forge client, orchestrator, handoff workflow | **2 failures** vs remounted pin: `test_loop_spec_pass_stops_at_live_verify_gate`, `test_pin_matrix_implement_lane_commit_workspace` (observed 2026-07-30) |
| Live verify | `verify_implement_lane`, `verify_pr_thread` (PR-at-start); no automated wave-pr assert | `tests/README.md` |
| As-built | 008 Draft not started; 007 dogfood parked; PR-at-start still FR-19 live | `implementation-status.md` |
| Pin submodule | Tip `355f403` = tag `v0.5.0-rc.2` (exact-match); has `authorization` + `wave-pr-action` | `.harness-pin.yaml`; `git -C prayog-skills describe --exact-match` |
| WorkManifest pin assets | Contract + validator present in submodule | `prayog-skills/references/workmanifest-contract.md`, `scripts/workmanifest_contract.py` |
| Draft spec PR | #91 Draft, label `spec-pending` | `gh pr view 91` |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-1 / W0 | Remount; harness pin == submodule | `.harness-pin.yaml` `v0.5.0-rc.2` ≡ `355f403` | pin load works | — | **exists** (record); consume of `authorization` still gap (REQ-2) |
| REQ-2–3 / W0 | Parse/carry `authorization` | `workflow_engine._to_resolved` only `parse_node_forge`; no field on `ResolvedWorkflowNode` | no auth enum tests | — | **gap** |
| REQ-4 / W0 | Amend ADR-009 dual mode | `adr-009` still “explicit authorization” for all EA mutates | — | — | **conflict** (ADR) |
| REQ-5 / W1 | required commit_workspace | `_publish_stage_workspace_if_needed` + dirty∪ahead (#89); pin now required on pre-implement + loop-spec | publish unit tests; pin matrix test **red** (expects optional pre-implement) | implement_lane | **partial** |
| REQ-6–8 / W1 | Branch STOP vs automated apply | `policy_engine._STOP_NODE_TYPES` includes all `external-action`; no automated apply | policy assumes STOP | — | **gap** |
| REQ-7 / W1 | explicit authorize retain | `ForgeActionService`; `POST …/forge/authorize` | `test_forge_action_service` | — | **exists** |
| REQ-9 / W1 | head_ref/base_ref from run context | Authorize/publish use run targeting; automated open not wired | forge tests | — | **partial** |
| REQ-10 / W1 | Retire PR-at-start | `run_orchestrator._ensure_run_pr` always before stages | `test_pr_opened_before_stage_*` | `verify_pr_thread` | **drift** (opposite of target) |
| REQ-11 / W1 | Pass-1 via wave-pr | Pin: `loop-spec`→`wave-pr-action`; Gateflow tests/docs still →`live-verify` | `test_loop_spec_pass_stops_at_live_verify` **FAIL** (got `wave-pr-action`) | README Pass-1 chain | **drift** |
| REQ-12 / W1 | automated spec-pr | Same as REQ-8 | — | — | **gap** |
| REQ-13–15 / W2 | prayog/v1 + pin validator | `work_manifest_models.py` “launchpad”; no call to pin `workmanifest_contract.py` | board/manifest unit | — | **gap** |
| REQ-16–17 / W2 | docs + 007 ordering | README/as-built point at 008 blocking 007; Pass-1 string lag | — | — | **partial** |

## ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-009 | pin forge publish/mutate, authorize | **Accepted** — **conflicts** with automated EA |
| ADR-010 | lane intake | Accepted — aligned (no change required for 008 core) |
| ADR-003 | ForgeClient infra | Accepted — aligned |
| ADR-005 | programme token | Accepted — authorize path retain for explicit |
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
| REQ-10 PR-at-start | ADR-009 head binding allows run context; create-at-start is product timing | design in TDD | FF-03 Should fix |
| REQ-13 WorkManifest | pin contract SSOT; no NEW-ADR if validator is pin script only | missing wiring | FF-04 Should fix |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F13 | REQ-4/REQ-8 automated Forge without interactive STOP | ADR-009 §Recommendation 2 + Consequences (“require the explicit authorization path”) | **Critical conflict** — amend or supersede before implement |
| FF-03 | F14/F5 | Retire PR-at-start | `run_orchestrator._ensure_run_pr`; tests assert PR before stage | Should-fix — TDD: ensure_branch-only vs delete path |
| FF-04 | F9/F2 | Pin WorkManifest validator | Gateflow-local parse; pin `scripts/workmanifest_contract.py` unused | Should-fix — wire pin validator; reject launchpad/v1 |
| FF-07 | F4/F5 | Unit suite matches remounted pin | `test_handoff_workflow` / `test_forge_policy` red after remount | Should-fix — update assertions in W0 with consume |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F13 | Spec REQ-4/8 contradict Accepted ADR-009 (all EA mutates need explicit authorize). Implementation without ADR amend is unconstitutional under SDD. | Spec REQ-4; `adr-009-…md` Recommendation 2 + Consequences; pin `authorization: automated` on `wave-pr-action` / `spec-pr-action` |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F2/F5 | PR-at-start still creates Draft PR before skills; opposite of REQ-10. | `run_orchestrator._ensure_run_pr` (~L829+); `verify_pr_thread` |
| FF-04 | F2/F9 | WorkManifest path does not enforce `prayog/v1` or call pin validator. | `work_manifest_models.py` (“launchpad”); no import of `workmanifest_contract.py` |
| FF-07 | F4/F5 | Unit tests assert obsolete Pass-1 (`loop-spec`→`live-verify`, `pre-implement` commit optional); remounted pin already differs — suite red. | pytest failures 2026-07-30; pin `workflow.yaml` outcomes |

### Verify / Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-05 | F3/F6 | Feature map / verify docs lag remounted Pass-1 edges. | `tests/README.md` still `pre-implement`→`loop-spec`→`live-verify` |
| FF-06 | F7/F8 | Live prove deferred to INIT-007 (REQ-17) — OK if plan states CI=unit only for 008. | Spec REQ-17; as-built |

### Resolved since prior run

| ID | Resolution |
|----|------------|
| FF-02 (remount record) | Harness `agent_skills.ref: v0.5.0-rc.2` exact-matches submodule HEAD `355f403` — no longer Critical drift |
| OQ-1 / Q-1 | Gate 1 PE-waived; `/spec-draft` `pass`; PR #91 open |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 remount consume + parse | Already remounted; `forge_types`/`forge_models`, `workflow_engine.py`, `ResolvedWorkflowNode` | fix red pin tests; new auth parse tests |
| W0 ADR | `docs/specification/adr/adr-009-…md` (amend) | inspection |
| W1 algorithm | `policy_engine.py`, `run_orchestrator.py`, `forge_action_service.py` | walker + automated open without authorize |
| W1 PR-at-start | `run_orchestrator._ensure_run_pr` | `test_run_orchestrator`, `verify_pr_thread` |
| W2 WorkManifest | `work_manifest_models.py`, `forge_action_service.execute_create_board_tickets` | reject launchpad/v1; pin validator |
| W2 docs | as-built, `tests/README.md` | inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | ~~Feasibility while draft needs-input~~ | Cleared — CURRENT |
| R-2 | Automated open without filled `title`/`body_path` in handoff | Fail closed (REQ-8); skill packages must fill forge slots |
| R-3 | head_ref in pin requires vs authorize `head` field naming | TDD maps run context → requires check |
| R-4 | CI already red on Pass-1 unit tests after pin remount (PR #90) | W0 must update tests with authorization parse — treat as first coding debt |
| A-spec | Gate 1 waived holds | Spec Q-1 |

## Recommended spec edits

- None required for freshness (header already waived + draft `pass`).
- Keep REQ-4 as ADR amend mandate; do not soften automated semantics without pin change.
- Optionally note in Spec Q-4: harness/tag already aligned at `v0.5.0-rc.2`/`355f403` as of this feasibility — remount *consume* (REQ-2+) remains the W0 work.
- Optionally split REQ-10 acceptance: “ensure_branch allowed; create_or_update_pull_request forbidden at job start.”

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| OQ-1 | PM / PE | Gate 1 PRD+Impact-Map **or** waive | **yes** | PE | **resolved** | — | waived | Spec Q-1 | Spec Q-1; PR #91 |
| FF-01 | PE / ADR | Amend ADR-009 for `authorization` dual mode | **yes** | PE | open | technical review | none | ADR-009 vs REQ-4/8 | `/spec-technical-review` |
| FF-02 | PE | Pin harness ref match submodule | **yes** | PE | **resolved** | W0 remount record | — | harness ≡ tip | this report F1 |
| FF-03 | PE | ensure_branch-only vs drop `_ensure_run_pr` entirely | no | PE | open | TDD W1 | ensure_branch yes; no PR create | REQ-10; orchestrator | Spec Q-3 |
| FF-04 | PE | How to invoke pin `workmanifest_contract.py` (subprocess vs port) | no | PE | open | TDD W2 | subprocess pinned script path | pin scripts | TDD |
| FF-07 | PE | Update unit tests for remounted Pass-1 + required commit_workspace | no | PE | open | W0 / plan | update with REQ-2 parse | pytest red | TDD / W0 |
| FF-05 | auto-fix | Update tests/README Pass-1 chain string | no | eng | open | W2 docs | — | README | later forge publish |

### PM questions

#### Blocking — must resolve before spec merge
1. None (Gate 1 waived).

#### Defer
1. None.

### PE questions

#### Blocking for implementation plan
1. **FF-01:** Amend ADR-009 in place vs ADR-011 — resolve in `/spec-technical-review` before plan (Spec Q-2 default: amend ADR-009).

#### Defer with default
1. **FF-03:** Default ensure_branch-only before first publish; never create PR at start (Spec Q-3).
2. **FF-04:** Default call pinned validator script from delivery-contract path.
3. **FF-07:** Update obsolete Pass-1 unit assertions as part of W0 (with authorization parse).

### Domain clarifications

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None | — | — |

### Auto-fixable

| # | Item | Fix |
|---|------|-----|
| AF-1 | README / verify feature-map Pass-1 edge string | Update when 008 docs wave lands (FF-05) |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline | PASS | remount record CURRENT; suite red noted FF-07 |
| F2 Spec→code | FAIL (gaps) | FF-03, FF-04, auth parse gap |
| F3 Spec→verify | PASS (informational lag) | FF-05 |
| F4 Spec→unit | FAIL (tests obsolete) | FF-07 |
| F5 As-built drift | FAIL | FF-03, STOP-all-EA, docs lag |
| F6 Docs drift | PASS (partial) | FF-05 |
| F7 Overlap | PASS | FF-06 Gap OK |
| F8 CI vs live | PASS | unit CI; live via 007 |
| F9 Cross-service | PASS | pin contracts exist; wiring gap FF-04 |
| F10 Assumptions | PASS | Gate 1 waived; pin match verified |
| F11 Effort drivers | PASS | W0 parse+ADR+test fix; W1 orchestrator; W2 validator |
| F12 PM questions | PASS | none blocking |
| F13 ADR | FAIL | FF-01 Critical |
| F14 MDC | PASS | fail-fast/SDD aligned with fail-closed auth parse |

**Check PASS (severity-aware):** **FAIL** — unresolved Critical FF-01 (plus Should-fix PE items for plan readiness).

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> Gate 2 label stays **`spec-pending`**.

1. **`/commit-workspace`** — publish this report onto `chore/INIT-GATEFLOW-008-spec-gateflow` / PR #91.
2. **`/spec-technical-review`** — amend ADR-009 (FF-01); resolve FF-03/04/07 in TDD.
3. Then **`/spec-implementation-plan`** — still **no INIT-007 dogfood** until 008 W0–W1 on `develop`.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md` |
| Target branch | `chore/INIT-GATEFLOW-008-spec-gateflow` (PR #91) |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-008-spec-gateflow  (#91, spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] Blocking PM / Gate 1 answered (waived)
  [ ] Spec + feasibility on branch tip (Forge `/commit-workspace` for this report)
  [ ] Proceed: /spec-technical-review (PE blockers → findings)
  [ ] After TDD + ADR Accepted: /spec-implementation-plan
  [ ] After full package: PE sets spec-lgtm + Approve → merge
  [ ] After merge: implement 008; then prove INIT-007 first
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md
    digest: sha256:cf40b3e95fde827bb909b24ae3d988f5fef8f745048045336f7eed711c15cfbb
  blockers:
    - FF-01
  signals:
    new_adr: false
    adr_amend: ADR-009
    freshness: CURRENT
    gate1_waived: true
    gate1_waived_at: "2026-07-30"
    draft_pr: "91"
    draft_pr_head: b3cb6c08e526d43f830116dc40965ad60e52374d
    findings_critical: 1
    findings_should_fix: 3
    brand: 006A
    blocks_init_007_dogfood: true
    remount_record: CURRENT
    pin_ref: v0.5.0-rc.2
    pin_sha: 355f40378b2eeacc31478ad2306e1f58172c6156
    unit_suite_pin_drift: true
    ripple_action: continue
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: initiative-feasibility forge.commit_workspace = required.
    # Publish this report onto Draft PR #91 head — invoke /commit-workspace
    # (or Gateflow ForgeClient). This skill does not mutate.
```
