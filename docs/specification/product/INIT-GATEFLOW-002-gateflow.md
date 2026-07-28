# INIT-GATEFLOW-002 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-002 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-002.md` |
| PRD digest | `sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/10 |
| Meta PR approved head | `8f291367134a686baaf650835a89dba92e887051` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-002.md` |
| Impact-map revision | `1` |
| Repo scope digest | `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` |
| Tech-lead approval | Review `4770823317` by `0xbeefdead`, APPROVED at `2026-07-24T06:49:29Z`; `commit_id` = approved head (map_revision 1 attestation) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-24 |
| Status | Draft — dev review required before committing |

## Overview

This repo delivers **INIT-GATEFLOW-002 platform readiness** on top of the
delivered INIT-GATEFLOW-001 control plane: an authenticated **API-only** wave
start path (label trigger removed for 002 programmes), **per-`workflow_node`
runner/model** resolution from gateflow programme config, **fail-closed**
AgentRunner/Notifier stub registration, **PR open/update at run start** with
stage comments on that thread, ops-ready **run list/detail** and **metrics**
APIs, and **wider board operation APIs** as dumb ForgeClient primitives that the
wave worker must never call. Deployed forge/board writes use **ForgeClient
only** (no `gh` on the production path). Skills pin remains **`v0.5.0-rc.2`**
(read-only consumer).

**Out of scope for this repo:** gateflow-ops BFF/UI; prayog-skills feature
delivery (including optional later board-seed → Gateflow board API wiring);
launchpad feature delivery; working OpenCode / Claude Code / Slack / Teams;
board-column or label wave triggers; WorkManifest/governance parsing in board
APIs; auto-merge and gate-approval label writes; dogfood programme execution.

**As-built baseline (INIT-GATEFLOW-001 W0+W1, human_approved):** signed webhook
ingress with label trigger (`gateflow:run-wave`), PostgreSQL RunStore + job
worker, PolicyEngine / WorkflowEngine / HandoffReader, Cursor AgentRunner +
GitHub Notifier via ForgeClient comments, programme-token
`GET /api/v1/runs/{run_id}` and `GET /api/v1/metrics/runs`, programme config with
empty `model.overrides`. **Missing for 002:** wave-start API; label-trigger
removal; stub registry fail-closed at run start; PR-at-run-start; run list/filter
+ richer timeline; metrics by runner/`model_id`; board APIs; ForgeClient PR/board
primitives; production-path `gh`-free verification.

**Delivery waves (product-normative; exact split may adjust in plan):** W0 API
trigger + run list/detail + stub registration; W1 per-node runner/model + PR at
start + metrics APIs + Cursor happy path; W2 board APIs + deploy `gh`-free proof.

## Functional requirements

| ID | Requirement | PRD source | Acceptance criteria | Evidence type |
|----|-------------|-----------|---------------------|---------------|
| FR-15 | Expose authenticated **wave-start API** as the **only** supported start path for 002 programmes; require **initiative_id + wave_id** (optional ticket must agree), **PR targeting** (`branch_slug`, `base_branch`), and **Enter-at** fields: `start_node` (pin skill with `dispatch: orchestrated`), `runner`, `model_id`; optional `node_dispatch` map for later nodes (else inherit start defaults); enqueue and return `run_id` when preconditions pass; **remove / disable INIT-001 label trigger**; do not infer intent from board columns. | PRD §2 FR-15, US-1; Scope boundary; Decision #1/#2; wave-run preconditions | Valid token + identity + orchestrated `start_node` + runner/model + preconditions → 2xx with `run_id`; non-orchestrated/unknown `start_node` → 400; disagreeing dual identity → 400; stub/not-live runner → 422; concurrent → 409; unauthenticated → 401; label webhook does not create runs. | unit + live verify |
| FR-16 | Resolve **runner + model** for orchestrated stages from the **wave-start dispatch plan** (request `runner`/`model_id` + optional per-node `node_dispatch`; unset nodes **inherit** start defaults). Persist `runner`, `model_profile`, `model_id`, `model_provider` on every orchestrated stage. **Do not** resolve from programme YAML `runner`/`model` (removed). Do not hardcode node allowlists; pin `dispatch` remains SSOT for eligibility. Supersedes programme-config FR-16 wording from W1. | PRD §2 FR-16, US-3; Decision #5 (evolved); supersedes INIT-001 FR-13 | ≥ 2 orchestrated nodes can use different API map entries or inherit; fields persisted; invalid start_node/runner/model → block at accept (FR-18); PolicyEngine unchanged when only plan values change. | unit + integration |
| FR-17 | Register multi AgentRunner adapters by id: **Cursor implemented**; **OpenCode** and **Claude Code** registered as **stubs**. | PRD §2 FR-17, US-4; §3 Tool & Runner | Registry lists three ids; selecting stub for a required runner blocks per FR-18; Cursor path produces `RunResult` with runner/model fields. | unit |
| FR-18 | **Fail-closed stub / config validation** before enqueue/dispatch: every **API-selected** runner and env `GATEFLOW_NOTIFIER` must resolve to an **implemented** backend; invalid `start_node` / runner / model blocks at start; unused stubs in registry are allowed if not selected; **never** silent fallback to Cursor/GitHub. | PRD §2 FR-18, US-4; Decision #7; Error Handling; wave-run preconditions #10/#11 | Selecting stub runner or stub notifier → 422 with stub id + key; 0 AgentRunner dispatches; invalid start_node → 400. | unit |
| FR-19 | At **run start**, open or update branch + PR via ForgeClient using the **same naming conventions** for runs that later succeed or fail; Notifier posts structured stage/stop/failed comments on **that** PR through the run; no auto-merge; wave workflow does **not** auto-link PR to ticket; status API remains supplementary for mid-run visibility. | PRD §2 FR-19, US-2; Decisions #3/#8/#9 | Before first orchestrated stage completes, PR exists (or update recorded); stage/terminal comments land on that PR; failure path uses same naming keys; auto-merge never called; zero workflow→board link side effects. | unit + integration + live verify |
| FR-20 | Ops-ready **run APIs**: authenticated `GET` list/filter runs and `GET` run detail with full stage/event timeline; programme service token; stable JSON documented for future gateflow-ops. | PRD §2 FR-20, US-5 | List supports documented filters; detail reconstructs timeline from RunStore alone; wrong/missing token → 401/403; invalid filter → 400; store unavailable → 503. | unit + live verify |
| FR-21 | Ops-ready **metrics APIs**: aggregates by `workflow_node`, `runner`, `model_id` (p50/p95 duration and outcome rates where data exists); extends INIT-001 `GET /metrics/runs`. | PRD §2 FR-21, US-5 | Query returns dimensions named above when events exist; auth same as FR-20; invalid filter → 400; store unavailable → 503. | unit + live verify |
| FR-22 | Emit **multi-stage metrics events** for API trigger, each orchestrated stage, contract stops, findings loops, and observable handoff/gate signals; retain per `metrics.retention_days`; queryable in RunStore. | PRD §2 FR-22; Success Criteria; vision metrics themes | Events present for API-accepted start, orchestrated stages, stops, findings loops; aggregates in FR-21 consume them. | unit + integration |
| FR-23 | Notifier slot: **GitHub PR comments live** via ForgeClient; **Slack** and **Teams** registered as **stubs**; event schema unchanged from INIT-001 structured run events; stub selection fail-closed per FR-18. | PRD §2 FR-23, US-4; Decision #7 | Live path posts via ForgeClient only (no `gh`); selecting Slack/Teams as required notifier blocks at start; unused stub registration OK. | unit + integration |
| FR-24 | Wider **board operation APIs** (dumb forge primitives): update ticket/column status; link PR to ticket; **create ticket**; **list tickets**. Caller supplies fields — **no** WorkManifest/governance parsing. Creates are **idempotent** for **EPIC** and **Feature** using `initiative_id` + type; optional client `Idempotency-Key` for multi-step create; **partial-failure** body when multi-step create fails mid-way. Via ForgeClient in deployment. **Wave worker must not invoke these** on start/finish. | PRD §2 FR-24, US-5; Decision #4/#8; Non-Goals | Authenticated calls mutate/read forge board resources as documented; bad payload → 400; forge failure → error (no silent success); partial create returns created-vs-failed; completing a wave run produces **zero** board API side effects from the worker; audit of board mutations separable from wave run events. | unit + integration + live verify |
| FR-25 | **Deployed forge path** performs all production PR/comment/board writes through ForgeClient (App installation token preferred). Production Gateflow runtime must **not** depend on `gh` CLI. | PRD §2 FR-25, US-6; Decision #6; Security | Spec-defined production-path verification fails if production forge path shells to / depends on `gh`; PAT not allowed in production (inherit ADR-003). | inspection + unit (path guards) |
| FR-26a | Gateflow-**deployed** board/forge apply uses ForgeClient only (testable runtime rule). | PRD §2 FR-26a; Decision #6 | Same as FR-25 for board API and run-start PR paths; runtime/config cannot enable `gh` transport in production environment. | unit + inspection |
| FR-26b | Document programme/skills **laptop** policy: board-seed apply **may** use local `gh`; does **not** replace board-seed skill judgment; **not enforced** inside Gateflow runtime. | PRD §2 FR-26b, US-6; Decision #6; impact-map (non-runtime) | Runbook/docs state laptop vs deploy transport split; no Gateflow code path required to call `gh`; board-seed skill not deleted or replaced by this INIT. | inspection |

**Inherited (unless superseded above):** INIT-GATEFLOW-001 FR-1 (webhook ingress may remain for non-start events), FR-3–FR-8, FR-10–FR-12, FR-14 remain in force for orchestration, contract stops, retry budget, ToolProvider `none`, and ForgeClient forbidden ops. INIT-001 **FR-2 (label trigger) is superseded / removed** for 002 programmes (see FR-15). INIT-001 FR-13 superseded by FR-16. INIT-001 FR-9 live GitHub notifier extended by FR-23.

### Wave-run preconditions (API trigger)

Authoritative checklist before PolicyEngine may dispatch after **API** wave start
(extends INIT-001; trigger source is API):

| # | Precondition | Spec FR |
|---|--------------|---------|
| 1 | Request authenticated with programme service token | FR-15 |
| 2 | Wave identity resolved (`initiative_id` + `wave_id`; optional ticket must agree) | FR-15 |
| 3 | PR targeting present (`branch_slug`, `base_branch`) when opening a new run PR | FR-19 |
| 4 | `start_node` exists on pin, `type: skill`, `dispatch: orchestrated` (**Enter-at**; hop-1 does **not** choose node from handoff) | FR-15; pin |
| 5 | API `runner` + `model_id` (dispatch plan) valid; runner implemented | FR-16 / FR-18 |
| 6 | Env `GATEFLOW_NOTIFIER` implemented | FR-18 / FR-23 |
| 7 | No active run for same wave identity / PR/issue scope | FR-15 |
| 8 | *(Hop 2+ only)* Latest handoff readable; contract matches; no blockers; human_checkpoint not set; next from pin | inherit; pin |

**Enter-at / walker:** Hop 1 dispatches `start_node` from the request (ignore handoff for node choice). After each skill, ingest handoff **facts** (`stage`/`outcome`/blockers/checkpoint); navigate **only** via pin `outcomes` + PolicyEngine (`next_candidates` is not authority). Loop DISPATCH while next node is orchestrated skill; STOP at human-checkpoint / terminal / non-orchestrated / external-action / findings budget. Cap hops with `GATEFLOW_MAX_ORCHESTRATED_HOPS`.

## Negative and failure paths

| FR | Condition | Required behavior | Evidence |
|----|-----------|-------------------|----------|
| FR-15 | Missing/invalid programme token | 401; no run | unit |
| FR-15 | Unresolvable wave identity | 400; no run | unit |
| FR-15 | Both identities provided but disagree | 400; no run | unit |
| FR-15 | Any wave-run precondition fails | 409/422; structured reason list; no dispatch | unit + integration |
| FR-15 | Active concurrent run for same scope | Reject; no second run; optional existing `run_id` in error | unit |
| FR-15 | Label webhook / board column change | No new wave run for 002 programmes | unit |
| FR-16 / FR-18 | Unknown override node, missing profile, unresolvable model | Block at start; structured error with config key / node id | unit |
| FR-18 | Stub runner or stub notifier required | 422; name stub id + config key; 0 dispatches | unit |
| FR-18 | Unused stub present in registry | Allowed | unit |
| FR-19 | AgentRunner timeout/crash | Stop run `failed`; comments on run PR; no workflow advance | unit + live verify |
| FR-19 | ForgeClient comment failure mid-run | Set `notify_pending` if delivery cannot complete; run continues per policy | unit |
| FR-19 | Run-start or terminal PR open/update failure | Preserve outcome in RunStore; escalate `notify_pending`; do not invent success visibility; PE alert per Q-5 default until decided | unit + integration |
| FR-20 / FR-21 | Invalid list/metrics filter | 400 structured reason | unit |
| FR-20 / FR-21 | Store unavailable | 503 | unit |
| FR-24 | Bad board API payload | 400; no partial silent success | unit |
| FR-24 | Board forge failure | Error with guidance; no silent success | unit |
| FR-24 | Multi-step create partial failure | Structured body: which resources created vs failed; idempotent retry supported for EPIC/Feature | unit + integration |
| FR-24 | Wave run completes | Zero board mutations from wave worker | integration |
| FR-25 / FR-26a | `gh` invoked on production path | Forbidden — must not occur; verification fails | inspection |
| inherit | Contract stop nodes / `human_checkpoint: true` | Stop; record; comment; no auto-transition; no gate-label writes; no auto-merge | unit (inherit INIT-001) |

## Out of scope for this repo

- **gateflow-ops** BFF/UI and any ops dashboard (deferred; impact-map §3)
- **prayog-skills** product changes (pin consumer only; optional later board-seed → board APIs is monitor-only)
- **launchpad** feature delivery (consume existing harness sync only)
- Board column as wave **trigger**; label trigger for 002 programmes
- Wave engine auto board status / auto-link PR to ticket
- Replace or delete the **board-seed** skill
- WorkManifest / governance parsing inside Gateflow board APIs
- Working OpenCode / Claude Code / Slack / Teams backends
- Graphify / ToolProvider beyond `none`; LiteLLM / model gateway
- Auto-merge; gate-approval label writes
- Dogfood programme as INIT driver
- Meta/harness shared config keys for runner/model (stay in gateflow repo config)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow / prayog-pe-team | Pinned `workflow.yaml` + delivery contract + handoff @ **`v0.5.0-rc.2`** | `handoff.stage`, `handoff.outcome`, contract id | Next node + `dispatch` eligibility | No hardcoded allowlists; missing `dispatch` ⇒ manual | Pin unavailable ⇒ block + comment/API error | Pin ref in `.harness-pin.yaml`; `sdd-delivery/v2` | `tests/unit/` contract fixtures (extend INIT-001) |
| CTR-02 | gateflow / prayog-pe-team | clients / tools / PE | Authenticated HTTP: wave-start + runs + metrics + board APIs | Programme service token + request bodies/filters | `run_id` / run JSON / metrics JSON / board JSON | API authorize only for waves; board APIs unused by wave worker | 401/400/409/422/503 per FR tables | Paths/schemas owned by this spec (Q-1); additive vs INIT-001 status API | Planned: `tests/unit/` + `tests/verify/` |
| CTR-03 | gateflow / prayog-pe-team | GitHub (forge) | ForgeClient REST (PR create/update, comments, board ops) | PR/comment/board payloads | Forge resource ids / results | No `gh` in production; no gate-approval labels; no auto-merge; no workflow auto-link | Retry + `notify_pending`; board errors surface to API | App installation token preferred (ADR-003); widened vs INIT-001 comments | Planned: unit ForgeClient audit + production-path inspection |
| CTR-04 | gateflow / prayog-pe-team | gateflow-ops (deferred) | Stable run/metrics/board JSON | Programme token | Documented ops contracts | Provider ships in 002; consumer deferred | Same HTTP errors as CTR-02 | Version via OpenAPI/docs in this repo | Planned: verify scripts; ops consumer later |
| CTR-05 | launchpad / prayog-pe-team | gateflow / prayog-pe-team | Worker pre-dispatch harness sync | Workspace / pin | Synced harness tree | Sync before AgentRunner on dispatch | Sync failure ⇒ run `failed` + notify | Unchanged from INIT-001 | Worker integration / verify |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme service token for wave-start, run/metrics, and board APIs (network boundary; no per-user RBAC in this INIT); ForgeClient App token in production; no `gh` on deploy path; board mutation audit separable from wave events; zero gate-approval label writes; zero auto-merge; secrets stay in env/secret store. | unit + inspection + verify |
| Reliability | Precondition fail-closed at API edge; stub/config validation before dispatch; concurrent-run reject; RunStore durability for PR-open failures (`notify_pending`); board partial-failure + idempotent EPIC/Feature create. | unit + integration |
| Performance / capacity | Wave-start API enqueues quickly (worker owns agent/forge work); numeric cycle-time KPIs remain `[TBD]` / deferred (PRD). Prove correctness of API path, not load SLOs. | live verify (ack latency) + inspection |
| Observability | Structured loguru logging with correlation id; RunStore events for API trigger + stages + stops; metrics aggregates by node/runner/model; ForgeClient write audit with run. | inspection + verify |
| Privacy / data handling | Programme-token holders can read runs/metrics (open audit among programme engineers); no cross-run workspace leakage; board APIs do not persist governance docs beyond forge fields supplied by caller. | inspection |
| Migration / compatibility | Schema/API additive over INIT-001; human-owned Alembic revisions for any new tables/columns; pin remains `v0.5.0-rc.2`; label-trigger removal is a breaking ops change for 002 programmes (document in README/CHANGELOG). | inspection + migration review |
| Rollback / recovery | Disable wave-start route or stop worker to halt new dispatches; runs reconstructable from Postgres + status API when PR visibility fails; board creates retry via idempotency. | runbook inspection |
| Operations / support | Document API wave-start, PR naming config, board API usage, and laptop `gh` vs deploy ForgeClient split (FR-26b); production-path `gh`-free verification procedure; PE alert channel for PR-open failure per Q-5 default until decided. | docs + verify |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | INIT-GATEFLOW-001 control plane is delivered in this repo (W0+W1 human_approved) | PRD A1; as-built `implementation-status.md` | PE | confirmed | As-built regresses below W1 |
| A-2 | prayog-skills pin **`v0.5.0-rc.2`** with `dispatch` remains the consumer target | PRD; `.harness-pin.yaml` | PE | confirmed | Pin retracted |
| A-3 | GitHub App installation token available for ForgeClient in deployment | PRD A2 | PE | confirmed | App install blocked |
| A-4 | App permissions suffice for PR create/comment and board create/list/status/link (including Projects where used) | PRD A3; IM-04 | PE | open | Permissions insufficient for W2 board exit — see Q-4 |
| A-5 | Programme service token authenticates wave-start and ops/board APIs (extends INIT-001 read model) | PRD A4; ADR-002 may need extension | PE | confirmed for product intent | Token model replaced by RBAC/JWT |
| A-6 | Board-seed skill remains SSOT for *what* to seed; Gateflow board APIs are dumb apply primitives | PRD A5; Decision #4 | PE | confirmed | Skill ownership moves into Gateflow |
| A-7 | **No `programme.yaml`.** Notifier + findings/metrics/hop-cap live in env (`GATEFLOW_*`); handoff scan globs are code constants; runner/model + PR targeting are wave-start API fields; pin remains process SSOT. | ADR-004 (carrier is TDD); FR-15/16/18 | PE | confirmed | Reintroduce shared overlays via meta |
| A-8 | Exact HTTP paths/schemas may be finalized in TDD while product FRs stay normative | PRD OQ #1; IM-01 | PE | open | Product changes FR semantics |
| A-9 | ADR-001 dual API+worker + Postgres RunStore remains topology for 002 | ADR-001 Accepted | Eng | confirmed | Topology ADR superseded |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact HTTP paths and request/response schemas for FR-15 / FR-20 / FR-21 / FR-24 (PRD OQ #1 / IM-01) | PE | no | technical review / W0 | Mount under `/api/v1` with programme-token dependency (extend ADR-002 write surfaces); OpenAPI models in `src/models/`; product FRs remain normative | open | pending — meta PR #10 / IM-01 |
| Q-2 | PE | PR head/base from wave-start (`initiative_id`, `wave_id`, `branch_slug`, `base_branch`); no programme `pr.branch_prefix` | PE | no | W1 PR-at-start | Fail-fast at API; TDD §3.1/§8 | resolved | TDD Q-2 |
| Q-3 | PE | Board API list filters (by initiative label, project, state, etc.) (PRD OQ #3 / IM-03) | PE | no | W2 board APIs | Narrow filter set in TDD; dumb primitives only — no governance parsing | open | pending — IM-03 |
| Q-4 | PE | Assumption A-4 / PRD A3 App/Projects permission matrix (PRD OQ #5 / IM-04) | PE | no | W2 board create/list exit | Confirm matrix in technical review before W2 exit; block W2 exit if permissions missing | open | pending — IM-04 |
| Q-5 | PE | PE alert channel when run-start / terminal PR open or update fails beyond status API + `notify_pending` (PRD OQ #6 / IM-05) | PE | no | W1 error path | status API + `notify_pending` until dedicated alert decided | open | pending — IM-05 |
| Q-6 | PE | ADR-002 today scopes programme token to **read-only** status/metrics — confirm extension to wave-start + board **write** APIs under same token (no per-user RBAC) | PE | no | technical review / ADR amend | Extend ADR-002 trust zone to programme-token **mutations** for documented write routes; revisit if RBAC required | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #10 head `8f291367134a686baaf650835a89dba92e887051` = APPROVED review `4770823317` `commit_id`; map rev 1; PRD digest match; label `impact-map-lgtm`; gateflow affected with scope digest; not deferred/blocked |
| D2 Complete PRD traceability | PASS | PRD FR-15…FR-26b, US-1…US-6, wave-run preconditions, Decisions #1–10 mapped; inherited INIT-001 FRs cited |
| D3 Repo-bounded scope | PASS | Matches impact-map gateflow scope digest; gateflow-ops deferred; skills/launchpad monitor-only; FR-26b documented as non-runtime |
| D4 Observable acceptance | PASS | Each FR has observable criteria + evidence type |
| D5 Negative/failure paths | PASS | Auth, identity, preconditions, stubs, concurrent, PR failures, board partials, `gh` forbid, metrics errors covered |
| D6 Assumptions/questions | PASS | A-1…A-9 with status; Q-1…Q-6 non-blocking with defaults |
| D7 Cross-repository contracts | PASS | CTR-01…CTR-05 with shapes/invariants/tests planned; CTR-04 consumer deferred noted |
| D8 NFR applicability | PASS | All eight NFR rows populated |
| D9 As-built alignment | PASS | Overview + FR notes distinguish INIT-001 existing vs 002 changed/new |
| D10 Dependency order | PASS | Aligns with map §7: pin → W0 → W1 → W2 → gateflow-ops deferred |
| D11 Zero unresolved blockers | PASS | No blocking questions; Q-1…Q-6 have safe defaults |
| D12 Output completeness | PASS | Header, FR/NFR/contracts/questions, D-summary, PR readiness, handoff envelope present |

**Draft verdict:** PASS

Do not advance to `/initiative-feasibility` unless the verdict is PASS and the
developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-002-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-002] Spec — gateflow` |
| PR type | **Draft** (entire spec lifecycle) |
| Files to commit | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`, `docs/specification/README.md` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** The agent must present this section in
chat and ask whether to create or update the Draft spec PR. Continue only after
explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-002 — API-triggered waves & platform readiness (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/10
- Approved meta head: `8f291367134a686baaf650835a89dba92e887051`
- Impact-map revision: 1
- PRD digest: `sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c`
- Repo scope digest: `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901`

## Spec path

`docs/specification/product/INIT-GATEFLOW-002-gateflow.md`

## Summary

- 13 FRs (FR-15…FR-26b) for API-first wave start, per-node runner/model, fail-closed stubs, PR-at-run-start, run/metrics/board APIs, ForgeClient-only deploy path
- Open engineering questions (non-blocking): Q-1…Q-6 (paths/schemas, PR naming, board filters, App permissions, PR-failure alert, ADR-002 write-token extension)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice committed on this PR head
- [ ] Feasibility report (later commit)
- [ ] Technical design + ADRs (later commit)
- [ ] Implementation plan §9 (later commit)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [ ] Scope matches the approved impact-map repo scope digest
- [ ] FRs and acceptance criteria are complete
- [ ] Contracts and NFR applicability are explicit
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Never infer approval from labels
alone — `spec-lgtm` requires matching artifacts on the exact PR head.

Provision labels before PR creation when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-002.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/10
- Spec PR: https://github.com/drivestream-lab/gateflow/pull/10
- Service profile: not present (`docs/specification/product/00-service-profile.md`)
- Predecessor spec: `docs/specification/product/INIT-GATEFLOW-001-gateflow.md`
- As-built: `docs/specification/as-built/implementation-status.md`

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
    digest: sha256:98f8d3fadf1d1f75f81b293678e3bb24338ca1e3618cf8459b0a7a104cd21605
  blockers: []
  signals:
    pr_ready: true
    draft_verdict: PASS
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/10
    meta_pr_head_sha: 8f291367134a686baaf650835a89dba92e887051
    map_revision: 1
    prd_digest: sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c
    scope_digest: sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901
    open_questions: [Q-1, Q-2, Q-3, Q-4, Q-5, Q-6]
    blocking_questions: []
  next_candidates:
    - initiative-feasibility
  human_checkpoint: true
  external_action: true
```
