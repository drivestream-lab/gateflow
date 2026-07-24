# Technical Design Document — INIT-GATEFLOW-002

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-002 |
| Spec | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` |
| Spec digest | `sha256:9d437c0ecd3cacfc0ec12ba8c9e7fa05a4ec42c543f1284fff670dc134aa3867` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-002.md` |
| Feasibility digest | `sha256:33d5b40bec323cca9efcf84fa7372e50cd41bfda26036a6534935f414e7c0bac` |
| PRD digest | `sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-002.md` / `1` |
| Repo scope digest | `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` |
| Approved meta PR head | `8f291367134a686baaf650835a89dba92e887051` |
| Source freshness | CURRENT — meta PR #10 head + APPROVED review `4770823317` + digests match spec/feasibility headers |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-24 |
| Branch | `chore/INIT-GATEFLOW-002-spec-gateflow` (Draft spec PR #10) |
| Initiative segment | `INIT-GATEFLOW-002` |
| Status | Draft |
| Review deadline | 2026-07-31 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit acceptance required, not approval by silence |

---

## 1. Problem statement

On top of the delivered INIT-001 control plane, Gateflow must become **API-first**:
authenticate wave start with the programme service token (label trigger removed),
resolve **per-node runner/model**, **fail-closed** on stub adapters at start, open
a **PR thread at run start**, deepen **run/metrics** APIs, and expose **board
forge primitives** that the wave worker never calls — all without violating
Accepted ADR-001/003/004 or platform layering.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/app.py` | exists | Extend `public_paths` for waves + board prefixes (ADR-005) | HTTP composition |
| `src/api/v1/waves_routes.py` | new | `POST /waves/start` | Programme-token wave mutation |
| `src/api/v1/runs_routes.py` | exists (detail only) | Add list/filter; enrich detail timeline | Programme-token run reads |
| `src/api/v1/metrics_routes.py` | exists (by node) | Add runner / model_id aggregates | Programme-token metrics reads |
| `src/api/v1/board_routes.py` | new | Board dumb primitives | Programme-token board mutations/reads |
| `src/api/v1/programme_token.py` | exists | Reuse for all programme-token routes | AuthN dependency |
| `src/business_services/trigger_router.py` | label-centric | API identity path; disable label authorize for 002 | Preconditions / concurrent |
| `src/business_services/wave_start_service.py` | new | Orchestrate validate → optional PR prep enqueue | Wave-start use case |
| `src/business_services/slot_validator.py` + registry | new | Fail-closed selection (ADR-006) | Required slot validation |
| `src/business_services/run_orchestrator.py` | exists | PR-at-start; per-node runner; no board calls | Run lifecycle |
| `src/business_services/notifier.py` | GitHub-only | Registry-selected notifier | Event → adapter |
| `src/business_services/metrics_emitter.py` | by node | Multi-dim aggregates + api_trigger events | Metrics |
| `src/business_services/board_service.py` | new | Board use cases → ForgeClient only | Board API orchestration |
| `src/infra_services/forge_client.py` | comments | PR create/update + board ops; no `gh` | Forge I/O |
| `src/infra_services/cursor_agent_runner.py` | stub | Stay infra; register as `cursor` | AgentRunner |
| `src/infra_services/*_stub_runner.py` / notifier stubs | new | OpenCode, Claude, Slack, Teams stubs | Honest stubs |
| `src/models/*` | exists | Wave/board/run list DTOs; override shape | Pydantic contracts |
| `config/programme.yaml` | exists | `notifier.*`, `pr.*`, structured overrides; deprecate label trigger for 002 | Programme knobs (ADR-004) |
| `src/database/postgres/schema|repository` | exists | `wave_id`, richer PR refs as needed | Persistence |
| `postgres_migrations/versions/` | human-owned | Human DDL for new columns | Migrations |
| Webhook path | exists | May remain for non-start events; **must not** start waves via label for 002 | Ingress |

**Boundary diagram (text):**

```
PE/tools ──Bearer programme token──► POST /api/v1/waves/start
                                   ► GET  /api/v1/runs[/{id}]
                                   ► GET  /api/v1/metrics/runs
                                   ► /api/v1/board/*  (never called by worker)
         │
         ▼ enqueue (wave start only)
[worker] → [RunOrchestrator]
              ├── [SlotValidator] (again)
              ├── [ForgeClient] PR open/update + comments
              ├── [AgentRunner registry] cursor|stubs
              ├── [Notifier registry] github|stubs
              ├── [LaunchpadClient]
              └── RunStore
                     ▲
GitHub webhook ──────┘  (no label wave-start for 002)
```

---

## 3. Public interface contracts

### 3.1 HTTP — wave start (Q-1 resolved)

**Entry point:** `POST /api/v1/waves/start`  
**Auth:** programme service token (ADR-005)  
**Body (Pydantic, `src/models/`):**

| Field | Shape | Invariant |
|-------|-------|-----------|
| `ticket_id` | optional string/int forge issue id | At least one of ticket **or** (initiative_id + wave_id) |
| `initiative_id` | optional string | Required with `wave_id` if no ticket |
| `wave_id` | optional string (e.g. `W0`) | Required with `initiative_id` if no ticket |
| `org` / `repo` | strings | Target repository |
| `workspace_path` | optional string | Worker workspace; required before dispatch if not derivable |
| `pr_number` / `issue_number` | optional ints | Concurrent-scope helpers when known |

**Dual identity rule:** if ticket **and** initiative+wave provided, they **must
agree** (resolved ticket metadata matches initiative/wave) or **400**.

**Return (2xx):** `{ run_id, job_id?, status }`  
**Errors:** 401 token; 400 identity; 409/422 precondition/stub/config list; 503 store down.

**Invariants:** no board API calls; no AgentRunner in request path; label not accepted.

### 3.2 HTTP — runs / metrics (Q-1)

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/api/v1/runs` | Filters: `initiative_id`, `wave_id`, `status_type`, `org`, `repo`, `limit`, `cursor`/`skip` |
| `GET` | `/api/v1/runs/{run_id}` | Header + **full stage/event timeline** |
| `GET` | `/api/v1/metrics/runs` | Aggregates `by_workflow_node`, `by_runner`, `by_model_id` (p50/p95 + outcome rates when data exists) |

Auth: programme token. Invalid filter → 400; missing run → 404; store down → 503.

### 3.3 HTTP — board APIs (Q-1, Q-3)

Prefix: `/api/v1/board` (programme token). Dumb forge primitives — caller supplies fields.

| Method | Path | Purpose |
|--------|------|---------|
| `PATCH` | `/api/v1/board/tickets/{ticket_id}/status` | Column/state update |
| `POST` | `/api/v1/board/tickets/{ticket_id}/links` | Link PR to ticket |
| `POST` | `/api/v1/board/tickets` | Create ticket (EPIC/Feature idempotent on `initiative_id`+type) |
| `GET` | `/api/v1/board/tickets` | List — **narrow filters (Q-3):** `initiative_id`, `type` (`EPIC`\|`Feature`\|…), `state`, `org`, `repo` / project id if Projects used |

Optional header `Idempotency-Key` on multi-step create. Partial-failure body lists
created vs failed resources. **Wave worker must not invoke these routes.**

### 3.4 WaveStartService → SlotValidator (ADR-006)

**Method:** `validate_for_run`  
**Arguments:** resolved runner ids for required orchestrated nodes; notifier id;
config keys used.  
**Return:** ok | failures `[{slot_kind, adapter_id, config_key, reason}]`  
**Invariant:** any `implemented=false` required slot → failure; unused stubs ignored.

### 3.5 RunOrchestrator → ForgeClient (FR-19)

**Methods:** `create_or_update_pull_request`, `post_comment` (existing)  
**Arguments:** org/repo, branch name from `pr.branch_prefix` + run id, title/body
from programme templates (Q-2), base branch.  
**Invariant:** same naming for success and failure paths; no auto-merge; no
gate-approval labels; no board link from orchestrator.

### 3.6 BoardService → ForgeClient (FR-24)

**Methods:** update issue/project status; create issue; list issues; link PR.  
**Invariant:** no WorkManifest/governance parsing; production uses App token path
(ADR-003); never shell `gh`.

### 3.7 Trigger / label policy (S-1)

**Resolution:** For INIT-002 programmes, `TriggerRouter` **rejects** label-based
wave authorization (PC-01 label match does not enqueue wave runs). Webhook may
still ack/idempotent-store non-start events. Programme config may retain
`trigger.label` for migration docs but it is **not** a start mechanism.

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|--------------------------|--------|--------|
| C-1 / F13-1 / Q-6 | ADR_REQUIRED | `docs/specification/adr/adr-005-programme-token-control-plane-mutations.md` | Widen programme-token zone to documented reads+writes (paths stay TDD) | Draft | `sha256:7591cf39fb78ecc2fb1f5e0c55f52456a0ac0fef5cf93936bb1e8a30c1f4427d` |
| S-6 / F13-2 | ADR_REQUIRED | `docs/specification/adr/adr-006-adapter-registry-fail-closed.md` | Business registry + fail-closed before accept (adapter catalogue stays TDD) | Draft | `sha256:cfeb47a726ee66023f549bd08ebc3ca2b46c478100cf5caf7b81111238102230` |
| ForgeClient widen (S-3) | TDD_ONLY | §3.5–3.6 | Extend ForgeClient under ADR-003; no new ADR | Resolved | N/A |
| Label removal (S-1) | TDD_ONLY | §3.7 | Disable label wave-start for 002 | Resolved | N/A |
| Q-1 paths/schemas | TDD_ONLY | §3.1–3.3 | `/api/v1/waves|runs|metrics|board` | Resolved | N/A |
| Q-2 PR naming | TDD_ONLY | §9 | `pr.branch_prefix`, title/body templates in programme config | Resolved | N/A |
| Q-3 board filters | TDD_ONLY | §3.3 | Narrow filter set listed | Resolved | N/A |
| Q-4 App permissions | DEFERRED_WITH_DEFAULT | §9 | Proceed W0/W1; **block W2 exit** until permission matrix confirmed | Deferred | N/A |
| Q-5 PE alert channel | DEFERRED_WITH_DEFAULT | §9 | `notify_pending` + status API only until dedicated alert | Deferred | N/A |
| V-3 Cursor SDK | DEFERRED_WITH_DEFAULT | §9 | W1 exit may use stub/`GATEFLOW_AGENT_STUB`/`mock-*`; real SDK follow-on | Deferred | N/A |

**ADR product boundary (hygiene):** Draft ADR-005/006 state architectural
trust-zone and registry/fail-closed rules only. Feature catalogues (wave-start,
board ops, named runner/notifier ids, FR refs, HTTP paths) live in this TDD §3
and the INIT spec — matching Accepted ADR-002/003 style.

**Constraint table (Accepted ADRs):**

| ADR | Interaction |
|-----|-------------|
| ADR-001 | **constrains** — keep API + worker + Postgres jobs |
| ADR-002 | **constrains** — JWT/webhook unchanged; programme row **superseded by ADR-005** |
| ADR-003 | **constrains** — adapters stay infra; registry policy in ADR-006 |
| ADR-004 | **constrains** — programme config stays in gateflow repo |

**Derived counts:** ADR_REQUIRED 2 · TDD_ONLY 5 · DEFERRED_WITH_DEFAULT 3 · Draft ADR files created 2 · Missing/broken 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|------------------|-------------------|-------------|----------------------|
| Wave-start API | Auth, dual identity agree/disagree, stub 422, concurrent 409 | Session + enqueue | Replace label smoke with API start | Exact status + error codes |
| SlotValidator | Stub selected vs unused stub | — | — | Exact failure list |
| Run list/detail/metrics | Filters, timeline shape, dim aggregates | DB fixtures | Extend `verify_status_metrics` | Exact JSON keys; numeric fuzzy OK for p50/p95 |
| PR-at-start | Orchestrator calls ForgeClient before stage; naming keys | Mock ForgeClient | Assert PR exists before stage complete | Exact call order |
| Board APIs | Idempotent EPIC/Feature; partial failure; worker isolation audit | Mock ForgeClient | W2 board verify | Exact bodies |
| Label disabled | TriggerRouter rejects label authorize | — | Label payload must **not** create run | Exact |
| No `gh` | ForgeClient path has no subprocess `gh` | — | Production-path inspection checklist | Exact absence |
| Cursor path (V-3) | Stub success under mock/`GATEFLOW_AGENT_STUB` | — | Optional | Exact outcome enums |

**AI-output determinism policy:** Agent narrative text is out of scope for exact
match; assert `outcome`, persisted runner/model fields, and stop reasons exactly.

---

## 6. Error handling strategy

| Failure mode | Module | Propagation | Recovery |
|--------------|--------|-------------|----------|
| Missing/invalid programme token | API dependency | 401 UnauthorizedError | terminal |
| Dual identity disagree / unresolvable | WaveStartService | 400 | terminal |
| Precondition / stub / bad overrides | SlotValidator / TriggerRouter | 409/422 structured list | terminal — no enqueue |
| Concurrent active run | TriggerRouter | 409 + optional existing `run_id` | terminal |
| Store unavailable at start | API / repo | 503 | GitHub/client retry |
| PR open/update failure at start | RunOrchestrator / ForgeClient | set `notify_pending`; persist run; continue or stop per policy in plan | recoverable visibility via status API (Q-5 deferred) |
| AgentRunner timeout/crash | CursorAgentRunner | stop run `failed`; comment on run PR | terminal for wave advance |
| Comment mid-run failure | Notifier | `notify_pending` | recoverable |
| Board bad payload | BoardService | 400 | terminal |
| Board forge failure | ForgeClient | API error | no silent success |
| Board partial create | BoardService | 207-style or 200 with partial body (TDD: **200 + `partial: true`**) | idempotent retry |
| `gh` on production path | ForgeClient / settings | must not occur; startup/test fails | terminal misconfig |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| WaveStartService | INFO | `run_id`, `initiative_id`, `wave_id`, `ticket_id`, `correlation_id` | Static message labels |
| SlotValidator | WARNING | `adapter_id`, `config_key`, `slot_kind` | On block |
| RunOrchestrator | INFO | `run_id`, `workflow_node`, `runner`, `model_profile` | |
| ForgeClient | INFO | `owner`, `repo`, `pr_number`, `operation` | Board ops use `operation=board_*` |
| BoardService | INFO | `ticket_id`, `initiative_id`, `operation` | Separate from wave events |
| MetricsEmitter | INFO | `workflow_node`, `runner`, `model_id`, `duration_ms` | |

No silent swallow — failures log ERROR with `exc_info` when handled and re-raised/mapped.

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Wave start / board / run list request-response models | `src/models/` | API edge (`model_validate`) | Amend-by-PE per INIT |
| Programme config (`notifier`, `pr.*`, structured overrides) | `programme_config_models.py` | Startup load (ADR-004) | File + Pydantic; breaking keys changelog |
| RunStore ORM ↔ DTOs | repositories | Repo boundary | Human Alembic |
| Metrics event payload JSONB | models + MetricsEmitter | Repo validate | Additive event_type strings |
| Handoff envelope | pinned skills contract | HandoffReader | Pin `v0.5.0-rc.2` |

**Config shape change (FR-16):** `model.overrides` becomes
`dict[str, NodeOverride]` where `NodeOverride` has optional `profile` and
`runner` (string ids). Legacy `dict[str, str]` profile-only values **accepted
during migration** via validator coerce-to-object (TDD_ONLY) then prefer object form.

**PR config (Q-2):**

```yaml
pr:
  branch_prefix: gateflow/run-
  title_template: "[gateflow] {initiative_id} {wave_id} {run_id_short}"
  body_template: "Run `{run_id}` — status API supplementary."
```

Same templates for success and failure paths.

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| C-1 / Q-6 | PE | resolved | Programme-token writes vs ADR-002 | ADR-005 Option C — programme token may mutate allowlisted control-plane routes; catalogue in TDD §3 | plan W0 | — | ADR-005 |
| S-6 | PE | resolved | Adapter registry + fail-closed | ADR-006 Option B — business registry; validate before accept; ids/stubs in TDD/config | plan W0 | — | ADR-006 |
| S-1 | PE | resolved | Label trigger | Disable label wave-start for 002; webhook non-start OK | plan W0 | — | §3.7 |
| S-3 | PE | resolved | ForgeClient PR/board | Extend infra client; no NEW-ADR | plan W1/W2 | — | ADR-003 + §3.5–3.6 |
| Q-1 | PE | resolved | HTTP paths/schemas | §3.1–3.3 catalog | plan W0 | — | this TDD |
| Q-2 | PE | resolved | PR naming templates | Programme `pr.*` keys; §8 defaults | plan W1 | — | §8 |
| Q-3 | PE | resolved | Board list filters | Narrow set in §3.3 | plan W2 | — | §3.3 |
| Q-4 | PE | deferred | App/Projects permissions | Confirm matrix before **W2 exit**; W0/W1 proceed | W2 exit | Narrow board MVP if Projects unavailable | Spec A-4 |
| Q-5 | PE | deferred | PE alert on PR failure | status API + `notify_pending` only | W1 | Dedicated alert later | Spec Q-5 |
| V-3 | PE | deferred | Cursor SDK vs stub W1 exit | Stub/`mock-*`/`GATEFLOW_AGENT_STUB` allowed for W1 exit; SDK follow-on | W1 exit | Document in as-built | as-built D-W1-A1 |
| S-4 | PE | resolved | Run/metrics depth | List+timeline; metrics by node/runner/model_id | plan W0/W1 | — | §3.2 |
| G-1 | PE | resolved | Wave identity concurrency | Concurrent key includes resolved wave identity (initiative+wave and/or ticket) in addition to PR/issue scope | plan W0 | — | FR-15 precondition #7 |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None — product Decisions #1–10 locked on meta PR #10 | no | — | — | PRD §5 | meta #10 |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None this review | no | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | auto-fixed | Spec PR URL | `INIT-GATEFLOW-002-gateflow.md` References | prior feasibility commit |
| AF-2 | auto-fixed | tests/README 002 map | `tests/README.md` | prior feasibility commit |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T11 checks | PASS |
| Engineering decisions resolved | 10 resolved, 3 deferred with defaults (Q-4, Q-5, V-3) |
| Draft ADR files written | 2 / 2 required (ADR-005, ADR-006) |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Ready for PE review | **YES** |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE acceptance of Draft→Accepted ADRs + TDD Status required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram |
| T2 Interface contracts | PASS | §3 HTTP + service contracts |
| T3 NEW-ADR dispositions | PASS | C-1→ADR-005; S-6→ADR-006; others TDD_ONLY/deferred |
| T4 Test policy | PASS | §5 |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | api→business→repo; infra injected; no worker→board |
| T9 Engineering questions zero | PASS | All PE items resolved or deferred with defaults |
| T10 PE review readiness | PASS | `ready_for_pe_review: true`; `ready_for_plan: false` |
| T11 ADR artifact integrity | PASS | Draft ADR-005/006 exist with digests in §4 |

---

## PR instructions

> Commit this TDD + Draft ADRs to the **Draft spec PR** branch. PE reviews on the
> **same PR**. Gate 2 label stays **`spec-pending`** until the implementation plan
> exists. PE accepts architecture by committing **Accepted** TDD/ADR files — not
> by setting `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-002-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/10
Reviewers: @drivestream-lab/prayog-pe-team

PE review checklist:
  [ ] T1 Module boundaries
  [ ] T2 Interface contracts (esp. §3.1–3.3 paths)
  [ ] T3 ADR-005 + ADR-006 Draft files
  [ ] T4 Test policy / label-smoke replacement
  [ ] T9 Zero unresolved PE items (deferred defaults OK)
  [ ] T11 ADR digests match files

PE action (artifact acceptance — mid-lane):
  Comment or Request changes → update files
  Explicitly state decisions ready for acceptance
  Update ADR-005/006 + this TDD Status → Accepted
  Commit acceptance package (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md
    digest: sha256:5c30e5c0040ccc581f9989bee41f8be2efaf60a95ae1a5cd3bc7ed5d0a88e8ff
  blockers: []
  signals:
    ready_for_pe_review: true
    ready_for_plan: false
    source_freshness: CURRENT
    draft_adrs:
      - path: docs/specification/adr/adr-005-programme-token-control-plane-mutations.md
        digest: sha256:7591cf39fb78ecc2fb1f5e0c55f52456a0ac0fef5cf93936bb1e8a30c1f4427d
        finding: C-1
      - path: docs/specification/adr/adr-006-adapter-registry-fail-closed.md
        digest: sha256:cfeb47a726ee66023f549bd08ebc3ca2b46c478100cf5caf7b81111238102230
        finding: S-6
    adr_required_count: 2
    tdd_only_count: 5
    deferred_count: 3
    pe_blocking_resolved: [C-1, S-6]
    deferred_with_defaults: [Q-4, Q-5, V-3]
    gate2_label: spec-pending
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/10
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/10
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
```
