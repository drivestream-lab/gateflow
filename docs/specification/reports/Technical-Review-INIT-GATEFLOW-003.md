# Technical Design Document — INIT-GATEFLOW-003

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-003 |
| Spec | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` |
| Spec digest | `sha256:4d0fd484deb7eaad6dca3632355547604644a570140bf70d03e60ee642d41f18` |
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
| Status | **Accepted** — PE @nikd10x 2026-07-24 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/18); posture A1+B1+C1; ADR-001…006 reused (already Accepted); no new ADR for 003 |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-24 via Cursor chat on Draft spec PR #18 |
| Approved head | `7072533b71a1061b740c4b4be36e6fcb12d2cf93` |
| Review deadline | 2026-07-31 |
| Deciders | PE: @nikd10x / @drivestream-lab/prayog-pe-team |
| ADR posture (PE) | **A1:** no new ADR for 003 — reuse ADR-001…006 (Accepted); Draft ADR-007 withdrawn |
| Layer posture (PE) | **B1:** `cursor-sdk` is an in-process pip dependency; wrapper stays in `infra_services/` (ADR-003 Accepted — leave as-is; not Cursor Cloud) |
| Evidence posture (PE) | **C1:** local SDK contract + Docker/bridge spike live in this TDD (not an ADR) |

---

## 1. Problem statement

With the INIT-001/002 control plane delivered, Gateflow must run a **live Cursor
AgentRunner** in the worker for `dispatch: orchestrated` skills (no node
allowlist), **fail fast** when Cursor auth/SDK or not-live runners are required,
and persist **stage + wave cycle-time** metrics (including p50/p95 for
`runner=cursor`) — without rebuilding wave-start, PR thread, board APIs, or
PolicyEngine pin consumption.

**Runtime (product + engineering):** official **local** Cursor Python SDK
(`cursor-sdk` + `LocalAgentOptions(cwd=workspace)`) in the **same worker
process**. Cursor **cloud** agents are out of scope. This is an application pip
dependency wrapped as an outbound adapter — not a separate process product and
not a new architecture ADR.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/infra_services/cursor_agent_runner.py` | stub | Wrap `cursor-sdk` local agent; quarantine test doubles from live exit | AgentRunner adapter (ADR-003) |
| `src/configs/cursor_agent_settings.py` | new | Env-backed `CURSOR_API_KEY` (`get_instance()`) | Secrets (ADR-004) |
| `src/business_services/slot_validator.py` | exists | Start-gate: ADR-006 `implemented` + required Cursor secret present (fail-fast) | Accept honesty |
| `src/business_services/adapter_registry.py` | exists | Keep ADR-006; after live SDK wired, `cursor` = `implemented=True` means callable production backend | Registry |
| `src/business_services/wave_start_service.py` | exists | Run SlotValidator (+ secret check) before enqueue | Accept boundary |
| `src/business_services/run_orchestrator.py` | hardwired cursor | Persist failed stages + duration; compute `wave_duration_ms` on finalize; keep cursor DI for 003 | Run lifecycle |
| `src/business_services/metrics_emitter.py` | by_runner dims | Ensure failure stages emit `duration_ms` | Metrics |
| `src/business_services/node_model_resolver.py` | exists | unchanged | Per-node runner/model |
| `src/business_services/policy_engine.py` | exists | unchanged — pin `dispatch` SSOT | Dispatch eligibility |
| `src/api/v1/runs_routes.py` / run detail models | exists | Expose `wave_duration_ms` on run detail | Programme-token reads |
| `src/api/v1/metrics_routes.py` | exists | **No** new query param required (PE-3) | Metrics reads |
| `src/models/*` | exists | Stage/run DTOs; settings models | Pydantic contracts |
| `src/database/postgres/schema/run_store_schema.py` | exists | Add `runs.wave_duration_ms` (nullable int) | ORM |
| `postgres_migrations/versions/` | human-owned | Human Alembic for `wave_duration_ms` | DDL |
| `config/programme.yaml` | exists | Intended `cursor` / model profiles; no secrets | Programme knobs |
| `pyproject.toml` | no Cursor SDK | Add `cursor-sdk` (and document bridge/Node image needs) | Packaging |
| `tests/unit/*` | stub coverage | Secret start-gate, failure stage metrics, wave duration; mock SDK | Unit |
| `tests/verify/*` | no Scenario A/B | Scenario B (W1) + Scenario A (W2 after pin) | Live prove-it |

**Accepted ADR constraint set (no new ADR for 003):**

| ADR | Interaction |
|-----|-------------|
| ADR-001 | Dual API+worker + Postgres RunStore — wave duration on runs |
| ADR-002 / ADR-005 | Programme token zones unchanged |
| ADR-003 | AgentRunner **adapter** in `infra_services/` — wraps in-process `cursor-sdk`; business must not import SDK types |
| ADR-004 | Cursor secrets via settings/env, not programme.yaml |
| ADR-006 | Fail-closed on unimplemented required adapters; do **not** catalogue product live/stub lists in ADRs |

**Boundary diagram (text):**

```
PE/tools ──programme token──► POST /waves/start
         │                      └── SlotValidator (ADR-006 implemented
         │                           + CURSOR_API_KEY present when runner=cursor)
         ▼ enqueue
[worker process]
  RunOrchestrator (business)
       ├── PolicyEngine (pin dispatch)
       ├── resolve_node_dispatch
       ├── CursorAgentRunner (infra adapter)
       │        └── cursor-sdk Agent + LocalAgentOptions(cwd=workspace)
       ├── MetricsEmitter / ForgeClient / Notifier
       └── RunStore
```

---

## 3. Public interface contracts

### 3.1 CursorAgentSettings → CursorAgentRunner (Q-1)

**Settings class:** `CursorAgentSettings` (PREFIX `CURSOR`), `get_instance()`,
not DI-injected.

| Field | Shape | Invariant |
|-------|-------|-----------|
| `api_key` (env `CURSOR_API_KEY`) | secret string | Required when resolved runner is `cursor`; never logged in full; never in programme.yaml |
| Optional SDK knobs | timeout_ms, etc. | Defaults in settings |

**Invariant:** Missing/blank key ⇒ start-gate failure (fail-fast). Maps to official
SDK `api_key=` argument.

### 3.2 Start-gate checks (ADR-006 + ADR-004 + fail-fast) — PE-1 / TDD_ONLY

**No new ADR.** Honesty is an application of Accepted ADR-006 and ADR-004.

**Entry:** `WaveStartService` before enqueue; worker defense-in-depth before
`run_skill`.

**When required runner includes `cursor`:**

1. Registry: adapter exists, slot=RUNNER, `implemented=True` (ADR-006).
2. `CURSOR_API_KEY` present and non-empty (ADR-004 settings).
3. Test-double mode (`GATEFLOW_AGENT_STUB` / `mock-*`) must not be treated as
   production live success for exit evidence (Q-3 — product/test policy in TDD).

**Output:** ok | structured failures naming adapter id + settings key.  
**HTTP:** 422 (or existing precondition status); no job enqueued.

**ADR-006 alignment:** after the live SDK adapter is wired, `cursor` remains
`implemented=True` because a callable production backend exists. Marking
`implemented=True` while only a silent stub succeeds was the INIT-002 honesty
bug — fixed by (2)+(3), not by inventing a second ADR capability bit.

### 3.3 Cursor local SDK contract (C1) — in-process pip, not cloud

**Official path (product-aligned):**

```text
pip: cursor-sdk
auth: CURSOR_API_KEY (user/service-account key; Admin team keys not supported per Cursor docs)
runtime: Agent.create(..., local=LocalAgentOptions(cwd=<workspace_path>))
cloud Cursor agents: OUT of 003
```

**Infra adapter responsibilities (`CursorAgentRunner`):**

- Construct SDK client from settings + `workspace_path` / `cwd`.
- Map skill prompt / model profile → `send(...)` (exact prompt assembly is plan/TDD detail).
- Translate SDK outcomes/errors → existing `AgentRunResult`.
- Never import SDK types into business or routers (ADR-003).

**Dependencies to prove (spike before W1 live prove-it):**

| Risk | Spike |
|------|--------|
| Python `cursor-sdk` + local cwd on laptop | One `Agent.create` + `send` against a checkout |
| Docker worker image | Same with `CURSOR_API_KEY` injected; confirm bridge/Node pieces the package needs |
| Long agent turns vs job timeouts | Measure; set orchestrator/SDK timeouts deliberately |
| Account/model entitlements | Confirm programme key can use configured model id |

**Not required:** Cursor IDE GUI in the worker.

### 3.4 CursorAgentRunner.run_skill

**Method:** `run_skill(workspace_path, skill_id, prompt_context, model_profile, …)`  

| Mode | When | Result |
|------|------|--------|
| Live local SDK | credentials ok; stub env off; real skill id | `cursor-sdk` against `cwd=workspace_path` |
| Test double | `mock-*` skill **or** stub env in **unit/test** only | Synthetic SUCCESS/FAILED — not live exit evidence |
| Reject | Live required but SDK/auth unavailable | `FAILED`; never invent SUCCESS |

**Invariant:** no silent fallback to another runner id; no cloud agent runtime.

### 3.5 RunOrchestrator — stage + wave cycle-time (REQ-30, PE-4, Q-2)

**Stage (success and failure):** persist `StageCreate` + `record_stage_duration`
with `duration_ms` on **both** success and AgentRunner failure.

**Wave:** on finalize, set `runs.wave_duration_ms` from API accept/enqueue anchor
to stop/fail; expose on run detail.

### 3.6 Metrics API (PE-3)

`GET /api/v1/metrics/runs` — clients use `by_runner` row `key == "cursor"` for
p50/p95. **No** new query parameter for 003 exit.

### 3.7 Orchestrator runner wiring (PE-2)

Keep injecting `CursorAgentRunner` for 003. Multi-runner DI routing deferred.
Non-`cursor` required runners fail via ADR-006 at start (or worker fail-closed).

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|--------------------------|--------|--------|
| FF-02 / FF-09 / PE-1 | **TDD_ONLY** | §3.2 | Apply ADR-006 + secret presence + stub quarantine; **no ADR-007** | Resolved | N/A |
| PE-2 | TDD_ONLY | §3.7 | Hardwired CursorAgentRunner for 003; multi-runner DI deferred | Resolved | N/A |
| PE-3 / FF-07 / FF-11 | TDD_ONLY | §3.6 | `by_runner` sufficient; events + timestamps for stage duration | Resolved | N/A |
| PE-4 / FF-05 | TDD_ONLY | §3.5 | Persist stage + duration on AgentRunner failure | Resolved | N/A |
| Q-1 | TDD_ONLY | §3.1 / §3.3 | `CURSOR_API_KEY` + local SDK | Resolved | N/A |
| Q-2 | TDD_ONLY | §3.5 | `runs.wave_duration_ms` | Resolved | N/A |
| Q-3 | TDD_ONLY | §3.2 / §3.4 | Quarantine stub/`mock-*` — test doubles only | Resolved | N/A |
| Q-4 | DEFERRED_WITH_DEFAULT | §9 | Proceed on as-built 002 W2 human_approved | Deferred | N/A |
| FF-01 (SDK choice) | TDD_ONLY | §3.3 | Official local `cursor-sdk`; cloud out — **not an ADR** | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: **0** (Draft ADR-007 **withdrawn**)
- TDD_ONLY: 8
- DEFERRED_WITH_DEFAULT: 1
- Draft ADR files created: **0**
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| CursorAgentRunner | Mock `cursor_sdk`; auth missing → FAILED; stub not live exit | optional | Scenario B/A; stub env **unset** | exact outcome fields; coding-work = workspace change presence (fuzzy) |
| Start-gate secrets | Missing key → 422 / validation failures | wave-start | reject without key | exact error keys |
| Orchestrator metrics | Failure path stage + duration; wave_duration_ms | — | run detail + `by_runner` cursor | exact presence |
| Policy / allowlist | pin orchestrated tests | — | — | exact |
| Scenario B / A | — | — | after spike; A after CTR-01 pin | live coding work + `runner=cursor` |
| Docker spike | — | minimal image + key + cwd | gate before W1 prove-it | pass/fail spike note |

**AI-output determinism:** RunStore/HTTP/metrics **exact**; agent workspace
content **fuzzy** presence. Unit tests mock SDK — no live Cursor in `make test`.

---

## 6. Error handling strategy

| Failure mode | Module | Propagation | Recovery |
|--------------|--------|-------------|----------|
| Missing `CURSOR_API_KEY` | settings / SlotValidator | Wave-start 422 | terminal — fix secrets |
| Not-live runner required | SlotValidator ADR-006 | Wave-start 422 | terminal — change config |
| SDK start / timeout / crash | CursorAgentRunner | finalize `failed` + stage metrics | terminal — no workflow advance |
| Stub env in production-like path | start-gate / runner | reject or fail | unset stub |
| Human-checkpoint mid scenario | PolicyEngine | expected stop | resume / new run |
| Metrics persist failure | MetricsEmitter | log; preserve outcome | ops |
| CTR-01 Scenario A still manual | pin | W2 blocked | skills supporting delivery |
| Docker bridge/Node missing | image / spike | fail spike before W1 prove-it | fix image |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| CursorAgentRunner | INFO/ERROR | `skill_id`, `runner`, `model_profile`, `model_id`, `workspace_path` | never full API key |
| SlotValidator / start-gate | WARNING/ERROR | `adapter_id`, `settings_key`, `reason` | |
| RunOrchestrator | INFO | `run_id`, `workflow_node`, `duration_ms`, `wave_duration_ms`, `outcome` | |
| MetricsEmitter | DEBUG/INFO | `event_type`, `runner`, `workflow_node` | existing |

---

## 8. Data contract ownership

| Schema / data type | Owner | Validation layer | Versioning |
|--------------------|-------|------------------|------------|
| `AgentRunResult` | `src/models/` | infra → business | amend-by-PE |
| `CursorAgentSettings` | `src/configs/` | settings load | env in README / `.env.example` |
| Stage + event `duration_ms` | run_store + metrics | repository + emitter | additive |
| `runs.wave_duration_ms` | schema + API | repository | human Alembic |
| `RunMetricsResponse.by_runner` | control_plane_models | metrics API | additive |
| Programme runner/model YAML | programme_config_models | loader | ADR-004 |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| PE-1 / FF-02 / FF-09 | PE | resolved | live vs `implemented` / NEW-ADR? | **No new ADR** — ADR-006 + secret check + stub quarantine (TDD) | W0 | — | §3.2; A1 |
| PE-2 / FF-06 | PE | resolved | hardwired vs registry DI | Hardwired Cursor for 003; multi-runner DI deferred | W0 | — | §3.7 |
| PE-3 / FF-07 / FF-11 | PE | resolved | metrics filter + duration column | `by_runner`; events + timestamps | W1 | — | §3.6 |
| PE-4 / FF-05 | PE | resolved | failure-path stage metrics | Persist stage + duration on failure | W1 | — | §3.5 |
| Q-1 | PE | resolved | Cursor secret shape | `CURSOR_API_KEY` via settings | W0 | — | §3.1 |
| Q-2 | PE | resolved | wave duration field | `runs.wave_duration_ms` | W1 | — | §3.5 |
| Q-3 | PE | resolved | stub quarantine | Test doubles only; not live exit | W1 exit | — | §3.2 / §3.4 |
| Q-4 | PE | deferred | meta #10 vs as-built | Proceed on as-built W2 | W0 | same | as-built |
| FF-01 / layer | PE | resolved | SDK placement | B1: infra adapter wrapping in-process `cursor-sdk` | W0 | — | §3.3; ADR-003 |
| FF-12 | PE | deferred | Scenario A pin | Out of repo; W2 after CTR-01 | W2 | hold W2 | impact-map |

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
| AF-1 | planned-auto-fix | INIT-003 as-built + tests README | after waves | N/A |
| AF-2 | auto-fixed | REQ-30 `by_runner` clarification | spec | prior commit |
| AF-3 | auto-fixed | Withdraw ADR-007; A1+B1+C1 in TDD | this revision | see commit |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T11 checks | PASS |
| Engineering decisions resolved | 9 resolved, 2 deferred (Q-4, FF-12) |
| Draft ADR files written | **0 / 0** required (ADR-007 withdrawn) |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Ready for PE review | **DONE** — Accepted |
| **Ready for /spec-implementation-plan** | **YES** — TDD Accepted; no new ADR files required |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2; B1 infra wrapper |
| T2 Interface contracts | PASS | §3.1–3.7 including local SDK contract |
| T3 NEW-ADR dispositions | PASS | ADR_REQUIRED **0**; PE-1 demoted to TDD_ONLY |
| T4 Test policy | PASS | §5 + Docker spike before W1 |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | business → infra adapter → `cursor-sdk`; no ADR-003 violation |
| T9 Engineering questions zero | PASS | §9 |
| T10 PE review readiness | PASS | TDD **Accepted**; ready_for_plan true |
| T11 ADR artifact integrity | PASS | ADR_REQUIRED 0; ADR-001…006 remain Accepted; ADR-007 withdrawn |

---

## PR instructions

> TDD is **Accepted** on this Draft spec PR. Gate 2 label stays **`spec-pending`**
> until the implementation plan is on head. No new ADR files for 003 — Accepted
> ADR-001…006 reused; ADR-003 left as-is (layer ownership ≠ Cursor Cloud).

```
Branch:   chore/INIT-GATEFLOW-003-spec-gateflow
Draft PR: https://github.com/drivestream-lab/gateflow/pull/18

Accepted:
  [x] TDD Status → Accepted (PE @nikd10x, 2026-07-24)
  [x] A1 — no new ADR; ADR-007 withdrawn
  [x] B1 — ADR-003 retained (infra adapter for in-process cursor-sdk)
  [x] C1 — local SDK contract in TDD §3.3

Next:
  → /spec-implementation-plan on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → board-seed from merged plan §9
```

## References

- Spec: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`
- Feasibility: `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md`
- Accepted ADRs reused: ADR-001…006 (no ADR-007; ADR-003 unchanged)
- Cursor Python SDK: https://cursor.com/docs/sdk/python
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
    digest: sha256:fb9ee7c73d4e780b2bc4a94ea340255c19e5c8fb83a2cacfda1088c6ef275a6c
  blockers: []
  signals:
    ready_for_pe_review: true
    ready_for_plan: true
    tdd_status: Accepted
    pe_acceptor: nikd10x
    pe_accepted_at: 2026-07-24
    adr_posture: A1-no-new-adr
    layer_posture: B1-infra-adapter-in-process-sdk
    evidence_posture: C1-tdd-local-sdk-contract
    draft_adr_paths: []
    draft_adr_digests: []
    adr_required_count: 0
    tdd_only_count: 8
    deferred_count: 1
    adr_007_withdrawn: true
    adr_003_retained: true
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
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
```
