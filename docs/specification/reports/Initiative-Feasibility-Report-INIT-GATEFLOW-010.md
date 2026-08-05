# Feasibility report — INIT-GATEFLOW-010

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-010 |
| Spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Spec digest | `sha256:39f22510e6ea700af223e674b488f091ca4a9ce86a0a5a94ac3f3a788f5fe133` |
| PRD digest | `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` / `1` |
| Repo scope digest | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` |
| Approved meta PR head | `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Impact-map approval | Meta PR [#28](https://github.com/drivestream-lab/prayog-meta/pull/28) — @0xbeefdead APPROVED 2026-08-05T09:32:32Z on `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Source freshness | **CURRENT** — H1/H2/H3/G1 match live meta checkout; pin submodule `6561c7c` on `v0.5.0-rc.2` family matches `.harness-pin.yaml` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-05 |
| Branch | `chore/INIT-GATEFLOW-010-spec-gateflow` — Draft spec PR (single review surface) |
| Initiative segment | `INIT-GATEFLOW-010` |
| Status | Draft |
| Review deadline | 2026-08-10 |
| Deciders | PM: programme PM · Domain SME: N/A (eng control plane) |

## Summary

INIT-GATEFLOW-010 is **buildable in gateflow as scoped**. The spec correctly
separates **W0 parse/model targets** (board-status hop parse, `purpose`/`owner`
on resolved nodes, 0 BROKEN `get_node`) from **W1–W4 apply/lane work**
(board-status APPLY_FORGE, ticket gates, closure Enter-at, verify expansion).
Today **2 of 39** pinned nodes fail closed on `WorkflowEngine.get_node`
(`wave-in-progress-action`, `wave-done-action`) because `ForgeActionType` omits
`update_board_status` — exactly the gap the spec names as W0 exit criteria.
Accepted **ADR-009** / **ADR-010** align; no Accepted ADR contradiction.
Open questions Q-1…Q-3 are non-blocking with documented defaults.

**Findings:** 9 total (0 Critical, 0 Should fix, 2 Verify, 7 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 1 | 0 |
| PE / ADR | 0 | 2 | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 1 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 0 |
| Verify / Gap (informational) | 9 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `pass` |
| Rationale | Source freshness CURRENT; zero unresolved blocking PE/ADR/PM/domain items; W1–W4 gaps are spec-normative delivery surface, not spec drift |
| Next (from workflow) | `spec-technical-review` |

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `make test` → `tests/unit/` — forge policy, workflow engine, wave start, board, orchestrator | `tests/README.md`; `test_forge_policy.py`, `test_handoff_workflow.py` |
| Live verify | `tests/verify/` — spec, implement, closeout lanes proven for INIT-009; no closure Enter-at script | `verify_spec_lane.py`, `verify_implement_lane.py`, `verify_wave_closeout.py`; no `verify_*closure*` |
| Toolchain | `make check` (black, ruff, pyright, import-linter) | `implementation-status.md` §Testing harness |
| As-built | INIT-009 freeze human_approved; INIT-010 not yet listed | `docs/specification/as-built/implementation-status.md` (Updated 2026-07-30) |
| Pin consume | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2`; submodule `6561c7c` | `.harness-pin.yaml`; `git submodule status prayog-skills` |
| Pin parse health | **37/39** nodes OK; **2 BROKEN** board-status hops | Runtime probe: `WorkflowEngine.get_node` on all pin ids |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01 / W0 | Consume pin `v0.5.0-rc.2`; harness ref == submodule | `.harness-pin.yaml`; submodule `6561c7c` | pin load in `test_forge_policy` | inspection | **exists** |
| REQ-02 parse / W0 | Parse `update_board_status` + `status` + `ticket` requires; 0 BROKEN get_node | `ForgeActionType` lacks enum member; `parse_node_forge` raises on unknown action | partial pin tests skip broken nodes | — | **gap** (W0 target) |
| REQ-02 apply / W1+ | APPLY_FORGE board status | `ForgeActionService` handles `open_draft_pr`, `create_board_tickets` only | `test_forge_action_service` | — | **gap** (W1) |
| REQ-03 / W1 | Board-status hop applies pin `forge.status` | No `update_board_status` branch in `forge_action_service.py` | — | — | **gap** (W1) |
| REQ-04 / W1 | Implement-start → In Progress before `pre-implement` | `WaveStartService.start_implement_wave` enqueues only; no BoardService status hop | `test_wave_start` | `verify_wave_start` | **gap** (W1) |
| REQ-05 / W3 | Closeout Done → stop at `wave-signoff` with purpose | Closeout route exists; board-status hops still unparsed | `test_wave_closeout` | `verify_wave_closeout` | **partial** |
| REQ-06 / W2 | Create predicates hard-fail | Pin lists `spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass` on `board-tickets-action`; **no predicate evaluator in `src/`** | workmanifest only at apply in `execute_create_board_tickets` | — | **gap** (W2) |
| REQ-07 / W2 | Return `epic_ticket_id` + `wave_ticket_ids[]` | `ForgeActionService.execute_create_board_tickets` returns both | `test_forge_action_service` | — | **exists** |
| REQ-08 / W2 | Implement-start ticket gate 400/422 | `_resolve_ticket_identity` checks format/mismatch; **no board column/state resolve** | `test_wave_start` | — | **partial** |
| REQ-09 / all | No Forge merge | No merge action in `ForgeActionType`; guards in forge paths | `test_forge_merge` | — | **exists** |
| REQ-10 / W0 | Expose pin `purpose` / `owner` on resolved nodes & stops | `ResolvedWorkflowNode` has no `purpose`/`owner`; `_to_resolved` does not parse pin fields | `test_handoff_workflow` | — | **gap** (W0 target) |
| REQ-11 / W2 | Create success does not resume implement | Walker separate Enter-at for implement | orchestrator unit tests | — | **exists** (baseline) |
| REQ-12–15 / W4 | Closure Enter-at + Done-gate + purge walk | **No** `POST /api/v1/initiatives/closure/start`; routes under `waves_routes.py` only | — | — | **gap** (W4) |
| REQ-16 / W3 | Never auto `*-lgtm` | `parse_node_forge` rejects `*-lgtm` labels | `test_forge_policy` | — | **exists** |
| REQ-17 / W3–W4 | Verify suite covers all eng lanes | Spec/impl/closeout verify exist; closure lane script missing | unit regression | partial live | **partial** |
| REQ-18 / W4 | Feature-readiness freeze doc | Prior pattern: `Feature-Readiness-INIT-GATEFLOW-009.md` | — | inspection | **gap** (W4 deliverable) |
| REQ-19 / W3 | No auto-chain after wave-signoff | Orchestrator stops at human-checkpoint nodes | `test_run_orchestrator` | — | **exists** |
| REQ-20 / W4 | Partial closure failure handling | Not implemented (no closure walk) | — | — | **gap** (W4) |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-01–03, REQ-16 / W0–W1 | ADR-009 pin forge authority | aligned | Extend `ForgeActionType` + automated apply under existing pin SSOT — no NEW-ADR |
| REQ-04, REQ-12 / W1,W4 | ADR-010 lane intake | aligned | Closure Enter-at is additive route; TDD should detail body — not ADR conflict |
| REQ-06 / W2 | ADR-009 + pin predicates | aligned | Predicate enforcement is implementation gap, not ADR gap |
| CTR-02 / W1+ | ADR-003 ForgeClient | aligned | Board status uses existing ForgeClient/BoardService transport |

### ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-009 | forge publish/mutate, automated vs explicit | **Accepted** — aligned |
| ADR-010 | implement/spec/closeout intake | **Accepted** — aligned; closure route detail → TDD |
| ADR-005 | programme token mutations | **Accepted** — aligned |
| ADR-003 | ForgeClient infra boundary | **Accepted** — aligned |
| ADR-008 | handoff ingest | **Accepted** — N/A W0 |

### MDC pass (pre-T2)

| MDC file | Domain covered | Read / skipped |
|----------|----------------|----------------|
| `http-api-conventions.mdc` | closure/implement POST bodies | read — REQ-12 shape matches body-only mutations |
| `fail-fast.mdc` | parse fail closed on unknown forge action | read — current behavior matches spec negative paths |
| `architecture.mdc` | api vs business layering | read — new routes belong in `src/api/v1/` + services |
| `testing-verify-flows.mdc` | live verify layout | read — W4 verify additions fit existing `tests/verify/` pattern |
| Other MDC (DB, logging, …) | not touched by W0 parse slice | skipped — out of scope |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| — | F13 | Spec cites ADR-009, ADR-010 Accepted | `docs/specification/adr/adr-009-*.md`, `adr-010-*.md` | No conflict |
| — | F14 | POST lane starts use Pydantic body models | `http-api-conventions.mdc` | Aligned |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Verify / Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F2 / F10 | **2 BROKEN** pin nodes: `wave-in-progress-action`, `wave-done-action` fail `get_node` with `Invalid forge.action 'update_board_status'` | `src/models/forge_types.py` (no enum member); runtime: 37/39 OK |
| FF-02 | F2 | `ResolvedWorkflowNode` lacks `purpose` and `owner`; walker timeline cannot expose pin metadata (REQ-10 W0) | `src/models/handoff_models.py`; `workflow_engine._to_resolved` |
| FF-03 | F2 | `NodeForgePolicy` has no `status` field for board-status pin `forge.status` | `src/models/forge_models.py` `NodeForgePolicy` |
| FF-04 | F9 | No `POST /api/v1/initiatives/closure/start` route (REQ-12 W4) | `src/api/v1/waves_routes.py` — implement/spec/closeout only |
| FF-05 | F2 / F10 | Pin `board-tickets-action` predicates (`spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass`) not evaluated in orchestrator authorize path (REQ-06 W2) | `prayog-skills/workflow.yaml`; no matches under `src/` |
| FF-06 | F2 | Implement-start does not board-resolve ticket state or apply In Progress hop before `pre-implement` (REQ-04 W1) | `wave_start_service.start_implement_wave` → `_enqueue_wave` only |
| FF-07 | F3 / F4 | No live-verify script for closure Enter-at lane (REQ-17 W4 partial) | `tests/verify/` inventory |
| FF-08 | F5 | `implementation-status.md` has no INIT-010 section; Updated 2026-07-30 | `docs/specification/as-built/implementation-status.md` |
| FF-09 | F6 | `tests/README.md` documents INIT-009 prove-out; closure lane knobs not yet listed for 010 | `tests/README.md` |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| **W0** parse + purpose/owner | `src/models/forge_types.py`, `forge_models.py`, `handoff_models.py`, `workflow_engine.py`, run timeline DTOs | `test_forge_policy.py`, `test_handoff_workflow.py`, new all-node walk test |
| **W1** board-status APPLY_FORGE + implement In Progress | `forge_action_service.py`, `run_orchestrator.py`, `wave_start_service.py`, `board_service.py` | `test_forge_action_service.py`, `test_wave_start.py`, `verify_implement_lane.py` |
| **W2** create predicates + ticket gate | `policy_engine.py` or forge authorize pre-checks, `wave_start_service.py` | `test_forge_action_service.py`, `test_wave_start.py` |
| **W3** closeout Done hop + no auto-chain | `run_orchestrator.py` | `test_wave_closeout.py`, `verify_wave_closeout.py` |
| **W4** closure Enter-at + freeze | new `initiatives_routes.py` (or waves router extension), closure service, verify script | new unit + `tests/verify/verify_closure_lane.py` (name TBD in plan) |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | W0 “0 BROKEN get_node” requires enum + policy model change — may affect existing forge tests | Spec Q-2: pin-walk test + extend `test_forge_policy`; TDD in technical review |
| R-2 | W1 board-status apply needs run-bound `ticket` in job payload | Pin `forge.requires: [ticket]`; orchestrator already reads `ticket_id` from payload in packaged automate path |
| R-3 | W2 predicate evaluation order vs authorize UX | Resolve in TDD; pin SSOT lists three predicates on `board-tickets-action` |
| A-1 | Board Done/In Progress vocabulary = pin `status` enum | Confirmed in spec A-1; `BoardService.update_ticket_status` exists |
| A-3 | Pin family frozen at `v0.5.0-rc.2` | Submodule + harness pin verified CURRENT |

## Recommended spec edits

- None blocking. Optional: cross-link FF-01/FF-02 evidence paths in W0 exit bullets when publishing spec PR (auto-fixable narrative).

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | Exact problem+json / OpenAPI error body field names (PRD OQ-01) | no | PE | open | technical review / OpenAPI | HTTP 400/422 semantics remain normative | Spec §Spec questions | PRD OQ-01 |
| Q-2 | PE | W0 unit scope: all-node `get_node` walk vs minimal orchestrator resolve smoke for board-status nodes | no | PE | open | W0 plan | All-node unit + existing workflow contract tests | Spec Q-2; FF-01 | `/spec-technical-review` |
| Q-3 | PM | Parallel open GATEFLOW meta PRs (#10–#23) sequencing vs this INIT (IM-02) | no | PM | open | Gate 1 scheduling | Proceed; distinct INIT ids | Impact map IM-02 | Meta PR #28 thread |
| AF-01 | auto-fix | Add INIT-010 capability matrix to `implementation-status.md` when W0 coding starts | no | PE | open | W0 ground-spec | Manual as-built row until then | FF-08 | W0 implement |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None.

#### Defer — can proceed with documented assumption

1. **Q-3** — Parallel meta PR sequencing; default: proceed with distinct INIT ids.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

None.

#### Defer with default

1. **Q-1** — OpenAPI error field names; defer naming; keep HTTP semantics.
2. **Q-2** — W0 test scope; default all-node `get_node` unit walk.

### Domain clarifications (business source-of-truth)

None.

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| AF-01 | As-built missing INIT-010 section | Add capability matrix row during W0 `/loop-spec` or plan publish |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | FF-08 Verify |
| F2 Spec → code map | PASS | FF-01…FF-06 Gap — W0–W4 scoped gaps match spec waves |
| F3 Spec → verify map | PASS | FF-07 Gap — closure verify deferred W4 |
| F4 Spec → unit map | PASS | W0 extends `test_forge_policy` / handoff tests |
| F5 As-built drift | PASS | FF-08 Verify — spec D9 distinguishes baseline vs targets |
| F6 Docs drift | PASS | FF-09 Verify |
| F7 Overlap risk | PASS | W0 parse unit-only; live verify unchanged until W1+ |
| F8 CI vs live boundary | PASS | `make test` CI; verify opt-in per `tests/README.md` |
| F9 Cross-service touch | PASS | FF-04 Gap — closure API W4; CTR-01…03 files exist |
| F10 Assumptions | PASS | A-1…A-5 confirmed; gaps are delivery targets |
| F11 Effort drivers | PASS | W0 model parse; W1 forge apply; W2 gates; W3 closeout hop; W4 closure + verify |
| F12 PM questions | PASS | Q-3 non-blocking |
| F13 ADR conformance | PASS | ADR-009/010 aligned; no NEW-ADR required for W0 |
| F14 MDC conformance | PASS | HTTP body conventions respected |

**Check PASS** = zero unresolved blocking findings (informational Gap/Verify OK).

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> Gate 2 label stays **`spec-pending`**.

1. **`/commit-workspace`** — publish spec + this feasibility report onto `chore/INIT-GATEFLOW-010-spec-gateflow` (after `/open-draft-pr` if not yet opened).
2. **`/spec-technical-review`** — resolve Q-1/Q-2 in TDD; confirm W0 test matrix and forge model shapes.
3. Then **`/spec-implementation-plan`** after Accepted TDD on branch head.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md` |
| Target branch | `chore/INIT-GATEFLOW-010-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-010-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (Q-3 deferred)
  [x] All blocking Domain clarifications answered (none)
  [x] Spec reflects approved impact map (H1–H3/G1)
  [x] Incremental feasibility on current spec is clean (pass)
  [ ] Proceed: /spec-technical-review
  [ ] After spec + feasibility + TDD + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: `/create-board-tickets` from plan §9 — then /pre-implement → /loop-spec
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: pass
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md
    digest: sha256:cb8fa640bcf04c4b469954fadad42f8163210b7a469cf7c300f617fad3d2b3db
  blockers: []
  signals:
    freshness: CURRENT
    ripple_action: continue
    wave_ticket: W0
    map_revision: 1
    source_prd_digest: sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206
    repo_scope_digest: sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532
    meta_pr_head: df0f5a5c09b6c4f951463bb42f277305310aaa80
    req_count: 20
    open_questions: [Q-1, Q-2, Q-3]
    new_adr: false
    broken_get_node: 2
    pin_nodes_total: 39
    pin_ref: v0.5.0-rc.2
    pin_sha: 6561c7c508539fbdb182159d3fdae5abef4b9b01
    findings_gap: 7
    findings_verify: 2
    findings_critical: 0
    findings_should_fix: 0
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: initiative-feasibility forge.commit_workspace = required.
    # Publish spec + this report onto chore/INIT-GATEFLOW-010-spec-gateflow —
    # invoke /commit-workspace (or Gateflow ForgeClient). This skill does not mutate.
```
