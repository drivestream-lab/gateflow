# Technical Design Document — INIT-GATEFLOW-011

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-011 |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Spec digest | `sha256:0edf9b72b5e66e9edb9686faddbe24ced7bfe5ca30aed4462dead234d7376ac4` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md` |
| Feasibility digest | `sha256:61cd10b2f402d517bd45e62cac3d165cdf39ff923293ea99f812729f32a8ace8` |
| PRD digest | `sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-011.md` / `1` |
| Repo scope digest | `sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d` |
| Approved meta PR head | `f3da8148f3e861fad4720a3491f11f1fdc0145aa` |
| Source freshness | **CURRENT** — H1/H2/H3 match meta @ `f3da8148…`; G1 APPROVED + `impact-map-lgtm`; Draft spec PR [#159](https://github.com/drivestream-lab/gateflow/pull/159) tip `059e1f3`; Gate 2 `spec-pending` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-06 |
| Branch | `chore/INIT-GATEFLOW-011-spec-gateflow` (Draft spec PR — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-011` |
| Status | **Accepted** |
| Review deadline | 2026-08-13 |
| Deciders | PE: @drivestream-lab/prayog-pe-team |
| Approval evidence | Explicit PE acceptance via Cursor chat 2026-08-06 (TDD accepted; proceed to `/spec-implementation-plan`); no ADR_REQUIRED |
| Approved head | `059e1f3700bfedc0cf8c4ceb6f45a78c967c2f5a` (pre-acceptance tip; acceptance commit updates tip) |

---

## 1. Problem statement

Gateflow needs a **read-only control-plane composition layer** that (a) evaluates
live GitHub PR evidence against pinned `delivery-contract.yaml` checkpoint
vocabulary and (b) projects existing RunStore / board / meta PR state into GET
aggregates under programme-token auth. Feasibility confirmed no NEW-ADR: design
stays inside ADR-001 (store), ADR-003/009 (ForgeClient reads vs mutate),
ADR-004 (pin contract load), ADR-005 (programme-token zone), and ADR-010
(meta intake remains accept-gate). This TDD resolves module boundaries,
interface contracts, and PE questions Q-2…Q-4 for waves W0–W9 against
**REQ-01…REQ-28**.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/infra_services/forge_client.py` | `get_pull_request` (labels + head/base SHA) | **W0:** add read methods for reviews, check-runs; extend PR document with merge fields | Outbound GitHub REST (read) |
| `src/models/meta_pr_models.py` (or sibling checkpoint models) | `GithubPullRequestDocument` limited fields | **W0:** additive fields + review/check-run DTOs | Edge validation of GitHub JSON |
| `src/business_services/workflow_engine.py` | Loads contract YAML; retains `_contract_id` only | **W0:** retain typed contract slice (`github.labels`, `review_roles`) for evidence resolver | Pin load / contract accessor |
| `src/business_services/checkpoint_evidence_service.py` | **new** | **W0:** live evidence evaluation; **never** mutates Forge | CAP-01 core |
| `src/business_services/meta_pr_intake.py` | Accept-gate (initiative derive) | **unchanged** (ADR-010) | Spec-lane meta accept only |
| `src/database/postgres/*` + `run_store_*` | `run_events` JSONB timeline | **W1:** new `event_type` + payload model for check records; history query by initiative/wave/checkpoint | CAP-02 persistence |
| `src/api/v1/checkpoints_routes.py` | **new** | **W0–W1:** GET status + history | HTTP edge CAP-01/02 |
| `src/api/v1/initiatives_routes.py` | POST closure/start only | **W2+:** additive GET list/detail/spec/waves/… siblings | HTTP edge CAP-03…10 |
| `src/business_services/initiative_readout_service.py` (name TDD) | **new** | **W2–W9:** compose runs + board + CAP-01 + meta bridge | Visibility aggregates |
| `src/business_services/board_service.py` | `list_tickets` | **unchanged** read API; consumed by wave map / completion | Board reads |
| `src/business_services/closure_done_gate.py` | Mutate Done-gate helper | **W8:** reuse semantics for GET completion (no mutate) | Done rollup logic |
| `src/app.py` | `public_paths` programme zone | **W0:** add `/api/v1/checkpoints` prefix | JWT bypass allowlist |
| `tests/unit/*` / `tests/verify/*` | No 011 coverage | Per-wave unit + live scripts | Evidence layers |

**Accepted ADR constraint set:**

| ADR | Status | Interaction with INIT-011 |
|-----|--------|---------------------------|
| ADR-001 | Accepted | **Constrains:** Postgres RunStore SSOT for check records |
| ADR-003 | Accepted | **Constrains:** ForgeClient in infra; business owns evaluation |
| ADR-004 | Accepted | **Constrains:** pin/contract ownership; expose vocabulary without redesign |
| ADR-005 | Accepted | **Constrains:** programme-token auth on new GETs |
| ADR-009 | Accepted | **Constrains:** no mutate forge actions on CAP paths (REQ-05/28) |
| ADR-010 | Accepted | **Constrains:** MetaPrIntake stays accept-gate; CAP-01 is separate |

**Boundary diagram (text):**

```
[delivery-contract.yaml] → WorkflowEngine.contract_github_vocab
         ↓
GET /checkpoints/status → CheckpointEvidenceService
         ↓                    ↓
   ForgeClient (read)    RunEventRepository.append (W1+)
   list_reviews /
   list_check_runs /
   get_pull_request(+merge)

GET /initiatives… → InitiativeReadoutService
         ↓
   RunRepository + BoardService + CheckpointEvidenceService
   (+ ForgeClient → prayog-meta for PRD-approval line, W3)
```

---

## 3. Public interface contracts

### 3.1 ForgeClient read extension (W0 — REQ-01/02/21)

**Methods (new):**
- `list_reviews(owner, repo, pr_number) → list[GithubPullRequestReviewDocument]`
- `list_check_runs(owner, repo, ref_sha) → list[GithubCheckRunDocument]` (or PR-scoped equivalent that yields conclusions for required checks)
- Extend `get_pull_request` document: `merged: bool`, `merge_commit_sha: optional string`, `merged_at: optional timestamp` (names finalized in models; shapes only)

**Invariants:**
- Read-only HTTP verbs only on these paths
- Fail closed on transport/rate-limit (raise typed error; never invent pass)
- No call to `apply_pull_request_labels`, review create/update, merge, or board status update from CAP-01 callers (REQ-05/28)

### 3.2 WorkflowEngine → contract vocabulary (W0 — REQ-02)

**Method:** accessor e.g. `get_github_checkpoint_vocab()` (exact name TDD-owned)

**Return:** structured mapping:
- per checkpoint node id → required labels, blocking labels, `review_roles` entry
- sourced from pinned `delivery-contract.yaml` at same tip as workflow load

**Invariants:**
- Never hardcode phase label strings in business code
- Unknown checkpoint id → fail closed at service edge (404/400 per API error table)

### 3.3 CheckpointEvidenceService → live verdict (W0–W1 — REQ-01…05,03)

**Method:** `evaluate(checkpoint_id, pr_ref) → CheckpointStatusResult`

**Arguments:**
- `checkpoint_id`: pin node id ∈ closed set from contract `review_roles` keys
- `pr_ref`: `{owner, repo, number}` already resolved by caller

**Return (logical fields — OpenAPI names deferred Q-1):**
- `verdict`: satisfied | not_satisfied | could_not_verify
- `checked_sha`, `checked_at` (W1+ required on all responses; W0 may emit without persistence)
- `missing_items`: list of named misses (empty when satisfied)
- `stale_reason`: present when evidence predates later head commit

**Errors:**
- Unresolvable PR / unknown checkpoint → propagate as not-found to route
- GitHub unreachable → `could_not_verify` (fail closed; never cached-as-current)

**Invariants:**
- Live GitHub fetch every call (no silent cache of current decision)
- Historical records never substituted for live verdict (REQ-07)

### 3.4 Check persistence (W1 — REQ-06/07)

**Method:** after each successful evaluate path that completes a live attempt, append RunStore event

**Shape:**
- `event_type`: dedicated closed enum member (e.g. `checkpoint_check`) — exact string in models
- `payload`: checkpoint_id, pr_ref, checked_sha, checked_at, verdict, missing_items, initiative_id?, wave_id?

**History query:** list by initiative/wave/checkpoint filters → responses marked `historical: true`

**Invariants:**
- Persistence uses existing RunStore (ADR-001); **default: `run_events` JSONB**, not a parallel product SoT
- Sibling table only if PE accepts later revisit (see §9 PE-5)

### 3.5 Checkpoints HTTP edge (W0–W1)

**Entry points:**
- `GET /api/v1/checkpoints/status` — live CAP-01
- `GET /api/v1/checkpoints/history` — CAP-02 historical only

**Auth:** `Depends(verify_programme_service_token)`; add `/api/v1/checkpoints` to `public_paths`

**Errors:** 404 unresolvable; 400 mutating/query abuse; GitHub fail → structured body. **Default:** HTTP 200 with `verdict=could_not_verify` (aligns with partial observability patterns). Plan may refine after OpenAPI.

**Invariants:** GET-only; programme token required.

### 3.6 Initiative readout HTTP edge (W2–W9)

**Entry points:** Appendix A GET paths under `/api/v1/initiatives…` (product-normative paths)

**Composition rules:**
- W2: Gateflow-owned runs + board only
- W3: + read-only meta PR evidence via same ForgeClient; meta down → field `unavailable`, HTTP 200 (REQ-11)
- W4–W9: wave map / progress / closeout / merge / completion / closure compose CAP-01/05 and existing Done-gate semantics without second divergent Done logic (REQ-24)

**Invariants:**
- GET-only; no enqueue, no board write, no forge mutate

### 3.7 MetaPrIntakeService (unchanged)

**Boundary:** remains `accept()` for spec-lane start. CAP-01 must **not** overload this service into a general reconciler (Q-4). Shared pieces: ForgeClient + URL parse helpers may be extracted as pure functions if needed — intake semantics stay ADR-010.

---

## 4. ADR resolutions

Feasibility `new_adr: false` — **no NEW-ADR findings**. No Draft ADR files created.

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| — | — | — | — | — | No ADR_REQUIRED | N/A | N/A |
| Q-3 / FF-06 | TDD_ONLY | §3.1, §9 PE-1 | `[REQ-01, REQ-02, REQ-21]` | OpenAPI field names (Q-1) | Extend ForgeClient reads in W0 | Resolved | N/A |
| Q-4 | TDD_ONLY | §3.3, §3.7, §9 PE-2 | `[REQ-01, REQ-02, REQ-03, REQ-04, REQ-05]` | Accept-gate product rules (ADR-010) | New `CheckpointEvidenceService`; leave MetaPrIntake unchanged | Resolved | N/A |
| Q-2 | TDD_ONLY | §9 PE-3 | `[REQ-09, REQ-11]` | Meta process ownership | Same ForgeClient / App installation | Resolved | N/A |
| CAP-02 storage | TDD_ONLY | §3.4, §9 PE-5 | `[REQ-06, REQ-07]` | Retention product policy | Persist via `run_events`; sibling table revisit if query needs force it | Resolved | N/A |
| Contract vocab load | TDD_ONLY | §3.2, §9 PE-4 | `[REQ-02]` | Pin redesign | Retain typed github vocab on WorkflowEngine | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: 0
- TDD_ONLY: 5
- DEFERRED_WITH_DEFAULT: 1 (Q-1 OpenAPI names — §9 PE-6)
- Draft ADR files created: 0
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| ForgeClient reviews/check-runs/merge | Mock httpx responses; document validation | — | optional smoke against fixture PR | Exact field presence |
| Contract vocab accessor | Fixture `delivery-contract.yaml` tip slice | — | — | Exact label/role sets per checkpoint id |
| CheckpointEvidenceService | Fixture PRs: pass / missing label / stale SHA / unreachable | — | `verify_checkpoint_status` (new) | Exact verdict + missing_item names |
| Check persistence + history | append + list filters; historical flag | Postgres session fixture if existing pattern | history smoke | Exact event_type + payload keys |
| Initiative GETs W2–W9 | Service composition with mocked repos/board/CAP-01 | — | per-wave `verify_initiative_*` | Exact status enums / HTTP codes |
| REQ-05/28 write guard | Assert CAP path never calls mutate ForgeClient methods | — | code guard in verify | Exact call-count 0 |

**AI-output determinism policy:** N/A — no LLM on request path.

**T4 vocabulary:** unit = doubles for ForgeClient/repos; integration = one real dependency (e.g. Postgres for event append) when repo already uses that pattern; live verify = programme-token GET against running API + real or fixture GitHub as documented in `tests/README.md`.

---

## 6. Error handling strategy

| Failure mode | Module | Propagation | Recovery |
|--------------|--------|-------------|----------|
| Unknown checkpoint id | CheckpointEvidenceService / route | 404 | Terminal |
| PR not resolvable / no run for wave | Route / readout | 404 + reason code | Terminal |
| GitHub unreachable / rate limit | ForgeClient → evidence service | `could_not_verify`; no cached pass | Terminal for current decision; retry by caller |
| Stale evidence vs head | Evidence service | `not_satisfied` + stale reason | Terminal for pass; record persisted W1+ |
| Meta unreachable (initiative detail) | Initiative readout | 200 + `unavailable` on meta fields | Partial success |
| Mutating query/body on GET surface | Route | 400 | Terminal; 0 GitHub writes |
| History without live | History route | Return historical only; never claim current | N/A |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| CheckpointEvidenceService | INFO | `checkpoint_id`, `owner`, `repo`, `pr_number`, `checked_sha`, `verdict` | No tokens/secrets |
| CheckpointEvidenceService | WARNING | same + `error_class` | GitHub unreachable |
| Initiative readout | INFO | `initiative_id`, `wave_id?`, `fields_unavailable[]` | Meta degradation |
| Routes | INFO | `path`, `status_code` | Existing HTTP middleware patterns |
| Persistence | DEBUG/INFO | `event_type`, `run_id`, `checkpoint_id` | Avoid payload dump at INFO |

---

## 8. Data contract ownership

| Schema / data type | Owner | Validation layer | Versioning |
|--------------------|-------|------------------|------------|
| `GithubPullRequestDocument` (+ merge) | `src/models/*` + ForgeClient | Infra edge (`model_validate`) | Additive fields |
| Review / check-run documents | `src/models/*` | Infra edge | Additive |
| Checkpoint vocab DTO | WorkflowEngine + models | Pin load | Tip-locked to pin family |
| `CheckpointStatusResult` | business + models | Service out / HTTP response model | Amend-by-PE with OpenAPI |
| Check `run_events` payload | models + RunEventRepository | Repo validate on write/read | Additive event_type enum |
| Initiative readout responses | models + readout service | HTTP edge | OpenAPI pass (Q-1) |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| PE-1 (Q-3) | PE | resolved | W0 ForgeClient extension scope | **Include** `list_reviews`, `list_check_runs`, merge fields in W0 | W0 | Include | Feas FF-06; §3.1 |
| PE-2 (Q-4) | PE | resolved | CAP-01 vs MetaPrIntake | **New** `CheckpointEvidenceService`; MetaPrIntake unchanged | W0 | New service | ADR-010; §3.3/3.7 |
| PE-3 (Q-2) | PE | resolved | Meta credentials | Same ForgeClient / App installation; revisit if meta outside installation | W3 | Same credentials | Feas Q-2 |
| PE-4 | PE | resolved | Contract vocabulary load | Retain typed github labels/roles on WorkflowEngine after `load_pin` | W0 | Retain | Feas FF-07; ADR-004 |
| PE-5 | PE | resolved | Check-record storage | **Default `run_events`** with dedicated `event_type`; sibling table only if query/indexing forces it (human Alembic) | W1 | run_events | ADR-001; feas A-3 |
| PE-6 (Q-1) | PE | deferred | OpenAPI / problem+json field names | Defer to OpenAPI pass; paths + HTTP semantics normative | OpenAPI / implement | Keep Appendix A paths | Spec Q-1 |
| PE-7 | PE | resolved | GitHub fail HTTP status | Default **200 + `could_not_verify`** body for live status-check | W0 OpenAPI | As stated | §3.5 |
| PE-8 | PE | resolved | Completion Done logic | Reuse `closure_done_gate` semantics / shared helper; no second Done vocabulary | W8 | Shared helper | REQ-23/24; existing gate |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| PM-1 (Q-1) | PM/PE | deferred | Exact response field names | no | OpenAPI | Paths + status codes normative | Spec Q-1; PRD OQ-01 | meta [#30](https://github.com/drivestream-lab/prayog-meta/pull/30) optional |

---

## 11. Routed out — domain clarifications (SME)

_None — eng control-plane visibility; no domain SME lane items._

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | suggested-fix | Clarify in as-built later that `initiatives_routes` today is POST closure only | ground-spec / as-built | N/A |
| AF-2 | planned-auto-fix | Feature-map rows for 011 verify scripts | `tests/README.md` at implement waves | N/A |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | PASS |
| Engineering decisions resolved | 7 resolved, 1 deferred with default (Q-1) |
| Draft ADR files written | 0 / 0 required |
| Product-boundary integrity (T12) | PASS (TDD lint + manual re-read; no ADR bodies) |
| PM questions outstanding | 1 non-blocking (PM-1) |
| Domain questions outstanding | 0 |
| Selected workflow outcome | `pass` — engineering package ready for PE artifact review; no blocking PM/domain |
| Ready for PE review | **YES** |
| **Ready for /spec-implementation-plan** | **YES — TDD Accepted; run `/spec-implementation-plan` on this branch** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram |
| T2 Interface contracts | PASS | §3.1–3.7 |
| T3 NEW-ADR dispositions | PASS | Zero NEW-ADR; five TDD_ONLY + one defer |
| T4 Test policy | PASS | §5 with unit/integration/live vocabulary |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 structured fields |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | api → business → infra/repo; no cycles; ADR-aligned |
| T9 Engineering questions zero | PASS | Q-2…Q-4 resolved; Q-1 deferred |
| T10 PE review readiness | PASS | ready_for_pe_review true; ready_for_plan false |
| T11 ADR artifact integrity | PASS | N/A — no ADR_REQUIRED |
| T12 Product-boundary integrity | PASS | See lint evidence below; REQ ids cited not paraphrased |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` to Draft spec PR
> [#159](https://github.com/drivestream-lab/gateflow/pull/159). Do **not** commit,
> push, or apply labels inside this skill. Gate 2 stays **`spec-pending`**.
> PE accepts by setting TDD `Status: Accepted` on exact head — **not** `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-011-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/159
Reviewer: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-13

PE checklist:
  [ ] T1–T2 boundaries/contracts
  [ ] T3 no missing ADR_REQUIRED
  [ ] T9 PE decisions PE-1…PE-8 acceptable
  [ ] T12 no product leakage
  [x] Explicit accept → Status Draft→Accepted → Forge publish → /spec-implementation-plan
```

### Lint evidence (TDD)

```
lint passed (1 source(s) checked).
tool: prayog-skills/skills/development/spec-technical-review/scripts/adr_boundary_lint.py --tdd
sources: REQ-01..REQ-28 table sentences from product spec
approved-req-ids: REQ-01..REQ-28
```

Manual T12 re-read: problem/§9 use engineering vocabulary; REQ ids cited without
paraphrasing acceptance prose; no ADR bodies to audit.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: technical-review-approval
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-011.md
    digest: sha256:411607931e193b352eaafc843352b115dc9cd5d5b213732e48298fcdff8d5ea2
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/159"
    tdd_status: Accepted
    new_adr: false
    adr_required: 0
    ready_for_pe_review: true
    ready_for_plan: true
    approval_evidence: "Cursor chat 2026-08-06 — TDD accepted"
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: true
    apply_labels: []
    title: "[INIT-GATEFLOW-011] TDD Accepted — proceed to implementation plan"
    body_path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-011.md
```
