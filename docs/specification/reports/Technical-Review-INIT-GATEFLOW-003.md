# Technical Design Document — INIT-GATEFLOW-003

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-003 |
| Spec | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` |
| Spec digest | `sha256:2fa921bec645e0f60f7e9917cb0977a880374dff8d376d3829c98d5fc702bc43` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md` |
| Feasibility digest | `sha256:7fa2b2b011e5079b689c15c09071ffa5cc56f5bc7e85bea8687db3f577fd1c59` |
| PRD digest | `sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-003.md` / `2` |
| Repo scope digest | `sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85` |
| Approved meta PR head | `4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5` |
| Source freshness | CURRENT — meta PR #11 head `4c9cacb8…ece5` + APPROVED review `4773322287` + PRD/map/scope digests match spec + feasibility headers |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-24 |
| Branch | `chore/INIT-GATEFLOW-003-spec-gateflow` (Draft spec PR #18) |
| Initiative segment | `INIT-GATEFLOW-003` |
| Status | Draft |
| Review deadline | 2026-07-31 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit acceptance required, not approval by silence |

---

## 1. Problem statement

With the INIT-001/002 control plane delivered, Gateflow must run a **live Cursor
AgentRunner** in the worker for `dispatch: orchestrated` skills (no node
allowlist), **fail fast** when Cursor auth/SDK or not-live runners are required,
and persist **stage + wave cycle-time** metrics (including p50/p95 for
`runner=cursor`) — without rebuilding wave-start, PR thread, board APIs, or
PolicyEngine pin consumption.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/infra_services/cursor_agent_runner.py` | stub | Live Cursor SDK path; quarantine stub success from REQ-27 | AgentRunner I/O (ADR-003) |
| `src/configs/cursor_agent_settings.py` | new | Env-backed Cursor auth material (`get_instance()`) | Secrets (ADR-004) |
| `src/business_services/slot_validator.py` (+ optional live preflight helper) | exists | Live-readiness check for `cursor` (ADR-007) | Start-gate honesty |
| `src/business_services/adapter_registry.py` | exists | Keep ADR-006; `cursor` stays implemented once live SDK wired | Registry |
| `src/business_services/wave_start_service.py` | exists | Call live-readiness with SlotValidator before enqueue | Accept boundary |
| `src/business_services/run_orchestrator.py` | hardwired cursor | Persist failed stages + duration; compute `wave_duration_ms` on finalize; keep cursor DI for 003 | Run lifecycle |
| `src/business_services/metrics_emitter.py` | by_runner dims | Unchanged aggregates; ensure failure stages emit `duration_ms` | Metrics |
| `src/business_services/node_model_resolver.py` | exists | unchanged | Per-node runner/model |
| `src/business_services/policy_engine.py` | exists | unchanged — pin `dispatch` SSOT | Dispatch eligibility |
| `src/api/v1/runs_routes.py` / run detail models | exists | Expose `wave_duration_ms` on run detail | Programme-token reads |
| `src/api/v1/metrics_routes.py` | exists | **No** new query param required (PE-3) | Metrics reads |
| `src/models/*` | exists | Stage/run DTOs; optional prompt-context model; settings models | Pydantic contracts |
| `src/database/postgres/schema/run_store_schema.py` | exists | Add `runs.wave_duration_ms` (nullable int) | ORM |
| `postgres_migrations/versions/` | human-owned | Human Alembic for `wave_duration_ms` | DDL |
| `config/programme.yaml` | exists | Intended `cursor` / `auto`; no secrets | Programme knobs |
| `pyproject.toml` | no Cursor SDK | Add Cursor SDK dependency for live path | Packaging |
| `tests/unit/*` | stub coverage | Live readiness, failure stage metrics, wave duration | Unit |
| `tests/verify/*` | no Scenario A/B | Scenario B (W1) + Scenario A (W2 after pin) | Live prove-it |

**Accepted ADR constraint set (constrains design):**

| ADR | Interaction |
|-----|-------------|
| ADR-001 | Dual API+worker + Postgres RunStore — wave duration on runs |
| ADR-002 / ADR-005 | Programme token zones unchanged (no new public write surface for 003) |
| ADR-003 | Cursor SDK stays in infra |
| ADR-004 | Cursor secrets via settings/env, not programme.yaml |
| ADR-006 | `implemented` fail-closed retained; OpenCode/Claude still stubs |
| ADR-007 (Draft) | Live readiness separate from `implemented` |

**Boundary diagram (text):**

```
PE/tools ──programme token──► POST /waves/start (unchanged path)
         │                      ├── SlotValidator (ADR-006 implemented)
         │                      └── LiveReadiness (ADR-007 cursor auth+SDK)
         ▼ enqueue
[worker] → RunOrchestrator
              ├── PolicyEngine (pin dispatch: orchestrated)
              ├── resolve_node_dispatch (runner/model)
              ├── CursorAgentRunner (live SDK) ──► workspace coding work
              ├── MetricsEmitter (stage duration + wave_duration_ms)
              ├── ForgeClient / Notifier (unchanged)
              └── RunStore
```

---

## 3. Public interface contracts

### 3.1 CursorAgentSettings → CursorAgentRunner (Q-1)

**Settings class:** `CursorAgentSettings` (PREFIX e.g. `CURSOR`), `get_instance()`,
not DI-injected (dependency-injection.mdc).

| Field | Shape | Invariant |
|-------|-------|-----------|
| `api_key` (env `CURSOR_API_KEY`) | secret string | Required for live-readiness when runner=`cursor`; never logged in full; never in programme.yaml |
| Optional SDK knobs | timeout_ms, etc. | Defaults in settings; fail-fast if required for start |

**Invariant:** Missing/blank key ⇒ live-readiness failure (REQ-29). Exact SDK
constructor mapping is implementation detail inside infra.

### 3.2 Live readiness preflight (ADR-007)

**Entry:** called from `WaveStartService` before enqueue; again in worker before
`run_skill` (defense in depth).

**Input:** required runner ids for the run; environment flags.

**Checks for `cursor`:**

1. Registry: adapter exists, slot=RUNNER, `implemented=True` (ADR-006).
2. `CURSOR_API_KEY` (or successor settings field) present and non-empty.
3. Stub env **not** treating this as live success: `GATEFLOW_AGENT_STUB` unset/false
   for production-like / live-verify paths; if stub forced in production env → fail.

**Output:** ok | structured failures `[{adapter_id, settings_key, reason}]`.  
**Errors at HTTP:** 422 (or existing stub/precondition status) with reason list; no job.

### 3.3 CursorAgentRunner.run_skill (REQ-27 / FR-6 I/O)

**Method:** `run_skill(workspace_path, skill_id, prompt_context, model_profile, …)`  
**Behavior:**

| Mode | When | Result |
|------|------|--------|
| Live SDK | credentials ok; stub env off; real skill id | Invoke Cursor SDK against workspace; return `AgentRunResult` with outcome + model fields |
| Test double | `skill_id` starts with `mock-` **or** stub env in **unit/test** only | Synthetic SUCCESS/FAILED — **not** REQ-27 evidence |
| Reject | Live required but SDK/auth unavailable | `FAILED` with clear error; never invent SUCCESS |

**Return:** existing `AgentRunResult` (runner, outcome, model_profile, model_id,
model_provider, error_message, optional duration).  
**Invariant:** no silent fallback to another runner id.

### 3.4 RunOrchestrator — stage + wave cycle-time (REQ-30, PE-4, Q-2)

**Stage (success and failure):**

- Persist `StageCreate` with `started_at`, `ended_at`, `runner`, `model_profile`,
  `model_id`, `outcome_type`.
- Emit `record_stage_duration` with `duration_ms` on **both** success and AgentRunner
  failure (FF-05 / PE-4).

**Wave:**

- On finalize (contract stop or terminal `failed`), set `runs.wave_duration_ms` =
  elapsed ms from API accept/enqueue anchor (`api_trigger` / run `created_at`) to
  finalize timestamp.
- Expose `wave_duration_ms` on run detail JSON.

### 3.5 Metrics API (PE-3)

**Entry:** `GET /api/v1/metrics/runs` (unchanged).  
**Contract:** response includes `by_runner[]` with `key`, `count`, `p50_ms`, `p95_ms`.  
**REQ-30 “filterable by runner=cursor”** = clients select the `by_runner` row where
`key == "cursor"` — **no** new query parameter required for 003 exit.  
Optional later INIT may add `?runner=` without breaking this contract.

### 3.6 Orchestrator runner wiring (PE-2)

**003 scope:** keep injecting `CursorAgentRunner` directly.  
**Start gate:** if required runner ≠ `cursor` and not implemented → SlotValidator
already fails at wave-start; if somehow reaches worker → fail closed (existing
message may be updated from “W1 Cursor path only” to “runner not wired”).  
**Deferred:** multi-runner registry→DI factory routing (later INIT).

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|--------------------------|--------|--------|
| FF-02 / FF-09 / PE-1 | ADR_REQUIRED | `docs/specification/adr/adr-007-agent-runner-live-readiness.md` | Separate live-readiness preflight from ADR-006 `implemented`; quarantine stub | Draft | `sha256:1ee304b47af42e99a6cf2594892f289d1f6dad3a8cedd535719b1e003a4ed589` |
| PE-2 | TDD_ONLY | §3.6 / §9 | Hardwired CursorAgentRunner for 003; start-time validation; multi-runner DI deferred | Resolved | N/A |
| PE-3 / FF-07 / FF-11 | TDD_ONLY | §3.5 / §9 | `by_runner` satisfies filter; stage `duration_ms` on events + timestamps — no stages column / no metrics query param | Resolved | N/A |
| PE-4 / FF-05 | TDD_ONLY | §3.4 / §9 | Persist stage + duration on AgentRunner failure | Resolved | N/A |
| Q-1 | TDD_ONLY | §3.1 | `CURSOR_API_KEY` via `CursorAgentSettings` | Resolved | N/A |
| Q-2 | TDD_ONLY | §3.4 | Explicit `runs.wave_duration_ms` | Resolved | N/A |
| Q-3 | TDD_ONLY | §3.3 / ADR-007 | Quarantine stub/`mock-*` — not REQ-27 evidence | Resolved | N/A |
| Q-4 | DEFERRED_WITH_DEFAULT | §9 | Proceed on as-built 002 W2 human_approved; reconcile meta #10 separately | Deferred | N/A |

**Derived counts:**

- ADR_REQUIRED: 1
- TDD_ONLY: 6
- DEFERRED_WITH_DEFAULT: 1
- Draft ADR files created: 1
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| CursorAgentRunner live | Mock SDK; assert auth missing → FAILED; stub env cannot mark live success when asserting live mode | optional | Scenario B/A with stub env **unset** | exact outcome + runner fields; coding-work evidence = workspace file/diff presence (fuzzy ok) |
| Live readiness | Missing key / stub+production → validation failures | wave-start 422 | wave-start reject without key | exact error keys |
| Orchestrator metrics | Failure path writes stage + duration; finalize sets wave_duration_ms | — | run detail + metrics `by_runner` cursor row after live stage | exact field presence; percentiles numeric |
| Policy / allowlist | unchanged pin orchestrated tests | — | — | exact |
| Scenario B | — | — | `verify_scenario_b` (or extend pr_thread): pre-implement→… per pin | live coding work + RunStore `runner=cursor` |
| Scenario A | pin fixture when orchestrated | — | after CTR-01 pin; post–Gate 2 node | same |

**AI-output determinism policy:**

- RunStore fields, HTTP status, adapter ids, metrics keys: **exact**.
- Agent-authored workspace content: **fuzzy** / presence checks (file changed,
  non-empty diff) — not byte-identical golden files.
- Unit tests must not call live Cursor cloud; mock the SDK boundary.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Missing `CURSOR_API_KEY` | live readiness / settings | Wave-start 422; or worker fail-closed | terminal for that run — fix secrets |
| Not-live runner required (`opencode`, etc.) | SlotValidator ADR-006 | Wave-start 422 | terminal — change programme config |
| Cursor SDK start failure / timeout / crash | CursorAgentRunner | Orchestrator finalize `failed`; stage+duration persisted; Notifier | terminal — no workflow advance |
| Stub env set in production-like env | live readiness | Reject start / fail run | terminal — unset stub |
| Human-checkpoint mid Scenario A/B | PolicyEngine | Stop (not AgentRunner failure) | expected — resume / new run |
| Metrics persist failure | MetricsEmitter / repo | Log error; preserve run outcome; do not invent success metrics | ops flag |
| CTR-01 pin still manual for Scenario A | pin consumer | W2 blocked until skills supporting delivery | dependency — not gateflow code |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| CursorAgentRunner | INFO success start/end; ERROR auth/SDK fail | `skill_id`, `runner`, `model_profile`, `model_id`, `workspace_path` (no full API key) | loguru kwargs |
| Live readiness | WARNING/ERROR on fail | `adapter_id`, `settings_key`, `reason` | |
| RunOrchestrator | INFO dispatch/finalize | `run_id`, `workflow_node`, `duration_ms`, `wave_duration_ms`, `outcome` | |
| MetricsEmitter | DEBUG/INFO | `event_type`, `runner`, `workflow_node` | existing |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| `AgentRunResult` | `src/models/control_plane_models` | infra → business | amend-by-PE |
| `CursorAgentSettings` | `src/configs/` | settings load | env contract documented in README |
| `StageModel` + event `duration_ms` | run_store models + metrics payload | repository + emitter | additive |
| `runs.wave_duration_ms` | schema + RunModel + run detail API | repository | human Alembic; additive |
| `RunMetricsResponse.by_runner` | control_plane_models | metrics API | additive; no query-param required |
| Programme runner/model YAML | programme_config_models | loader | ADR-004 |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| PE-1 / FF-02 / FF-09 | PE | resolved | live vs `implemented` | ADR-007 live-readiness preflight; ADR-006 boolean unchanged | plan W0 | — | ADR-007 |
| PE-2 / FF-06 | PE | resolved | hardwired vs registry DI | Keep hardwired Cursor for 003; validate at start; multi-runner DI deferred | W0 | — | §3.6 |
| PE-3 / FF-07 / FF-11 | PE | resolved | metrics filter + duration column | `by_runner` sufficient; events+timestamps for stage duration | W1 | — | §3.5 |
| PE-4 / FF-05 | PE | resolved | failure-path stage metrics | Persist stage + `duration_ms` on AgentRunner failure | W1 | — | §3.4 |
| Q-1 | PE | resolved | Cursor secret shape | `CURSOR_API_KEY` via `CursorAgentSettings` | W0 | — | §3.1 |
| Q-2 | PE | resolved | wave duration field | `runs.wave_duration_ms` (+ run detail) | W1 | — | §3.4 |
| Q-3 | PE | resolved | stub delete vs quarantine | Quarantine — stub/`mock-*` test-only; not REQ-27 | W1 exit | — | ADR-007 §3 |
| Q-4 | PE | deferred | meta #10 vs as-built A-1 | Proceed on as-built W2 human_approved | W0 | same | as-built |
| FF-01 | PE | resolved (design) | live SDK | Implement in infra; dependency in poetry | W0–W1 | — | §2 |
| FF-12 | PE | deferred | Scenario A pin | Out of repo; W2 after CTR-01 | W2 | hold W2 prove-it | impact-map |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None | — | — | — | — | — |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None | — | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | INIT-003 as-built + tests README feature map | after waves / ground-spec | N/A |
| AF-2 | auto-fixed | Clarify REQ-30 “filterable by runner=cursor” = `by_runner` dimension | `INIT-GATEFLOW-003-gateflow.md` | see commit |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T11 checks | PASS |
| Engineering decisions resolved | 9 resolved, 2 deferred with defaults (Q-4, FF-12/CTR-01) |
| Draft ADR files written | 1 / 1 required (`adr-007`) |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Ready for PE review | **YES** |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE acceptance of TDD/ADR required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram |
| T2 Interface contracts | PASS | §3.1–3.6 |
| T3 NEW-ADR dispositions | PASS | FF-09 → ADR_REQUIRED ADR-007; others TDD_ONLY/deferred |
| T4 Test policy | PASS | §5; live verify Scenario A/B; fuzzy coding-work |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | infra SDK; business preflight; no ADR-003 violation |
| T9 Engineering questions zero | PASS | §9 all PE items resolved or deferred with defaults |
| T10 PE review readiness | PASS | ready_for_pe_review true; ready_for_plan false |
| T11 ADR artifact integrity | PASS | Draft ADR-007 file present; indexed in §4 |

---

## PR instructions

> Commit this TDD to the **Draft spec PR** branch. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by committing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-003-spec-gateflow
PR title: "[INIT-GATEFLOW-003] Spec — gateflow"
Draft PR: https://github.com/drivestream-lab/gateflow/pull/18

Required reviewers:
  @drivestream-lab/prayog-pe-team

Review deadline: 2026-07-31
PE review checklist:
  [ ] T1 Module boundaries
  [ ] T2 Interface contracts
  [ ] T3 ADR-007 Draft disposition
  [ ] T4 Test policy / Scenario prove-it
  [ ] T9 Zero unresolved PE items
  [ ] T11 ADR artifact integrity

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates ADR-007 Draft → Accepted and TDD Status → Accepted
  Commit acceptance package to spec branch (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → board-seed from merged plan §9
```

## References

- Spec: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`
- Feasibility: `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md`
- Draft ADR: `docs/specification/adr/adr-007-agent-runner-live-readiness.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/11
- Draft spec PR: https://github.com/drivestream-lab/gateflow/pull/18

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md
    digest: sha256:4fa543ff62fd9d5e08031552d6f11e8281f54310f8b45cf37af956e8d3296b8b
  blockers: []
  signals:
    ready_for_pe_review: true
    ready_for_plan: false
    draft_adr_paths:
      - docs/specification/adr/adr-007-agent-runner-live-readiness.md
    draft_adr_digests:
      - sha256:1ee304b47af42e99a6cf2594892f289d1f6dad3a8cedd535719b1e003a4ed589
    adr_required_count: 1
    tdd_only_count: 6
    deferred_count: 1
    pe_resolved: [PE-1, PE-2, PE-3, PE-4, Q-1, Q-2, Q-3]
    pe_deferred: [Q-4, FF-12]
    pm_questions: []
    domain_questions: []
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/11
    meta_pr_head_sha: 4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5
    map_revision: 2
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/18
    gate2_label: spec-pending
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
```
