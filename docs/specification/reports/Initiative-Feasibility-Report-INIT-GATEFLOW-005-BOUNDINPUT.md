# Feasibility report — INIT-GATEFLOW-005-BOUNDINPUT

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-005-BOUNDINPUT |
| Spec | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` |
| Spec digest | `sha256:b2f46628ee639116442ec83fdc3cac28689c555679603b929a0cbcda11cdc8c4` |
| PRD digest | `sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-005-BOUNDINPUT.md` / `1` |
| Repo scope digest | `sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b` |
| Approved meta PR head | `0b6b11e4470517842affb894d7ea581c3819ead3` |
| Impact-map approval | Review `4788143334` by `0xbeefdead`, APPROVED `2026-07-27T14:31:41Z` on matching head; https://github.com/drivestream-lab/prayog-meta/pull/16#pullrequestreview-4788143334 |
| Source freshness | CURRENT — meta PR #16 head + APPROVED review `commit_id` + PRD digest + map rev 1 + gateflow scope digest match spec header; label `impact-map-lgtm`; repo affected, not deferred/blocked |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-27 |
| Branch | `chore/INIT-GATEFLOW-005-BOUNDINPUT-spec-gateflow` — Draft spec PR #52 |
| Initiative segment | `INIT-GATEFLOW-005-BOUNDINPUT` |
| Status | Draft |
| Review deadline | 2026-07-30 |
| Deciders | PM: programme PM · Domain SME: prayog-pe-team |

## Summary

INIT-GATEFLOW-005-BOUNDINPUT is **buildable** on the delivered INIT-001…003
control plane (wave-start, pin walker, live Cursor AgentRunner, RunStore stages,
programme token). The product gap is concentrated in the **invocation substrate**:
pin prompt resolve/validate/render, thin message-only dispatch (remove invent-prose),
RunStore `handoff_path` + stage `prompt_id`/`prompt_revision`, and ingest-from-stored-path.
No Critical ADR contradiction blocks the spec. Recommendation: keep Gate 2
`spec-pending`, resolve PE questions + NEW-ADR in `/spec-technical-review`, then plan
W0→W1→W2.

**Findings:** 11 total (0 Critical, 5 Should fix, 3 Verify, 3 Gap)

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — wave-start, orchestrator, cursor runner, handoff glob reader, policy, metrics | `tests/unit/test_wave_start.py`, `test_run_orchestrator.py`, `test_cursor_agent_runner.py`, `test_handoff_workflow.py`; `Makefile` `test`; `pyproject.toml` `testpaths = ["tests/unit"]` |
| Live verify | health, webhook, status/metrics, wave-start, pr_thread, board, implement-lane prove-it | `tests/verify/`, `tests/README.md`; `verify_implement_lane.py` (no pin-render assertions) |
| As-built | INIT-001…003 W1 **human_approved**; invent-prose + ambient handoff still live | `docs/specification/as-built/implementation-status.md` |
| Toolchain | `make check` (black/ruff/pyright/import-linter); CI placeholder | `Makefile`, `.github/workflows/ci.yml` |
| Source | API + worker; `CursorAgentRunner._build_prompt` invent-prose; `HandoffReader.find_latest_handoff` globs; pin packages on consumable tree | `src/infra_services/cursor_agent_runner.py`, `src/business_services/handoff_reader.py`, `prayog-skills/skills/development/*/prompts/` |

## ADR pass (pre-T2)

| ADR id | Domain matched | Status |
|--------|----------------|--------|
| ADR-001 | Dual API+worker, Postgres RunStore | Accepted — aligned (additive columns + human Alembic) |
| ADR-002 | Programme token / public_paths | Accepted — aligned (wave-start auth unchanged) |
| ADR-003 | AgentRunner / harness infra vs business orchestration | Accepted — **constrains** PromptResolver placement + message-only runner I/O (see FF-06) |
| ADR-004 | Programme config authority | Accepted — aligned (no YAML programme-file revive; pin consume) |
| ADR-005 | Programme-token mutations | Accepted — aligned (wave-start remains programme-token surface) |
| ADR-006 | Adapter registry fail-closed | Accepted — aligned (Cursor-only; no second runner) |

## MDC pass (pre-T2)

| MDC file | Domain covered | Read / skipped |
|----------|----------------|----------------|
| `architecture.mdc` | Layout; business vs infra | read |
| `dependency-injection.mdc` | `@inject`, service lifecycle | read |
| `infra-services.mdc` | AgentRunner as infra; no business I/O in infra | read |
| `fail-fast.mdc` | Fail closed / no silent fallback | read |
| `pydantic-schemas.mdc` | Models in `src/models/` | read |
| `repository-pattern.mdc` | ORM isolation for RunStore | read |
| `database-migrations.mdc` | Human-owned Alembic for new columns | read |
| `testing-verify-flows.mdc` | unit vs live verify prove-it | read |
| `http-api-conventions.mdc` | Wave-start body fields | read |
| `strong-typing.mdc` | Typed bind map / schema | read |
| `logging-loguru.mdc` | Structured logging | skipped — no wording conflict |
| `python-imports.mdc` / `python-tooling.mdc` | Tooling | skipped — not initiative-specific |
| `spec-driven-development.mdc` | Process | skipped — process only |
| `code-guidelines-index.mdc` | Index | skipped |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-1 / W0 | Resolve pin `prompts/` package | No resolver; pin packages exist under `prayog-skills/skills/development/*/prompts/`; `WorkflowEngine` loads `prayog-skills/workflow.yaml` only | none | none | **gap** |
| REQ-2 / W0 | Bind ticket/initiative/skill_id/workspace/handoff_path | `WaveStartRequest.ticket_id` **optional**; `initiative_id` required; orchestrator `prompt_context` is invent-prose JSON (`run_orchestrator.py` ~410–416) | `test_wave_start.py` | `verify_wave_start.py` | **partial** |
| REQ-3 / W0 | Validate against `schema.yaml` | No schema validate in `src/` | none | none | **gap** |
| REQ-4 / W0 | Simple `{{var}}` render | No renderer in `src/`; packages declare `{{var}}` in pin templates | none | none | **gap** |
| REQ-5 / W0 | Message = render only; remove invent-prose | `CursorAgentRunner._build_prompt` (lines 270–286) still authors skill brief + handoff instructions | `test_cursor_agent_runner.py` (does not anti-hardcode pin) | implement-lane does not assert message source | **drift** (as-built vs target) |
| REQ-6 / W0 | Persist `prompt_id` + `prompt_revision` | `StageSchema` / `StageCreate` lack fields (`run_store_schema.py`, `run_store_models.py`) | none | none | **gap** |
| REQ-7 / W0 | Persist runner + model_id | Already on stages (`StageCreate.runner` / `model_id`) | orchestrator / metrics tests | implement-lane | **exists** (reuse) |
| REQ-8a / W0 | Define + store `run.handoff_path` | `RunSchema` has no `handoff_path` | none | none | **gap** |
| REQ-8b / W1 | Ingest only from stored path | `RunOrchestrator._ingest_handoff_after_stage` → `HandoffReader.find_latest_handoff` ambient globs (`DEFAULT_ARTIFACT_GLOBS`) | `test_handoff_workflow.py` (glob path) | none for isolation | **drift** |
| REQ-9 / W0 | Fail closed before AgentRunner | Patterns exist for auth/concurrent/cursor key; **not** for package/bind/path | wave-start fail tests | — | **partial** |
| REQ-10 / W0 | Prove-it ≥1 Cursor hop on packaged orchestrated skill | Live Cursor + implement-lane exist; **not** bound-input prove-it | — | `verify_implement_lane.py` (no pin render / prompt_id AC) | **partial** |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-1…REQ-4 / W0 | ADR-003 (business orchestration vs infra I/O); ADR-004 (pin consume) | aligned + **NEW-ADR** for PromptResolver module boundary / pin path | FF-06 |
| REQ-5 / W0 | ADR-003 AgentRunner infra slot — message source changes | aligned if runner stays thin infra | — |
| REQ-6 / REQ-8a / W0 | ADR-001 RunStore + human Alembic | aligned | FF-04 (schema work) |
| REQ-8b / W1 | ADR-003 handoff read orchestration is business | aligned; ambient→stored path is product supersession | FF-03 |
| REQ-7 / REQ-9 / REQ-10 | ADR-006 fail-closed; ADR-005 wave-start | aligned | — |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-06 | F13 | “Gateflow defines and persists `handoff_path`”; resolve pin package; thin AgentRunner | ADR-003; ADR-001 | **NEW-ADR** needed for (a) `handoff_path` concrete representation + RunStore contract and (b) PromptResolver as business service feeding message-only AgentRunner — not covered by existing Accepted ADRs beyond layer split |
| FF-11 | F14 | Fail closed; models; human Alembic; verify prove-it | `fail-fast.mdc`, `pydantic-schemas.mdc`, `database-migrations.mdc`, `testing-verify-flows.mdc` | Spec wording **aligns** if TDD places resolve/render in business + Pydantic models + human migration + live verify prove-it; risk only if PromptResolver is wrongly put in infra SDK wrappers |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | none | — |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-02 | F5 | Invent-prose still the live AgentRunner message path; conflicts with REQ-5 target | Spec REQ-5; `CursorAgentRunner._build_prompt` `src/infra_services/cursor_agent_runner.py:270-286`; called from `_run_local_sdk` `:161` |
| FF-03 | F5 | Ambient glob/mtime handoff ingest still SSOT; conflicts with REQ-8b target | Spec REQ-8b; `RunOrchestrator._ingest_handoff_after_stage` `run_orchestrator.py:492`; `HandoffReader.DEFAULT_ARTIFACT_GLOBS` `handoff_reader.py:14-17` |
| FF-04 | F2 | No RunStore fields for `handoff_path` / `prompt_id` / `prompt_revision` | Spec REQ-6, REQ-8a, Q-2; `RunSchema` / `StageSchema` in `run_store_schema.py`; DTOs in `run_store_models.py` |
| FF-06 | F13 | NEW-ADR for handoff_path representation + PromptResolver layer/I/O contract | Spec REQ-8a/8b, REQ-1…5; ADR-003 Option B; no Accepted ADR names pin prompt consume |
| FF-08 | F10 | As-built `ticket_id` optional vs required bind `ticket` — must tighten at automate | Spec REQ-2 / Q-1; `WaveStartRequest.ticket_id` `adapter_models.py:63-66` |

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-05 | F3 | No live-verify artifact asserts pin-rendered message, prompt ids, or stored-path ingest | Spec REQ-10 / Success Criteria; `tests/verify/verify_implement_lane.py` (no prompt/handoff_path matches); `tests/README.md` feature map lacks BOUNDINPUT row |
| FF-09 | F9 | CTR-01 packages present on pin for orchestrated skills; Launchpad sync is still no-op stub — resolve path must work from workspace pin tree without real sync | Spec CTR-01; packages under `prayog-skills/skills/development/{pre-implement,loop-spec,verify,ground-spec}/prompts/`; `LaunchpadClient.sync_harness` stub `launchpad_client.py:31-38` |
| FF-10 | F8 | CI stays unit-only; prove-it remains live verify — aligned with repo methodology; document BOUNDINPUT in `tests/README.md` when planned | `Makefile` `test`; `tests/README.md`; `testing-verify-flows.mdc` |

### Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F2 | No PromptResolver / schema validate / `{{var}}` render modules under `src/` | Spec REQ-1, REQ-3, REQ-4; grep `src/` — no package resolve/render |
| FF-07 | F4 | No unit area for anti-hardcode / bind/render fail-closed | Spec REQ-5/9 Evaluation Strategy; no `test_prompt_*` under `tests/unit/` |
| FF-12 | F11 | Effort drivers: multi-layer touch (API model, RunStore+Alembic, orchestrator, runner, handoff reader, verify) across W0/W1 | Impact surface below |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 Resolve/bind/render | New business service(s) under `src/business_services/`; models under `src/models/`; wire DI | new `tests/unit/test_prompt_*.py` |
| W0 Thin Cursor | `src/infra_services/cursor_agent_runner.py` (`_build_prompt` → accept rendered message); `run_orchestrator.py` stage path | `test_cursor_agent_runner.py`, `test_run_orchestrator.py` |
| W0 Wave-start bind | `src/models/adapter_models.py` (`ticket_id` required on automate); `wave_start_service.py` | `test_wave_start.py`, `verify_wave_start.py` |
| W0 RunStore persist | `run_store_schema.py`, `run_store_models.py`, repository; **human** Alembic | `test_run_store_models.py` |
| W0 Prove-it | `tests/verify/` (extend implement-lane or dedicated script); `tests/README.md` | live verify |
| W1 Ingest-only | `handoff_reader.py`, `run_orchestrator._ingest_handoff_after_stage` | `test_handoff_workflow.py` + dual-run isolation |
| W2 Broaden | same substrate; additional skill ids under pin policy | verify multi-skill |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Residual invent-prose path after W0 | Anti-hardcode unit (REQ-5); code review gate |
| R-2 | Agent writes handoff outside `run.handoff_path` | Bind path in prompt; ingest-only stored path; fail closed (REQ-8b) |
| R-3 | Launchpad harness sync still stub — pin packages must be on workspace tree | Resolve from known pin path (cwd `prayog-skills/` or synced tree); fail closed if missing (FF-09) |
| R-4 | Confusion with INIT-001 artifact globs | Narrow supersession documented in spec; delete/disable ambient SSOT for packaged-skill automate only |
| A-spec | Spec A-1…A-10 (packages delivered, wave-start bind, Cursor-only, etc.) | Confirmed against pin packages + as-built; keep Q-1…Q-4 defaults |

## Recommended spec edits

- Cite as-built symbols explicitly for invent-prose and ambient ingest (already in overview — keep through TDD).
- Record Q-1 default in REQ-2 acceptance: bind `ticket` ← `WaveStartRequest.ticket_id` (required for automate).
- Add planned verify script name for REQ-10 (e.g. extend `verify_implement_lane` or `verify_bound_input`) once TDD picks it — Auto-fix in technical review.
- No product-scope changes required for Gate 1 freshness.

---

## Open items by lane

> Routing rubric: product scope / UX → PM · engineering decisions / ADR → PE ·
> business source-of-truth → Domain SME · naming drift / inferred fixes → Auto-fix.
> Full rubric: `.agents/skills/spec-technical-review/references/governance.md`

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | Wave-start field for bind `ticket`: require `ticket_id` vs add `ticket` alias | no | PE | open | technical review / W0 | Map `ticket` ← `ticket_id`; require non-empty on automate | Spec Q-1; `adapter_models.py:63-66`; FF-08 | pending TDD |
| Q-2 | PE | RunStore column names for `handoff_path`, `prompt_id`, `prompt_revision` | no | PE | open | technical review / W0 | `runs.handoff_path`; `stages.prompt_id` + `stages.prompt_revision` | Spec Q-2; FF-04 | pending TDD |
| Q-3 | PE | Concrete `handoff_path` representation (workspace file path vs URI/blob) | no | PE | open | technical review / W0 | Workspace-absolute file path unique per `run_id` | Spec Q-3; FF-06 NEW-ADR | pending ADR + TDD |
| Q-4 | PE | Prove-it skill id among pin orchestrated packaged skills | no | PE | open | W0 | `pre-implement` | Spec Q-4; pin `dispatch: orchestrated` set | pending W0 evidence |
| FF-06 | PE | NEW-ADR: PromptResolver business ownership + handoff_path storage/ingest contract | yes (for plan) | PE | open | technical review | PromptResolver in `business_services`; AgentRunner message-only; path unique per run | ADR-003; FF-06 | pending `/spec-technical-review` |
| FF-05 | PE | Verify policy for bound-input prove-it assertions | no | PE | open | plan / W0 | Extend implement-lane verify with prompt_id + message-source checks | FF-05; `tests/README.md` | pending TDD/plan |
| FF-09 | PE | Pin package resolve root while Launchpad sync is stub | no | PE | open | W0 | Resolve under workspace `prayog-skills/skills/.../prompts/` (or documented harness path); fail closed | `launchpad_client.py`; CTR-01 | pending TDD |
| AF-1 | auto-fix | Name planned verify module in spec REQ-10 evidence column after TDD | no | agent | open | technical review | Align to chosen script path | FF-05 | pending |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge
1. none

#### Defer — can proceed with documented assumption
1. none — product decisions already confirmed on meta PR #16 (Gateflow-owned `handoff_path`, invent-prose removal, gateflow-only map)

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan
1. **FF-06 / NEW-ADR** — Accept PromptResolver as business service + message-only AgentRunner I/O; choose `handoff_path` storage representation (Q-3) and RunStore field layout (Q-2).

#### Defer with default
1. **Q-1** — require `ticket_id` for automate; bind as `ticket`.
2. **Q-4** — prove-it on `pre-implement`.
3. **FF-05 / FF-09** — verify assertions + pin path while Launchpad sync remains stub.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | none | — | — |

### Auto-fixable (agent resolves — no human needed)

| # | Item | Fix |
|---|------|-----|
| AF-1 | REQ-10 verify evidence path unnamed | After TDD picks script, update spec evidence column on same branch |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Unit/verify/as-built/toolchain inventoried |
| F2 Spec → code map | FAIL | FF-01, FF-04 — expected gaps for new substrate |
| F3 Spec → verify map | FAIL | FF-05 — no BOUNDINPUT prove-it assertions yet |
| F4 Spec → unit map | FAIL | FF-07 — no prompt unit area yet |
| F5 As-built drift | FAIL | FF-02, FF-03, FF-08 — invent-prose + ambient ingest + optional ticket |
| F6 Docs drift | PASS | Spec aligns with `tests/README.md` / AGENTS lane naming; BOUNDINPUT row deferred to plan |
| F7 Overlap risk | PASS | No duplicate unit+live journey for BOUNDINPUT yet (nothing to overlap) |
| F8 CI vs live boundary | PASS | FF-10 informational — CI unit-only; prove-it live |
| F9 Cross-service touch | PASS | FF-09 Verify — CTR-01 packages present; consume-only |
| F10 Assumptions | FAIL | FF-08 ticket required vs optional as-built |
| F11 Effort drivers | PASS | FF-12 Gap — multi-layer W0/W1 surface listed |
| F12 PM questions | PASS | No blocking PM gaps |
| F13 ADR conformance | FAIL | FF-06 NEW-ADR (no Critical contradiction) |
| F14 MDC conformance | PASS | FF-11 aligned if TDD follows business/infra split |

**Feasibility verdict:** FINDINGS — buildable; proceed to `/spec-technical-review` (not straight to plan).

---

## Next steps

> This report lives on the spec PR branch alongside the spec draft.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → none blocking on meta PRD PR #16.

**PE questions** → discuss on Draft spec PR #52; run `/spec-technical-review` next.
  PE accepts TDD/ADRs in **files** (`Draft` → `Accepted`); do **not** set
  `spec-lgtm` until the full package includes the implementation plan.

**Domain clarifications** → none.

**Auto-fixable items** → AF-1 after TDD (defer until technical review).

```
Draft spec PR: chore/INIT-GATEFLOW-005-BOUNDINPUT-spec-gateflow  (spec-pending) #52
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] All blocking Domain clarifications answered (none)
  [ ] Spec updated only if PE answers change defaults (same branch)
  [ ] Proceed: /spec-technical-review (PE questions + NEW-ADR exist)
  [ ] After spec + feasibility + TDD/ADRs + plan on branch:
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: board-seed from plan §9 — then /pre-implement → /loop-spec
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-005-BOUNDINPUT.md
    digest: sha256:c97aec5c6c731823f601d20078782b4e0219cb134d42822b8cbabf959d767cf7
  blockers:
    - FF-06
  signals:
    draft_verdict: FINDINGS
    finding_counts: {critical: 0, should_fix: 5, verify: 3, gap: 3}
    new_adr: true
    ripple_action: continue
    map_revision: 1
    prd_digest: sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970
    scope_digest: sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b
    meta_pr_head_sha: 0b6b11e4470517842affb894d7ea581c3819ead3
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/52
    gate2_label: spec-pending
    open_pe_questions: Q-1,Q-2,Q-3,Q-4,FF-06,FF-05,FF-09
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
```
