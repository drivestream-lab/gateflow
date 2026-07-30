# Technical Design Document — INIT-GATEFLOW-008

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| Spec digest | `sha256:8e4333dcf72dcfdf03288fc64a3b5bf1c98bfc9070393b83ffadb3099d8ba980` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md` |
| Feasibility digest | `sha256:7289a8d299bbfdd9da0474e4ff72481230562e1aad9dee0607bd76305c89edb5` |
| PRD digest | **waived** — Gate 1 PE waive (Q-1, 2026-07-30) |
| Impact map / revision | **waived** |
| Repo scope digest | **waived** — gateflow-only |
| Approved meta PR head | **waived** |
| Source freshness | **CURRENT** — spec + feasibility on Draft PR [#91](https://github.com/drivestream-lab/gateflow/pull/91) tip `79940db`; Gate 1 waived; harness pin `v0.5.0-rc.2` ≡ submodule `355f403` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-30 |
| Branch | `chore/INIT-GATEFLOW-008-spec-gateflow` (Draft spec PR #91) |
| Initiative segment | `INIT-GATEFLOW-008` |
| Status | **Accepted** — PE Accept 2026-07-30 via Cursor chat (Draft spec PR #91): amend ADR-009; ensure_branch-only; pin WorkManifest subprocess; W0 unit-test fix. Mid-lane architecture acceptance — not Gate 2 `spec-lgtm`. |
| Approval evidence | Explicit PE yes on technical-review decisions 1–4 (2026-07-30); Q-5/FF-06 live-verify deferral point removed as not needed |
| Approved head | Record on this acceptance publish tip |
| Review deadline | 2026-08-06 |
| Deciders | PE: @nikd10x / @drivestream-lab/prayog-pe-team |

---

## 1. Problem statement

Gateflow must **consume** the remounted delivery pin’s dual
`authorization: explicit | automated` and Pass-1 placement
(`pre-implement` → `loop-spec` → `wave-pr-action` → `live-verify`) without
laptop overlays, without env backdoors, and without treating every
`external-action` as STOP. Accepted ADR-009’s “always explicit authorize”
consequence conflicts with approved REQ-4/REQ-8; PR-at-start Draft PR create
conflicts with REQ-10; WorkManifest must use pin `prayog/v1` validator (REQ-13).

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `.harness-pin.yaml` / `prayog-skills` | Remounted tip CURRENT | Unchanged record; **consume** fields | Pin SSOT |
| `src/models/forge_types.py` (or sibling) | forge action / commit modes | Add `AuthorizationModeType` (`explicit` \| `automated`) | Closed vocab |
| `src/models/handoff_models.py` `ResolvedWorkflowNode` | forge policy only | Carry required `authorization` when `node_type=external-action` | Resolved pin node |
| `src/business_services/workflow_engine.py` | `parse_node_forge` only | Parse + fail-closed `authorization` for EA nodes | Pin load |
| `src/business_services/policy_engine.py` | All `external-action` ∈ STOP set | Stop only **`explicit`** EA (and other stop types); do **not** treat automated EA as walker STOP | Dispatch/stop policy |
| `src/business_services/run_orchestrator.py` | STOP+pending forge; PR-at-start `_ensure_run_pr` creates PR | Post-hop: apply automated EA via shared forge apply; retire PR create at start; optional ensure_branch-only | Run lifecycle |
| `src/business_services/forge_action_service.py` | Authorize then execute | Shared **apply** used by authorize path **and** automated path (pin ⋉ handoff merge, requires check) | Forge mutate orchestration |
| `src/infra_services/forge_client.py` | commit + open_draft_pr | Unchanged transport (ADR-003) | GitHub I/O |
| `src/models/work_manifest_models.py` + board create | Local “launchpad” parse | Validate via **pinned** `workmanifest_contract.py` first; accept only `prayog/v1`; projection DTO after pass | Manifest edge |
| `docs/specification/adr/adr-009-…md` | Accepted (always-explicit consequence) | **Amendment Accepted** dual authorization (no ADR-011) | Forge authority |
| `tests/unit/test_forge_policy.py`, `test_handoff_workflow.py`, orchestrator tests | Assert old Pass-1 edges / optional pre-implement | Update to remounted pin; add auth parse + automated apply tests | Unit |
| `tests/README.md` / as-built | Old Pass-1 string; PR-at-start | Docs in W2 (REQ-16) | Docs |

**Accepted ADR constraint set:**

| ADR | Interaction |
|-----|-------------|
| ADR-003 | ForgeClient stays infra; business decides *when* |
| ADR-005 | Programme authorize retained for **`explicit`** only |
| ADR-009 | **Amended** — dual `authorization` (this INIT) |
| ADR-010 | Lane starts unchanged; Pass-1 PR timing is forge authority not intake |
| ADR-001 / 006 / 007 / 008 | Independent |

**Boundary diagram (text):**

```
[content hop success]
  → ForgeClient.commit_workspace (pin required/optional)  [existing]
  → resolve_next(stage, outcome)
       ├── skill orchestrated → DISPATCH
       ├── human-checkpoint / decision / terminal → STOP
       ├── external-action + authorization=explicit → STOP (pending forge)
       └── external-action + authorization=automated
              → ForgeActionService.apply(pin ⋉ handoff, head/base from run)
              → continue outcomes.pass  (e.g. wave-pr → live-verify STOP)

[implement/spec job start]
  → optional ensure_branch_from_base (no create_or_update_pull_request)
  → first skill hop…
```

---

## 3. Public interface contracts

### 3.1 WorkflowEngine → ResolvedWorkflowNode

**Method:** `get_node` / `resolve_next` / `_to_resolved`

**Arguments:** raw pin node mapping.

**Return additions:**
- `authorization`: enum `explicit` \| `automated` when `node_type == "external-action"`
- unchanged `forge: NodeForgePolicy`

**Errors / fail closed:**
- EA node missing `authorization` or unknown string → `ValueError` (pin load / get_node)
- Non-EA nodes: `authorization` absent (do not invent defaults)

**Invariants:**
- Day-one pin: `wave-pr-action` / `spec-pr-action` = automated; board/prd/merges = explicit (asserted in unit; not hardcoded in production beyond pin)

### 3.2 PolicyEngine.evaluate_dispatch

**Behaviour change:**
- `human-checkpoint`, `decision`, `terminal` → STOP (unchanged)
- `external-action` + `authorization == explicit` → STOP (pending forge)
- `external-action` + `authorization == automated` → **not** a Policy STOP for authorize; orchestrator owns apply-then-continue (Policy may return a dedicated decision or STOP-with-signal that orchestrator interprets — **recommendation:** return STOP only for explicit; for automated return a non-dispatch decision such as `APPLY_FORGE` **or** let orchestrator short-circuit before policy when next is automated EA). **Chosen:** orchestrator, after hop + publish, if `resolve_next` is automated EA, **apply forge inline** without calling policy as STOP-for-authorize; policy’s `_STOP_NODE_TYPES` **removes blanket EA** and stops only when `authorization == explicit` (inspect resolved node).

**Invariants:** Missing authorization never reaches “continue as skill”.

### 3.3 ForgeActionService — shared apply

**Method (engineering name):** `apply_external_action(run, next_node, handoff) → ApplyResult`

**Used by:**
1. Programme `authorize_and_execute` when `authorized=true` and pending node is explicit
2. Orchestrator automated path (no authorize flag)

**Arguments:**
- Pin node forge policy (action, draft, labels, requires) — **pin wins** on action/draft/labels
- Handoff forge instance slots (`title`, `body_path`, …)
- Run-context `head_ref` / `base_ref` when listed in `requires`

**Return:** forge result (PR number/URL, commit SHA as applicable); updates run PR bind when `open_draft_pr`

**Errors:** incomplete requires → terminal fail closed; ForgeClient I/O → fail closed; `*-lgtm` labels already rejected at parse

**Invariants:**
- Automated path never requires prior authorize API
- Explicit path never applies without authorize (or human forge skill dual executor)
- No merge Forge action

### 3.4 RunOrchestrator — job start PR policy

**Method:** replace `_ensure_run_pr` PR-create with `_ensure_run_branch` (name TDD-local)

**Behaviour:**
- If head branch missing: `ForgeClient.ensure_branch_from_base(head, base)`
- **Must not** call `create_or_update_pull_request` at job start
- `run.pr_number` remains null until `open_draft_pr` apply succeeds

**Invariants:** Same head used for commit_workspace hops and later open_draft_pr

### 3.5 WorkManifest validation before board create

**Entry:** `execute_create_board_tickets` (explicit authorize only — REQ-15)

**Steps:**
1. Resolve pin script path: `{workspace}/prayog-skills/scripts/workmanifest_contract.py` (or delivery-contract `workmanifest_spec` path if present)
2. **Subprocess:** `sys.executable` + script + plan markdown path; nonzero exit → fail closed with validator stderr/JSON
3. Reject if contract would accept non-`prayog/v1` (validator owns this — do not reimplement in Gateflow)
4. After pass: map to BoardService projection DTOs; **do not** write runtime status into approved manifest

**Invariants:** Gateflow-local parse alone is insufficient; pin validator is SSOT (REQ-13/14)

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| FF-01 | **ADR_REQUIRED** (amend in place; **no ADR-011**) | `docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md` | `[REQ-4, REQ-5, REQ-6, REQ-7, REQ-8, REQ-9, REQ-10, REQ-12]` | day-one automated set | Option D dual authorization | **Accepted** | `sha256:bb5eb1f97e3cadb4072e17d58ddb751d41dda4269dedbcbabc6470772be868c5` |
| FF-03 | TDD_ONLY | §3.4 / §9 | `[REQ-10]` | — | ensure_branch-only; no PR create at start | Resolved | N/A |
| FF-04 | TDD_ONLY | §3.5 / §9 | `[REQ-13, REQ-14, REQ-15]` | — | subprocess pinned `workmanifest_contract.py` | Resolved | N/A |
| FF-07 | TDD_ONLY | §5 / §9 | `[REQ-2, REQ-11]` | — | Fix red Pass-1 unit tests in W0 | Resolved | N/A |
| FF-05 | planned-auto-fix | §12 | `[REQ-16]` | — | README Pass-1 string in W2 | Planned | N/A |

**Derived counts:**

- ADR_REQUIRED: **1** (ADR-009 amendment; 0 new ADR numbers)
- TDD_ONLY: **3**
- DEFERRED_WITH_DEFAULT: **0**
- Draft ADR files created: **0** new; **1** existing ADR amended (now Accepted)
- Missing/broken ADR files: **0**

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| Auth parse / ResolvedWorkflowNode | omit/unknown fail; day-one matrix | — | — | exact enum |
| Policy STOP branching | explicit STOP; automated not authorize-STOP | — | — | exact |
| Automated wave-pr walker | after loop-spec publish, open_draft_pr mock without authorize; continues to live-verify STOP | — | — | exact call order |
| Job start | no `create_or_update_pull_request`; ensure_branch may run | — | — | mock assert |
| WorkManifest | reject launchpad/v1 fixture; pass prayog/v1 via pin script | — | — | exact exit/codes |
| Pass-1 pin edges | `loop-spec`→`wave-pr-action`; pre-implement commit **required** | — | — | exact (fix FF-07 reds) |
| Live Pass-1 automated PR | — | — | Optional; product sequencing outside this TDD | N/A |

**AI-output determinism policy:** N/A (no LLM outputs in this INIT).

---

## 6. Error handling strategy

| Failure mode | Module | Propagation | Recovery |
|--------------|--------|-------------|----------|
| Missing/unknown `authorization` on EA | WorkflowEngine | ValueError → job fail / BLOCK | terminal |
| Automated EA incomplete requires | ForgeActionService.apply | fail closed; no PR | terminal |
| Required commit_workspace empty | orchestrator publish | fail closed; do not open PR | terminal |
| Automated open missing run head/base | apply | fail closed | terminal |
| Explicit authorize `authorized=false` / wrong node | forge routes | 4xx | terminal |
| WorkManifest validator nonzero | board create | fail closed before BoardService | terminal |
| ForgeClient I/O | ForgeClient | propagate; fail closed | terminal |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| WorkflowEngine | WARNING/ERROR | `node_id`, `authorization` | parse failures |
| PolicyEngine | INFO | `node_id`, `node_type`, `authorization`, `decision` | |
| Orchestrator automated apply | INFO | `run_id`, `node_id`, `authorization`, `action`, `pr_number` | static message + kwargs |
| Orchestrator ensure_branch | INFO | `run_id`, `head_ref`, `base_ref` | no PR number at start |
| WorkManifest validate | INFO/ERROR | `initiative`, `api_version`, `exit_code` | |

---

## 8. Data contract ownership

| Schema / data type | Owner | Validation layer | Versioning |
|--------------------|-------|------------------|------------|
| Pin `authorization` | prayog-skills pin | WorkflowEngine at load | pin tip |
| `NodeForgePolicy` / handoff forge slots | pin ⋉ handoff merge | ForgeActionService | pin wins policy |
| WorkManifest `prayog/v1` | pin `workmanifest_contract.py` | subprocess before board | pin contract |
| Board issue projection | BoardService | after contract pass | not SSOT |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-01 / Q-2 | PE | **resolved** | Amend ADR-009 vs ADR-011? | **Amend ADR-009 in place** (fold); **no ADR-011** | PE accept | — | Spec Q-2; ADR-009 amendment; mirrors INIT-007/ADR-010 |
| FF-03 / Q-3 | PE | **resolved** | ensure_branch required or optional? | **Yes ensure_branch-only** before first publish; **never** create PR at start | W1 | — | REQ-10; §3.4 |
| FF-04 | PE | **resolved** | How invoke pin validator? | **Subprocess** `sys.executable` + `prayog-skills/scripts/workmanifest_contract.py` | W2 | — | REQ-13; §3.5 |
| FF-07 | PE | **resolved** | Red Pass-1 unit tests | Update assertions + add auth/automated tests in **W0** with parse | W0 | — | feasibility pytest evidence |
| Q-4 | PE | **resolved** | Exact pin ref string | Keep **`v0.5.0-rc.2`** while it exact-matches tip; remount again when new tag cuts | W0 | — | harness ≡ `355f403` |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None (Gate 1 waived; no PM blockers) | — | — | — | — | — |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None | — | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | README Pass-1 chain + PR-at-start feature map | `tests/README.md` in W2 | N/A |
| AF-2 | auto-fixed | ADR-009 dual authorization amendment text | `adr-009-pin-forge-publish-mutate-authority.md` | `sha256:9fb72189e17da607fcb62222c1e434118cc206fa5e2bf81ae11d400cfa6a2610` |
| AF-3 | suggested-fix | As-built INIT-006 REQ-7 superseded note | `implementation-status.md` W2 | N/A |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | **PASS** |
| Engineering decisions resolved | 5 resolved; Q-5/FF-06 removed (not needed) |
| ADR files | 0 new; ADR-009 amendment **Accepted** |
| Product-boundary integrity (T12) | **PASS** — all normative statements cite REQ-* |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` — PE Accepted; next `/spec-implementation-plan` after Forge publish |
| Ready for PE review | **YES** (Accepted) |
| **Ready for /spec-implementation-plan** | **YES — after this acceptance package is on PR tip** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 |
| T2 Interface contracts | PASS | §3.1–3.5 |
| T3 NEW-ADR dispositions | PASS | FF-01 → ADR-009 amend; no ADR-011 |
| T4 Test policy | PASS | §5 |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | api→business→infra; pin script via subprocess |
| T9 Engineering questions zero | PASS | §9 |
| T10 PE review readiness | PASS | Accepted; `ready_for_plan: true` after publish |
| T11 ADR artifact integrity | PASS | ADR-009 amendment Accepted + linked |
| T12 Product-boundary integrity | PASS | `changes_user_visible_behavior: false` |

---

## Forge / PR instructions

> Persist this TDD + ADR-009 amendment locally and publish via `/commit-workspace`
> to Draft spec PR [#91](https://github.com/drivestream-lab/gateflow/pull/91).
> Do **not** commit/push inside this skill. Gate 2 stays **`spec-pending`**.
> PE Accepts by moving ADR-009 amendment + TDD Status → **Accepted** (mid-lane);
> do **not** set `spec-lgtm` until implementation plan is on head.

```
Branch:   chore/INIT-GATEFLOW-008-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/91
Reviewers: @drivestream-lab/prayog-pe-team

PE checklist:
  [ ] T1–T2 boundaries + contracts
  [ ] T3 ADR-009 amendment (dual authorization; no ADR-011)
  [ ] T9 decisions (ensure_branch-only; subprocess validator; test fix W0)
  [ ] T11/T12 product-boundary fields false

PE action:
  Comment / Request changes → update files via Forge
  Explicit Accept → Status Accepted on TDD + clear ADR-009 "amendment Draft"
  Publish acceptance via /commit-workspace
  → /spec-implementation-plan (still no spec-lgtm until plan on tip)
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-008.md
    digest: sha256:3a317bd08c89f4f09e1739ee1f4f08aca0ffe7d9c55e81a5e0701b66fb6e9e7f
  blockers: []
  signals:
    ready_for_pe_review: true
    pe_accepted: true
    pe_accepted_at: "2026-07-30"
    ready_for_plan: true
    adr_amended:
      - docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md
    adr_required_new: []
    draft_pr: "91"
    draft_pr_head: 79940db6c114b47c0114ce99f27c3191c1c90e49
    brand: 006A
    blocks_init_007_dogfood: true
    ff01_disposition: amend-adr-009
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: spec-technical-review commit_workspace = required.
    # Publish TDD + ADR-009 amendment onto PR #91 — /commit-workspace.
```
