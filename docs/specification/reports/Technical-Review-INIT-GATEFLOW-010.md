# Technical Design Document — INIT-GATEFLOW-010

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-010 |
| Spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Spec digest | `sha256:39f22510e6ea700af223e674b488f091ca4a9ce86a0a5a94ac3f3a788f5fe133` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md` |
| Feasibility digest | `sha256:837a6f575b96b8856753718c9223fd6397ead0c14adb804963319f61708aae51` |
| PRD digest | `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` / `1` |
| Repo scope digest | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` |
| Approved meta PR head | `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Source freshness | **CURRENT** — H1/H2/H3/G1 match live meta checkout; harness pin `v0.5.0-rc.2` ≡ submodule `6561c7c`; feasibility pass on same spec tip |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-05 |
| Branch | `chore/INIT-GATEFLOW-010-spec-gateflow` (Draft spec PR — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-010` |
| Status | Draft |
| Review deadline | 2026-08-12 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

---

## 1. Problem statement

Gateflow must **parse and model** the remounted pin @ `v0.5.0-rc.2` tip-faithfully
before W1+ can wire automated board-status hops and later-wave lane gates. Today
**2/39** nodes fail `WorkflowEngine.get_node` because `update_board_status` is
unrecognized, pin `forge.status` is not modeled, and pin `purpose` / `owner` are
dropped on resolve/stop — blocking REQ-02 (parse), REQ-10, and the W0 exit
(0 BROKEN get_node). Later waves (W1–W4) add APPLY_FORGE board status, ticket
gates, create predicates, closeout Done, and closure Enter-at per approved REQs;
this TDD resolves **all** engineering decisions with W0 detail and deferred
defaults for W1–W4.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `prayog-skills/workflow.yaml` | Pin SSOT @ `6561c7c` | **Unchanged** — consume only | Pin policy |
| `src/models/forge_types.py` | `ForgeActionType` lacks `update_board_status` | Add `UPDATE_BOARD_STATUS`; add `BoardPinStatusType` (`in_progress` \| `done`) | Closed forge vocab |
| `src/models/forge_models.py` `NodeForgePolicy` | No `status` field | Add optional `status: BoardPinStatusType`; validate when action is board status | Parsed pin forge block |
| `src/models/forge_models.py` `EffectiveForgePolicy` | No `status` | Add `status` for W1 apply merge (W0 parse only) | Pin ⋉ handoff effective policy |
| `src/models/handoff_models.py` `ResolvedWorkflowNode` | No `purpose`/`owner` | Add optional `purpose`, `owner`; add optional `predicates: list[str]` (node-level `requires`, non-forge) | Resolved pin node |
| `src/business_services/workflow_engine.py` | `_to_resolved` drops pin metadata | Parse `purpose`, `owner`, node-level `requires` → `predicates`; fail-closed forge parse | Pin load / resolve |
| `src/models/adapter_models.py` timeline DTOs | No purpose/owner | W0: add optional `purpose`, `owner` on `TimelineStageItem`; optional top-level on `RunStatusResponse` when stopped | Status API projection |
| `src/business_services/metrics_emitter.py` | Timeline build only | W0: enrich timeline from resolved node / STOP event payload | Read path for REQ-10 |
| `src/business_services/run_orchestrator.py` | Automated apply for open_draft_pr / create only | W1: apply `update_board_status`; W0: unchanged apply surface | Run walk + forge apply |
| `src/business_services/forge_action_service.py` | No board-status branch | W1: `execute_update_board_status` → `BoardService.update_ticket_status` | Forge mutate orchestration |
| `src/business_services/board_service.py` | `update_ticket_status` exists | W1: map pin status → column+state (A-1); W0 unchanged | Board I/O primitive |
| `src/business_services/wave_start_service.py` | Enqueue only on implement-start | W1: board In Progress hop before enqueue (REQ-04); W2: full ticket gate (REQ-08) | Implement lane intake |
| `src/business_services/policy_engine.py` / new predicate helper | No pin predicate eval | W2: pre-authorize predicate checklist on `board-tickets-action` | Gate before create |
| `src/api/v1/waves_routes.py` | spec/implement/closeout starts | W4: add `POST …/initiatives/closure/start` (ADR-010 fourth lane) | HTTP edge |
| `tests/unit/test_forge_policy.py`, `test_handoff_workflow.py` | Skip broken nodes | W0: all-node walk + board-status parse matrix | Unit |
| `tests/verify/` | No closure script | W4: `verify_closure_lane.py` (name finalized in plan) | Live verify |

**Accepted ADR constraint set:**

| ADR | Interaction |
|-----|-------------|
| ADR-009 | **Constrains** — `update_board_status` is automated EA only; ForgeClient/BoardService; no human forge skill; pin `forge.status` is policy SSOT |
| ADR-010 | **Constrains** — closure Enter-at is a **distinct** lane start body/route; does not resume Pass-1 runs |
| ADR-003 | **Constrains** — board HTTP via ForgeClient in infra; apply orchestration in business |
| ADR-005 | **Constrains** — programme token on lane/forge routes |
| ADR-001, ADR-006–008 | **Independent** for W0 parse slice |

**Boundary diagram (W0 parse + W1 board-status apply):**

```
[pin workflow.yaml]
  → WorkflowEngine.get_node / resolve_next
       → ResolvedWorkflowNode (+ forge, authorization, purpose, owner, predicates)

[W0] unit tests: known_node_ids() walk — 0 BROKEN

[W1+] content hop success
  → resolve_next → external-action + authorization=automated
       → ForgeActionService.apply_external_action
            ├── open_draft_pr → ForgeClient
            ├── create_board_tickets → BoardService (after predicates W2)
            └── update_board_status → BoardService.update_ticket_status(ticket from run payload)
       → continue outcomes.pass

[W1] POST /waves/implement/start
  → WaveStartService: board In Progress (idempotent) → enqueue pre-implement

[W4] POST /initiatives/closure/start
  → ClosureStartService: Done-gate → EPIC Done → enqueue purge-initiative-artifacts-app
```

---

## 3. Public interface contracts

### 3.1 WorkflowEngine → ResolvedWorkflowNode (W0)

**Method / entry point:** `get_node(node_id)` / `_to_resolved`

**Arguments:** raw pin node mapping from `workflow.yaml`.

**Return additions:**
- `purpose`: optional string — copied from pin when present (human-checkpoint / external-action)
- `owner`: optional string — copied from pin when present
- `predicates`: list of strings — from pin top-level `requires` when node is external-action **and** entries are not forge instance slots (board-tickets-action: `spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass`)
- `forge.status`: `BoardPinStatusType` — required when `forge.action == update_board_status`

**Errors / fail closed:**
- Unknown `forge.action` → `ValueError` (existing behaviour; fixed by enum extension)
- `update_board_status` without `forge.status` or with invalid status → `ValueError`
- `update_board_status` without `ticket` in `forge.requires` → `ValueError`
- Invalid `forge.status` not in `{in_progress, done}` → `ValueError`

**Invariants:**
- **39/39** remounted node ids succeed `get_node` after W0 (REQ-02)
- Non-board-status nodes: `forge.status` absent
- Pin SSOT unchanged — Gateflow consumes only

### 3.2 parse_node_forge → NodeForgePolicy (W0)

**Behaviour:**
- When `action == update_board_status`: require `status` field; coerce to `BoardPinStatusType`
- `requires` must include `"ticket"` for board-status actions (pin contract)
- Reject `*-lgtm` in apply_labels (unchanged, REQ-16)

**Return:** `NodeForgePolicy` with populated `status` when applicable.

### 3.3 MetricsEmitter / RunStatusResponse — REQ-10 projection (W0)

**Method:** `get_run_status(run_id)`

**Return additions:**
- `TimelineStageItem.purpose`, `TimelineStageItem.owner` — optional; populated when stage's `workflow_node` resolves to a pin node declaring them
- `RunStatusResponse.purpose`, `RunStatusResponse.owner` — optional; set when run is STOPPED at a node with pin metadata (from last STOP event payload or live pin lookup)

**Write path (orchestrator STOP):**
- Include `purpose` and `owner` from `ResolvedWorkflowNode` in STOP `RunEventCreate.payload` when present

**Invariants:**
- Absent pin fields → omitted (not empty string)
- No invented purpose/owner values — pin-only

### 3.4 ForgeActionService — update_board_status apply (W1 — deferred default documented)

**Method:** `apply_external_action` branch for `ForgeActionType.UPDATE_BOARD_STATUS`

**Arguments:**
- Pin `forge.status` from effective policy
- Run job payload `ticket_id` (existing packaged-skill automate path — feasibility R-2)
- Run `org`, `repo`

**Return:** success marker; board side effect via `BoardService.update_ticket_status`

**Mapping (A-1, REQ-03):**
- `in_progress` → board column/state contract for In Progress (existing BoardService vocabulary)
- `done` → board column/state contract for Done

**Errors:**
- Missing `ticket_id` in run context at apply → terminal fail closed (REQ-02/REQ-03 negative table)
- Board I/O failure → propagate; fail closed

**Invariants:**
- Automated path only (`authorization: automated` on both board-status nodes)
- No merge; no `*-lgtm`

### 3.5 WaveStartService — implement-start board hop (W1)

**Method:** `start_implement_wave`

**Behaviour (REQ-04):**
- After ticket identity validation (partial W0/W2), call board status update to In Progress for `ticket_id` **before** `_enqueue_wave` / `pre-implement`
- Ticket already In Progress → idempotent accept (REQ-08 negative table)

**Invariants:** Does not auto-chain from create-tickets (REQ-11 — existing)

### 3.6 Predicate pre-check — board-tickets-action (W2)

**Method (engineering name):** `evaluate_node_predicates(run, node) → PredicateResult`

**Predicates (pin SSOT):**
- `spec-pr-merged` — spec PR merged on run bind
- `implementation-plan-current` — plan artifact on PR head matches pin contract
- `workmanifest-contract-pass` — subprocess pin validator (INIT-008 pattern)

**When:** Before explicit authorize / apply on `board-tickets-action`

**Failure:** `UnprocessableEntityError` (422); 0 tickets created (REQ-06)

### 3.7 Closure lane start (W4 — ADR-010 extension)

**Route:** `POST /api/v1/initiatives/closure/start` (exact mount in plan; body-only per `http-api-conventions.mdc`)

**Body binds (REQ-12):** programme token fields + `initiative_id`, `epic_ticket_id`, `wave_ticket_ids[]`, `workspace`, org/repo — Pydantic model in `src/models/`

**Behaviour:**
- Malformed/missing → **400** (`ValidationError`)
- Done-gate: all `wave_ticket_ids[]` board Done → else **422** (REQ-13)
- Pass → EPIC Done (REQ-14) → enqueue `purge-initiative-artifacts-app` (REQ-15)
- Partial failure handling per REQ-20 (W4)

---

## 4. ADR resolutions

Feasibility F13 confirmed **zero NEW-ADR** findings (`new_adr: false`). No new
ADR numbers; extend existing Accepted ADRs via TDD-only engineering choices.

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| F13 (no NEW-ADR) | TDD_ONLY | §2, §9 | `[REQ-01, REQ-02, REQ-09, REQ-16]` | pin redesign | Consume ADR-009/010; no ADR-011 | Resolved | N/A |
| FF-01 | TDD_ONLY | §3.1–3.2, §9 | `[REQ-02]` | apply timing (REQ-03) | Add enum + parse; 0 BROKEN get_node | Resolved | N/A |
| FF-02 | TDD_ONLY | §3.1, §3.3, §9 | `[REQ-10]` | — | `purpose`/`owner` on ResolvedWorkflowNode + timeline | Resolved | N/A |
| FF-03 | TDD_ONLY | §3.2 | `[REQ-02]` | — | `NodeForgePolicy.status` + validation | Resolved | N/A |
| FF-04 | DEFERRED_WITH_DEFAULT | §3.7, §9 | `[REQ-12–REQ-15]` | PM/meta purge | W4 closure route + service; ADR-010 lane pattern | Deferred | N/A |
| FF-05 | DEFERRED_WITH_DEFAULT | §3.6, §9 | `[REQ-06]` | — | W2 predicate engine before create apply; default fail-closed 422 | Deferred | N/A |
| FF-06 | DEFERRED_WITH_DEFAULT | §3.4–3.5, §9 | `[REQ-03, REQ-04]` | — | W1 automated apply + implement-start In Progress hop | Deferred | N/A |
| FF-07 | DEFERRED_WITH_DEFAULT | §5 | `[REQ-17]` | — | W4 `tests/verify/verify_closure_lane.py` | Deferred | N/A |
| FF-08 | planned-auto-fix | §12 | — | — | AF-01: INIT-010 row in as-built at W0 implement | Planned | N/A |
| FF-09 | planned-auto-fix | §12 | `[REQ-17]` | — | Update `tests/README.md` closure knobs in W4 | Planned | N/A |

**Derived counts:**

- ADR_REQUIRED: **0**
- TDD_ONLY: **4** (F13 + FF-01…FF-03)
- DEFERRED_WITH_DEFAULT: **4** (FF-04…FF-07)
- Draft ADR files created: **0**
- Missing/broken ADR files: **0**

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| W0 all-node parse | Parametrize `WorkflowEngine.known_node_ids()` — every id `get_node` succeeds; assert 39 nodes | — | — | exact — 0 failures |
| Board-status parse | `wave-in-progress-action`, `wave-done-action`: action, status, requires `[ticket]`, authorization automated | — | — | exact enum |
| purpose/owner | Nodes with pin purpose (e.g. `wave-signoff`, `live-verify`): resolved fields + STOP payload | — | — | exact string match |
| Negative parse | Unknown action (fixture), invalid status, missing ticket require | — | — | exact ValueError |
| W1 board apply | Mock BoardService; automated walker calls update before pre-implement | — | `verify_implement_lane.py` extended | exact call order |
| W2 predicates | Mock run/PR/plan state; 422 when any predicate fails | — | partial verify | exact |
| W3 closeout Done | Mock automated `wave-done-action` before wave-signoff STOP | — | `verify_wave_closeout.py` | exact |
| W4 closure | Route 400/422 matrix; Done-gate | — | new closure verify script | exit 0 under knobs |

**W0 scope decision (Q-2):** **All-node `get_node` unit walk** is required in W0.
Extend existing `test_forge_policy` / `test_handoff_workflow` for board-status
and purpose/owner assertions. **No** orchestrator end-to-end smoke in W0 — optional
in plan if PE wants belt-and-suspenders; default excluded to keep W0 unit-only
per spec wave table and feasibility F7.

**AI-output determinism policy:** N/A (no LLM outputs in this INIT).

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Unknown forge.action at parse | `parse_node_forge` / WorkflowEngine | ValueError → pin load / get_node fail | terminal — W0 target is elimination for tip pin |
| Invalid forge.status | parse_node_forge | ValueError | terminal |
| Missing ticket at board-status apply | ForgeActionService (W1) | ValidationError / fail run | terminal |
| Create predicate failure | Predicate eval (W2) | UnprocessableEntityError → HTTP 422 | terminal — 0 creates |
| Implement-start bad ticket | WaveStartService | ValidationError 400 / UnprocessableEntityError 422 | terminal — 0 enqueue (REQ-08) |
| Closure Done-gate miss | ClosureStartService (W4) | UnprocessableEntityError 422 | terminal — no purge, EPIC unchanged |
| Board GitHub I/O | BoardService / ForgeClient | ServiceUnavailableError 503 | terminal |
| Partial closure after EPIC Done | RunOrchestrator (W4) | Run FAILED; no false complete (REQ-20) | PE re-enter |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| WorkflowEngine | WARNING/ERROR | `node_id`, `action`, `status`, `authorization` | parse failures |
| RunOrchestrator STOP | INFO | `run_id`, `workflow_node`, `purpose`, `owner`, `stop_reason` | REQ-10 visibility |
| ForgeActionService board apply (W1) | INFO | `run_id`, `node_id`, `action`, `ticket_id`, `pin_status` | static message + kwargs |
| WaveStartService implement-start | INFO | `run_id`, `ticket_id`, `board_status_applied` | idempotent path logged |
| Predicate eval (W2) | INFO/WARNING | `run_id`, `node_id`, `predicate_id`, `passed` | fail-closed WARNING |
| Closure start (W4) | INFO | `run_id`, `initiative_id`, `wave_ticket_count`, `done_gate` | |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Pin `forge.status` vocab | prayog-skills pin | WorkflowEngine / parse_node_forge at load | frozen `v0.5.0-rc.2` (A-3) |
| `BoardPinStatusType` | gateflow models (mirror pin) | parse_node_forge | amend only on pin change |
| `NodeForgePolicy` / `EffectiveForgePolicy` | pin ⋉ handoff merge | ForgeActionService | pin wins policy |
| Node-level `predicates` | pin `requires` (non-forge) | Predicate eval (W2) | pin tip |
| Timeline purpose/owner | pin → ResolvedWorkflowNode | orchestrator write + metrics read | pin tip |
| Closure start body | product REQ-12 + ADR-010 | Pydantic at API edge | additive route |
| Board column/state mapping | BoardService + A-1 | apply time (W1+) | PE amend if GitHub labels change |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| Q-1 / PRD OQ-01 | PE | **resolved** | Exact problem+json / OpenAPI error field names | **Defer field names**; keep HTTP **400**/**422** semantics per spec error table; use existing `ValidationError` (400, `field_errors` in `details`) and `UnprocessableEntityError` (422) via `BaseAppException` → `HTTPException(detail=message)` at edge. OpenAPI structured body is follow-up — not blocking plan. | OpenAPI polish | Semantics-only responses | `src/exceptions/app_exceptions.py`; `api_helpers.handle_api_errors` |
| Q-2 / FF-01 | PE | **resolved** | W0 test scope: all-node walk vs orchestrator smoke | **All-node `get_node` unit walk** over `known_node_ids()` + targeted board-status / purpose tests; **no** orchestrator smoke in W0 | W0 implement | Same default | Spec Q-2; §5 |
| FF-01…FF-03 | PE | **resolved** | W0 parse/model gaps | Enum + `NodeForgePolicy.status` + purpose/owner on `ResolvedWorkflowNode` + timeline projection | W0 | — | §3.1–3.3 |
| FF-04 | PE | **deferred** | Closure Enter-at route shape | W4: `POST /api/v1/initiatives/closure/start`; distinct Pydantic body; ADR-010 fourth lane | W4 plan | Route + Done-gate service stub fail-closed | ADR-010 §6; REQ-12 |
| FF-05 | PE | **deferred** | Create predicate evaluation | W2: `evaluate_node_predicates` before `board-tickets-action` apply; 422 on any fail | W2 plan | Hard-fail authorize (no silent create) | pin `board-tickets-action.requires` |
| FF-06 | PE | **deferred** | Implement-start In Progress + automated board hops | W1: ForgeActionService board branch + WaveStartService pre-enqueue hop | W1 plan | Parse-only W0; board unchanged until W1 | REQ-03, REQ-04; ADR-009 |
| FF-07 | PE | **deferred** | Closure live verify | W4 script under `tests/verify/` | W4 plan | Manual PE prove-out | REQ-17 |
| R-3 | PE | **resolved** | Predicate order vs authorize UX | Evaluate **all** predicates before exposing authorize success; single 422 surface | W2 | Fail-closed batch | §3.6 |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| Q-3 | PM | open | Parallel open GATEFLOW meta PRs (#10–#23) sequencing vs this INIT (IM-02) | no | Gate 1 scheduling | Proceed; distinct INIT ids | Impact map IM-02 | [Meta PR #28](https://github.com/drivestream-lab/prayog-meta/pull/28) thread |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None (eng control plane) | — | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-01 | planned-auto-fix | INIT-010 capability matrix in as-built | `docs/specification/as-built/implementation-status.md` during W0 `/loop-spec` | N/A |
| AF-02 | suggested-fix | Optional cross-link FF-01/FF-02 evidence in spec W0 exit bullets | spec PR narrative | N/A |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | **PASS** |
| Engineering decisions resolved | 4 resolved; 4 deferred with defaults; Q-1/Q-2 closed |
| Draft ADR files written | **0 / 0 required** |
| Product-boundary integrity (T12) | **PASS** |
| PM questions outstanding | 1 non-blocking (Q-3) |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` — PE review ready; no blocking engineering or product gaps |
| Ready for PE review | **YES** |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE approval required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram |
| T2 Interface contracts | PASS | §3.1–3.7 |
| T3 NEW-ADR dispositions | PASS | 0 NEW-ADR; FF-* mapped |
| T4 Test policy | PASS | §5; Q-2 resolved |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | api→business→infra; no new cycles |
| T9 Engineering questions zero | PASS | §9; Q-1/Q-2 resolved |
| T10 PE review readiness | PASS | Draft TDD; `ready_for_plan: false` |
| T11 ADR artifact integrity | PASS | 0 ADR_REQUIRED files |
| T12 Product-boundary integrity | PASS | No invented UX; all norms cite REQ-* |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch `chore/INIT-GATEFLOW-010-spec-gateflow`.
> Do **not** commit, push, open PRs, or apply labels inside this skill.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD — not by setting
> `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-010-spec-gateflow
PR title: "[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)"
Reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-12

PE review checklist:
  [ ] T1 Module boundaries — W0 vs W1–W4 wave split clear?
  [ ] T2 Interface contracts — parse shapes + deferred apply paths?
  [ ] T3 No missing NEW-ADR — ADR-009/010 sufficient?
  [ ] T4 W0 all-node test policy acceptable?
  [ ] T9 Q-1/Q-2 resolutions acceptable?
  [ ] T12 Product-boundary — no scope invention?

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → update TDD via Forge
  Explicit Accept → TDD Status → Accepted (no new ADRs to accept)
  Publish acceptance package via /commit-workspace
  → /spec-implementation-plan (still no spec-lgtm until plan on tip)
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-010.md
    digest: sha256:dea9dd6c8f42c0d0e8170ca6cc88af6cf3e18572a90c725fb77a1c12baf63821
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
    open_questions: [Q-3]
    new_adr: false
    adr_required_new: []
    draft_adr_paths: []
    broken_get_node: 2
    pin_nodes_total: 39
    pin_ref: v0.5.0-rc.2
    pin_sha: 6561c7c508539fbdb182159d3fdae5abef4b9b01
    ready_for_pe_review: true
    ready_for_plan: false
    engineering_resolved: 4
    engineering_deferred: 4
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```
