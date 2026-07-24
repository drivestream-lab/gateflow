# INIT-GATEFLOW-003 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-003 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-003.md` |
| PRD digest | `sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/11 |
| Meta PR approved head | `4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-003.md` |
| Impact-map revision | `2` |
| Repo scope digest | `sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85` |
| Tech-lead approval | Review `4773322287` by `0xbeefdead`, APPROVED at `2026-07-24T12:55:22Z`; `commit_id` = approved head (map_revision 2 attestation); https://github.com/drivestream-lab/prayog-meta/pull/11#pullrequestreview-4773322287 |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-24 |
| Status | Draft — dev review required before committing |

## Overview

This repo delivers **live Cursor AgentRunner** in the Gateflow worker on top of the
delivered INIT-GATEFLOW-001 / INIT-GATEFLOW-002 control plane: when programme
config resolves `runner: cursor` for a `dispatch: orchestrated` skill, the worker
runs a **real Cursor coding agent** that performs **live coding work** (no
stand-in / empty success). Gateflow **triggers every** resolved
`dispatch: orchestrated` skill per the pinned workflow — **no** hardcoded node
allowlist. Unsupported / not-live runners and Cursor auth/start/crash **fail
fast**. Stage and wave **cycle-time** fields are persisted and exposed on existing
run/metrics APIs, including **p50/p95** for `runner=cursor`.

**Out of scope for this repo:** gateflow-ops BFF/UI; Launchpad product features;
cloud Cursor agents; live OpenCode / Claude Code / Slack / Teams; rebuilding
wave-start / PR-at-start / board / ForgeClient platform from 001/002; pin
`dispatch` content edits (owned by **prayog-skills** supporting delivery);
hardcoding orchestrated node lists or Cursor brand in PolicyEngine.

**As-built baseline (INIT-001 + INIT-002 W0–W2, human_approved):** API wave start,
per-node runner/model resolve, fail-closed adapter registry (ADR-006), PR-at-start
+ Notifier, run/metrics/board APIs, ForgeClient-only deploy path. **Cursor path
today:** `CursorAgentRunner` is a **W1 stub** (`mock-*` / `GATEFLOW_AGENT_STUB`) —
real SDK deferred. Stage timestamps + `runner` / `model_profile` / `model_id` and
metrics p50/p95 by node/runner/`model_id` exist; **wave cycle-time field** and
**live Cursor prove-it** do not. Pin `v0.5.0-rc.2`: Scenario B skills already
`dispatch: orchestrated`; Scenario A eng skills remain `manual` until
prayog-skills supporting pin edit.

**Delivery waves (product-normative; exact split may adjust in plan):** W0 live
Cursor skeleton + config/credential fail-fast; W1 Scenario B prove-it + crash/auth
fail-fast + stage/wave cycle-time; W2 Scenario A prove-it (after pin support) +
post–Gate 2 Scenario A still runnable + metrics p50/p95 for `runner=cursor`.

## Functional requirements

| ID | Requirement | PRD source | Acceptance criteria | Evidence type |
|----|-------------|-----------|---------------------|---------------|
| REQ-27 | Make **Cursor AgentRunner live** in the worker: for every resolved `dispatch: orchestrated` skill with resolved `runner: cursor`, invoke a **live** Cursor agent that performs **live coding work** in the workspace (stand-in / stub / empty success does **not** satisfy). Gateflow must **not** hardcode a node allowlist — pin `dispatch` is SSOT. **Prove-it:** Scenario B skill set `pre-implement`, `loop-spec`, `verify`, `ground-spec` (W1); Scenario A skill set `spec-draft`, `initiative-feasibility`, `spec-technical-review`, `spec-implementation-plan` when those nodes are `orchestrated` in the pin (W2; pin content owned by prayog-skills). Intended programme config `cursor` + `auto` (overridable). After Gate 2 opens, Scenario A remains triggerable when orchestrated. Human-checkpoints between skills are **expected stops**, not AgentRunner failures. Harness/skills/MDC remain from programme pin / existing Launchpad sync. Supersedes INIT-002 FR-17 **product meaning** of “Cursor implemented” for live exit. | PRD §2 FR-27, US-1; Success Criteria; Decisions #8/#12; A5/A6; impact-map gateflow scope | Orchestrated ⇒ AgentRunner invoked with no hardcoded node list; live Cursor produces workspace coding work + RunStore stages with `runner=cursor` for Scenario B set; after supporting pin, same for Scenario A set; human-checkpoint mid-scenario → stopped (not `failed`); post–Gate 2 Scenario A node still dispatchable when orchestrated; `GATEFLOW_AGENT_STUB` / `mock-*` stand-in must not be the production `runner=cursor` success path (see Q-3). | unit + integration + live verify |
| REQ-28 | Resolve runner (and model profile) from **gateflow programme config** (`runner.default` + per-`workflow_node` overrides from INIT-002 FR-16). Selecting OpenCode, Claude Code, or any **unknown / not-live** runner id required for the run **blocks at start** with structured error naming runner id + config key — **never** silent substitute with Cursor. Extends INIT-002 FR-18 honesty for “not live” vs stub. | PRD §2 FR-28, US-2; Programme Config; Decision #10; Error Handling | Config with required `opencode` / `claude` / unknown → reject/fail at start; 0 Cursor dispatches; 0 silent fallback; PolicyEngine does not hardcode brand allowlists. | unit |
| REQ-29 | **Fail fast** on missing/invalid Cursor credentials/auth material, inability to start Cursor, timeout, or crash: stop run; `outcome: failed`; record + notify as today; **no pretend success**; no workflow advance on AgentRunner failure. Adds wave-run precondition **#12** when resolved runner is `cursor`. | PRD §2 FR-29, US-2; Error Handling; wave-run precondition #12; Decision #9 | Absent/invalid Cursor auth → fail before or at AgentRunner start; start/timeout/crash → `failed` + PR/status visibility; 0 invented successful coding stages. | unit + live verify |
| REQ-30 | Persist and expose **defined cycle-time metrics**: every live Cursor orchestrated stage records `started_at`, `ended_at`, `duration_ms`, `runner`, `model_profile`, `model_id`, `outcome`; every run that dispatches live Cursor records **wave cycle time** from API accept/enqueue to stop at next contract node **or** terminal `failed` (`wave_duration_ms` on the run — TDD §3.4); metrics API returns **p50 and p95** stage `duration_ms` for `runner=cursor` via the existing **`by_runner`** aggregate dimension (select row `key=cursor`; no new query param required for 003 — TDD PE-3) and by `workflow_node` when data exists. Extends INIT-002 FR-20/FR-21; sponsor SLA thresholds are **not** exit gates. | PRD §2 FR-30, US-3; §4 Cycle-time metrics; Success Criteria; Decision #11 | 100% live Cursor stages have named fields (success **and** AgentRunner failure); `wave_duration_ms` present on qualifying runs; `GET /metrics/runs` `by_runner` includes cursor p50/p95 when ≥1 sample; fields queryable via existing run/metrics APIs (no ops UI). | unit + live verify |
| REQ-31 | **Reuse** INIT-001/002 control plane: wave-start API, PR-at-start thread, Notifier comments, contract stops, RunStore, run/metrics/board APIs, ForgeClient deploy path — **consume, do not rebuild**. No new Launchpad product features. prayog-skills / harness remain SSOT for workflow. Zero auto human-gate transitions; zero auto-merge. | PRD §2 FR-31, US-4; Non-Goals; Scope boundary; Decision #6/#7 | Existing 002 paths remain authoritative; no parallel control-plane rewrite; Launchpad changes out of scope; contract-stop tests still pass. | inspection + unit (inherit) |

> **Id convention:** `REQ-*` is canonical. Legacy display alias `FR-{nn}` ≡ `REQ-{nn}`
> (same number) — PRD rows FR-27…FR-31 map 1:1 to REQ-27…REQ-31.

**Inherited (unless superseded above):** INIT-GATEFLOW-001 FR-1, FR-3–FR-8,
FR-10–FR-12, FR-14 remain in force as applicable under 002 supersessions.
INIT-GATEFLOW-002 FR-15–FR-16, FR-18–FR-26b remain in force. **INIT-002 FR-17
product meaning of “Cursor implemented” is satisfied only when REQ-27 is met**
(live Cursor agent + live coding work). FR-6 remains the AgentRunner interface
contract; REQ-27 is the live Cursor fulfillment.

### Wave-run preconditions (delta)

Inherits INIT-GATEFLOW-002 wave-run preconditions. Additional / clarified:

| # | Precondition | Spec REQ |
|---|--------------|----------|
| 10 | Resolved runner + notifier for this run are **implemented / live** where required (not stubs / not-live) | inherit FR-18; REQ-28 |
| 11 | Resolved runner/model config for required orchestrated nodes is **valid** | inherit FR-16 |
| **12** | If resolved runner is `cursor`, **Cursor worker credentials / auth material** required for live AgentRunner are present and usable — else **fail fast** (no dispatch or immediate `failed`) | REQ-29 |

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-28 | Required runner is OpenCode, Claude Code, unknown, or not-live | Block at start; structured error with runner id + config key; 0 dispatches; no Cursor substitute | unit |
| REQ-29 | Missing/invalid Cursor credentials | Fail fast; run `failed` or start rejected; notify/PR as today; 0 pretend success stages | unit + live verify |
| REQ-29 | Cursor cannot start | Stop; `failed`; no workflow advance; PR + RunStore | unit + live verify |
| REQ-29 | Cursor timeout / crash mid-stage | Stop; `failed`; no workflow advance; PR + RunStore | unit + live verify |
| REQ-27 | Human-checkpoint / gate between Scenario A or B skills | **Expected stop** — not AgentRunner failure; prove-it may resume after human or use multiple runs | unit + live verify |
| REQ-27 | Cursor completes then contract stop reached | Stop at contract node (automation success path); human owns next step | unit (inherit) |
| REQ-30 | Metrics persist failure | Do not invent success metrics; preserve run outcome; flag for ops | unit |
| inherit | INIT-002 auth / precondition / ForgeClient / stub failures | Unchanged from INIT-GATEFLOW-002 Error Handling | unit |
| inherit | Contract stop / `human_checkpoint: true` | Stop; record; comment; no auto-transition; no gate-label writes; no auto-merge | unit (inherit) |

## Out of scope for this repo

- **gateflow-ops** BFF/UI (deferred; cycle-time via existing APIs) — impact-map §3
- **prayog-skills** pin `dispatch: orchestrated` edits for Scenario A (supporting delivery in that repo; gateflow **consumes** pin only) — CTR-01
- **launchpad** product features (existing harness sync only; Decision #7)
- Cloud Cursor agents / cloud agent runtime
- Live OpenCode / Claude Code; live Slack / Teams notifiers
- Rebuilding API wave-start / board APIs / PR-at-start platform
- Redefining SDD / skills / harness inside Gateflow
- Dogfood programme as INIT driver
- Product-mandated CI AgentRunner stub as exit evidence (unit doubles are eng detail only)
- Hardcoding orchestrated node allowlists or Cursor brand in PolicyEngine
- Pin version-bump or calendar deadline as exit gate
- Sponsor SLA thresholds (e.g. beat manual N minutes)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow / prayog-pe-team | Pinned `workflow.yaml` + `dispatch`; Scenario A nodes become `orchestrated` for 003 exit | `handoff.stage`, `handoff.outcome`, `dispatch` | Next node + orchestrated eligibility | Orchestrated ⇒ triggerable; no Gateflow allowlist; missing `dispatch` ⇒ manual | Pin unavailable ⇒ block + notify | Pin content change (no version-bump exit gate); consumer still `.harness-pin.yaml` | Planned: unit pin fixtures + W2 live verify after skills pin |
| CTR-02 | Cursor SDK (external) / prayog-pe-team | gateflow / prayog-pe-team | Live AgentRunner in worker (`run_skill` FR-6 I/O) | workspace, skill_id, prompt_context, model profile, credentials | `AgentRunResult` + live coding work | Local/non-cloud worker path only this INIT; no pretend success | Auth/start/timeout/crash ⇒ `failed` (REQ-29) | New live path; supersedes stub for `runner=cursor` | Planned: unit + live verify Scenario B/A |
| CTR-03 | gateflow / prayog-pe-team | clients / tools / future gateflow-ops | Run detail + metrics APIs (extends FR-20/21) | Programme token + filters | Stage/wave cycle-time fields; p50/p95 for `runner=cursor` | Fields match §4 normative defs; no ops UI required | 401/400/503 per existing API errors | Additive over INIT-002 metrics | Planned: `tests/unit/` + `tests/verify/` |
| CTR-04 | launchpad / prayog-pe-team | gateflow / prayog-pe-team | Worker harness sync pre-dispatch | Workspace / pin | Synced harness tree | Sync before AgentRunner; Launchpad does **not** select Cursor | Sync failure ⇒ run `failed` + notify | Unchanged from 001/002 | Worker integration / verify (inherit) |
| CTR-05 | gateflow / prayog-pe-team | GitHub (forge) | ForgeClient + Notifier | PR/comment payloads | Forge resource ids | Unchanged from 002; no auto-merge; no gate-approval labels | Retry + `notify_pending` | Unchanged | Unit + verify (inherit) |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Cursor credentials via programme secret/config — never committed; missing → fail fast (REQ-29). Programme service token for APIs unchanged. ForgeClient App token in production unchanged. Zero gate-approval label writes; zero auto-merge. Cloud Cursor agents out of scope. | unit + inspection + verify |
| Reliability | Fail-closed at start for not-live runners (REQ-28) and Cursor auth (REQ-29); AgentRunner crash stops run without workflow advance; contract stops remain authoritative. | unit + live verify |
| Performance / capacity | Define and ship cycle-time metrics (REQ-30); numeric sponsor SLAs are **not** exit gates this INIT. | unit + live verify (metrics presence) |
| Observability | Structured loguru logging with correlation id; RunStore stage + wave cycle-time fields; metrics p50/p95 for `runner=cursor`; PR/status visibility on failures. | inspection + verify |
| Privacy / data handling | Programme-token holders can read runs/metrics; Cursor credentials not logged in full; no cross-run workspace leakage. | inspection |
| Migration / compatibility | Additive over INIT-002 RunStore/metrics; human-owned Alembic if new columns (e.g. wave duration — Q-2); pin consumer remains compatible when Scenario A becomes orchestrated. | inspection + migration review |
| Rollback / recovery | Stop worker or disable Cursor credentials / set not-live to halt live dispatches; runs reconstructable from Postgres + status API; stand-in path must not silently re-enable as live success (Q-3). | runbook inspection |
| Operations / support | Document Cursor secret injection (Q-1), prove-it Scenario A/B runbooks, and cycle-time field names; PE owns credential ops. | docs + verify |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | INIT-GATEFLOW-001 and INIT-GATEFLOW-002 are finished/delivered for control-plane reuse | PRD A1 User-confirmed; as-built W0–W2 human_approved | PE | confirmed (reconcile meta #10 separately — Q-4) | As-built regresses below 002 W2 |
| A-2 | Cursor agent can run in Gateflow’s programme-like worker (non-cloud) | PRD A2 User-confirmed | PE | confirmed | Only cloud path available |
| A-3 | Programme can supply Cursor auth material to the worker without repo commits | PRD A3; fail-fast if absent | PE | confirmed posture; shape open (Q-1) | Secret injection impossible |
| A-4 | Existing metrics/run APIs can expose new cycle-time fields without gateflow-ops UI | PRD A4; CTR-03 | PE | confirmed | Product requires new UI for exit |
| A-5 | Prove-it uses Scenario A and B skill **sets** as named in PRD; orchestrated ⇒ triggered; live coding work evidence; intended `cursor` + `auto` | PRD A5; Decision #8 | PE | confirmed | Product changes skill sets |
| A-6 | Scenario B already orchestrated in today’s pin; Scenario A **must** be orchestrated in pin for 003 exit (prayog-skills supporting) | PRD A6; local pin `v0.5.0-rc.2` (A=manual, B=orchestrated) | PE | confirmed | Pin retracts Scenario A orchestrated |
| A-7 | ADR-001 dual API+worker + Postgres RunStore and ADR-006 fail-closed registry remain topology/selection rules | Accepted ADRs | Eng | confirmed | ADR superseded |
| A-8 | FR-6 AgentRunner I/O remains the adapter contract; REQ-27 is live Cursor fulfillment | PRD §3; Scope boundary | Eng | confirmed | FR-6 I/O redesign |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact Cursor credential / secret injection shape for the worker (env var names, file path, SDK auth object) — PRD OQ #1 / IM-01 | PE | no | W0/W1 | `CURSOR_API_KEY` via `CursorAgentSettings` (TDD §3.1); fail-fast if absent | resolved | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md` §3.1 / §9 |
| Q-2 | PE | Exact RunStore field names for wave cycle time if not already present (`wave_duration_ms` vs derived from accept→stop timestamps) — PRD OQ #2 / IM-02 | PE | no | W1 | Explicit `runs.wave_duration_ms` + run detail (TDD §3.4) | resolved | TDD §3.4 / §9 |
| Q-3 | PE | Whether leftover stand-in code (`GATEFLOW_AGENT_STUB` / `mock-*`) is deleted vs unreachable when `runner=cursor` — PRD OQ #3 / IM-03 | PE | no | W1 exit | Quarantine — test doubles only; not REQ-27 evidence (ADR-007) | resolved | `docs/specification/adr/adr-007-agent-runner-live-readiness.md` |
| Q-4 | PE | Confirm gateflow runtime delivery of INIT-002 is complete for A-1 given meta PR [#10](https://github.com/drivestream-lab/prayog-meta/pull/10) still open — IM-04 | PE | no | W0 start | Proceed per PRD A1 User-confirmed + as-built human_approved W2; reconcile meta PR separately | open | pending — IM-04 |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #11 head `4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5` = APPROVED review `4773322287` `commit_id`; map rev 2 attestation; PRD digest `sha256:6062fa11…f9ad` matches file sha256; gateflow affected with scope digest `sha256:aaf398dc…eba85`; not deferred/blocked. Note: Gate 1 labels still show `impact-map-pending` + `impact-map-revised` (no `impact-map-lgtm`) — label projection lag; **APPROVED review is authoritative** per impact-map §12 / skill handoff gate |
| D2 Complete PRD traceability | PASS | PRD FR-27…FR-31 / US-1…US-4 / Success Criteria / Decisions #1–12 / A1–A6 / Error Handling mapped to REQ-27…REQ-31; inherited 001/002 FRs cited |
| D3 Repo-bounded scope | PASS | Matches impact-map gateflow scope digest; prayog-skills pin edits out of scope here; gateflow-ops deferred; launchpad monitor-only |
| D4 Observable acceptance | PASS | Each REQ has observable criteria + evidence type |
| D5 Negative/failure paths | PASS | Unsupported runners, auth, start/crash, checkpoints, metrics persist, inherited 002 paths covered |
| D6 Assumptions/questions | PASS | A-1…A-8 with status; Q-1…Q-4 non-blocking with defaults |
| D7 Cross-repository contracts | PASS | CTR-01…CTR-05 with shapes/invariants/tests planned |
| D8 NFR applicability | PASS | All eight NFR rows populated |
| D9 As-built alignment | PASS | Overview distinguishes stub Cursor + existing metrics vs new live path + wave cycle-time |
| D10 Dependency order | PASS | Aligns with map §7: W0 → W1 Scenario B → skills pin → W2 Scenario A → ops deferred |
| D11 Zero unresolved blockers | PASS | No blocking questions; Q-1…Q-4 have safe defaults |
| D12 Output completeness | PASS | Header, REQ/NFR/contracts/questions, D-summary, PR readiness, handoff envelope present |

**Draft verdict:** PASS

Do not advance to `/initiative-feasibility` unless the verdict is PASS and the
developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-003-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-003] Spec — gateflow` |
| PR type | **Draft** (entire spec lifecycle) |
| Files to commit | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`, `docs/specification/README.md` |
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

INIT-GATEFLOW-003 — Live Cursor AgentRunner (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/11
- Approved meta head: `4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5`
- Impact-map revision: 2
- PRD digest: `sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad`
- Repo scope digest: `sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85`

## Spec path

`docs/specification/product/INIT-GATEFLOW-003-gateflow.md`

## Summary

- 5 REQs (REQ-27…REQ-31) for live Cursor AgentRunner, fail-fast unsupported runners + Cursor auth/crash, stage/wave cycle-time + p50/p95, reuse 001/002 control plane, Scenario A/B prove-it
- Open engineering questions (non-blocking): Q-1…Q-4 (credential shape, wave duration field names, stand-in quarantine, INIT-002 meta #10 reconcile)

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

- PRD: `prayog-meta/prd/INIT-GATEFLOW-003.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/11
- Spec PR: pending
- Service profile: not present (`docs/specification/product/00-service-profile.md`)
- Predecessor specs: `docs/specification/product/INIT-GATEFLOW-001-gateflow.md`, `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`
- As-built: `docs/specification/as-built/implementation-status.md`
- ADRs: `docs/specification/adr/` (ADR-001…ADR-006 Accepted; live Cursor may need follow-on ADR in technical review)

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
    digest: sha256:4ad05073046c55ad07f778dbaa36e52eaa80cae5b15129be60ef9452467fa6d9
  blockers: []
  signals:
    pr_ready: true
    draft_verdict: PASS
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/11
    meta_pr_head_sha: 4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5
    map_revision: 2
    prd_digest: sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad
    scope_digest: sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85
    gate1_label_projection: lagging-pending-revised-without-lgtm
    open_questions: [Q-1, Q-2, Q-3, Q-4]
    blocking_questions: []
  next_candidates:
    - initiative-feasibility
  human_checkpoint: true
  external_action: true
```
