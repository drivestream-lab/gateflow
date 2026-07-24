# Feasibility report — INIT-GATEFLOW-003

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-003 |
| Spec | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` |
| Spec digest | `sha256:882ce66b2f89406feebc1d769496f7525da61903f49e14ae0f892b706686cc08` |
| PRD digest | `sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-003.md` / `2` |
| Repo scope digest | `sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85` |
| Approved meta PR head | `4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5` |
| Impact-map approval | Review `4773322287` by `0xbeefdead`, APPROVED `2026-07-24T12:55:22Z` on matching head; https://github.com/drivestream-lab/prayog-meta/pull/11#pullrequestreview-4773322287 |
| Source freshness | CURRENT — meta PR #11 head + APPROVED review + PRD/map digests + gateflow scope digest match spec header; repo affected, not deferred/blocked. Gate 1 labels still `impact-map-pending`+`impact-map-revised` (projection lag; review is authoritative). |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-24 |
| Branch | `chore/INIT-GATEFLOW-003-spec-gateflow` — Draft spec PR #18 |
| Initiative segment | `INIT-GATEFLOW-003` |
| Status | Draft |
| Review deadline | 2026-07-29 |
| Deciders | PM: programme PM · Domain SME: prayog-pe-team |

## Summary

INIT-GATEFLOW-003 is **buildable** on the delivered INIT-001/002 control plane
(wave-start, pin-driven PolicyEngine, FR-16 resolver, ADR-006 registry, RunStore
stage timestamps, metrics `by_runner` p50/p95). The product gap is concentrated:
**live Cursor SDK** (REQ-27), **credential / live honesty** (REQ-28/29), and
**wave cycle-time + failure-path stage metrics** (REQ-30). No Critical ADR
contradiction blocks the spec. Recommendation: keep Gate 2 `spec-pending`, resolve
PE questions in `/spec-technical-review` (live-vs-`implemented`, SDK/auth shape,
wave duration field, stub quarantine), then plan W0→W1→W2.

**Findings:** 12 total (0 Critical, 7 Should fix, 3 Verify, 2 Gap)

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — cursor stub, slot validator, metrics dims, orchestrator, wave-start, node resolver, trigger/policy | `tests/unit/test_cursor_agent_runner.py`, `test_slot_validator.py`, `test_metrics_emitter.py`, `test_run_orchestrator.py`, `Makefile` `test` |
| Live verify | health, webhook, status/metrics, wave-start, pr_thread, board (+ `verify_all`) — **no** Scenario A/B live Cursor prove-it | `tests/verify/`, `tests/README.md` |
| As-built | INIT-001 + INIT-002 W0–W2 **human_approved**; Cursor = stub / real SDK deferred | `docs/specification/as-built/implementation-status.md` |
| Toolchain | `make check` (black/ruff/pyright/import-linter); CI placeholder | `Makefile`, `.github/workflows/ci.yml` |
| Source | API + worker control plane; `CursorAgentRunner` stub in infra | `src/main.py`, `src/worker_main.py`, `src/infra_services/cursor_agent_runner.py` |

## ADR pass (pre-T2)

| ADR id | Domain matched | Status |
|--------|----------------|--------|
| ADR-001 | Dual API+worker, Postgres RunStore | Accepted — aligned (003 reuses topology) |
| ADR-002 | Programme token / public_paths | Accepted — aligned (no new public write surface required for 003 exit) |
| ADR-003 | AgentRunner / ForgeClient infra slots | Accepted — live Cursor stays in infra; may need TDD detail |
| ADR-004 | Programme config in gateflow repo | Accepted — aligned (runner/model already here; Cursor secrets TBD Q-1) |
| ADR-005 | Programme-token mutations | Accepted — wave-start already delivered; 003 does not reopen |
| ADR-006 | Adapter registry fail-closed | Accepted — **honesty tension** with stub Cursor marked `implemented=True` (see FF-02 / NEW-ADR) |

## MDC pass (pre-T2)

| MDC file | Domain covered | Read / skipped |
|----------|----------------|----------------|
| `architecture.mdc` | Layout, worker/API composition | read |
| `dependency-injection.mdc` | `@inject`, infra/business lifecycle | read |
| `infra-services.mdc` | AgentRunner as infra | read |
| `fail-fast.mdc` | No silent success / missing deps | read |
| `pydantic-schemas.mdc` | Models in `src/models/` | read |
| `repository-pattern.mdc` | ORM isolation for RunStore | read |
| `database-migrations.mdc` | Human-owned Alembic for wave duration | read |
| `testing-verify-flows.mdc` | verify vs unit; Scenario prove-it | read |
| `logging-loguru.mdc` | Structured logging | skipped — no wording conflict |
| `http-api-conventions.mdc` | Metrics query filters if added | read |
| `python-imports.mdc` / `python-tooling.mdc` / `strong-typing.mdc` | Tooling | skipped — not initiative-specific |
| `spec-driven-development.mdc` | Process | skipped — process only |
| `code-guidelines-index.mdc` | Index | skipped |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-27 / W0–W2 | Live Cursor AgentRunner; Scenario A/B prove-it; no node allowlist | `CursorAgentRunner.run_skill` stub only (`cursor_agent_runner.py`); PolicyEngine honors pin `dispatch: orchestrated` (`policy_engine.py`); no Cursor SDK in `pyproject.toml` | `test_cursor_agent_runner.py` (stub); `test_trigger_policy.py` (orchestrated) | none for live coding work | **gap** (expected product work) |
| REQ-28 / W0 | Config runner resolve; fail-fast not-live at **start** | `node_model_resolver.py` + SlotValidator at wave-start; registry `opencode`/`claude_code` `implemented=False`; orchestrator hardwires cursor at worker (`run_orchestrator.py:239–255`) | `test_slot_validator.py`, `test_node_model_resolver.py` | — | **partial** |
| REQ-29 / W0–W1 | Cursor credential PC-12; auth/start/crash fail-fast | No Cursor secret settings; stub returns FAILED without SDK; no timeout/crash handling | stub failure tests only | — | **gap** |
| REQ-30 / W1–W2 | Stage fields + wave duration + p50/p95 for `runner=cursor` | Stages have timestamps + runner/model; `duration_ms` on `stage_completed` events (success path); `by_runner` aggregates exist; **no** `wave_duration_ms`; failed path skips stage metrics | `test_metrics_emitter.py` | `verify_status_metrics` (shape only) | **partial** |
| REQ-31 / all | Reuse 001/002 control plane | Wave-start, PR-at-start, Notifier, board APIs, ForgeClient present | extensive 002 suite | `verify_wave_start`, `verify_pr_thread`, `verify_board` | **exists** |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-27 / W0–W1 | ADR-003 (AgentRunner infra) | aligned | Live SDK stays in infra; no conflict |
| REQ-28 / W0 | ADR-006 (+ possible NEW-ADR) | missing ADR for live vs stub | FF-02, FF-09 — `implemented` bool insufficient for “live Cursor” honesty |
| REQ-29 / W0 | ADR-004 (secrets out of committed config) | aligned | Credential injection shape is PE/TDD (Q-1), not ADR conflict |
| REQ-30 / W1 | ADR-001 (RunStore) | aligned | Additive columns/events; human Alembic |
| REQ-31 / all | ADR-001…006 | aligned | Reuse; no rebuild |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-02 | F13 | “Resolved runner + notifier … are **implemented / live**” (precondition #10); REQ-28 fail-fast not-live | ADR-006 | Registry registers `cursor` with `implemented=True` while runtime is stub — wave-start accepts Cursor without live capability |
| FF-09 | F13 | REQ-27 live Cursor fulfills FR-17 product meaning | ADR-006 / NEW-ADR | Need explicit decision: extend capability (`live` / credential-ready) vs keep boolean + separate preflight — route to technical review |
| FF-13 | F14 | Live AgentRunner in worker; fail-fast missing deps | `infra-services.mdc`, `fail-fast.mdc`, `database-migrations.mdc` | Spec aligns: SDK in infra; fail-fast; human Alembic for wave duration. No MDC contradiction. Note existing `prompt_context: dict[str, Any]` on `run_skill` — prefer Pydantic at boundary in TDD |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F2/F5 | **Live Cursor path absent** — REQ-27 requires SDK AgentRunner performing live coding work; current path is stub/`mock-*`/`GATEFLOW_AGENT_STUB` only | Spec REQ-27; `src/infra_services/cursor_agent_runner.py`; as-built “real SDK deferred”; no cursor package in `pyproject.toml` |
| FF-02 | F5/F13 | **Registry honesty drift** — `cursor` marked `implemented=True` while AgentRunner cannot run real skills without stub env | Spec precondition #10 / REQ-28; `adapter_registry.py:62`; `cursor_agent_runner.py:99–114` |
| FF-03 | F2/F10 | **No Cursor credentials / PC-12** — REQ-29 wave-run precondition #12 not modeled in settings or TriggerRouter/SlotValidator | Spec REQ-29; no Cursor keys in `ProgrammeConfig` / `.env.example`; `WavePreconditionIdType` has no credential check |
| FF-04 | F2 | **Wave cycle-time missing** — no `wave_duration_ms` (or equivalent) from API accept → contract stop/fail | Spec REQ-30 / Q-2; `RunSchema` / `RunModel` lack field; `record_api_trigger` exists as start anchor only |
| FF-05 | F2/F4 | **Failed AgentRunner stages omit duration metrics** — success path records stage + `duration_ms`; failure finalizes without `StageCreate` / `record_stage_duration` | Spec REQ-30 “every live Cursor orchestrated stage”; `run_orchestrator.py` failure branch vs success `302–326` |
| FF-06 | F2 | **Orchestrator hardwires Cursor** — non-cursor resolved runner fails at **worker** with “W1 Cursor path only”, not always at wave-start via registry routing | Spec REQ-28 “blocks at start”; `run_orchestrator.py:239–255` vs `WaveStartService` SlotValidator |
| FF-08 | F5 | **Stub can satisfy `runner=cursor` success** — `GATEFLOW_AGENT_STUB` / `mock-*` return SUCCESS; must not count as REQ-27 live exit | Spec REQ-27 / Q-3; `cursor_agent_runner.py:82–97` |

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-07 | F3/F8 | Metrics **p50/p95 for `runner=cursor`** already available under `by_runner` buckets; REQ-30 wording “filterable” may mean query param vs client select — clarify in TDD | Spec REQ-30; `metrics_emitter.aggregate_run_metrics`; `GET /metrics/runs` has no query params (`metrics_routes.py`) |
| FF-11 | F2 | Stage `duration_ms` lives on **events**, not `stages` columns — confirm whether timestamps + events satisfy REQ-30 or column/API field required | Spec REQ-30; `StageModel` vs `record_stage_duration` payload |
| FF-12 | F9/F10 | **CTR-01 / Scenario A** depends on prayog-skills pin edit (out of this repo); gateflow W2 prove-it blocked until supporting delivery | Spec out-of-scope + CTR-01; pin `workflow.yaml` Scenario A still `dispatch: manual` |

### Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-10 | F3 | No live verify for Scenario B/A prove-it or live coding-work evidence | `tests/verify/` inventory; `tests/README.md` feature maps stop at 002 |
| FF-14 | F5 | As-built has no INIT-003 capability rows yet (expected until waves ship) | `implementation-status.md` |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 live Cursor skeleton + credential fail-fast | `cursor_agent_runner.py`, settings/secrets, `adapter_registry.py` / capability model, `slot_validator.py` or wave-start preflight, `pyproject.toml` (SDK) | `test_cursor_agent_runner`, `test_slot_validator`, `test_wave_start` |
| W1 Scenario B + crash/auth + stage/wave cycle-time | `run_orchestrator.py`, RunStore schema/models/repo, `metrics_emitter.py`, run detail API | orchestrator + metrics unit; new `verify_scenario_b` (or extend `verify_pr_thread`) |
| W2 Scenario A + post–Gate 2 + metrics honesty | consume pin; verify Scenario A set; optional metrics query filter | verify after prayog-skills CTR-01; unit pin fixtures |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Cursor SDK worker auth harder than expected (PRD risk) | Fail-fast product rule already set; lock secret shape in TDD (Q-1) early in W0 |
| R-2 | Stand-in vs live ambiguity confuses exit evidence | Quarantine stub (Q-3); never count stub success as REQ-27 |
| R-3 | Scenario A exit depends on prayog-skills pin (CTR-01) | Parallel supporting PR; gateflow W2 after pin; document in plan dependency order |
| R-4 | Spec A-1 assumes 002 finished while meta PR #10 may still be open | Spec Q-4 default: proceed on as-built human_approved W2 |
| A-7/A-8 | ADR-001/006 + FR-6 I/O remain | Confirm in technical review; extend ADR-006 if live capability added |

## Recommended spec edits

- After PE answers Q-1…Q-3: record chosen credential shape, wave duration field name, and stub quarantine rule in REQ-29/30 acceptance or Assumptions (same Draft PR).
- Optionally clarify REQ-30 “filterable by `runner=cursor`” as either (a) existing `by_runner` response dimension or (b) explicit query param — remove ambiguity before plan.
- Cross-link CTR-01 supporting prayog-skills PR when opened (dependency for W2).
- Do **not** renumber REQ-27…31; keep FR≡REQ alias note.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | Cursor credential / secret injection shape for worker | no | PE | open | W0/W1 | Fail-fast if absent; shape in TDD/settings | Spec Q-1; FF-03 | pending — meta IM-01 / Draft PR #18 |
| Q-2 | PE | Exact RunStore field for wave cycle time | no | PE | open | W1 | Prefer explicit `wave_duration_ms` (or equivalent) on run + run detail | Spec Q-2; FF-04 | pending — IM-02 |
| Q-3 | PE | Delete vs quarantine stub/`GATEFLOW_AGENT_STUB` for `runner=cursor` | no | PE | open | W1 exit | Quarantine so stub cannot satisfy REQ-27 | Spec Q-3; FF-08 | pending — IM-03 |
| Q-4 | PE | Reconcile INIT-002 meta PR #10 vs as-built finished A-1 | no | PE | open | W0 start | Proceed per as-built human_approved W2 | Spec Q-4; FF-14 context | pending — IM-04 |
| PE-1 | PE | Extend ADR-006 (or NEW-ADR) for **live** vs `implemented` + credential-ready Cursor | no | PE | open | technical review | Separate preflight: registry `implemented` + Cursor auth check before accept | FF-02, FF-09 | `/spec-technical-review` |
| PE-2 | PE | Registry-routed AgentRunner vs hardwired `CursorAgentRunner` in orchestrator; block non-live at **start** | no | PE | open | technical review / W0 | Keep cursor-only DI for 003 but validate required runner live at wave-start; document | FF-06 | `/spec-technical-review` |
| PE-3 | PE | REQ-30 metrics: document `by_runner` as sufficient vs add `?runner=` filter; stage `duration_ms` column vs events | no | PE | open | technical review / W1 | Accept `by_runner` + event `duration_ms` + stage timestamps unless product requires query param/column | FF-07, FF-11 | `/spec-technical-review` |
| PE-4 | PE | Failure-path stage + duration persistence for REQ-30 completeness | no | PE | open | W1 | Persist stage + duration on failed AgentRunner outcomes | FF-05 | TDD / plan |
| AF-1 | auto-fix | Feature-map / as-built INIT-003 rows after waves | no | Eng | open | post-wave | Add rows when implementing | FF-10, FF-14 | plan / ground-spec |
| AF-2 | auto-fix | Spec optional clarification of metrics “filterable” once PE-3 decided | no | Eng | open | after PE-3 | One-line acceptance edit on Draft PR | FF-07 | same branch |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None.

#### Defer — can proceed with documented assumption

None new beyond PRD already locked. Supporting skills pin remains **out of gateflow** (CTR-01).

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

None strictly blocking plan authorship if defaults in Q-1…Q-3 / PE-1…PE-4 are accepted; **strongly recommended** to resolve PE-1/PE-2/PE-3 in TDD before plan TASK breakdown.

#### Defer with default

1. **PE-1** — live vs `implemented` (default: credential preflight + keep boolean until ADR amendment).
2. **PE-2** — hardwired Cursor for 003 exit OK if start-time validation covers not-live ids.
3. **PE-3** — `by_runner` dimension satisfies “filterable by runner=cursor” unless PE requires query param.
4. **Q-1…Q-3** — defaults already in spec.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None | — | — |

### Auto-fixable (agent resolves — no human needed)

| # | Item | Fix |
|---|------|-----|
| AF-1 | As-built / tests README INIT-003 feature map | Add when waves land (not before TDD) |
| AF-2 | REQ-30 filter wording after PE-3 | One-line spec acceptance clarification on Draft PR |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Unit/verify/as-built/toolchain inventoried |
| F2 Spec → code map | FAIL | FF-01, FF-03, FF-04, FF-05, FF-06 (expected gaps + honesty) |
| F3 Spec → verify map | FAIL | FF-10; FF-07 verify semantics |
| F4 Spec → unit map | PASS | Stub/registry/metrics/orchestrator areas exist; live SDK unit TBD |
| F5 As-built drift | FAIL | FF-01, FF-02, FF-08, FF-14 — stub vs live claim |
| F6 Docs drift | PASS | `tests/README.md` / AGENTS accurate for 001/002; 003 rows deferred |
| F7 Overlap risk | PASS | No duplicate full Scenario A/B journeys yet |
| F8 CI vs live | PASS | `make test` vs verify scripts; live Cursor prove-it must stay verify |
| F9 Cross-service | PASS w/ note | FF-12 CTR-01 external dependency documented |
| F10 Assumptions | PASS | Q-4 / A-1 evidenced as-built; credential assumption open as Q-1 |
| F11 Effort drivers | PASS | See Impact surface (SDK + honesty + cycle-time) |
| F12 PM questions | PASS | No blocking PM gaps |
| F13 ADR conformance | PASS w/ findings | No Critical conflict; FF-02/FF-09 NEW-ADR / ADR-006 extend |
| F14 MDC conformance | PASS | FF-13 note only; no contradiction |

**Feasibility verdict:** FINDINGS (buildable; proceed to `/spec-technical-review`)

---

## Next steps

> This report lives on the spec PR branch alongside the spec draft.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → none for this slice.

**PE questions** → discuss on Draft spec PR #18; run `/spec-technical-review` next.
  PE accepts TDD/ADRs in **files** (`Draft` → `Accepted`); do **not** set
  `spec-lgtm` until the full package includes the implementation plan.

**Domain clarifications** → none.

**Auto-fixable items** → defer AF-1 until waves; AF-2 after PE-3.

```
Draft spec PR: chore/INIT-GATEFLOW-003-spec-gateflow  (spec-pending)  #18
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] All blocking Domain clarifications answered (none)
  [ ] Spec updated if PE-3 clarifies metrics filter wording (optional)
  [ ] Proceed: /spec-technical-review (PE-1…PE-4 + Q-1…Q-3)
  [ ] After TDD/ADRs Accepted + implementation plan on branch:
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: board-seed from plan §9 — then /pre-implement → /loop-spec
```

## References

- Spec: `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/11
- Draft spec PR: https://github.com/drivestream-lab/gateflow/pull/18
- As-built: `docs/specification/as-built/implementation-status.md`
- ADRs: `docs/specification/adr/adr-001` … `adr-006`

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md
    digest: sha256:381c9a32d31266df1860bdf385a88188539e74a536ce86e8333285096ad3e0d2
  blockers:
    - FF-01
    - FF-02
    - FF-03
    - FF-04
    - FF-05
    - FF-06
    - FF-08
  signals:
    draft_verdict: FINDINGS
    critical_count: 0
    should_fix_count: 7
    verify_count: 3
    gap_count: 2
    new_adr: true
    pe_questions: [Q-1, Q-2, Q-3, Q-4, PE-1, PE-2, PE-3, PE-4]
    pm_questions: []
    domain_questions: []
    auto_fix: [AF-1, AF-2]
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/11
    meta_pr_head_sha: 4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5
    map_revision: 2
    prd_digest: sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad
    scope_digest: sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/18
    gate2_label: spec-pending
    ripple_action: continue
  next_candidates:
    - spec-technical-review
  human_checkpoint: true
  external_action: false
```
