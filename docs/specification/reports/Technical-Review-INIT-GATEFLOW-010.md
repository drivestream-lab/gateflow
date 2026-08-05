# Technical Design Document — INIT-GATEFLOW-010

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-010 |
| Spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Spec digest | `sha256:0016f090e69903f3e1624ac218b0c96ebb3ba37d9966cbcbf6da988012061843` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md` |
| Feasibility digest | `sha256:5342afb01e0b1c9e6329d628e1689da25ed6abfc19f69b39ef68812fc46561af` |
| PRD digest | `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` / `1` |
| Repo scope digest | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` |
| Approved meta PR head | `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Source freshness | **CURRENT** — H1/H2/H3 match meta @ `df0f5a5…`; G1 APPROVED on same head; harness pin `v0.5.0-rc.2` ≡ submodule `6561c7c` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-05 |
| Branch | `feature/INIT-GATEFLOW-010-w0-spec-lane` (Draft spec PR — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-010` |
| Status | Draft |
| Review deadline | 2026-08-12 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

---

## 1. Problem statement

Gateflow must execute the full engineering lifecycle against pinned
`sdd-delivery/v2` @ `v0.5.0-rc.2` with tip-faithful pin parse (W0), then
incrementally wire board-status apply, ticket gates, closeout Done hops, and
initiative closure Enter-at (W1–W4). W0 closes the parse gap: remounted pin
nodes including `update_board_status` must `get_node` without error, and stop
timeline events must expose pin `purpose` / `owner` per **REQ-10**. Later waves
inherit this TDD; W4 requires a documented closure intake authority (PE-1).

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `.harness-pin.yaml` / `prayog-skills` submodule | Tip CURRENT @ `6561c7c` | Consume only (REQ-01) | Pin SSOT |
| `src/models/handoff_models.py` `ResolvedWorkflowNode` | forge + authorization; no purpose/owner | **W0:** add optional `purpose`, `owner` from pin node | Resolved pin node DTO |
| `src/business_services/workflow_engine.py` | `_to_resolved` parses forge/authorization | **W0:** parse `purpose`/`owner` when present on raw pin node | Pin load / get_node |
| `src/models/forge_models.py` `parse_node_forge` | Parses `update_board_status` + status; rejects `*-lgtm` | **W0:** unchanged; **W1:** apply path consumes parsed policy | Forge policy parse |
| `src/business_services/forge_action_service.py` | apply for open_draft_pr, create_board_tickets; rejects update_board_status apply | **W1:** add `update_board_status` apply branch | Forge mutate orchestration |
| `src/business_services/run_orchestrator.py` | `_finalize_run` emits `run_stopped` without purpose/owner | **W0:** include pin purpose/owner on stop payload when resolved stop node carries them | Run lifecycle / timeline |
| `src/business_services/policy_engine.py` | Pin-driven STOP/CONTINUE | **W2:** create-tickets triple predicate gate; **W2:** implement-start ticket validation hooks | Dispatch policy |
| `src/api/*_routes.py` (waves) | implement/spec/closeout starts exist | **W2:** ticket gate validators; **W4:** new closure start route module | HTTP edge validation |
| `src/business_services/board_service.py` | Status update + resolve | **W1–W4:** board Done/In Progress hops; **W4:** Done-gate + EPIC Done | Board vocabulary (A-1) |
| `tests/unit/test_forge_policy.py` | Remounted pin parse matrix | **W0:** extend REQ-10 stop-payload tests | Unit |
| `tests/verify/*` | 10 scripts; no closure | **W2–W4:** incremental verify per REQ-17 | Live verify |
| `docs/specification/adr/adr-011-…md` | — | **Draft** initiative closure intake (W4 authority) | Architecture |

**Accepted ADR constraint set (full read — T2 Analyze):**

| ADR | Status | Interaction with INIT-010 |
|-----|--------|---------------------------|
| ADR-001 | Accepted | RunStore SSOT; closure creates new run — independent |
| ADR-002 | Accepted | Trust zones; programme token on lane routes — independent |
| ADR-003 | Accepted | **Constrains:** ForgeClient infra; business orchestrates apply |
| ADR-004 | Accepted | Programme config — independent |
| ADR-005 | Accepted | **Constrains:** programme-token mutations on lane/closure starts |
| ADR-006 | Accepted | Adapter registry — independent |
| ADR-007 | Accepted | **Constrains:** bound workspace keys; dual bind for spec lane |
| ADR-008 | Accepted | **Constrains:** handoff ingest after content hops |
| ADR-009 | Accepted | **Constrains:** pin forge SSOT; dual authorization; no merge; update_board_status apply W1+ |
| ADR-010 | Accepted | **Constrains:** separate lane start contracts; closeout ≠ closure |
| ADR-011 | Draft | **Extends:** fourth start contract for REQ-12–15 (this INIT) |

**Boundary diagram (text):**

```
[Pin YAML] → WorkflowEngine.get_node → ResolvedWorkflowNode
                (forge, authorization, purpose, owner)
       ↓
RunOrchestrator walker → PolicyEngine → ForgeActionService (W1+ apply)
       ↓
_finalize_run → run_stopped { purpose?, owner?, handoff_context? }

[W4 only]
POST /api/v1/initiatives/closure/start → validator (Done-gate)
  → EPIC Done (BoardService) → enqueue fixed Enter-at → walker
```

---

## 3. Public interface contracts

### 3.1 WorkflowEngine → ResolvedWorkflowNode (W0 — REQ-10)

**Method:** `get_node` / `_to_resolved`

**Arguments:** raw pin node mapping.

**Return additions (W0):**
- `purpose`: optional string — copied from pin node `purpose` when key present; absent → `None`
- `owner`: optional string — copied from pin node `owner` when key present; absent → `None`

**Errors / fail closed:** unchanged (EA missing `authorization`, invalid forge, etc.)

**Invariants:**
- Field names match pin YAML keys (REQ-10 / PRD G7); no rename at this layer
- Non-human-checkpoint nodes may carry purpose; payload includes only when stop node resolves with values
- Gateflow does **not** enforce pin `owner` / review_roles at stop (product exclusion per PRD G7)

### 3.2 RunOrchestrator → `_finalize_run` stop payload (W0 — REQ-10)

**Method:** `_finalize_run` when `status_type == STOPPED` (and FAILED/BLOCKED when `workflow_node` set)

**Arguments:** resolved stop node id; optional last handoff envelope.

**Return event payload (`run_stopped`):**
- Existing: `stop_reason`, `event_type`, `wave_duration_ms`, optional `handoff_context`
- **Add when stop node has values:** `purpose` (string), `owner` (string)

**Errors:** none — omission when pin omits fields is valid (REQ-10 negative row)

**Invariants:**
- Values sourced from `WorkflowEngine.get_node(workflow_node)` — not invented
- API/run-detail projection may flatten same keys for PE timeline consumers

### 3.3 ForgeActionService → `update_board_status` apply (W1 — REQ-03)

**Method:** `apply_external_action` branch when `forge.action == update_board_status`

**Arguments:**
- Pin policy: `status` ∈ `{in_progress, done}` (already parsed W0)
- Ticket id from run context / handoff forge merge (`requires: ticket`)
- org/repo from run context

**Return:** board update acknowledgement; no PR bind change

**Errors:** missing ticket → fail closed terminal hop (REQ-03 negative); BoardService failure → propagate

**Invariants:** ADR-009 automated vs explicit authorization unchanged; board-status hop nodes use pin `authorization`

### 3.4 Wave implement-start pre-hop (W1 — REQ-04)

**Entry:** existing `POST /api/v1/waves/implement/start` handler (ADR-010 implement intake)

**Behaviour:** before enqueue/dispatch, apply In Progress for bound `ticket_id` via BoardService; idempotent if already `in_progress`

**Invariants:** separate from create-tickets (REQ-11); no same-run resume

### 3.5 Create-tickets authorize gate (W2 — REQ-06–08)

**Entry:** `execute_create_board_tickets` / wave start validators

**Predicate gate (all three required):** `spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass`

**Implement-start ticket gate:** board-resolved `ticket_id` agreeing with initiative/wave; status codes per approved PRD table (**400** malformed, **422** unresolvable/mismatch/Done)

**Invariants:** exact problem+json field names deferred (Q-1); HTTP semantics normative

### 3.6 Initiative closure start (W4 — REQ-12–15; ADR-011)

**Method:** `POST /api/v1/initiatives/closure/start` (programme token)

**Arguments (engineering shapes):**
- `initiative_id`: non-empty string
- `epic_ticket_id`: non-empty string
- `wave_ticket_ids`: non-empty array of non-empty strings
- `workspace`: absolute path string
- org/repo binds per existing lane pattern

**Return:** **202** + `{ run_id }` on success

**Errors:** malformed/empty → **400** 0 enqueue; Done-gate fail → **422** 0 enqueue no EPIC mutation

**Invariants:** fixed Enter-at orchestrated node; new run; never purge-meta; EPIC Done before purge-app per REQ-14

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| PE-1 (F13 NEW-ADR signal) | ADR_REQUIRED | `docs/specification/adr/adr-011-initiative-closure-intake-authority.md` | `[REQ-12, REQ-13, REQ-14, REQ-15, REQ-18, REQ-20]` | HTTP path, 400/422 table, EPIC timing — see REQ-* | Separate ADR-011 fourth start contract (Option B); relate to ADR-010 | Draft | `sha256:6dfba06835681d2245af67540d3368646fcc4ddf391c4a91aaf818226ba7f4ce` |
| FF-03 / FF-01 (REQ-10 parse + stop payload) | TDD_ONLY | §3.1, §3.2, §9 PE-2 | `[REQ-10]` | No review_roles enforcement | Add optional `purpose`/`owner` on `ResolvedWorkflowNode`; emit on `run_stopped` | Resolved | N/A |
| FF-04 (REQ-03 apply gap) | TDD_ONLY | §3.3, §9 PE-3 | `[REQ-03]` | Board column names — A-1 | W1 `ForgeActionService` apply branch; W0 parse-only unchanged | Resolved | N/A |
| Q-1 (OpenAPI field names) | DEFERRED_WITH_DEFAULT | §9 PE-4 | `[REQ-06, REQ-08, REQ-12, REQ-13]` | PRD OQ-01 | Default: 400/422 semantics + side-effect table normative; timeline keys `purpose`/`owner` match pin; problem+json names in OpenAPI pass | Deferred | N/A |
| FF-05 (verify inventory W2–W4) | DEFERRED_WITH_DEFAULT | §5, §9 PE-5 | `[REQ-17]` | Script naming | Default: add verify scripts per wave in plan W2–W4; W0 unit-only per Q-3 | Deferred | N/A |
| FF-06 (closure route missing) | ADR_REQUIRED | adr-011 (same as PE-1) | `[REQ-12]` | Route path exact string — REQ-12 | Covered by ADR-011 + §3.6; implement W4 | Draft | (same file) |
| FF-02 (as-built lag) | TDD_ONLY | §12 AF-1 | — | — | Update as-built INIT-010 row during W0 implement | Planned | N/A |

**Derived counts:**

- ADR_REQUIRED: 1 (PE-1 / FF-06 → single adr-011 file)
- TDD_ONLY: 3
- DEFERRED_WITH_DEFAULT: 2
- Draft ADR files created: 1
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| **W0** pin parse (`WorkflowEngine`, `parse_node_forge`) | Extend `test_all_remounted_pin_nodes_parse`; status/ticket/lgtm guards | — | — | Exact match on node ids, forge action enums |
| **W0** REQ-10 stop payload | New tests: stop at `wave-signoff` / `technical-review-approval` includes purpose; owner when pin sets | — | — | Exact JSON key presence/absence |
| **W1** board-status apply | `test_forge_action_service` apply branch; orchestrator walker with mocked BoardService | — | — | Exact status enum |
| **W2** ticket/create gates | `test_wave_start`, `test_forge_action_service` negative cases | — | `verify_*` new scripts | Exact HTTP status codes |
| **W3** closeout Done hop | `test_wave_closeout`, orchestrator | — | `verify_wave_closeout` | Exact timeline event sequence |
| **W4** closure Enter-at | New route unit tests; Done-gate negatives | — | `verify_closure` (new) | Exact 400/422/202 matrix |

**AI-output determinism policy:** N/A — no LLM extraction in this INIT.

**W0 exit (Q-3 resolved):** unit tests only; REQ-17 live verify deferred to W2+.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Invalid pin forge (missing status on update_board_status) | `parse_node_forge` / `get_node` | ValueError at pin load / test | Terminal — fail closed (REQ-02) |
| Missing ticket at board-status apply | `ForgeActionService` W1 | Run hop FAILED | Terminal — no silent skip (REQ-03) |
| Create predicate fail | authorize / policy W2 | 422 to caller; 0 board creates | Terminal at API boundary |
| Implement-start bad ticket | wave routes W2 | 400/422 per table; 0 enqueue | Terminal at API boundary |
| Closure Done-gate fail | closure validator W4 | 422; no enqueue; EPIC untouched | Terminal at API boundary |
| EPIC Done ok; purge/PR fail | orchestrator W4 | Run FAILED; REQ-20 partial hygiene | PE re-enter; compensating manual ops |
| Agent hop failure | `run_orchestrator` | `_finalize_run` FAILED | Terminal — existing pattern |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| `workflow_engine` | INFO | `node_id`, `node_type`, `commit_workspace`, `authorization` | On resolve |
| `workflow_engine` W0 | DEBUG | `purpose`, `owner` when present | Avoid noise when absent |
| `run_orchestrator` | INFO | `run_id`, `workflow_node`, `event_type=run_stopped` | Include `purpose` in payload not duplicate in log unless DEBUG |
| `forge_action_service` W1+ | INFO | `forge.action`, `status`, `ticket_id` | No secrets |
| closure routes W4 | INFO | `initiative_id`, `wave_ticket_count`, `gate_result` | Done-gate pass/fail |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| `ResolvedWorkflowNode` | `handoff_models` / WorkflowEngine | pin parse (edge) | W0 additive optional fields — semver N/A internal |
| Pin forge policy (`NodeForgePolicy`) | `forge_models` / pin SSOT | parse at get_node | Pin family frozen A-3 |
| Closure start request body | `models/*` Pydantic + route | HTTP edge W4 | Amend-by-PE with spec sync |
| `run_stopped` event payload | `run_orchestrator` + run event repo | business on emit | Additive purpose/owner W0 |
| Board status vocabulary | BoardService / pin enum | business apply | Immutable A-1 |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| Q-3 | PE | resolved | W0 unit-only vs REQ-17 verify | W0 exit = unit only per PRD §5 | feasibility | — | PRD §5 W0 row |
| PE-1 | PE | resolved | NEW-ADR vs ADR-010 amend for closure Enter-at | **ADR-011 Draft** — fourth distinct start contract; Option B over ADR-010 inline amend for W0–W3 stability | W4 plan | Amend ADR-010 §7 mirror closeout | adr-011; ADR-010 §6 precedent |
| PE-2 | PE | resolved | How to satisfy REQ-10 purpose/owner | Parse optional fields on `ResolvedWorkflowNode`; project to `run_stopped` | W0 implement | Omit keys when pin omits | §3.1–3.2; FF-03, FF-01 |
| PE-3 | PE | resolved | When/how `update_board_status` executes | W0 parse only; W1 `ForgeActionService.apply` with ticket from run/handoff | W1 implement | Continue reject at apply W0 | §3.3; FF-04; ADR-009 |
| PE-4 | PE | deferred | Exact problem+json field names (Q-1) | Defer to OpenAPI pass; use pin-aligned timeline keys now | OpenAPI / W2 routes | 400/422 semantics + zero side-effect table remain normative | PRD OQ-01; spec Q-1 |
| PE-5 | PE | deferred | Verify script inventory timing (FF-05) | Plan adds scripts per wave W2–W4 | plan W2+ | W0 unit matrix only | Q-3; tests/README |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| Q-2 | PM | open | Parallel GATEFLOW meta PRs (#10–#23) sequencing vs INIT-010 | no | Gate 1 scheduling | Proceed; distinct INIT ids | spec Q-2; impact map IM-02 | [prayog-meta#28](https://github.com/drivestream-lab/prayog-meta/pull/28) comment |

---

## 11. Routed out — domain clarifications (SME)

_None — eng control plane; no domain SME lane items._

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | As-built INIT-010 row (FF-02) | `docs/specification/as-built/implementation-status.md` during W0 implement | N/A |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | **PASS** |
| Engineering decisions resolved | 4 resolved, 2 deferred with defaults |
| Draft ADR files written | 1 / 1 required |
| Product-boundary integrity (T12) | **PASS** — all normative statements cite REQ-*; ADR-011 `changes_user_visible_behavior: false` |
| PM questions outstanding | 1 non-blocking (Q-2) |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` — zero blocking PE items; W0 decisions resolved; W4 ADR Draft ready for PE review |
| Ready for PE review | **YES** |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE approval required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram |
| T2 Interface contracts | PASS | §3.1–3.6 shapes and invariants |
| T3 NEW-ADR dispositions | PASS | PE-1 → adr-011; others TDD_ONLY/DEFERRED |
| T4 Test policy | PASS | §5 per wave |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | No new cycles; ADR-003 layering preserved |
| T9 Engineering questions zero | PASS | PE-1–PE-3 resolved; PE-4/PE-5 deferred with defaults |
| T10 PE review readiness | PASS | Draft TDD + adr-011 listed; `ready_for_pe_review: true`; not claiming Accepted |
| T11 ADR artifact integrity | PASS | adr-011 exists, Draft, linked, full template sections |
| T12 Product-boundary integrity | PASS | No invented UX; ADR binds REQ-12–15 only |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.

```
Branch:   feature/INIT-GATEFLOW-010-w0-spec-lane
PR title: "[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)"
Required reviewers: @drivestream-lab/prayog-pe-team

PE review checklist:
  [ ] T1 Module boundaries — W0 vs W1–W4 touch surfaces clear?
  [ ] T2 Interface contracts — REQ-10 purpose/owner shapes acceptable?
  [ ] T3 ADR-011 disposition — fourth start contract vs ADR-010 amend preference?
  [ ] T4 W0 unit-only test policy acceptable?
  [ ] T11 adr-011 Draft complete?
  [ ] T12 Product-boundary — no scope invention?

After PE acceptance:
  → Update adr-011 + TDD Status → Accepted on spec branch
  → /spec-implementation-plan on same branch
  → after plan on head: PE sets spec-lgtm + Approve
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-010.md
    digest: sha256:45432626d84bf70d39ee79fdd35665e467d67c1b04052a37cf7e70124cc19668
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W0
    source_freshness: CURRENT
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/28"
    meta_pr_head: "df0f5a5c09b6c4f951463bb42f277305310aaa80"
    map_revision: 1
    prd_digest: "sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206"
    scope_digest: "sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532"
    pin_ref: v0.5.0-rc.2
    pin_sha: "6561c7c508539fbdb182159d3fdae5abef4b9b01"
    ready_for_pe_review: true
    ready_for_plan: false
    new_adr: true
    adr_drafts:
      - path: docs/specification/adr/adr-011-initiative-closure-intake-authority.md
        digest: sha256:6dfba06835681d2245af67540d3368646fcc4ddf391c4a91aaf818226ba7f4ce
    adr_required_count: 1
    adr_tdd_only_count: 3
    adr_deferred_count: 2
    lane_counts:
      pm: 1
      pe: 0
      domain: 0
      auto_fix: 1
    findings_critical: 0
    findings_should_fix: 0
    nonblocking_questions: "Q-1,Q-2"
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```
