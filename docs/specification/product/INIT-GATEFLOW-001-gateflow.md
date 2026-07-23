# INIT-GATEFLOW-001 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-001 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-001.md` |
| PRD digest | `sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/9 |
| Meta PR approved head | `d62a9bbcf5960c50c4429dd33bb206208dbbf246` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-001.md` |
| Impact-map revision | `3` |
| Repo scope digest | `sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0` |
| Tech-lead approval | Review `4763369852` by `0xbeefdead`, APPROVED at `2026-07-23T10:54:32Z`; `commit_id` = approved head (map_revision 3 attestation) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-23 |
| Status | Draft — dev review required before committing |

## Overview

This repo delivers the Gateflow **W1 delivery control plane**: FastAPI webhook ingress
with fast ack, PostgreSQL RunStore + job queue, async worker owning PolicyEngine /
AgentRunner / ForgeClient side effects, programme-config-driven trigger
(`gateflow:run-wave`), handoff-driven workflow resolution against pinned
prayog-skills **`v0.5.0-rc.2`** (`dispatch: orchestrated`), contract stops, metrics
v0, and a programme-token status/metrics JSON API.

**Out of scope for this repo (W1):** gateflow-ops BFF/UI; Slack/Teams notifiers;
commit-status progress; multi-runner / LiteLLM; ToolProvider beyond `none`;
queue/supersede of concurrent runs; formal PE cancel API; changes to prayog-skills
or launchpad product surfaces (consume only).

**As-built baseline:** Python FastAPI scaffold exists (`src/app.py`, health,
JWT AuthMiddleware, DI, Postgres/Redis infra stubs). No webhook, RunStore domain
schema, worker, PolicyEngine, or status/metrics routes are implemented yet.
`docs/specification/as-built/implementation-status.md` is not yet populated.

## Functional requirements

| ID | Requirement | PRD source | Acceptance criteria | Evidence type |
|----|-------------|-----------|---------------------|---------------|
| FR-1 | Expose GitHub App webhook ingress that validates App signature, persists delivery/event id for idempotency, and enqueues work without blocking the HTTP response. | PRD §2 FR-1; Decision #6 | Invalid signature → HTTP 401 and no run; duplicate delivery id → no second run; valid delivery → accepted (2xx/202) and job enqueued; Postgres unavailable → HTTP 503 so GitHub retries. | unit + live verify |
| FR-2 | Reject concurrent wave runs for the same PR or issue; do not queue or supersede in W1. | PRD §2 FR-1; Decision #2; wave-run precondition #6 | If an active run exists for the same PR/issue, no new run is created; ForgeClient posts a block comment naming concurrent-run rejection. | unit + integration |
| FR-3 | Authorize wave runs only via programme-configured trigger label loaded from gateflow programme config (not harness/meta YAML; not hardcoded). | PRD §2 FR-2, US-1; Decision #3; Programme Config | Default W1 label `gateflow:run-wave` from config key `trigger.label`; non-matching labels do not authorize runs; no board-state-only inference of run intent. | unit + live verify |
| FR-4 | Enforce the full wave-run precondition checklist before PolicyEngine may dispatch. | PRD §2 wave-run preconditions; US-1 | Failure of any precondition → ForgeClient comment with failed precondition id/reason and **no** AgentRunner dispatch; success path creates RunStore run within 30s of webhook delivery under normal load. | integration + live verify |
| FR-5 | Persist runs, stages, events, and async jobs in PostgreSQL (no SQLite fallback). | PRD §2 FR-3; Decision #6 | Schema supports at least `run_id`, `workflow_node`, `outcome`, timestamps, retry counter, `notify_pending`; run timeline reconstructable from DB alone. | unit + inspection |
| FR-6 | Implement HandoffReader: resolve git ref from triggering PR head when label is on a PR; on issue trigger without linked PR use `handoff.ref_fallback` (default `default_branch`); scan `handoff.artifact_globs` for latest durable `handoff:` YAML block. | PRD §2 FR-4; Decision #5 | Parse failure or missing handoff blocks the run with ForgeClient comment; no chat/session fallback; PR vs issue ref behaviour matches config keys. | unit + integration |
| FR-7 | Implement WorkflowEngine + PolicyEngine against installed contract `sdd-delivery/v2` and pin **`v0.5.0-rc.2`**: resolve next node from `handoff.stage` + `handoff.outcome`; dispatch only when `type: skill` **and** `dispatch: orchestrated`; never hardcode node allowlists. | PRD §2 FR-5; §3 Dispatch Preconditions; Decision #13 | Missing/`manual` dispatch (legacy pin) → treat as non-dispatch (manual); pin/orchestration unavailable → **block + ForgeClient comment** (Decision #9), never silent no-op; CI fixtures cover navigation + dispatch policy. | unit + contract tests |
| FR-8 | Stop without dispatch on `human-checkpoint`, `external-action`, `decision`, and `terminal` nodes; honor `handoff.human_checkpoint: true` and unresolved `handoff.blockers`. | PRD §2 FR-8; US-3 | Zero auto-transitions of human gates; stop events recorded with `workflow_node`, `node_type`, timestamp; PE-visible stop comment includes node id and reason. | unit + integration |
| FR-9 | Provide Cursor `AgentRunner` adapter: workspace + skill prompt + `model_profile` → `RunResult` with `runner`, `model_id`, `outcome` (and provider when available). | PRD §2 FR-6; §3 Tool & Runner | On failure/timeout: stop run, persist `outcome: failed`, notify PE, do not advance workflow; interface documented for H2 runners. | unit + live verify |
| FR-10 | Enforce programme-config `retry.findings_budget` (default 3) on `findings` loops; persist counter on run; expose via status API. | PRD §2 FR-7, US-5; Decision #11 | Exhaustion → stop run + structured ForgeClient comment (reason, retry count, last node); **no** GitHub issue creation and **no** auto-route to another checkpoint. | unit + integration |
| FR-11 | Fan out structured run events through Notifier → ForgeClient as PR/issue comments only (H1): `run_id`, `workflow_node`, `event` (`stage_started` \| `stage_completed` \| `run_stopped`), `outcome`, `duration_ms`, `timestamp`. | PRD §2 FR-9, US-2; Decision #1 | Start/end/stop/budget-exhaustion comments posted via GitHub API (no `gh` CLI in production); no commit-status checks in W1. | integration + live verify |
| FR-12 | Implement ForgeClient outbound GitHub access: comments, PR create/update, programme **run-status** labels; forbid gate-approval label writes and auto-merge. | PRD §2 FR-14, US-3 | Audit log shows zero gate-label writes and zero auto-merge calls for MVP scope; comment API failure → retry with backoff and/or set `notify_pending` on run. | unit + inspection |
| FR-13 | Emit metrics events per PRD metrics schema; expose `GET /metrics/runs` JSON aggregate (p50/p95 by `workflow_node`); retain events per `metrics.retention_days` (default 90); document SQL view for PE. | PRD §2 FR-10, US-4; Decision #7 | Orchestrated stages record `started_at`, `ended_at`, `outcome`, `runner`, `model_id` where available; at least one gate-interval metric uses label names from pinned `delivery-contract.yaml`; no scheduled export in W1. | unit + live verify |
| FR-14 | Wire `StageToolResolver` / ToolProvider slots; H1 implementation returns empty tool context (`none`). | PRD §2 FR-11 | Slot resolution from programme config / workflow metadata only — no hardcoded node→slot map; swapping provider does not require PolicyEngine changes. | unit |
| FR-15 | Expose read-only status JSON API authenticated with programme service token (shared among programme engineers; network boundary in W1). | PRD §2 FR-12, US-3; Decision #4 | Endpoint returns run id, current stage, outcome, timestamps, retry counter, history sufficient for W1 without gateflow-ops; unauthenticated → 401; wrong token → 401/403. | unit + live verify |
| FR-16 | Resolve runner/model from gateflow programme config: H1 single `default` profile for all orchestrated wave skills; persist `runner`, `model_profile`, `model_id`, `model_provider` on orchestrated stages when available. | PRD §2 FR-13; Decision #8 | Per-`workflow_node` overrides remain empty/`{}` in H1; config change does not require PolicyEngine code change. | unit |
| FR-17 | Ship W1 runtime as API process + async worker (Postgres job table); worker performs harness sync via launchpad before AgentRunner when dispatching. | PRD §4 Architecture / Deployment; W1 exit #1; CTR-04 | Health endpoint 200; webhook returns quickly while worker claims jobs; worker invokes launchpad sync on workspace before agent start. | live verify + inspection |
| FR-18 | Load W1 programme config from this repo (keys: trigger, handoff refs/globs, retry budget, metrics retention, runner default, model profiles/overrides, tools.slots). | PRD §4 Programme Config; Decisions #3,#5,#7,#8 | All listed keys load without code change for value updates; missing required keys fail fast at startup or first use per fail-fast policy. | unit + inspection |
| FR-19 | Deliver W1 documentation runbook: “Orchestrate a new initiative repo” (App install + programme config + skills pin). | PRD §5 W1 exit #11 | Runbook present under gateflow docs; PE can authorize runs without WorkflowEngine source edits. | inspection |

## Negative and failure paths

| FR | Condition | Required behavior | Evidence |
|----|-----------|-------------------|----------|
| FR-1 | Invalid webhook signature | HTTP 401; no run / no enqueue | unit |
| FR-1 | Duplicate webhook delivery | Idempotent skip; no duplicate run | unit |
| FR-1 | PostgreSQL unavailable at ingress | HTTP 503; no silent drop | unit / integration |
| FR-2 | Label while active run on same PR/issue | Reject; ForgeClient comment; no dispatch | unit + integration |
| FR-4 | Any wave-run precondition fails | Block; comment with reason; no dispatch | integration |
| FR-6 | Handoff missing or unparsable | Block; comment with parse error; no chat fallback | unit |
| FR-7 | `handoff.contract` ≠ installed contract | Block; ForgeClient comment | unit |
| FR-7 | Legacy pin / `dispatch` unavailable | Block + comment (Decision #9); never silent no-op | unit |
| FR-7 | Resolved skill `dispatch != orchestrated` | No AgentRunner dispatch; observe/metrics-only as applicable | unit |
| FR-8 | Next node human/external/decision/terminal or `human_checkpoint: true` | Stop; record stop event; comment; no dispatch | unit |
| FR-9 | AgentRunner timeout/crash | Stop; `outcome: failed`; notify; no workflow advance | unit + live verify |
| FR-10 | Retry budget exhausted | Stop + comment (reason, count, node); no issue; no auto-route | unit |
| FR-12 | ForgeClient 5xx / rate limit | Retry/backoff; set `notify_pending` if exhausted; recover comment when possible | unit |
| FR-15 | Missing/invalid programme service token | 401/403; no run payload leakage | unit |
| — | PE mid-run cancel | **N/A W1** — formal cancel API deferred W2 (Decision #10); W1 stops via failure / retry budget | inspection |

## Out of scope for this repo

- **gateflow-ops** BFF/UI and any ops dashboard (deferred W2+; Decision #12)
- Changes to **prayog-skills** workflow/contract contents (read-only pin consumer; CTR-01 available)
- New **launchpad** features (consume existing harness sync only; CTR-04)
- Auto-merge, auto gate-approval labels, board automation, Slack/Teams, commit status checks
- Concurrent-run queue/supersede; formal cancel API
- Multi-runner adapters, LiteLLM, ToolProvider beyond `none`
- Dogfood Phase B execution (post–W1 exit; product phase, not this FR set’s exit)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow / prayog-pe-team | Pinned `workflow.yaml` + `delivery-contract.yaml` + handoff envelope spec @ **`v0.5.0-rc.2`** | `handoff.stage`, `handoff.outcome`, contract id | Next node + `dispatch` eligibility | No hardcoded allowlists; missing `dispatch` ⇒ manual | Pin unavailable ⇒ block + comment | Pin ref in `.harness-pin.yaml`; schema `sdd-delivery/v2` | Planned: `tests/unit/` contract fixtures + pinned `workflow_scenarios.json` navigation |
| CTR-02 | GitHub (forge) / prayog-pe-team | gateflow / prayog-pe-team | GitHub App webhooks (PR, issue, label) | Signed webhook payload | HTTP ack + enqueued job | Signature required; delivery idempotency | 401 invalid sig; 503 if DB down | GitHub App webhook API | Planned: `tests/verify/` webhook signature + idempotency |
| CTR-03 | gateflow / prayog-pe-team | GitHub (forge) / prayog-pe-team | ForgeClient REST/GraphQL | Comment body / run-status label ops | GitHub comment/label result | No gate-approval label writes; no auto-merge; no `gh` CLI in prod | Retry + `notify_pending` | App installation token preferred (PAT dev-only — Q-1) | Planned: unit ForgeClient audit assertions |
| CTR-04 | launchpad / prayog-pe-team | gateflow / prayog-pe-team | Worker pre-dispatch harness sync | Repo workspace path / pin | Synced harness tree | Sync before AgentRunner | Sync failure ⇒ stop run `failed` + notify | Existing launchpad CLI/API | Planned: worker integration / verify |
| CTR-05 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Status JSON API | Programme service token + run id | Run status JSON | Read-only; no BFF required for W1 exit | 401/404 | Deferred consumer W2+; W1 ships provider shape | Planned: `tests/verify/` status API; ops consumer later |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Validate webhook signatures; secrets (App key, Postgres, deploy keys, programme token) outside repo; ForgeClient forbids gate labels/auto-merge; status/metrics APIs require programme service token; ephemeral agent worktree per run. | unit + inspection + verify |
| Reliability | Webhook idempotency; concurrent-run reject; Postgres job claim; AgentRunner/ForgeClient failure stops with durable RunStore state; GitHub retries on 503. | unit + integration |
| Performance / capacity | Webhook ack fast (API enqueues only); numeric p50 cycle-time baselines deferred until Phase B dogfood (PRD KPI TBD). W1 proves loop correctness, not load SLOs. | live verify (latency of ack) + inspection |
| Observability | Structured loguru logging with correlation id; RunStore events queryable; ForgeClient write audit retained with run; metrics aggregate endpoint. | inspection + verify |
| Privacy / data handling | No cross-run workspace leakage; audit data readable by any holder of programme service token (W1 open audit — Decision #4). | inspection |
| Migration / compatibility | New Postgres schemas via human-owned Alembic revisions; pin target `v0.5.0-rc.2`; legacy pins without `dispatch` ⇒ manual / block path (Decision #9). | inspection + migration review |
| Rollback / recovery | Disable App webhook or stop worker to halt dispatches; runs remain reconstructable from Postgres; `notify_pending` recoverable comments. | runbook inspection |
| Operations / support | Docker API + worker; health 200; W1 runbook for new-repo orchestration; Postgres-down ops alerting mechanism still product `[TBD]` — see Q-2 (non-blocking for feasibility if documented as ops follow-up). | live verify + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | prayog-skills pin **`v0.5.0-rc.2`** with `dispatch` is available (INIT-PRAYOG-SKILLS-002 delivered) | PRD Decisions #13; repo `.harness-pin.yaml` ref `v0.5.0-rc.2` | PM + PE | confirmed | Pin retracted or `dispatch` removed |
| A-2 | GitHub App can be installed on drivestream-lab programme repos | PRD A2 | PE | confirmed | App install blocked |
| A-3 | Cursor SDK can run in container/worker (not laptop-only) | PRD A3 | PE | open | SDK cannot run headless in target runtime |
| A-4 | PostgreSQL available in all Gateflow environments | PRD A4 | Eng | confirmed | Env without Postgres |
| A-5 | W1 programme config lives in gateflow repo | PRD Decision #5/#A5; impact map | PE | confirmed | Config moved to meta-only |
| A-6 | Programme service token shared among programme engineers (no per-user RBAC on audit in W1) | PRD Decision #4 / A6 | PE | confirmed | RBAC required before W1 exit |
| A-7 | Metrics retention default 90 days | PRD Decision #7 / A7 | PE | confirmed | Config changes default |
| A-8 | Single `default` model profile for all orchestrated skills in H1 | PRD Decision #8 / A8 | PE | confirmed | Per-node overrides required for W1 exit |
| A-9 | Existing JWT AuthMiddleware remains for future product routes; webhook + programme-token routes are explicit public/alternate-auth paths | Source: `src/app.py` public_paths today `/health`, `/internal` | Eng | open | Auth design ADR chooses differently |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | ForgeClient auth: App installation token only vs PAT allowed in dev? (PRD OQ #1 / IM-05) | PE | no | technical review / W0 ForgeClient | App token preferred; PAT scoped, dev-only per FR-14 | open | pending — meta PR #9 / IM-05 |
| Q-2 | PE / ops | When PostgreSQL is unavailable, beyond HTTP 503 + GitHub retry, what alert channel is required for W1 exit? (PRD Error Handling `[TBD]`) | PE | no | implementation plan / ops runbook | Document “GitHub delivery retries + operator watch on 503 rate”; dedicated alert deferred | open | pending |
| Q-3 | PE | Exact public URL paths for status and metrics (`GET /runs/{id}` vs `/api/v1/runs/{id}`, and `/metrics/runs` mount) relative to existing JWT middleware `public_paths` | PE | no | technical review | Mount under `/api/v1` with programme-token auth dependency (not JWT user auth); add paths to middleware allowlist as needed | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #9 head `d62a9bbcf5960c50c4429dd33bb206208dbbf246` = APPROVED review `4763369852` `commit_id`; map rev 3; PRD digest match; label `impact-map-lgtm`; gateflow affected with scope digest; not deferred/blocked |
| D2 Complete PRD traceability | PASS | PRD FR-1…FR-14, wave preconditions, Decisions #1–13, W1 exit themes mapped to FR-1…FR-19 |
| D3 Repo-bounded scope | PASS | Matches impact-map gateflow scope digest; gateflow-ops / skills / launchpad feature delivery excluded |
| D4 Observable acceptance | PASS | Each FR has observable criteria + evidence type |
| D5 Negative/failure paths | PASS | Webhook, concurrent, handoff, policy, runner, retry, ForgeClient, auth, cancel-N/A covered |
| D6 Assumptions/questions | PASS | A-1…A-9 with status; Q-1…Q-3 non-blocking with defaults |
| D7 Cross-repository contracts | PASS | CTR-01…CTR-05 with shapes/invariants/tests planned; CTR-05 deferred consumer noted |
| D8 NFR applicability | PASS | All eight NFR rows populated |
| D9 As-built alignment | PASS | Source scan: FastAPI scaffold only; domain control plane **new**; as-built file absent — noted in Overview |
| D10 Dependency order | PASS | Aligns with map §7: pin delivered → W0 skeleton → W1 PolicyEngine/AgentRunner → W1 exit → Phase B → ops |
| D11 Zero unresolved blockers | PASS | No blocking questions; Q-1…Q-3 have safe defaults |
| D12 Output completeness | PASS | Header, FR/NFR/contracts/questions, D-summary, PR readiness, handoff envelope present |

**Draft verdict:** PASS

Do not advance to `/initiative-feasibility` unless the verdict is PASS and the
developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-001-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-001] Spec — gateflow` |
| PR type | **Draft** (entire spec lifecycle) |
| Files to commit | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md`, `docs/specification/README.md` |
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

INIT-GATEFLOW-001 — Gateflow delivery orchestrator (W1 gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/9
- Approved meta head: `d62a9bbcf5960c50c4429dd33bb206208dbbf246`
- Impact-map revision: 3
- PRD digest: `sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d`
- Repo scope digest: `sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0`

## Spec path

`docs/specification/product/INIT-GATEFLOW-001-gateflow.md`

## Summary

- 19 FRs covering W0/W1 control plane in gateflow only (webhooks, RunStore, PolicyEngine, AgentRunner, ForgeClient, metrics, status API, programme config)
- Open engineering questions (non-blocking): Q-1 ForgeClient auth, Q-2 Postgres alert channel, Q-3 status/metrics path mounts

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

- PRD: `prayog-meta/prd/INIT-GATEFLOW-001.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/9
- Spec PR: pending
- Service profile: not present yet (`docs/specification/product/00-service-profile.md`)

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-001-gateflow.md
    digest: sha256:7df18bc66685fa3130bb0103968cd0d345de74379848104b769a9ad5b6c11ebc
  blockers: []
  signals:
    pr_ready: true
    draft_verdict: PASS
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/9
    meta_pr_head_sha: d62a9bbcf5960c50c4429dd33bb206208dbbf246
    map_revision: 3
    prd_digest: sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d
    scope_digest: sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0
    open_questions: [Q-1, Q-2, Q-3]
    blocking_questions: []
  next_candidates:
    - initiative-feasibility
  human_checkpoint: true
  external_action: true
```
